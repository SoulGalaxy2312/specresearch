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
  ChatMessage,
  JudgeAggregate,
  JudgeFinding,
  KnowledgeItem,
  RelatedWorkEntry,
  SessionListItem,
  SourceRef,
  SpecCard,
  SessionSummary,
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

const FSM_TO_STEP: Record<string, number> = {
  IDEA: 0,
  RESTATED: 2,
  DECOMPOSED: 3,
  RELATED_WORK: 4,
  GAP_CHOSEN: 5,
  CLAIMS_READY: 6,
  EXPERIMENT_READY: 7,
  FEASIBILITY_CHECKED: 8,
  SPEC_DRAFT: 9,
  JUDGING: 9,
  REVISION: 10,
  FINAL: 11,
}

const CHAT_TOPICS = [
  { label: 'Ý tưởng', keywords: ['ý tưởng', 'idea', 'problem', 'research question'] },
  { label: 'Nguồn', keywords: ['source', 'citation', 'related', 'paper', 'evidence'] },
  { label: 'Thí nghiệm', keywords: ['experiment', 'baseline', 'metric', 'ablation'] },
  { label: 'Judge', keywords: ['judge', 'phản biện', 'major', 'minor', 'readiness'] },
  { label: 'Tài nguyên', keywords: ['feasibility', 'gpu', 'vram', 'token', 'rtx'] },
]

