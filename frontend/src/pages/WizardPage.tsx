import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../lib/api'
import { clearSessionId, getSessionId, setSessionId } from '../lib/session'
import { IdeaStep } from '../steps/IdeaStep'
import { RestateStep } from '../steps/RestateStep'
import { DecomposeStep } from '../steps/DecomposeStep'
import { RelatedWorkStep } from '../steps/RelatedWorkStep'
import { GapStep } from '../steps/GapStep'
import { ClaimStep } from '../steps/ClaimStep'
import { ExperimentStep } from '../steps/ExperimentStep'
import { FeasibilityStep } from '../steps/FeasibilityStep'
import { SpecDraftStep } from '../steps/SpecDraftStep'
import { JudgeStep } from '../steps/JudgeStep'
import { RevisionStep } from '../steps/RevisionStep'
import { FinalStep } from '../steps/FinalStep'
import type {
  ClaimEvidenceCard,
  DecomposeIssue,
  DiffItem,
  ExperimentPlan,
  FeasibilityEstimate,
  GapProposal,
  JudgeAggregate,
  JudgeFinding,
  RelatedWorkEntry,
  SourceRef,
  SpecCard,
  VersionSummary,
} from '../lib/types'

const STEPS = [
  'Ý tưởng',
  'Diễn giải',
  'Phân rã',
  'Related work',
  'Gap',
  'Claim',
  'Thí nghiệm',
  'Feasibility',
  'Spec',
  'Judges',
  'Sửa đổi',
  'Final',
]

