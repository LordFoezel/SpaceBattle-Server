# app/routes/users.py
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.users import UserCreate, UserUpdate
from app.repositories import users as repo

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[dict])
def list_users(offset: int = 0, limit: int = 50):
    return [u.model_dump() for u in repo.list_users(offset, limit)]

@router.get("/{user_id}", response_model=dict)
def get_user(user_id: int):
    u = repo.get_by_id(user_id)
    if not u:
        raise HTTPException(404, "User not found")
    return u.model_dump()

@router.post("/", response_model=dict, status_code=201)
def create_user(payload: UserCreate):
    u = repo.create(payload)
    return u.model_dump()

@router.patch("/{user_id}", response_model=dict)
def update_user(user_id: int, payload: UserUpdate):
    u = repo.update(user_id, payload)
    if not u:
        raise HTTPException(404, "User not found")
    return u.model_dump()

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int):
    affected = repo.delete(user_id)
    if affected == 0:
        raise HTTPException(404, "User not found")
