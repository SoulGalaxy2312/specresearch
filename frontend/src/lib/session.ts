const SESSION_KEY = 'specresearch_session_id'

export function getSessionId(): string | null {
    return localStorage.getItem(SESSION_KEY)
}

export function setSessionId(id: string) {
    localStorage.setItem(SESSION_KEY, id)
}

export function clearSessionId() {
    localStorage.removeItem(SESSION_KEY)
}