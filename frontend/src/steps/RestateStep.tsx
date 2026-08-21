import { useState } from "react";
import { ChoiceGroup } from "../components/ChoiceGroup";

type Interpretation = { id: string; text: string }

type Props = {
    interpretations: Interpretation[]
    loading: boolean
    onGenerate: () => void
    onConfirm: (action: string, text: string) => void
}

const ACTIONS = [
    { key: 'confirm', label: 'Xác nhận', explanation: 'Hệ thống đang hiểu đúng ý bạn', example: null },
    { key: 'edit', label: 'Chỉnh sửa', explanation: 'Sửa diễn giải rồi xác nhận.', example: null },
    { key: 'alternative', label: 'Yêu cầu ví dụ khác', explanation: 'Sinh diễn giải khác', example: null },
    { key: 'other', label: 'Other', explanation: 'Nhập cách hiểu riêng.', example: null },
]

export function RestateStep({ interpretations, loading, onGenerate, onConfirm }: Props) {
    const [selected, setSelected] = useState<string | null>(null)
    const [text, setText] = useState('')
    const [choice, setChoice] = useState<string | null>(null)
    const [other, setOther] = useState('')
    const selectedInterpretation = interpretations.find((it) => it.id === selected) || interpretations[0]
    const draftText = text || selectedInterpretation?.text || ''

    return (
        <div className="stack">
            <h2>2. Diễn giải lại ý tưởng</h2>
            <p className="muted">Tôi đang hiểu đúng ý tưởng của bạn không?</p>
            {!interpretations.length ? (
                <button className="btn" disabled={loading} onClick={onGenerate}>
                    {loading ? 'Đang sinh...' : 'Sinh diễn giải'}
                </button>
            ) : (
                <>
                    <div className="stack">
                        {interpretations.map((it) => (
                            <button
                                key={it.id}
                                type="button"
                                className={`choice-item ${selected === it.id ? 'selected' : ''}`}
                                onClick={() => {
                                    setSelected(it.id)
                                    setText(it.text)
                                }}
                            >
                                {it.text}
                            </button>
                        ))}
                    </div>

                    <textarea className="field-long" value={draftText} onChange={(e) => setText(e.target.value)} />
                    <ChoiceGroup 
                        options={ACTIONS}
                        value={choice}
                        otherText={other}
                        onSelect={setChoice}
                        onOtherText={setOther}
                        otherKeys={['other', 'edit']}
                    />

                    <div className="row">
                        <button
                            className="btn"
                            disabled={!choice || loading}
                            onClick={() => {
                                if (choice === 'alternative') {
                                    onConfirm('alternative', draftText)
                                    return
                                }
                                const finalText = choice === 'other' || choice === 'edit' ? other || draftText : draftText
                                onConfirm(choice === 'other' ? 'other' : choice === 'edit' ? 'edit' : 'confirm', finalText)
                            }}
                        >
                            {loading ? 'Đang xử lý...' : 'Xác nhận bước này'}
                        </button>
                    </div>
                </>
            )}
        </div>
    )
}
