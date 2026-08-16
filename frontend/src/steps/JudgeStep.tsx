import { CardBadge } from '../components/CardBadge'

type Props = {
  progress: string[]
  findings: any[]
  aggregate: any | null
  loading: boolean
  onRun: () => void
}

export function JudgeStep({
  progress,
  findings,
  aggregate,
  loading,
  onRun,
}: Props) {
  return (
    <div className="panel stack">
      <h2>10. Multi-Judge review</h2>
      <p className="muted">
        &gt;5 Judge tuần tự, isolated prompt, cùng một model Groq.
      </p>

      {!aggregate ? (
        <>
          <div className="row">
            {['contribution', 'experiment', 'evidence', 'readiness'].map((s) => (
              <span
                key={s}
                className={`step-pill ${
                  progress.includes(s) ? 'done' : ''
                }`}
              >
                {s}
              </span>
            ))}
          </div>

          <button className="btn" disabled={loading} onClick={onRun}>
            {loading ? 'Đang chạy judges...' : 'Bắt đầu Judge panel'}
          </button>

          {findings.length ? (
            <div className="stack">
              {findings.map((f, i) => (
                <div className="spec-card" key={i}>
                  <CardBadge status={f.severity} />
                  <strong>
                    [{f.judge_type}] {f.issue}
                  </strong>
                  <p className="muted">{f.reason}</p>
                  <p>Đề xuất: {f.suggestion}</p>
                </div>
              ))}
            </div>
          ) : null}
        </>
      ) : (
        <>
          <p>
            MAJOR: {aggregate.major_count} · Consensus: {(aggregate.consensus || []).length} · Disagreement:{' '}
            {(aggregate.disagreement || []).length}
          </p>

          <h3>Đồng thuận</h3>
          {(aggregate.consensus || []).map((c: any, i: number) => (
            <div className="spec-card" key={`c-${i}`}>
              <CardBadge status={c.severity} />
              {c.target}: {(c.issues || []).join(' | ')}
            </div>
          ))}

          <h3>Bất đồng</h3>
          {(aggregate.disagreement || []).map((d: any, i: number) => (
            <div className="spec-card" key={`d-${i}`}>
              <CardBadge status={d.severity} />
              {d.target}: {(d.issues || []).join(' | ')}
            </div>
          ))}
        </>
      )}
    </div>
  )
}