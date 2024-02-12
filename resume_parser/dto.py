from typing import Optional

from pydantic import BaseModel


class CriteriaDTO(BaseModel):
    position: str
    location: Optional[str] = None
    salary_from: Optional[int] = None
    salary_to: Optional[int] = None
    experience: Optional[float] = None
    skills_and_keywords: Optional[str] = None
