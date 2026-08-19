import type { ClaimEvidenceCard } from '../lib/types'

type Props = {
  contributions: string[]
  claimCards: ClaimEvidenceCard[]
  loading: boolean
  onGenerate: () => void
  onContributionsChange: (contributions: string[]) => void
  onClaimCardsChange: (claimCards: ClaimEvidenceCard[]) => void
  onConfirm: (
    payload: {
      contributions: string[]
      claim_cards: ClaimEvidenceCard[]
    }
  ) => void
}

export function ClaimStep({
  contributions,
  claimCards,
  loading,
  onGenerate,
  onContributionsChange,
  onClaimCardsChange,
  onConfirm,
}: Props) {
  return (
    <div className="panel stack">
      <h2>6. Contribution & Claim Evidence</h2>

      {!claimCards.length ? (
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

          {contributions.map((c, i) => (
            <textarea
              key={i}
              value={c}
              onChange={(e) => {
                const next = [...contributions]
                next[i] = e.target.value
                onContributionsChange(next)
              }}
            />
          ))}

          <h3>Claim Evidence cards</h3>

          {claimCards.map((card, i) => (
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
                      const next = [...claimCards]
                      next[i] = {
                        ...next[i],
                        [field]: e.target.value,
                      }
                      onClaimCardsChange(next)
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
                contributions,
                claim_cards: claimCards,
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
