from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from sqlmodel import Session, select

from app.db import get_session
from app.models import Poll, PollDay, Vote, VoteChoice
from app.schemas import SubmitVoteRequest, SubmitVoteResponse
from app.security import hash_token

router = APIRouter(prefix="/api/polls", tags=["votes"])


@router.post("/{poll_id}/votes", response_model=SubmitVoteResponse)
def submit_vote(
    poll_id: UUID,
    payload: SubmitVoteRequest,
    session: Session = Depends(get_session),
) -> SubmitVoteResponse:
    poll = session.get(Poll, poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    if poll.is_locked:
        raise HTTPException(status_code=423, detail="Poll is locked")

    candidate_days = set(
        session.exec(select(PollDay.day).where(PollDay.poll_id == poll.id)).all()
    )
    if not candidate_days:
        raise HTTPException(status_code=422, detail="No candidate days configured")

    submitted_days = {item.day for item in payload.choices}
    invalid_days = submitted_days - candidate_days
    if invalid_days:
        raise HTTPException(status_code=422, detail="Vote contains invalid days")

    participant_token_hash = hash_token(payload.participant_token)
    vote = session.exec(
        select(Vote).where(
            Vote.poll_id == poll.id,
            Vote.participant_token_hash == participant_token_hash,
        )
    ).first()

    if vote is None:
        vote = Vote(
            poll_id=poll.id,
            participant_name=payload.participant_name.strip(),
            participant_token_hash=participant_token_hash,
            updated_at=datetime.now(timezone.utc),
        )
        session.add(vote)
        session.commit()
        session.refresh(vote)
    else:
        vote.participant_name = payload.participant_name.strip()
        vote.updated_at = datetime.now(timezone.utc)
        session.add(vote)
        session.commit()

    session.exec(delete(VoteChoice).where(VoteChoice.vote_id == vote.id))
    for item in payload.choices:
        session.add(VoteChoice(vote_id=vote.id, day=item.day, choice=item.choice))

    session.commit()
    session.refresh(vote)

    return SubmitVoteResponse(vote_id=vote.id, updated_at=vote.updated_at)
