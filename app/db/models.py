from sqlalchemy import Column, Integer, String, Text, Time, Boolean, ForeignKey, ARRAY, TIMESTAMP, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.sql import func
from typing import List, Optional

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    phone_number = Column(String(20), nullable=False, unique=True)
    aws_phone_number_id = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    
    # Relationship to alarms
    alarms: Mapped[List["Alarm"]] = relationship(back_populates="user")

class Alarm(Base):
    __tablename__ = 'alarms'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = Column(Text, nullable=False)
    time = Column(Time, nullable=False)
    days_of_week = Column(ARRAY(Integer), nullable=False)  # Days of the week array Monday = 0, Sunday = 6
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationship to user
    user: Mapped["User"] = relationship(back_populates="alarms")
    
    # One-to-one relationship with AlarmJob
    alarm_job: Mapped[Optional["AlarmJob"]] = relationship("AlarmJob", back_populates="alarm", uselist=False)

class AlarmJob(Base):
    __tablename__ = 'alarm_jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alarm_id = Column(Integer, ForeignKey('alarms.id', ondelete='CASCADE'), nullable=False, unique=True)  # Ensure one-to-one
    sms_job_id = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    
    # Relationship to alarm
    alarm: Mapped["Alarm"] = relationship("Alarm", back_populates="alarm_job")
