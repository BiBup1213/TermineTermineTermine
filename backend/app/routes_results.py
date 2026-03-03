from collections import defaultdict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Poll, PollDay, Vote, VoteChoice, VoteChoiceEnum
from app.schemas import DayResult, ParticipantRow, ResultsResponse

router = APIRouter(prefix="/api/polls", tags=["results"])


@router.get("/{poll_id}/results", response_model=ResultsResponse)
def get_results(poll_id: UUID, session: Session = Depends(get_session)) -> ResultsResponse:
    poll = session.get(Poll, poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")

    candidate_days = list(
        session.exec(select(PollDay.day).where(PollDay.poll_id == poll.id).order_by(PollDay.day)).all()
    )
    votes = list(session.exec(select(Vote).where(Vote.poll_id == poll.id)).all())

    choices_by_vote_day: dict[UUID, dict] = defaultdict(dict)
    if votes:
        vote_ids = [v.id for v in votes]
        all_choices = session.exec(select(VoteChoice).where(VoteChoice.vote_id.in_(vote_ids))).all()
        for c in all_choices:
            choices_by_vote_day[c.vote_id][c.day] = c.choice

    per_day = []
    best_score = None
    for day in candidate_days:
        yes = 0
        maybe = 0
        no = 0
        for vote in votes:
            choice = choices_by_vote_day[vote.id].get(day, VoteChoiceEnum.no)
            if choice == VoteChoiceEnum.yes:
                yes += 1
            elif choice == VoteChoiceEnum.maybe:
                maybe += 1
            else:
                no += 1

        score = yes * 2 + maybe
        if best_score is None or score > best_score:
            best_score = score
        per_day.append({"day": day, "yes": yes, "maybe": maybe, "no": no, "score": score})

    per_day.sort(key=lambda item: (-item["score"], item["day"]))

    sorted_days = [
        DayResult(
            day=item["day"],
            yes=item["yes"],
            maybe=item["maybe"],
            no=item["no"],
            score=item["score"],
            is_top=(best_score is not None and item["score"] == best_score),
        )
        for item in per_day
    ]

    participants = [
        ParticipantRow(
            participant_name=vote.participant_name,
            choices={
                day: choices_by_vote_day[vote.id].get(day, VoteChoiceEnum.no) for day in candidate_days
            },
        )
        for vote in sorted(votes, key=lambda item: item.participant_name.lower())
    ]

    return ResultsResponse(
        poll_id=poll.id,
        title=poll.title,
        is_locked=poll.is_locked,
        sorted_days=sorted_days,
        participants=participants,
    )
