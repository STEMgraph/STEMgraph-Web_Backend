from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.keycloak import get_current_user
from services.db import get_db

router = APIRouter(prefix="/users", tags=["users"])


class NodeRequest(BaseModel):
    node_id: str


# ---------------------------------------------------------
# TODO
# ---------------------------------------------------------
@router.get("/{userId}/todo")
def get_todo(userId: str, db=Depends(get_db), user=Depends(get_current_user)):
    if user["sub"] != userId and "admin" not in user["roles"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT node_id FROM user_nodes WHERE user_id = %s AND type = 'todo'",
            (userId,)
        )
        return cursor.fetchall()


@router.post("/{userId}/todo")
def add_todo(userId: str, body: NodeRequest, db=Depends(get_db), user=Depends(get_current_user)):
    if user["sub"] != userId and "admin" not in user["roles"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    with db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO user_nodes (user_id, node_id, type) VALUES (%s, %s, 'todo') ON DUPLICATE KEY UPDATE type = 'todo'",
            (userId, body.node_id)
        )
    db.commit()
    return {"status": "ok"}


@router.delete("/{userId}/todo/{nodeId}")
def delete_todo(userId: str, nodeId: str, db=Depends(get_db), user=Depends(get_current_user)):
    if user["sub"] != userId and "admin" not in user["roles"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    with db.cursor() as cursor:
        cursor.execute(
            "DELETE FROM user_nodes WHERE user_id = %s AND node_id = %s AND type = 'todo'",
            (userId, nodeId)
        )
    db.commit()
    return {"status": "ok"}


# ---------------------------------------------------------
# FINISHED
# ---------------------------------------------------------
@router.get("/{userId}/finished")
def get_finished(userId: str, db=Depends(get_db), user=Depends(get_current_user)):
    if user["sub"] != userId and "admin" not in user["roles"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT node_id FROM user_nodes WHERE user_id = %s AND type = 'completed'",
            (userId,)
        )
        return cursor.fetchall()


@router.post("/{userId}/finished")
def add_finished(userId: str, body: NodeRequest, db=Depends(get_db), user=Depends(get_current_user)):
    if user["sub"] != userId and "admin" not in user["roles"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    with db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO user_nodes (user_id, node_id, type) VALUES (%s, %s, 'completed') ON DUPLICATE KEY UPDATE type = 'completed'",
            (userId, body.node_id)
        )
    db.commit()
    return {"status": "ok"}


@router.delete("/{userId}/finished/{nodeId}")
def delete_finished(userId: str, nodeId: str, db=Depends(get_db), user=Depends(get_current_user)):
    if user["sub"] != userId and "admin" not in user["roles"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    with db.cursor() as cursor:
        cursor.execute(
            "DELETE FROM user_nodes WHERE user_id = %s AND node_id = %s AND type = 'completed'",
            (userId, nodeId)
        )
    db.commit()
    return {"status": "ok"}
