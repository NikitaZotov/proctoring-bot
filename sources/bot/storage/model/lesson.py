from pydantic import BaseModel, Field, validator
from sources.bot.storage.model.lesson_type import LessonType
from sources.bot.storage.model.subgroup import Subgroup
from datetime import datetime
from typing import List

class Lesson(BaseModel):
    """
    Stores lesson data.
    """
    date: datetime = None
    short_name: str = Field(alias="subject")
    week_number: List[int] = Field(alias="weekNumber")
    lesson_type: LessonType = Field(alias="lessonTypeAbbrev")
    subgroup: Subgroup = Field(alias="numSubgroup")
