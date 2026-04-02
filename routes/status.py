from fastapi import APIRouter, HTTPException
from routes.apply import get_store

router = APIRouter()

@router.get("/{application_id}")
async def get_application_status(application_id: str):
    store = get_store()
    if application_id not in store:
        raise HTTPException(status_code=404, detail="Candidature introuvable.")
    return {"success": True, "application": store[application_id]}

@router.get("")
async def list_applications():
    store = get_store()
    return {
        "success": True,
        "total": len(store),
        "applications": list(store.values())
    }
