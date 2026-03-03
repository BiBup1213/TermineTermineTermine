export type VoteChoice = 'no' | 'maybe' | 'yes'

export interface CreatePollRequest {
  title: string
  description?: string
  timezone: string
  date_range_from: string
  date_range_to: string
}

export interface CreatePollResponse {
  poll_id: string
  admin_token: string
}

export interface PollResponse {
  id: string
  title: string
  description: string | null
  timezone: string
  date_range_from: string
  date_range_to: string
  is_locked: boolean
  candidate_days: string[]
  created_at: string
}

export interface SubmitVoteRequest {
  participant_name: string
  participant_token: string
  choices: Array<{ day: string; choice: VoteChoice }>
}

export interface DayResult {
  day: string
  yes: number
  maybe: number
  no: number
  score: number
  is_top: boolean
}

export interface ResultsResponse {
  poll_id: string
  title: string
  is_locked: boolean
  sorted_days: DayResult[]
  participants: Array<{ participant_name: string; choices: Record<string, VoteChoice> }>
}
