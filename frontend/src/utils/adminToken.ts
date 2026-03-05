const ADMIN_KEY_PREFIX = 'poll-admin-token-'

function key(pollId: string): string {
  return `${ADMIN_KEY_PREFIX}${pollId}`
}

export function getStoredAdminToken(pollId: string): string {
  return localStorage.getItem(key(pollId)) ?? ''
}

export function setStoredAdminToken(pollId: string, token: string): void {
  localStorage.setItem(key(pollId), token)
}

export function clearStoredAdminToken(pollId: string): void {
  localStorage.removeItem(key(pollId))
}
