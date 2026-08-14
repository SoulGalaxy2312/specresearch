type ChoiceOption = {
    key: string
    label: string
    explanation: string
    example?: string | null
}

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
    return (
        <div className="stack">
            <div className="choice-list">
                {options.map((opt) => (
                    <button
                        key={opt.key}
                        type="button"
                        className={`choice-item ${value === opt.key ? 'selected' : ''}`}
                        onClick={() => onSelect(opt.key)}
                    >
                        <strong>
                            {opt.key}. {opt.label}
                        </strong>
                        <div className="muted">{opt.explanation}</div>
                        {opt.example ? <div className="muted">Ví dụ: {opt.example}</div> : null}
                    </button>
                ))}
            </div>
            {isOther ? (
                <textarea 
                    placeholder="Nhập phương án Other..."
                    value={otherText}
                    onChange={(e) => onOtherText(e.target.value)}
                />
            ) : null}
        </div>
    )
}