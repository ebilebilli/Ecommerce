from sqlalchemy.orm import Session
from typing import TypeVar, Generic, List, Optional
from uuid import UUID
from sqlalchemy import update, delete

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, model: T, db_session: Session):
        self.model = model
        self.db_session = db_session

    def create(self, obj_in) -> T:
        db_obj = self.model(**obj_in.dict())
        self.db_session.add(db_obj)
        self.db_session.commit()
        self.db_session.refresh(db_obj)
        return db_obj

    def get(self, id: UUID) -> Optional[T]:
        return self.db_session.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.db_session.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: UUID, obj_in) -> Optional[T]:
        db_obj = self.get(id)
        if not db_obj:
            return None
        for key, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, key, value)
        self.db_session.commit()
        self.db_session.refresh(db_obj)
        return db_obj

    def delete(self, id: UUID) -> bool:
        db_obj = self.get(id)
        if not db_obj:
            return False
        self.db_session.delete(db_obj)
        self.db_session.commit()
        return True