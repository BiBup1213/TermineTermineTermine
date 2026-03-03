from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import delete
from sqlmodel import Session, select

from app.db import get_session
from app.models import Poll, PollDay
from app.schemas import (
    CreatePollRequest,
    CreatePollResponse,
    PatchPollRequest,
    PollResponse,
)
from app.security import generate_token, hash_token, verify_token

router = APIRouter(prefix="/api/polls", tags=["polls"])


def _require_poll(session: Session, poll_id: UUID) -> Poll:
    poll = session.get(Poll, poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    return poll


def _require_admin_token(poll: Poll, admin_token: str | None) -> None:
    if not admin_token or not verify_token(admin_token, poll.admin_token_hash):
        raise HTTPException(status_code=403, detail="Invalid admin token")


def _validate_days(days: list[date], range_from: date, range_to: date) -> None:
    for d in days:
        if d < range_from or d > range_to:
            raise HTTPException(status_code=422, detail="Candidate day outside poll range")


@router.post("", response_model=CreatePollResponse, status_code=status.HTTP_201_CREATED)
def create_poll(payload: CreatePollRequest, session: Session = Depends(get_session)) -> CreatePollResponse:
    admin_token = generate_token()
    poll = Poll(
        title=payload.title.strip(),
        description=payload.description,
        timezone=payload.timezone,
        range_from=payload.date_range_from,
        range_to=payload.date_range_to,
        admin_token_hash=hash_token(admin_token),
    )
    session.add(poll)
    session.commit()
    session.refresh(poll)

    return CreatePollResponse(poll_id=poll.id, admin_token=admin_token)


@router.get("/{poll_id}", response_model=PollResponse)
def get_poll(poll_id: UUID, session: Session = Depends(get_session)) -> PollResponse:
    poll = _require_poll(session, poll_id)
    days = session.exec(select(PollDay.day).where(PollDay.poll_id == poll.id).order_by(PollDay.day)).all()
    return PollResponse(
        id=poll.id,
        title=poll.title,
        description=poll.description,
        timezone=poll.timezone,
        date_range_from=poll.range_from,
        date_range_to=poll.range_to,
        is_locked=poll.is_locked,
        candidate_days=list(days),
        created_at=poll.created_at,
    )


@router.patch("/{poll_id}", response_model=PollResponse)
def patch_poll(
    poll_id: UUID,
    payload: PatchPollRequest,
    session: Session = Depends(get_session),
    x_admin_token: str | None = Header(default=None),
) -> PollResponse:
    poll = _require_poll(session, poll_id)
    _require_admin_token(poll, x_admin_token)

    if payload.candidate_days is not None:
        uniq_days = sorted(set(payload.candidate_days))
        _validate_days(uniq_days, poll.range_from, poll.range_to)

        session.exec(delete(PollDay).where(PollDay.poll_id == poll.id))
        for d in uniq_days:
            session.add(PollDay(poll_id=poll.id, day=d))

    if payload.is_locked is not None:
        poll.is_locked = payload.is_locked

    session.add(poll)
    session.commit()

    return get_poll(poll.id, session)
