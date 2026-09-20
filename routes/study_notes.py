from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from models.models import StudyNote, User
from models.schemas import StudyNoteCreate, StudyNoteUpdate, StudyNoteResponse
from security.auth import get_current_user

router = APIRouter(
    prefix="/study-notes",
    tags=["Estudos"]
)

@router.post("/", response_model=StudyNoteResponse, status_code=201)
def create_study_note(
    note: StudyNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria uma nova nota de estudo com os dados fornecidos."""
    db_note = StudyNote(
        title=note.title,
        content=note.content,
        tags=note.tags,
        owner_id=current_user.id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return db_note

@router.get("/", response_model=List[StudyNoteResponse])
def get_study_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna a lista de notas de estudo apenas do usuário logado."""
    notes = db.query(StudyNote).filter(StudyNote.owner_id == current_user.id).all()
    return notes

@router.put("/{note_id}", response_model=StudyNoteResponse)
def update_study_note(
    note_id: int,
    note_update: StudyNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza parcialmente uma nota existente, se pertencer ao usuário logado."""
    db_note = db.query(StudyNote).filter(StudyNote.id == note_id, StudyNote.owner_id == current_user.id).first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Nota não encontrada ou não pertence a você")

    update_data = note_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_note, field, value)

    db.commit()
    db.refresh(db_note)

    return db_note

@router.delete("/{note_id}", status_code=204)
def delete_study_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deleta uma nota existente, se pertencer ao usuário."""
    db_note = db.query(StudyNote).filter(StudyNote.id == note_id, StudyNote.owner_id == current_user.id).first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Nota não encontrada ou não pertence a você")

    db.delete(db_note)
    db.commit()
