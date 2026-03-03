from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models import VoteChoiceEnum


class CreatePollRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    timezone: str = "Europe/Berlin"
    date_range_from: date
    date_range_to: date

    @field_validator("date_range_to")
    @classmethod
    def validate_range(cls, v: date, info):
        date_from = info.data.get("date_range_from")
        if date_from and v < date_from:
            raise ValueError("date_range_to must be on or after date_range_from")
        return v


class CreatePollResponse(BaseModel):
    poll_id: UUID
    admin_token: str


class PollResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    timezone: str
    date_range_from: date
    date_range_to: date
    is_locked: bool
    candidate_days: list[date]
    created_at: datetime


class PatchPollRequest(BaseModel):
    candidate_days: list[date] | None = None
    is_locked: bool | None = None


class VoteChoiceInput(BaseModel):
    day: date
    choice: VoteChoiceEnum


class SubmitVoteRequest(BaseModel):
    participant_name: str = Field(min_length=1, max_length=120)
    participant_token: str = Field(min_length=8, max_length=200)
    choices: list[VoteChoiceInput]


class SubmitVoteResponse(BaseModel):
    vote_id: UUID
    updated_at: datetime


class DayResult(BaseModel):
    day: date
    yes: int
    maybe: int
    no: int
    score: int
    is_top: bool


class ParticipantRow(BaseModel):
    participant_name: str
    choices: dict[date, VoteChoiceEnum]


class ResultsResponse(BaseModel):
    poll_id: UUID
    title: str
    is_locked: bool
    sorted_days: list[DayResult]
    participants: list[ParticipantRow]
