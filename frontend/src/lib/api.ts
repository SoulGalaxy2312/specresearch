const BASE = '/api/v1'

type ReviseResponse = {
  diffs: any[];
  markdown: string;
  revise_count: number;
};

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${BASE}${path}`, {
        headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
        ...options,
    })
    if (!res.ok) {
        let detail = res.statusText
        try {
            const body = await res.json()
            detail = body.detail || JSON.stringify(body)
        } catch {
            /* ignore */
        }
        throw new Error(detail)
    }
    return res.json() as Promise<T>
}

export const api = {
  createSession: () =>
    request<{ session_id: string; fsm_state: string }>(
      '/sessions',
      { method: 'POST' }
    ),

  getSession: (id: string) =>
    request<any>(`/sessions/${id}`),

  setIdea: (id: string, idea: string) =>
    request(
      `/sessions/${id}/idea`,
      {
        method: 'POST',
        body: JSON.stringify({ idea }),
      }
    ),

  restate: (id: string) =>
    request<{ interpretations: { id: string; text: string }[] }>(
      `/sessions/${id}/restate`,
      { method: 'POST' }
    ),

  restateConfirm: (
    id: string,
    action: string,
    text?: string
  ) =>
    request(
      `/sessions/${id}/restate/confirm`,
      {
        method: 'POST',
        body: JSON.stringify({ action, text }),
      }
    ),

  decompose: (id: string) =>
    request<any>(
      `/sessions/${id}/decompose`,
      { method: 'POST' }
    ),

  decomposeResolve: (id: string, payload: any) =>
    request(
      `/sessions/${id}/decompose/resolve`,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    ),

  relatedWork: (id: string) =>
    request<any>(
      `/sessions/${id}/related-work`,
      { method: 'POST' }
    ),

  relatedWorkManual: (
    id: string,
    payload: {
      title: string;
      url?: string;
      abstract?: string;
    }
  ) =>
    request(
      `/sessions/${id}/related-work/manual`,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    ),

  gap: (id: string) =>
    request<any>(
      `/sessions/${id}/gap`,
      { method: 'POST' }
    ),

  gapChoose: (
    id: string,
    choice: string,
    other_text?: string
  ) =>
    request(
      `/sessions/${id}/gap/choose`,
      {
        method: 'POST',
        body: JSON.stringify({ choice, other_text }),
      }
    ),

  claims: (id: string) =>
    request<any>(
      `/sessions/${id}/claims`,
      { method: 'POST' }
    ),

  claimsConfirm: (id: string, payload: any) =>
    request(
      `/sessions/${id}/claims/confirm`,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    ),

  experiment: (id: string) =>
    request<any>(
      `/sessions/${id}/experiment`,
      { method: 'POST' }
    ),

  feasibility: (id: string) =>
    request<any>(
      `/sessions/${id}/feasibility`,
      { method: 'POST' }
    ),

  feasibilityChoose: (id: string, choice: string) =>
    request(
      `/sessions/${id}/feasibility/choose`,
      {
        method: 'POST',
        body: JSON.stringify({ choice }),
      }
    ),

  assemble: (id: string) =>
    request<any>(
      `/sessions/${id}/spec/assemble`,
      { method: 'POST' }
    ),

  judge: (id: string, judgeType: string) =>
    request<any>(
      `/sessions/${id}/judges/${judgeType}`,
      { method: 'POST' }
    ),

  aggregate: (id: string) =>
    request<any>(
      `/sessions/${id}/judges/aggregate`,
      { method: 'POST' }
    ),

  revise: (
    id: string,
    choice: string,
    other_text?: string
  ): Promise<ReviseResponse> =>
    request<ReviseResponse>(
      `/sessions/${id}/revise`,
      {
        method: 'POST',
        body: JSON.stringify({ choice, other_text }),
      }
    ),

  finalize: (id: string) =>
    request<any>(
      `/sessions/${id}/finalize`,
      { method: 'POST' }
    ),

  export: (id: string, format: 'md' | 'json' = 'md') =>
    request<any>(
      `/sessions/${id}/export?format=${format}`
    ),
};