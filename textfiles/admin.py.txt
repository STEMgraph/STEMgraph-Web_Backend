from fastapi import APIRouter, BackgroundTasks
from services.updater import refresh_challenge_db_task

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/refresh")
def refresh_database(background_tasks: BackgroundTasks):
    background_tasks.add_task(refresh_challenge_db_task)
    return {"status": "refresh started"}
