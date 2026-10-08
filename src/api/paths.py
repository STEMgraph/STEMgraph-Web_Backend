import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.keycloak import get_current_user
from services.db import get_db

router = APIRouter(prefix="/paths", tags=["paths"])


class PathRequest(BaseModel):
    name: str        # Name des Lernpfads, z.B. "Grundlagen Mathematik"


class PathNodeRequest(BaseModel):
    node_id: str     # Knoten-ID, der dem Pfad hinzugefuegt werden soll


class ReorderRequest(BaseModel):
    node_ids: list[str]  # Knoten in gewuenschter Reihenfolge


# ---------------------------------------------------------
# PATHS (public list / detail, owner/admin write)
# ---------------------------------------------------------
@router.get("")
def get_paths(db=Depends(get_db)):
    """Gibt alle Lernpfade zurueck (oeffentlich, kein Login noetig)."""
    with db.cursor() as cursor:
        cursor.execute("SELECT id, name, creator_id, created_at FROM learning_paths")
        return cursor.fetchall()


@router.get("/{pathId}")
def get_path(pathId: str, db=Depends(get_db)):
    """Gibt einen Lernpfad mit all seinen Knoten zurueck (oeffentlich, kein Login noetig)."""
    with db.cursor() as cursor:
        cursor.execute("SELECT id, name, creator_id, created_at FROM learning_paths WHERE id = %s", (pathId,))
        path = cursor.fetchone()
        if not path:
            raise HTTPException(status_code=404, detail="Path not found")
        cursor.execute("SELECT node_id FROM learning_path_nodes WHERE path_id = %s ORDER BY position", (pathId,))
        nodes = cursor.fetchall()
        path["nodes"] = [row["node_id"] for row in nodes]
        return path


@router.post("")
def create_path(body: PathRequest, db=Depends(get_db), user=Depends(get_current_user)):
    """Erstellt einen neuen Lernpfad. Nur fuer Teacher und Admins."""
    if "teacher" not in user["roles"] and "admin" not in user["roles"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    path_id = str(uuid.uuid4())
    with db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO learning_paths (id, name, creator_id) VALUES (%s, %s, %s)",
            (path_id, body.name, user["sub"])
        )
    db.commit()
    return {"id": path_id, "name": body.name}


@router.put("/{pathId}")
def rename_path(pathId: str, body: PathRequest, db=Depends(get_db), user=Depends(get_current_user)):
    """Benennt einen Lernpfad um. Nur der Ersteller oder ein Admin darf das."""
    with db.cursor() as cursor:
        cursor.execute("SELECT creator_id FROM learning_paths WHERE id = %s", (pathId,))
        path = cursor.fetchone()
        if not path:
            raise HTTPException(status_code=404, detail="Path not found")
        if path["creator_id"] != user["sub"] and "admin" not in user["roles"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        cursor.execute("UPDATE learning_paths SET name = %s WHERE id = %s", (body.name, pathId))
    db.commit()
    return {"status": "ok"}


@router.delete("/{pathId}")
def delete_path(pathId: str, db=Depends(get_db), user=Depends(get_current_user)):
    """Loescht einen Lernpfad. Nur der Ersteller oder ein Admin darf das."""
    with db.cursor() as cursor:
        cursor.execute("SELECT creator_id FROM learning_paths WHERE id = %s", (pathId,))
        path = cursor.fetchone()
        if not path:
            raise HTTPException(status_code=404, detail="Path not found")
        if path["creator_id"] != user["sub"] and "admin" not in user["roles"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        cursor.execute("DELETE FROM learning_paths WHERE id = %s", (pathId,))
    db.commit()
    return {"status": "ok"}


# ---------------------------------------------------------
# PATH NODES (owner/admin write)
# ---------------------------------------------------------
@router.post("/{pathId}/nodes")
def add_node_to_path(pathId: str, body: PathNodeRequest, db=Depends(get_db), user=Depends(get_current_user)):
    """Fuegt einen Knoten zu einem Lernpfad hinzu. Nur der Ersteller oder ein Admin darf das."""
    with db.cursor() as cursor:
        cursor.execute("SELECT creator_id FROM learning_paths WHERE id = %s", (pathId,))
        path = cursor.fetchone()
        if not path:
            raise HTTPException(status_code=404, detail="Path not found")
        if path["creator_id"] != user["sub"] and "admin" not in user["roles"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        cursor.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 AS next_pos FROM learning_path_nodes WHERE path_id = %s",
            (pathId,)
        )
        next_pos = cursor.fetchone()["next_pos"]
        cursor.execute(
            "INSERT IGNORE INTO learning_path_nodes (path_id, node_id, position) VALUES (%s, %s, %s)",
            (pathId, body.node_id, next_pos)
        )
    db.commit()
    return {"status": "ok"}


@router.put("/{pathId}/nodes/reorder")
def reorder_path_nodes(pathId: str, body: ReorderRequest, db=Depends(get_db), user=Depends(get_current_user)):
    """Setzt die Reihenfolge der Knoten im Lernpfad. Nur der Ersteller oder ein Admin darf das."""
    with db.cursor() as cursor:
        cursor.execute("SELECT creator_id FROM learning_paths WHERE id = %s", (pathId,))
        path = cursor.fetchone()
        if not path:
            raise HTTPException(status_code=404, detail="Path not found")
        if path["creator_id"] != user["sub"] and "admin" not in user["roles"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        for pos, node_id in enumerate(body.node_ids):
            cursor.execute(
                "UPDATE learning_path_nodes SET position = %s WHERE path_id = %s AND node_id = %s",
                (pos, pathId, node_id)
            )
    db.commit()
    return {"status": "ok"}


@router.delete("/{pathId}/nodes/{nodeId}")
def remove_node_from_path(pathId: str, nodeId: str, db=Depends(get_db), user=Depends(get_current_user)):
    """Entfernt einen Knoten aus einem Lernpfad. Nur der Ersteller oder ein Admin darf das."""
    with db.cursor() as cursor:
        cursor.execute("SELECT creator_id FROM learning_paths WHERE id = %s", (pathId,))
        path = cursor.fetchone()
        if not path:
            raise HTTPException(status_code=404, detail="Path not found")
        if path["creator_id"] != user["sub"] and "admin" not in user["roles"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        cursor.execute(
            "DELETE FROM learning_path_nodes WHERE path_id = %s AND node_id = %s",
            (pathId, nodeId)
        )
    db.commit()
    return {"status": "ok"}
