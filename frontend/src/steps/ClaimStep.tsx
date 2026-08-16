import { useEffect, useState } from 'react'

type ClaimCard = {
  id?: string
  claim: string
  baseline: string
  metric: string
  evidence: string
  falsification: string
}

type Props = {
  contributions: string[]
  claimCards: ClaimCard[]
  loading: boolean
  onGenerate: () => void
  onConfirm: (
    payload: {
      contributions: string[]
      claim_cards: ClaimCard[]
    }
  ) => void
}

export function ClaimStep({
  contributions,
  claimCards,
  loading,
  onGenerate,
  onConfirm,
}: Props) {
  const [contribs, setContribs] = useState(contributions)
  const [cards, setCards] = useState(claimCards)

  useEffect(() => {
    setContribs(contributions)
    setCards(claimCards)
  }, [contributions, claimCards])

  return (
    <div className="panel stack">
      <h2>6. Contribution & Claim Evidence</h2>

      {!cards.length ? (
        <button
          className="btn"
          disabled={loading}
          onClick={onGenerate}
        >
          {loading ? 'Đang xây...' : 'Sinh contribution & claims'}
        </button>
      ) : (
        <>
          <h3>Contributions</h3>

          {contribs.map((c, i) => (
            <textarea
              key={i}
              value={c}
              onChange={(e) => {
                const next = [...contribs]
                next[i] = e.target.value
                setContribs(next)
              }}
            />
          ))}

          <h3>Claim Evidence cards</h3>

          {cards.map((card, i) => (
            <div
              className="spec-card stack"
              key={card.id || i}
            >
              {(
                [
                  'claim',
                  'baseline',
                  'metric',
                  'evidence',
                  'falsification',
                ] as const
              ).map((field) => (
                <label
                  key={field}
                  className="stack"
                >
                  <span className="muted">{field}</span>

                  <textarea
                    value={card[field]}
                    onChange={(e) => {
                      const next = [...cards]
                      next[i] = {
                        ...next[i],
                        [field]: e.target.value,
                      }
                      setCards(next)
                    }}
                  />
                </label>
              ))}
            </div>
          ))}

          <button
            className="btn"
            disabled={loading}
            onClick={() =>
              onConfirm({
                contributions: contribs,
                claim_cards: cards,
              })
            }
          >
            Xác nhận và sang thí nghiệm
          </button>
        </>
      )}
    </div>
  )
}