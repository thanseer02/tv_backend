from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from app.schemas.schemas import UrlItemCreate, UrlItemUpdate, UrlItemResponse
from app.db.memory_store import db
from app.api.deps import get_current_user

router = APIRouter(prefix="/urls", tags=["URLs Management"])

@router.get("", response_model=List[UrlItemResponse])
def get_urls(
    search: Optional[str] = Query(None, description="Search term for name, url, description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status (active/inactive)"),
    environment: Optional[str] = Query(None, description="Filter by environment"),
    current_user: dict = Depends(get_current_user),
):
    items = db.list_urls()
    
    if search:
        s = search.lower()
        items = [
            i for i in items
            if s in i.get("title", "").lower()
            or s in i.get("name", "").lower()
            or s in i.get("url", "").lower()
            or s in i.get("address", "").lower()
            or s in i.get("description", "").lower()
            or s in i.get("notes", "").lower()
        ]

    if category:
        items = [i for i in items if i.get("category", "").lower() == category.lower()]

    if status and status.lower() != "all":
        items = [i for i in items if i.get("status", "").lower() == status.lower()]

    if environment and environment.lower() != "all":
        items = [i for i in items if i.get("environment", "").lower() == environment.lower()]

    return items

@router.get("/{url_id}", response_model=UrlItemResponse)
def get_url_by_id(url_id: str, current_user: dict = Depends(get_current_user)):
    item = db.get_url(url_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL entry not found")
    return item

@router.post("", response_model=UrlItemResponse, status_code=status.HTTP_201_CREATED)
def create_url(payload: UrlItemCreate, current_user: dict = Depends(get_current_user)):
    data = payload.model_dump()
    new_item = db.add_url(data)
    return new_item

@router.put("/{url_id}", response_model=UrlItemResponse)
def update_url(url_id: str, payload: UrlItemUpdate, current_user: dict = Depends(get_current_user)):
    data = payload.model_dump(exclude_unset=True)
    updated = db.update_url(url_id, data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL entry not found")
    return updated

@router.delete("/{url_id}")
def delete_url(url_id: str, current_user: dict = Depends(get_current_user)):
    success = db.delete_url(url_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL entry not found")
    return {"success": True, "id": url_id, "message": "URL entry deleted successfully"}

@router.patch("/{url_id}/toggle-status", response_model=UrlItemResponse)
def toggle_url_status(url_id: str, current_user: dict = Depends(get_current_user)):
    updated = db.toggle_url_status(url_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL entry not found")
    return updated