export function WizardPage() {
  const [sessionId, setSid] = useState<string | null>(getSessionId())
  const [step, setStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [idea, setIdea] = useState('')
  const [interpretations, setInterpretations] = useState<{ id: string; text: string }[]>([])
  const [cards, setCards] = useState<SpecCard[]>([])
  const [issues, setIssues] = useState<DecomposeIssue[]>([])
  const [rwStatus, setRwStatus] = useState('OK')
  const [sources, setSources] = useState<SourceRef[]>([])
  const [relatedWork, setRelatedWork] = useState<RelatedWorkEntry[]>([])
  const [gap, setGap] = useState<GapProposal | null>(null)
  const [contributions, setContributions] = useState<string[]>([])
  const [claimCards, setClaimCards] = useState<ClaimEvidenceCard[]>([])
  const [experiment, setExperiment] = useState<ExperimentPlan | null>(null)
  const [feasibility, setFeasibility] = useState<FeasibilityEstimate | null>(null)
  const [markdown, setMarkdown] = useState('')
  const [judgeProgress, setJudgeProgress] = useState<string[]>([])
  const [findings, setFindings] = useState<JudgeFinding[]>([])
  const [aggregate, setAggregate] = useState<JudgeAggregate | null>(null)
  const [diffs, setDiffs] = useState<DiffItem[]>([])
  const [reviseCount, setReviseCount] = useState(0)
  const [versions, setVersions] = useState<VersionSummary[]>([])
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null)
  const [versionDiff, setVersionDiff] = useState<DiffItem[]>([])

  const ensureSession = useCallback(async () => {
    if (sessionId) return sessionId
    const res = await api.createSession()
    setSessionId(res.session_id)
    setSid(res.session_id)
    return res.session_id
  }, [sessionId])

  const run = useCallback(async (fn: () => Promise<void>) => {
    setLoading(true)
    setError(null)
    try {
      await fn()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }, [])

  const bootstrappedRef = useRef(false)

  useEffect(() => {
    if (bootstrappedRef.current) return
    bootstrappedRef.current = true
    run(async () => {
      const stored = getSessionId()
      if (stored) {
        try {
          await api.getSession(stored)
          setSid(stored)
          return
        } catch {
          // Session biến mất khỏi backend (vd. xoá file db) — bỏ id cũ đi.
          clearSessionId()
        }
      }
      const res = await api.createSession()
      setSessionId(res.session_id)
      setSid(res.session_id)
    })
  }, [run])

  const content = useMemo(() => {
    switch (step) {
      case 0:
        return (
          <IdeaStep
            idea={idea}
            setIdea={setIdea}
            loading={loading}
            onSubmit={() =>
              run(async () => {
                const id = await ensureSession()
                await api.setIdea(id, idea)
                setStep(1)
              })
            }
          />
        )
      case 1:
        return (
          <RestateStep
            interpretations={interpretations}
            loading={loading}
            onGenerate={() =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.restate(id)
                setInterpretations(data.interpretations || [])
              })
            }
            onConfirm={(action, text) =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.restateConfirm(id, action, text)
                if (action === 'alternative') {
                  setInterpretations('interpretations' in data ? data.interpretations : [])
                  return
                }
                setStep(2)
              })
            }
          />
        )
      case 2:
        return (
          <DecomposeStep
            cards={cards}
            issues={issues}
            loading={loading}
            onDecompose={() =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.decompose(id)
                setCards(data.cards || [])
                setIssues(data.issues || [])
              })
            }
            onResolve={(payload) =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.decomposeResolve(id, payload)
                setCards(data.cards || cards)
              })
            }
            onContinue={() => setStep(3)}
          />
        )
      case 3:
        return (
          <RelatedWorkStep
            status={rwStatus}
            sources={sources}
            relatedWork={relatedWork}
            loading={loading}
            onFetch={() =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.relatedWork(id)
                setRwStatus(data.status)
                setSources(data.sources || [])
                setRelatedWork(data.related_work || [])
              })
            }
            onAddManual={(payload) =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.relatedWorkManual(id, payload)
                setSources(data.sources || [])
                setRelatedWork(data.related_work || [])
              })
            }
            onContinue={() => setStep(4)}
          />
        )
      case 4:
        return (
          <GapStep
            gap={gap}
            loading={loading}
            onGenerate={() =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.gap(id)
                setGap(data)
              })
            }
            onChoose={(choice, other_text) =>
              run(async () => {
                const id = await ensureSession()
                await api.gapChoose(id, choice, other_text)
                setStep(5)
              })
            }
          />
        )
      case 5:
        return (
          <ClaimStep
            contributions={contributions}
            claimCards={claimCards}
            loading={loading}
            onContributionsChange={setContributions}
            onClaimCardsChange={setClaimCards}
            onGenerate={() =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.claims(id)
                setContributions(data.contributions || [])
                setClaimCards(data.claim_cards || [])
              })
            }
            onConfirm={(payload) =>
              run(async () => {
                const id = await ensureSession()
                await api.claimsConfirm(id, payload)
                setContributions(payload.contributions)
                setClaimCards(payload.claim_cards)
                setStep(6)
              })
            }
          />
        )
      case 6:
        return (
          <ExperimentStep
            experiment={experiment}
            loading={loading}
            onGenerate={() =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.experiment(id)
                setExperiment(data)
              })
            }
            onContinue={() => setStep(7)}
          />
        )
      case 7:
        return (
          <FeasibilityStep
            feasibility={feasibility}
            loading={loading}
            onEstimate={() =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.feasibility(id)
                setFeasibility(data)
              })
            }
            onChoose={(choice) =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.feasibilityChoose(id, choice)
                setFeasibility(data)
                setStep(8)
              })
            }
          />
        )
      case 8:
        return (
          <SpecDraftStep
            markdown={markdown}
            loading={loading}
            onAssemble={() =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.assemble(id)
                setMarkdown(data.markdown || '')
              })
            }
            onStartJudges={() => setStep(9)}
          />
        )
      case 9:
        return (
          <JudgeStep
            progress={judgeProgress}
            findings={findings}
            aggregate={aggregate}
            loading={loading}
            onRun={() =>
              run(async () => {
                const id = await ensureSession()
                const types = ['gap', 'contribution', 'experiment', 'evidence', 'readiness']
                const all: JudgeFinding[] = []
                const done: string[] = []
                for (const t of types) {
                  const res = await api.judge(id, t)
                  done.push(t)
                  setJudgeProgress([...done])
                  all.push(...(res.findings || []))
                  setFindings([...all])
                }
                const agg = await api.aggregate(id)
                setAggregate(agg)
                setReviseCount(agg.revise_count || 0)
                setStep(10)
              })
            }
          />
        )
      case 10:
        return (
          <RevisionStep
            aggregate={aggregate}
            diffs={diffs}
            reviseCount={reviseCount}
            loading={loading}
            onRevise={(choice, other_text) =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.revise(id, choice, other_text)
                setDiffs(data.diffs || data.diff || [])
                setMarkdown(data.markdown || markdown)
                setReviseCount(data.revise_count || reviseCount)
                setAggregate(null)
                setFindings([])
                setJudgeProgress([])
              })
            }
            onFinalize={() =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.finalize(id)
                setMarkdown(data.markdown || markdown)
                setStep(11)
              })
            }
            onRejudge={() => {
              setAggregate(null)
              setFindings([])
              setJudgeProgress([])
              setStep(9)
            }}
          />
        )
      case 11:
        return (
          <FinalStep
            markdown={markdown}
            versions={versions}
            selectedVersionId={selectedVersionId}
            versionDiff={versionDiff}
            loading={loading}
            onCopy={() => navigator.clipboard.writeText(markdown)}
            onExportJson={() =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.export(id, 'json')
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = 'specresearch-ast.json'
                a.click()
                URL.revokeObjectURL(url)
              })
            }
            onLoadVersions={() =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.listVersions(id)
                setVersions(data)
              })
            }
            onSelectVersion={(versionId) =>
              run(async () => {
                const id = await ensureSession()
                const data = await api.versionDiff(id, versionId)
                setSelectedVersionId(versionId)
                setVersionDiff(data.diff || [])
              })
            }
          />
        )
      default:
        return null
    }
  }, [
    step,
    idea,
    loading,
    interpretations,
    cards,
    issues,
    rwStatus,
    sources,
    relatedWork,
    gap,
    contributions,
    claimCards,
    experiment,
    feasibility,
    markdown,
    judgeProgress,
    findings,
    aggregate,
    diffs,
    reviseCount,
    versions,
    selectedVersionId,
    versionDiff,
    ensureSession,
    run,
  ])

  return (
    <div className="app-shell">
      <header className="hero">
        <h1>SpecResearch Loop</h1>
        <p>
          Chuyển ý tưởng nghiên cứu mơ hồ thành research specification có bằng chứng, kế hoạch thí nghiệm và
          phản biện đa Judge.
        </p>
        <div className="row" style={{ marginTop: '1rem' }}>
          <button
            className="btn secondary"
            disabled={loading}
            onClick={() =>
              run(async () => {
                clearSessionId()
                setSid(null)
                setStep(0)
                setInterpretations([])
                setCards([])
                setIssues([])
                setRelatedWork([])
                setSources([])
                setGap(null)
                setContributions([])
                setClaimCards([])
                setExperiment(null)
                setFeasibility(null)
                setMarkdown('')
                setFindings([])
                setAggregate(null)
                setDiffs([])
                setJudgeProgress([])
                setIdea('')
                setVersions([])
                setSelectedVersionId(null)
                setVersionDiff([])
                const res = await api.createSession()
                setSessionId(res.session_id)
                setSid(res.session_id)
              })
            }
          >
            Session mới
          </button>
          {sessionId ? <span className="muted">Session: {sessionId.slice(0, 8)}…</span> : null}
        </div>
      </header>

      <nav className="stepper">
        {STEPS.map((label, i) => (
          <span key={label} className={`step-pill ${i === step ? 'active' : i < step ? 'done' : ''}`}>
            {i + 1}. {label}
          </span>
        ))}
      </nav>

      {error ? <div className="error">{error}</div> : null}
      {content}
    </div>
  )
}
