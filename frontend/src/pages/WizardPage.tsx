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

const STEP_GROUPS = [
  { label: 'Định hình', steps: [0, 1, 2] },
  { label: 'Grounding', steps: [3, 4] },
  { label: 'Thiết kế', steps: [5, 6, 7] },
  { label: 'Phản biện', steps: [8, 9, 10, 11] },
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

  const [maxStep, setMaxStep] = useState(0)
  const [stepErrors, setStepErrors] = useState<Set<number>>(new Set())

  const advanceStep = useCallback((i: number) => {
    setStep(i)
    setMaxStep((m) => Math.max(m, i))
  }, [])

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
    setStepErrors((prev) => {
      if (!prev.has(step)) return prev
      const next = new Set(prev)
      next.delete(step)
      return next
    })
    try {
      await fn()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e))
      setStepErrors((prev) => new Set(prev).add(step))
    } finally {
      setLoading(false)
    }
  }, [step])

  const goToStep = useCallback(
    (i: number) => {
      if (i <= maxStep) setStep(i)
    },
    [maxStep]
  )

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
                advanceStep(1)
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
                advanceStep(2)
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
            onContinue={() => advanceStep(3)}
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
            onContinue={() => advanceStep(4)}
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
                advanceStep(5)
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
                advanceStep(6)
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
            onContinue={() => advanceStep(7)}
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
                advanceStep(8)
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
            onStartJudges={() => advanceStep(9)}
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
                advanceStep(10)
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
                advanceStep(11)
              })
            }
            onRejudge={() => {
              setAggregate(null)
              setFindings([])
              setJudgeProgress([])
              advanceStep(9)
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
    advanceStep,
  ])

  const startNewSession = () =>
    run(async () => {
      clearSessionId()
      setSid(null)
      advanceStep(0)
      setMaxStep(0)
      setStepErrors(new Set())
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

  const currentGroup = STEP_GROUPS.find((group) => group.steps.includes(step))?.label

  return (
    <div className="app-shell">
      <header className="doc-header">
        <div className="brand-lockup">
          <span className="brand-monogram" aria-hidden="true">
            SR
          </span>
          <div>
            <div className="doc-header-title">SpecResearch</div>
            <div className="doc-header-subtitle">Research specification workbench</div>
          </div>
        </div>
        <div className="doc-header-right">
          <div className="step-position" aria-label={`Bước ${step + 1} trên ${STEPS.length}`}>
            <span>Đang làm việc</span>
            <strong>{String(step + 1).padStart(2, '0')}</strong>
            <span>/ {STEPS.length}</span>
          </div>
          {sessionId ? (
            <span className="session-chip" title={sessionId}>
              Session {sessionId.slice(0, 8)}
            </span>
          ) : null}
          <button className="text-button" disabled={loading} onClick={startNewSession}>
            Tạo session mới
          </button>
        </div>
      </header>

      <div className="workspace-layout">
        <nav className="step-nav" aria-label="Quy trình xây dựng research specification">
          {STEP_GROUPS.map((group) => (
            <div className="workflow-group" key={group.label}>
              <div className="workflow-group-label">{group.label}</div>
              {group.steps.map((i) => {
                const state = i === step ? 'current' : i <= maxStep ? 'completed' : ''
                return (
                  <button
                    key={STEPS[i]}
                    type="button"
                    className={`step-nav-item ${state}`}
                    disabled={i > maxStep}
                    aria-current={i === step ? 'step' : undefined}
                    onClick={() => goToStep(i)}
                  >
                    <span className="step-nav-number">{String(i + 1).padStart(2, '0')}</span>
                    <span className="step-nav-label">{STEPS[i]}</span>
                    {stepErrors.has(i) ? (
                      <span className="step-nav-flag" title="Cần xem lại">
                        !
                      </span>
                    ) : i < maxStep ? (
                      <span className="step-nav-check" aria-label="Đã hoàn tất">
                        ✓
                      </span>
                    ) : null}
                  </button>
                )
              })}
            </div>
          ))}
        </nav>

        <main className="workspace-main" aria-busy={loading}>
          <div className="step-nav-mobile">
            <span className="step-nav-mobile-label">
              {currentGroup} · Bước {step + 1}/{STEPS.length}
              {stepErrors.has(step) ? ' · cần xem lại' : ''}
            </span>
            <select value={step} onChange={(e) => goToStep(Number(e.target.value))}>
              {STEPS.map((label, i) => (
                <option key={label} value={i} disabled={i > maxStep}>
                  {i + 1}. {label}
                  {stepErrors.has(i) ? ' ⚠' : ''}
                </option>
              ))}
            </select>
          </div>

          <div className="workspace-context">
            <span>{currentGroup}</span>
            <span aria-hidden="true">/</span>
            <strong>{STEPS[step]}</strong>
            {loading ? <em>Đang xử lý…</em> : null}
          </div>
          {error ? (
            <div className="error" role="alert">
              {error}
            </div>
          ) : null}
          {content}
        </main>
      </div>
    </div>
  )
}
