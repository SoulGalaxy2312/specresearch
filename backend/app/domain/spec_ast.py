from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

class FsmState(str, Enum):
    IDEA = "IDEA"
    RESTATED = "RESTATED"
    DECOMPOSED = "DECOMPOSED"
    RELATED_WORK = "RELATED_WORK"
    GAP_CHOSEN = "GAP_CHOSEN"
    CLAIMS_READY = "CLAIMS_READY"
    EXPERIMENT_READY = "EXPERIMENT_READY"
    FEASIBILITY_CHECKED = "FEASIBILITY_CHECKED"
    SPEC_DRAFT = "SPEC_DRAFT"
    JUDGING = "JUDGING"
    REVISION = "REVISION"
    FINAL = "FINAL"

ALLOWED_TRANSITIONS: dict[FsmState, set[FsmState]] = {
    FsmState.IDEA: {FsmState.RESTATED},
    FsmState.RESTATED: {FsmState.DECOMPOSED},
    FsmState.DECOMPOSED: {FsmState.RELATED_WORK},
    FsmState.RELATED_WORK: {FsmState.GAP_CHOSEN},
    FsmState.GAP_CHOSEN: {FsmState.CLAIMS_READY},
    FsmState.CLAIMS_READY: {FsmState.EXPERIMENT_READY},
    FsmState.EXPERIMENT_READY: {FsmState.FEASIBILITY_CHECKED},
    FsmState.FEASIBILITY_CHECKED: {FsmState.SPEC_DRAFT},
    FsmState.SPEC_DRAFT: {FsmState.JUDGING},
    FsmState.JUDGING: {FsmState.REVISION, FsmState.FINAL},
    FsmState.REVISION: {FsmState.JUDGING, FsmState.FINAL},
    FsmState.FINAL: set(),
}

def can_transition(current: FsmState, target: FsmState) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())

class CardType(str, Enum):
    PROBLEM = "Problem"
    RESEARCH_QUESTION = "ResearchQuestion"
    GAP = "Gap"
    CONTRIBUTION = "Contribution"
    CLAIM = "Claim"
    EVIDENCE = "Evidence"
    CONSTRAINT = "Constraint"
    OPEN_QUESTION = "OpenQuestion"
    BASELINE = "Baseline"
    METRIC = "Metric"

class CardStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    PROPOSED = "PROPOSED"
    MISSING = "MISSING"
    AMBIGUOUS = "AMBIGUOUS"
    UNSUPPORTED = "UNSUPPORTED"
    CONFLICT = "CONFLICT"

class SpecCard(BaseModel):
    id: str
    card_type: CardType
    status: CardStatus = CardStatus.PROPOSED
    content: str
    meta: dict[str, Any] = Field(default_factory=dict)

class SourceRef(BaseModel):
    id: str
    openalex_id: Optional[str] = None
    title: str
    year: Optional[int] = None
    authors: list[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    doi_url: Optional[str] = None
    cited_by_count: Optional[int] = None

class RelatedWorkEntry(BaseModel):
    id: str
    source_id: str
    did_what: str
    feedback_used: str
    open_point: str
    support_label: str = "UNVERIFIABLE"

class ChoiceOption(BaseModel):
    key: str
    label: str
    explanation: str
    example: Optional[str] = None

class GapProposal(BaseModel):
    statement: str
    prior_work: str
    limitation: str
    why_matters: str
    how_to_test: str
    options: list[ChoiceOption] = Field(default_factory=list)

class ClaimEvidenceCard(BaseModel):
    id: str
    claim: str
    baseline: str
    metric: str
    evidence: str
    falsification: str

class ExperimentPlan(BaseModel):
    baseline_compare: str
    quality_eval: str
    ablation: str
    generalization: str
    fairness_constraints: list[str] = Field(default_factory=list)

class FeasibilityEstimate(BaseModel):
    model: str
    vram_gb: float
    candidates_per_round: int
    rounds: int
    samples_dev: int
    samples_val: int
    estimated_hours: float
    estimated_tokens: int
    over_budget: bool
    narrative: str
    scale_down_options: list[ChoiceOption] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)

class JudgeFinding(BaseModel):
    target: str
    target_id: Optional[str] = None
    issue: str
    reason: str
    severity: str
    suggestion: str
    judge_type: Optional[str] = None

class ReadinessScores(BaseModel):
    originality: str = "Acceptable"
    significance: str = "Acceptable"
    soundness: str = "Acceptable"
    clarity: str = "Acceptable"
    reproducibility: str = "Acceptable"
    overall: str = "Acceptable"

class SpecAST(BaseModel):
    raw_idea: str = ""
    interpretation: str = ""
    cards: list[SpecCard] = Field(default_factory=list)
    sources: list[SourceRef] = Field(default_factory=list)
    related_work: list[RelatedWorkEntry] = Field(default_factory=list)
    related_work_status: str = "OK"
    gap: Optional[GapProposal] = None
    chosen_gap_key: Optional[str] = None
    chosen_gap_text: Optional[str] = None
    contributions: list[str] = Field(default_factory=list)
    claim_cards: list[ClaimEvidenceCard] = Field(default_factory=list)
    experiment: Optional[ExperimentPlan] = None
    feasibility: Optional[FeasibilityEstimate] = None
    open_issues: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    decision_history: list[dict[str, Any]] = Field(default_factory=list)
    judge_findings: list[JudgeFinding] = Field(default_factory=list)
    readiness: Optional[ReadinessScores] = None
    aggregate: Optional[dict[str, Any]] = None