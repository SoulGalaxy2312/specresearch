import type { ExperimentPlan } from '../lib/types'

type Props = {
  experiment: ExperimentPlan | null
  loading: boolean
  onGenerate: () => void
  onContinue: () => void
}

export function ExperimentStep({
  experiment,
  loading,
  onGenerate,
  onContinue,
}: Props) {
  return (
    <div className="panel stack">
      <h2>7. Thiết kế thí nghiệm</h2>

      {!experiment ? (
        <button
          className="btn"
          disabled={loading}
          onClick={onGenerate}
        >
          {loading
            ? 'Đang lập kế hoạch...'
            : 'Sinh experimental protocol'}
        </button>
      ) : (
        <>
          <div className="spec-card">
            <h3>So sánh baseline</h3>
            <p>{experiment.baseline_compare}</p>

            <h3>Đánh giá chất lượng</h3>
            <p>{experiment.quality_eval}</p>

            <h3>Ablation</h3>
            <p>{experiment.ablation}</p>

            <h3>Generalization</h3>
            <p>{experiment.generalization}</p>

            <h3>Fairness</h3>
            <ul>
              {(experiment.fairness_constraints || []).map(
                (f: string) => (
                  <li key={f}>{f}</li>
                )
              )}
            </ul>
          </div>

          <button className="btn" onClick={onContinue}>
            Tiếp tục - Feasibility
          </button>
        </>
      )}
    </div>
  )
}
