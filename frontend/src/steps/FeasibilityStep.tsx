import { useState } from 'react'
import { ChoiceGroup } from '../components/ChoiceGroup'

type Props = {
  feasibility: any | null
  loading: boolean
  onEstimate: () => void
  onChoose: (choice: string) => void
}

export function FeasibilityStep({
  feasibility,
  loading,
  onEstimate,
  onChoose,
}: Props) {
  const [choice, setChoice] = useState<string | null>('accept')
  const [other, setOther] = useState('')

  return (
    <div className="panel stack">
      <h2>8. Kiểm tra tính khả thi</h2>

      {!feasibility ? (
        <button
          className="btn"
          disabled={loading}
          onClick={onEstimate}
        >
          {loading ? 'Đang ước lượng...' : 'Ước lượng tài nguyên'}
        </button>
      ) : (
        <>
          {feasibility.over_budget ? (
            <div className="error">
              Có thể vượt ngân sách - cân nhắc scale-down.
            </div>
          ) : null}

          <div className="spec-card">
            <p>
              Model: {feasibility.model} · VRAM ~
              {feasibility.vram_gb}GB · Candidates{' '}
              {feasibility.candidates_per_round} · Rounds{' '}
              {feasibility.rounds}
            </p>

            <p>
              Samples {feasibility.samples_dev}/
              {feasibility.samples_val} · Tokens ~
              {feasibility.estimated_tokens?.toLocaleString() ||
                feasibility.estimated_tokens} · Hours ~
              {feasibility.estimated_hours}
            </p>

            <p>{feasibility.narrative}</p>

            <ul>
              {(feasibility.assumptions || []).map(
                (a: string) => (
                  <li key={a} className="muted">
                    {a}
                  </li>
                )
              )}
            </ul>
          </div>

          <ChoiceGroup
            options={feasibility.scale_down_options || []}
            value={choice}
            otherText={other}
            onSelect={setChoice}
            onOtherText={setOther}
            otherKeys={[]}
          />

          <button
            className="btn"
            disabled={!choice || loading}
            onClick={() => onChoose(choice!)}
          >
            Xác nhận cấu hình & assemble spec
          </button>
        </>
      )}
    </div>
  )
}