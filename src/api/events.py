from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from auth.keycloak import get_current_user, get_optional_user
from services.db import get_db

router = APIRouter(prefix="/events", tags=["events"])


class EventRequest(BaseModel):
    event_type: str
    node_id: str | None = None
    path_id: str | None = None


@router.post("")
def track_event(body: EventRequest, db=Depends(get_db), user=Depends(get_optional_user)):
    """Speichert ein Frontend-Event. Eingeloggte User werden per Token erkannt, sonst user_id '0'."""
    with db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO frontend_events (user_id, event_type, node_id, path_id) VALUES (%s, %s, %s, %s)",
            (user["sub"], body.event_type, body.node_id, body.path_id)
        )
    db.commit()
    return {"status": "ok"}


@router.get("")
def get_events(type: str = Query(None), db=Depends(get_db), user=Depends(get_current_user)):
    """Gibt aggregierte Event-Daten zurueck. Nur fuer Admins und Teacher."""
    if "admin" not in user["roles"] and "teacher" not in user["roles"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    with db.cursor() as cursor:
        if type == "users":
            cursor.execute(
                "SELECT COUNT(DISTINCT user_id) AS total_users FROM frontend_events WHERE user_id != '0'"
            )
            total = cursor.fetchone()["total_users"]
            cursor.execute(
                "SELECT COUNT(DISTINCT user_id) AS active_7d FROM frontend_events WHERE user_id != '0' AND created_at >= NOW() - INTERVAL 7 DAY"
            )
            active_7d = cursor.fetchone()["active_7d"]
            cursor.execute(
                "SELECT COUNT(DISTINCT user_id) AS active_30d FROM frontend_events WHERE user_id != '0' AND created_at >= NOW() - INTERVAL 30 DAY"
            )
            active_30d = cursor.fetchone()["active_30d"]
            return {"total_users": total, "active_7d": active_7d, "active_30d": active_30d}
        elif type in ("link_open", "todo_add", "todo_remove", "finished"):
            cursor.execute(
                "SELECT node_id, COUNT(*) AS count FROM frontend_events WHERE event_type = %s GROUP BY node_id ORDER BY count DESC",
                (type,)
            )
        elif type == "path_load":
            cursor.execute(
                "SELECT path_id, COUNT(*) AS count FROM frontend_events WHERE event_type = %s GROUP BY path_id ORDER BY count DESC",
                (type,)
            )
        else:
            cursor.execute(
                "SELECT event_type, COUNT(*) AS count FROM frontend_events GROUP BY event_type ORDER BY count DESC"
            )
        return cursor.fetchall()