export function WizardPage() {
  const [activeView, setActiveView] = useState<'pipeline' | 'sessions' | 'knowledge' | 'chat'>('pipeline')
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
  const [sessionList, setSessionList] = useState<SessionListItem[]>([])
  const [sessionTotal, setSessionTotal] = useState(0)
  const [sessionOffset, setSessionOffset] = useState(0)
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([])
  const [knowledgeCategory, setKnowledgeCategory] = useState('')
  const [selectedKnowledge, setSelectedKnowledge] = useState<KnowledgeItem | null>(null)
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatDraft, setChatDraft] = useState('')

  const [maxStep, setMaxStep] = useState(0)
  const [stepErrors, setStepErrors] = useState<Set<number>>(new Set())

  const advanceStep = useCallback((i: number) => {
    setStep(i)
    setMaxStep((m) => Math.max(m, i))
  }, [])

  const applySessionSummary = useCallback((summary: SessionSummary) => {
    const ast = summary.ast as Record<string, unknown>
    setSid(summary.session_id)
    setSessionId(summary.session_id)
    setIdea(summary.raw_idea || '')
    setReviseCount(summary.revise_count || 0)
    setVersions(summary.versions || [])
    setChatMessages(summary.chat_messages || [])
    setInterpretations([])
    setCards(Array.isArray(ast.cards) ? ast.cards as SpecCard[] : [])
    setIssues([])
    setSources(Array.isArray(ast.sources) ? ast.sources as SourceRef[] : [])
    setRelatedWork(Array.isArray(ast.related_work) ? ast.related_work as RelatedWorkEntry[] : [])
    setGap(ast.gap && typeof ast.gap === 'object' ? ast.gap as GapProposal : null)
    setContributions(Array.isArray(ast.contributions) ? ast.contributions as string[] : [])
    setClaimCards(Array.isArray(ast.claim_cards) ? ast.claim_cards as ClaimEvidenceCard[] : [])
    setExperiment(ast.experiment && typeof ast.experiment === 'object' ? ast.experiment as ExperimentPlan : null)
    setFeasibility(ast.feasibility && typeof ast.feasibility === 'object' ? ast.feasibility as FeasibilityEstimate : null)
    setFindings(Array.isArray(ast.judge_findings) ? ast.judge_findings as JudgeFinding[] : [])
    setAggregate(ast.aggregate && typeof ast.aggregate === 'object' ? ast.aggregate as JudgeAggregate : null)
    setDiffs([])
    setJudgeProgress([])
    setSelectedVersionId(null)
    setVersionDiff([])
    setMaxStep(STEPS.length - 1)
    setStep(FSM_TO_STEP[summary.fsm_state] ?? 0)
  }, [])

  const ensureSession = useCallback(async () => {
    if (sessionId) return sessionId
    const res = await api.createSession()
    setSessionId(res.session_id)
    setSid(res.session_id)
    return res.session_id
  }, [sessionId])

  const refreshSessions = useCallback(async (offset = sessionOffset) => {
    const data = await api.listSessions(6, offset)
    setSessionList(data.items)
    setSessionTotal(data.total)
    setSessionOffset(data.offset)
  }, [sessionOffset])

  const refreshKnowledge = useCallback(async (category = knowledgeCategory) => {
    const data = await api.listKnowledge(category || undefined)
    setKnowledgeItems(data.items)
  }, [knowledgeCategory])

  const refreshChat = useCallback(async () => {
    const id = await ensureSession()
    const data = await api.listChat(id)
    setChatMessages(data.items)
  }, [ensureSession])

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
          const summary = await api.getSession(stored)
          applySessionSummary(summary)
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
  }, [applySessionSummary, run])

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
  const completedSteps = Math.max(0, Math.min(maxStep, STEPS.length - 1))
  const progressPercent = Math.round(((completedSteps + 1) / STEPS.length) * 100)
  const chatTopicStats = CHAT_TOPICS.map((topic) => {
    const count = chatMessages.filter((message) => {
      const content = `${message.content} ${message.step}`.toLowerCase()
      return topic.keywords.some((keyword) => content.includes(keyword.toLowerCase()))
    }).length
    return { ...topic, count }
  })
  const maxTopicCount = Math.max(1, ...chatTopicStats.map((topic) => topic.count))
  const totalSessionSources = sessionList.reduce((sum, item) => sum + item.source_count, 0)
  const totalSessionChats = sessionList.reduce((sum, item) => sum + item.chat_count, 0)

  const resumeSession = (id: string, targetStep?: number) => {
    run(async () => {
      const summary = await api.getSession(id)
      applySessionSummary(summary)
      if (typeof targetStep === 'number') setStep(targetStep)
      setMaxStep(STEPS.length - 1)
      setActiveView('pipeline')
    })
  }
  const openView = (view: typeof activeView) => {
    setActiveView(view)
    if (view === 'sessions') {
      run(async () => refreshSessions())
    }
    if (view === 'knowledge') {
      run(async () => refreshKnowledge())
    }
    if (view === 'chat') {
      run(async () => refreshChat())
    }
  }

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

      <div className="top-tabs" role="tablist" aria-label="Không gian làm việc">
        {[
          ['pipeline', 'Pipeline'],
          ['sessions', 'Sessions'],
          ['knowledge', 'Knowledge'],
          ['chat', 'Chat history'],
        ].map(([key, label]) => (
          <button
            key={key}
            type="button"
            className={`top-tab ${activeView === key ? 'active' : ''}`}
            onClick={() => openView(key as typeof activeView)}
          >
            {label}
          </button>
        ))}
      </div>

      <div className={`workspace-layout ${activeView === 'pipeline' ? '' : 'page-layout'}`}>
        {activeView === 'pipeline' ? (
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
        ) : null}

        <main className="workspace-main" aria-busy={loading}>
          {activeView === 'pipeline' ? (
          <div className="pipeline-strip" aria-label="Tổng quan pipeline">
            <div>
              <span className="metric-label">Tiến độ</span>
              <strong>{progressPercent}%</strong>
            </div>
            <div>
              <span className="metric-label">FSM</span>
              <strong>{STEPS[step]}</strong>
            </div>
            <div>
              <span className="metric-label">Nguồn</span>
              <strong>{sources.length}</strong>
            </div>
            <div>
              <span className="metric-label">Judge findings</span>
              <strong>{findings.length}</strong>
            </div>
          </div>
          ) : null}
          {activeView === 'pipeline' ? (
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
          ) : null}

          {activeView === 'pipeline' ? (
          <div className="workspace-context">
            <span>{currentGroup}</span>
            <span aria-hidden="true">/</span>
            <strong>{STEPS[step]}</strong>
            {loading ? <em>Đang xử lý…</em> : null}
          </div>
          ) : null}
          {error ? (
            <div className="error" role="alert">
              {error}
            </div>
          ) : null}
          {activeView === 'pipeline' ? content : null}
          {activeView === 'sessions' ? (
            <section className="page-panel stack">
              <div className="page-hero sessions-hero">
                <div>
                  <span className="eyebrow">Session memory</span>
                  <h1>Sessions</h1>
                  <p>Quản lý lịch sử từng phiên, xem pipeline đã đi đến đâu và tiếp tục tại bất kỳ stage nào.</p>
                </div>
                <button className="btn secondary" disabled={loading} onClick={() => run(async () => refreshSessions(0))}>
                  Tải lại
                </button>
              </div>
              <div className="analytics-grid">
                <div><span className="metric-label">Tổng session</span><strong>{sessionTotal}</strong></div>
                <div><span className="metric-label">Chat history</span><strong>{totalSessionChats}</strong></div>
                <div><span className="metric-label">Nguồn đã lưu</span><strong>{totalSessionSources}</strong></div>
                <div><span className="metric-label">Trang hiện tại</span><strong>{sessionTotal ? `${sessionOffset + 1}-${Math.min(sessionOffset + 6, sessionTotal)}` : '0'}</strong></div>
              </div>
              <div className="session-list">
                {sessionList.map((item) => (
                  <article
                    className={`session-card ${item.session_id === sessionId ? 'active' : ''}`}
                    key={item.session_id}
                  >
                    <div className="session-card-main">
                      <div>
                        <h3>{item.raw_idea || 'Session chưa có ý tưởng'}</h3>
                        <p>{item.session_id}</p>
                      </div>
                      <button className="btn secondary" type="button" onClick={() => resumeSession(item.session_id)}>
                        Mở pipeline
                      </button>
                    </div>
                    <div className="session-card-stats">
                      <span>{item.fsm_state}</span>
                      <span>{item.chat_count} chat</span>
                      <span>{item.source_count} nguồn</span>
                      <span>{item.version_count} version</span>
                      <span>{item.decision_count} quyết định</span>
                    </div>
                    <div className="mini-pipeline" aria-label="Tiếp tục tại stage">
                      {STEPS.map((label, i) => (
                        <button key={label} type="button" onClick={() => resumeSession(item.session_id, i)}>
                          <span>{String(i + 1).padStart(2, '0')}</span>
                          {label}
                        </button>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
              <div className="pagination-row">
                <button className="btn secondary" disabled={sessionOffset === 0 || loading} onClick={() => run(async () => refreshSessions(Math.max(0, sessionOffset - 6)))}>
                  Trước
                </button>
                <span>
                  {sessionTotal ? sessionOffset + 1 : 0}-{Math.min(sessionOffset + 6, sessionTotal)} / {sessionTotal}
                </span>
                <button className="btn secondary" disabled={sessionOffset + 6 >= sessionTotal || loading} onClick={() => run(async () => refreshSessions(sessionOffset + 6))}>
                  Sau
                </button>
              </div>
            </section>
          ) : null}
          {activeView === 'knowledge' ? (
            <section className="page-panel stack">
              <div className="page-hero knowledge-hero">
                <div>
                  <span className="eyebrow">Seeded backend data</span>
                  <h1>Knowledge base</h1>
                  <p>Dữ liệu nền được seed vào DB khi Docker start: research, baseline, backend method và design system.</p>
                </div>
                <select value={knowledgeCategory} onChange={(e) => setKnowledgeCategory(e.target.value)}>
                  <option value="">Tất cả</option>
                  <option value="research">Research</option>
                  <option value="evaluation">Evaluation</option>
                  <option value="backend-method">Backend method</option>
                  <option value="design-system">Design system</option>
                </select>
              </div>
              <button className="btn secondary" disabled={loading} onClick={() => run(async () => refreshKnowledge())}>
                Lọc dữ liệu
              </button>
              <div className="knowledge-grid">
                {knowledgeItems.map((item) => (
                  <article className="knowledge-card" key={item.id}>
                    <div className="knowledge-card-top">
                      <span className="badge PROPOSED">{item.category}</span>
                      <a href={item.source_url} target="_blank" rel="noreferrer">Nguồn</a>
                    </div>
                    <h3>{item.title}</h3>
                    <p>{item.summary}</p>
                    <div className="tag-row">
                      {item.tags.map((tag) => <span key={tag}>{tag}</span>)}
                    </div>
                    <button className="text-button card-link" type="button" onClick={() => setSelectedKnowledge(item)}>
                      Xem toàn bộ
                    </button>
                  </article>
                ))}
              </div>
              {selectedKnowledge ? (
                <aside className="knowledge-detail">
                  <div className="knowledge-card-top">
                    <span className="badge CONFIRMED">{selectedKnowledge.category}</span>
                    <button className="text-button" type="button" onClick={() => setSelectedKnowledge(null)}>Đóng</button>
                  </div>
                  <h2>{selectedKnowledge.title}</h2>
                  <p>{selectedKnowledge.summary}</p>
                  <a href={selectedKnowledge.source_url} target="_blank" rel="noreferrer">{selectedKnowledge.source_url}</a>
                  <pre>{JSON.stringify(selectedKnowledge.payload, null, 2)}</pre>
                </aside>
              ) : null}
            </section>
          ) : null}
          {activeView === 'chat' ? (
            <section className="page-panel stack">
              <div className="page-hero chat-hero">
                <div>
                  <span className="eyebrow">Per-session history</span>
                  <h1>Lịch sử trò chuyện</h1>
                  <p>Mỗi session có lịch sử riêng trong DB. Tạo session mới không làm mất lịch sử session cũ.</p>
                </div>
                <button className="btn secondary" disabled={loading} onClick={() => run(async () => refreshChat())}>
                  Tải lại
                </button>
              </div>
              <div className="analytics-grid">
                <div><span className="metric-label">Tổng lịch sử</span><strong>{chatMessages.length}</strong></div>
                <div><span className="metric-label">Nguồn trong session</span><strong>{sources.length}</strong></div>
                <div><span className="metric-label">Versions</span><strong>{versions.length}</strong></div>
                <div><span className="metric-label">Findings</span><strong>{findings.length}</strong></div>
              </div>
              <div className="topic-chart">
                {chatTopicStats.map((topic) => (
                  <div className="topic-row" key={topic.label}>
                    <span>{topic.label}</span>
                    <div><i style={{ width: `${Math.max(6, (topic.count / maxTopicCount) * 100)}%` }} /></div>
                    <strong>{topic.count}</strong>
                  </div>
                ))}
              </div>
              <div className="chat-log">
                {chatMessages.length ? chatMessages.map((message) => (
                  <article className={`chat-message ${message.role}`} key={message.id}>
                    <div>
                      <strong>{message.role}</strong>
                      <small>{message.step || 'general'} · {new Date(message.created_at).toLocaleString()}</small>
                    </div>
                    <p>{message.content}</p>
                  </article>
                )) : <p className="muted">Chưa có lịch sử trò chuyện cho session này.</p>}
              </div>
              <div className="chat-compose">
                <textarea value={chatDraft} placeholder="Ghi chú hoặc câu hỏi trong session này..." onChange={(e) => setChatDraft(e.target.value)} />
                <button
                  className="btn"
                  disabled={!chatDraft.trim() || loading}
                  onClick={() =>
                    run(async () => {
                      const id = await ensureSession()
                      const saved = await api.addChat(id, chatDraft.trim(), STEPS[step])
                      setChatMessages((items) => [...items, saved])
                      setChatDraft('')
                    })
                  }
                >
                  Lưu vào lịch sử
                </button>
              </div>
            </section>
          ) : null}
        </main>
      </div>
    </div>
  )
}
