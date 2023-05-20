from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base



class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    name = Column(String(50))
    email = Column(String(50))
    password = Column(String(255))
    is_active = Column(Boolean, default=True)

    # todo = relationship("Todo", back_populates="owner")



class Todo(Base):
    __tablename__ = "todo"

    id = Column(String(36), primary_key=True)
    title = Column(String(50))
    desc = Column(String(50))
    owner = Column(String(36), ForeignKey('users.id'))
    img = Column(String(59))
    is_active = Column(Boolean, default=True)

    user = relationship("User", backref="todo")





