import { useState } from "react"
import { ChoiceGroup } from "../components/ChoiceGroup"

type Props = {
  gap: any | null
  loading: boolean
  onGenerate: () => void
  onChoose: (choice: string, other_text?: string) => void
}

export function GapStep({ gap, loading, onGenerate, onChoose }: Props) {
  const [choice, setChoice] = useState<string | null>(null)
  const [other, setOther] = useState('')

  return (
    <div className="panel stack">
      <h2>5. Đề xuất research gap</h2>
      {!gap ? (
        <button className="btn" disabled={loading} onClick={onGenerate}>
          {loading ? 'Đang đề xuất...' : 'Sinh gap candidates'}
        </button>
      ) : (
        <>
          <div className="spec-card">
            <p>{gap.statement}</p>
            <p className="muted">Prior: {gap.prior_work}</p>
            <p className="muted">Limitation: {gap.limitation}</p>
            <p className="muted">Why: {gap.why_matters}</p>
            <p className="muted">How to test: {gap.how_to_test}</p>
          </div>

          <ChoiceGroup
            options={gap.options || []}
            value={choice}
            otherText={other}
            onSelect={setChoice}
            onOtherText={setOther}
          />

          <button
            className="btn"
            disabled={!choice}
            onClick={() => onChoose(choice!, choice === 'E' ? other : undefined)}
          >
            Chọn hướng contribution
          </button>
        </>
      )}
    </div>
  )
}