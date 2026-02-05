from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.progress import ProgressCreate, ProgressResponse, ProgressUpdate
from app.models.progress import Progress

router = APIRouter()

@router.post("/", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED)
def create_progress(progress: ProgressCreate, db: Session = Depends(get_db)):
    """Record progress for a user on a module"""
    db_progress = Progress(**progress.dict())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

@router.get("/user/{user_id}", response_model=List[ProgressResponse])
def get_user_progress(user_id: int, db: Session = Depends(get_db)):
    """Get all progress records for a user"""
    progress = db.query(Progress).filter(Progress.user_id == user_id).all()
    return progress

@router.get("/user/{user_id}/module/{module_id}", response_model=ProgressResponse)
def get_module_progress(user_id: int, module_id: int, db: Session = Depends(get_db)):
    """Get progress for a specific user and module"""
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.module_id == module_id
    ).first()
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")
    return progress

@router.put("/{progress_id}", response_model=ProgressResponse)
def update_progress(progress_id: int, progress: ProgressUpdate, db: Session = Depends(get_db)):
    """Update progress record"""
    db_progress = db.query(Progress).filter(Progress.id == progress_id).first()
    if not db_progress:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    for field, value in progress.dict(exclude_unset=True).items():
        setattr(db_progress, field, value)
    
    db.commit()
    db.refresh(db_progress)
    return db_progress
