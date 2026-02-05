from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.module import ModuleCreate, ModuleResponse, ModuleUpdate
from app.models.module import Module

router = APIRouter()

@router.post("/", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
def create_module(module: ModuleCreate, db: Session = Depends(get_db)):
    """Create a new learning module"""
    db_module = Module(**module.dict())
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module

@router.get("/{module_id}", response_model=ModuleResponse)
def get_module(module_id: int, db: Session = Depends(get_db)):
    """Get module by ID"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module

@router.get("/", response_model=List[ModuleResponse])
def list_modules(
    skip: int = 0, 
    limit: int = 100, 
    category: str = None,
    db: Session = Depends(get_db)
):
    """List all modules with optional filtering"""
    query = db.query(Module)
    if category:
        query = query.filter(Module.category == category)
    modules = query.offset(skip).limit(limit).all()
    return modules

@router.put("/{module_id}", response_model=ModuleResponse)
def update_module(module_id: int, module: ModuleUpdate, db: Session = Depends(get_db)):
    """Update module"""
    db_module = db.query(Module).filter(Module.id == module_id).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    for field, value in module.dict(exclude_unset=True).items():
        setattr(db_module, field, value)
    
    db.commit()
    db.refresh(db_module)
    return db_module
