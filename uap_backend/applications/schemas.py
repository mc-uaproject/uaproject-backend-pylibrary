from datetime import datetime
from enum import Enum

from uap_backend.base.schemas import BaseUserBackendModel


class ApplicationStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    REVIEW = "REVIEW"
    EDITING = "EDITING"
    NOT_SENT = "NOT_SENT"


class ApplicationForm(BaseUserBackendModel):
    status: ApplicationStatus = ApplicationStatus.NOT_SENT
    birth_date: datetime | None
    launcher: str | None
    server_source: str | None
    private_server_experience: str | None
    useful_skills: str | None
    conflict_reaction: str | None
    quiz_answer: str | None
