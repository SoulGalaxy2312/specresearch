import type { ChoiceOption } from '../lib/types'

type Props = {
    options: ChoiceOption[],
    value: string | null,
    otherText: string
    onSelect: (key: string) => void
    onOtherText: (text: string) => void
    otherKeys?: string[]
}

export function ChoiceGroup({
    options,
    value,
    otherText,
    onSelect,
    onOtherText,
    otherKeys = ['E', 'other', 'Other'],
}: Props) {
    const isOther = value !== null && otherKeys.includes(value)
    const displayKey = (key: string, index: number) => {
        if (/^[A-Z]$/i.test(key)) return key.toUpperCase()
        return String.fromCharCode(65 + index)
    }

    return (
        <div className="stack">
            <div className="choice-list" role="radiogroup" aria-label="Các phương án">
                {options.map((opt, index) => (
                    <button
                        key={opt.key}
                        type="button"
                        role="radio"
                        aria-checked={value === opt.key}
                        className={`choice-item ${value === opt.key ? 'selected' : ''}`}
                        onClick={() => onSelect(opt.key)}
                    >
                        <span className="choice-key" aria-hidden="true">
                            {displayKey(opt.key, index)}
                        </span>
                        <span className="choice-copy">
                            <strong>{opt.label}</strong>
                            <span className="choice-description">{opt.explanation}</span>
                            {opt.example ? (
                                <span className="choice-example">Ví dụ: {opt.example}</span>
                            ) : null}
                        </span>
                    </button>
                ))}
            </div>
            {isOther ? (
                <textarea
                    className="choice-other"
                    aria-label="Nội dung phương án khác"
                    placeholder="Mô tả phương án của bạn…"
                    value={otherText}
                    onChange={(e) => onOtherText(e.target.value)}
                />
            ) : null}
        </div>
    )
}
