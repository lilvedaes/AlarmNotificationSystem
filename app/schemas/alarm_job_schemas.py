from pydantic import BaseModel
from typing import Optional

# AlarmJob Schemas
class AlarmJobBase(BaseModel):
    alarm_id: int
    sms_job_id: Optional[str] = None

# AlarmJobCreate will include all AlarmJobBase fields
class AlarmJobCreate(AlarmJobBase):
    pass

# The AlarmJob schema will include all AlarmJobBase fields + id
class AlarmJob(AlarmJobBase):
    id: int

    class Config:
        from_attributes = True