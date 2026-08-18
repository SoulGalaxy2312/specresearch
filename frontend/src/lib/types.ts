export type ChoiceOption = {
  key: string
  label: string
  explanation: string
  example?: string | null
}

export type SpecCard = {
  id: string
  card_type: string
  status: string
  content: string
  meta?: Record<string, unknown>
}

export type DecomposeIssue = {
  card_hint?: string
  question: string
  options: ChoiceOption[]
}

export type SourceRef = {
  id: string
  openalex_id?: string | null
  title: string
  year?: number | null
  authors?: string[]
  abstract?: string | null
  doi_url?: string | null
  cited_by_count?: number | null
}

export type RelatedWorkEntry = {
  id: string
  source_id: string
  did_what: string
  feedback_used: string
  open_point: string
  support_label: string
}

export type GapProposal = {
  statement: string
  prior_work: string
  limitation: string
  why_matters: string
  how_to_test: string
  options: ChoiceOption[]
}

export type ClaimEvidenceCard = {
  id?: string
  claim: string
  baseline: string
  metric: string
  evidence: string
  falsification: string
}

export type ExperimentPlan = {
  baseline_compare: string
  quality_eval: string
  ablation: string
  generalization: string
  fairness_constraints: string[]
}

export type FeasibilityEstimate = {
  model: string
  vram_gb: number
  candidates_per_round: number
  rounds: number
  samples_dev: number
  samples_val: number
  estimated_hours: number
  estimated_tokens: number
  over_budget: boolean
  narrative: string
  scale_down_options: ChoiceOption[]
  assumptions: string[]
}

export type JudgeFinding = {
  target: string
  target_id?: string | null
  issue: string
  reason: string
  severity: string
  suggestion: string
  judge_type?: string | null
}

export type AggregateEntry = {
  target: string
  severity: string
  count?: number
  judges?: string[]
  issues: string[]
  suggestions?: string[]
}

export type JudgeAggregate = {
  consensus: AggregateEntry[]
  disagreement: AggregateEntry[]
  major_count: number
  can_finalize_early: boolean
  revision_options: ChoiceOption[]
  fsm_state?: string
  revise_count?: number
}

export type DiffItem = {
  section: string
  before: string
  after: string
}

export type SessionSummary = {
  session_id: string
  fsm_state: string
  revise_count: number
  raw_idea: string
  confirmed_interpretation: string
  ast: Record<string, unknown>
}

export type DecomposeResolvePayload = {
  choice_key: string
  choice_text: string
  options: ChoiceOption[]
  card_updates?: Partial<SpecCard>[]
}
