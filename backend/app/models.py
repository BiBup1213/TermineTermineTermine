from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
import uuid

from sqlalchemy import Column, Date, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class VoteChoiceEnum(str, Enum):
    no = "no"
    maybe = "maybe"
    yes = "yes"


class Poll(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: str | None = None
    timezone: str = Field(default="Europe/Berlin")
    range_from: date
    range_to: date
    is_locked: bool = Field(default=False)
    admin_token_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    days: list[PollDay] = Relationship(back_populates="poll")
    votes: list[Vote] = Relationship(back_populates="poll")


class PollDay(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("poll_id", "day", name="uq_pollday_poll_day"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    poll_id: uuid.UUID = Field(foreign_key="poll.id", index=True)
    day: date = Field(sa_column=Column(Date, nullable=False))

    poll: Poll | None = Relationship(back_populates="days")


class Vote(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "poll_id",
            "participant_token_hash",
            name="uq_vote_poll_participant_token_hash",
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    poll_id: uuid.UUID = Field(foreign_key="poll.id", index=True)
    participant_name: str
    participant_token_hash: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    poll: Poll | None = Relationship(back_populates="votes")
    choices: list[VoteChoice] = Relationship(back_populates="vote")


class VoteChoice(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("vote_id", "day", name="uq_votechoice_vote_day"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    vote_id: uuid.UUID = Field(foreign_key="vote.id", index=True)
    day: date = Field(sa_column=Column(Date, nullable=False))
    choice: VoteChoiceEnum = Field(default=VoteChoiceEnum.no)

    vote: Vote | None = Relationship(back_populates="choices")
