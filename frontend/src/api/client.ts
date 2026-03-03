import type {
  CreatePollRequest,
  CreatePollResponse,
  PollResponse,
  ResultsResponse,
  SubmitVoteRequest
} from './types'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {})
    },
    ...init
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail ?? `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

export function createPoll(payload: CreatePollRequest): Promise<CreatePollResponse> {
  return req('/api/polls', { method: 'POST', body: JSON.stringify(payload) })
}

export function getPoll(pollId: string): Promise<PollResponse> {
  return req(`/api/polls/${pollId}`)
}

export function patchPoll(
  pollId: string,
  payload: { candidate_days?: string[]; is_locked?: boolean },
  adminToken: string
): Promise<PollResponse> {
  return req(`/api/polls/${pollId}`, {
    method: 'PATCH',
    headers: {
      'x-admin-token': adminToken
    },
    body: JSON.stringify(payload)
  })
}

export function submitVote(pollId: string, payload: SubmitVoteRequest): Promise<{ vote_id: string }> {
  return req(`/api/polls/${pollId}/votes`, { method: 'POST', body: JSON.stringify(payload) })
}

export function getResults(pollId: string): Promise<ResultsResponse> {
  return req(`/api/polls/${pollId}/results`)
}
