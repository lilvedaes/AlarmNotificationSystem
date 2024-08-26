from sqlalchemy import Column, Integer, String, Text, Time, Boolean, ForeignKey, ARRAY, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default='CURRENT_TIMESTAMP')
    
    # Relationship to alarms
    alarms = relationship("Alarm", back_populates="user")

class Alarm(Base):
    __tablename__ = 'alarms'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = Column(Text, nullable=False)
    time = Column(Time, nullable=False)
    days_of_week = Column(ARRAY(Integer), nullable=False)  # Days of the week array Monday = 0, Sunday = 6
    is_active = Column(Boolean, default=True)
    send_sms = Column(Boolean, default=False)
    send_email = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), default='CURRENT_TIMESTAMP')
    updated_at = Column(TIMESTAMP(timezone=True), default='CURRENT_TIMESTAMP', onupdate='CURRENT_TIMESTAMP')
    
    # Relationship to users
    user = relationship("User", back_populates="alarms")
