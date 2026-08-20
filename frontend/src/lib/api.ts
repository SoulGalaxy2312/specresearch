import type {
  ClaimEvidenceCard,
  DecomposeIssue,
  DecomposeResolvePayload,
  DiffItem,
  ExperimentPlan,
  FeasibilityEstimate,
  GapProposal,
  JudgeAggregate,
  JudgeFinding,
  RelatedWorkEntry,
  SessionSummary,
  SourceRef,
  SpecCard,
  VersionDiffResponse,
  VersionSummary,
} from './types'

const BASE = '/api/v1'

type OkResponse = { ok: true }

type RestateResponse = {
  interpretations: { id: string; text: string }[]
}

type DecomposeResponse = {
  cards: SpecCard[]
  issues: DecomposeIssue[]
  fsm_state: string
}

type RelatedWorkResponse = {
  status: string
  sources: SourceRef[]
  related_work: RelatedWorkEntry[]
  fsm_state?: string
}

type ClaimsResponse = {
  contributions: string[]
  claim_cards: ClaimEvidenceCard[]
  fsm_state: string
}

type AssembleResponse = {
  version_id: string
  version_no?: number
  markdown: string
  fsm_state: string
}

type JudgeResponse = {
  run_id: string
  findings: JudgeFinding[]
  readiness?: Record<string, string> | null
  judge_type: string
  fsm_state: string
}

type ReviseResponse = {
  diff?: DiffItem[]
  diffs?: DiffItem[]
  markdown: string
  revise_count: number
}

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
    request<SessionSummary>(`/sessions/${id}`),

  setIdea: (id: string, idea: string) =>
    request(
      `/sessions/${id}/idea`,
      {
        method: 'POST',
        body: JSON.stringify({ idea }),
      }
    ),

  restate: (id: string) =>
    request<RestateResponse>(
      `/sessions/${id}/restate`,
      { method: 'POST' }
    ),

  restateConfirm: (
    id: string,
    action: string,
    text?: string
  ) =>
    request<RestateResponse | OkResponse & { interpretation?: string; fsm_state?: string }>(
      `/sessions/${id}/restate/confirm`,
      {
        method: 'POST',
        body: JSON.stringify({ action, text }),
      }
    ),

  decompose: (id: string) =>
    request<DecomposeResponse>(
      `/sessions/${id}/decompose`,
      { method: 'POST' }
    ),

  decomposeResolve: (id: string, payload: DecomposeResolvePayload) =>
    request<{ ok: true; cards: SpecCard[] }>(
      `/sessions/${id}/decompose/resolve`,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    ),

  relatedWork: (id: string) =>
    request<RelatedWorkResponse>(
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
    request<Pick<RelatedWorkResponse, 'sources' | 'related_work'>>(
      `/sessions/${id}/related-work/manual`,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    ),

  gap: (id: string) =>
    request<GapProposal>(
      `/sessions/${id}/gap`,
      { method: 'POST' }
    ),

  gapChoose: (
    id: string,
    choice: string,
    other_text?: string
  ) =>
    request<OkResponse & { chosen_gap_text?: string; fsm_state?: string }>(
      `/sessions/${id}/gap/choose`,
      {
        method: 'POST',
        body: JSON.stringify({ choice, other_text }),
      }
    ),

  claims: (id: string) =>
    request<ClaimsResponse>(
      `/sessions/${id}/claims`,
      { method: 'POST' }
    ),

  claimsConfirm: (id: string, payload: { contributions: string[]; claim_cards: ClaimEvidenceCard[] }) =>
    request<OkResponse>(
      `/sessions/${id}/claims/confirm`,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    ),

  experiment: (id: string) =>
    request<ExperimentPlan & { fsm_state: string }>(
      `/sessions/${id}/experiment`,
      { method: 'POST' }
    ),

  feasibility: (id: string) =>
    request<FeasibilityEstimate & { fsm_state: string }>(
      `/sessions/${id}/feasibility`,
      { method: 'POST' }
    ),

  feasibilityChoose: (id: string, choice: string) =>
    request<FeasibilityEstimate>(
      `/sessions/${id}/feasibility/choose`,
      {
        method: 'POST',
        body: JSON.stringify({ choice }),
      }
    ),

  assemble: (id: string) =>
    request<AssembleResponse>(
      `/sessions/${id}/spec/assemble`,
      { method: 'POST' }
    ),

  judge: (id: string, judgeType: string) =>
    request<JudgeResponse>(
      `/sessions/${id}/judges/${judgeType}`,
      { method: 'POST' }
    ),

  aggregate: (id: string) =>
    request<JudgeAggregate>(
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
    request<Pick<AssembleResponse, 'version_id' | 'markdown' | 'fsm_state'>>(
      `/sessions/${id}/finalize`,
      { method: 'POST' }
    ),

  export: (id: string, format: 'md' | 'json' = 'md') =>
    request<Record<string, unknown> | { markdown: string }>(
      `/sessions/${id}/export?format=${format}`
    ),

  listVersions: (id: string) =>
    request<VersionSummary[]>(`/sessions/${id}/versions`),

  versionDiff: (id: string, versionId: string) =>
    request<VersionDiffResponse>(`/sessions/${id}/versions/${versionId}/diff`),
};
