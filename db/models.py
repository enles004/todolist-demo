from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False)
    password = Column(String(80), nullable=False)
    confirm_password = Column(String(80), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    created = Column(DateTime(timezone=True), default=func.now())
    projects = relationship("Project", backref="user")
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    completed = Column(Boolean, default=False)
    name = Column(String(1000))
    tasks = relationship("Task", backref="project")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title_task = Column(String(10000), nullable=False)
    name_task = Column(String(10000), nullable=False)
    expiry_task = Column(DateTime, default=None)
    action_task = Column(Boolean, default=False)
    date_completed = Column(DateTime, default=None)
    created_task = Column(DateTime(timezone=True), default=func.now())


# many to many
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


class Role_Per(Base):
    __tablename__ = "role_per"

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    per_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
