import { useState } from 'react'
import { CardBadge } from '../components/CardBadge'
import { ChoiceGroup } from '../components/ChoiceGroup'

type Card = {
  id: string
  card_type: string
  status: string
  content: string
}

type Issue = {
  card_hint?: string
  question: string
  options: {
    key: string
    label: string
    explanation: string
    example?: string | null
  }[]
}

type Props = {
  cards: Card[]
  issues: Issue[]
  loading: boolean
  onDecompose: () => void
  onResolve: (payload: {
    choice_key: string
    choice_text: string
    options: Issue['options']
  }) => void
  onContinue: () => void
}

export function DecomposeStep({
  cards,
  issues,
  loading,
  onDecompose,
  onResolve,
  onContinue,
}: Props) {
  const [choice, setChoice] = useState<string | null>(null)
  const [other, setOther] = useState('')

  const issue = issues[0]

  return (
    <div className="panel stack">
      <h2>3. Phân rã ý tưởng</h2>

      {!cards.length ? (
        <button
          className="btn"
          disabled={loading}
          onClick={onDecompose}
        >
          {loading ? 'Đang phân rã...' : 'Phân rã thành thẻ'}
        </button>
      ) : (
        <>
          <div className="card-grid two">
            {cards.map((c) => (
              <div className="spec-card" key={c.id}>
                <CardBadge status={c.status} />
                <strong>{c.card_type}</strong>
                <p>{c.content}</p>
              </div>
            ))}
          </div>

          {issue ? (
            <div className="stack">
              <h3>{issue.question}</h3>

              <ChoiceGroup
                options={issue.options}
                value={choice}
                otherText={other}
                onSelect={setChoice}
                onOtherText={setOther}
              />

              <button
                className="btn secondary"
                disabled={!choice || loading}
                onClick={() => {
                  const opt = issue.options.find(
                    (o) => o.key === choice
                  )

                  const text =
                    choice === 'E'
                      ? other
                      : `${opt?.label || choice}: ${
                          opt?.explanation || ''
                        }`

                  onResolve({
                    choice_key: choice!,
                    choice_text: text,
                    options: issue.options,
                  })
                }}
              >
                Lưu quyết định làm rõ
              </button>
            </div>
          ) : null}

          <button
            className="btn"
            disabled={loading}
            onClick={onContinue}
          >
            Tiếp tục - Related work
          </button>
        </>
      )}
    </div>
  )
}