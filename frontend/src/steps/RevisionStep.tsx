import { useState } from "react";
import { ChoiceGroup } from "../components/ChoiceGroup";
import { DiffView } from "../components/DiffView";
import type { DiffItem, JudgeAggregate } from "../lib/types";

type Props = {
    aggregate: JudgeAggregate | null
    diffs: DiffItem[]
    reviseCount: number
    loading: boolean
    onRevise: (choice: string, other_text?: string) => void
    onFinalize: () => void
    onRejudge: () => void
}

export function RevisionStep({
    aggregate,
    diffs,
    reviseCount,
    loading,
    onRevise,
    onFinalize,
    onRejudge,
}: Props) {
    const [choice, setChoice] = useState<string | null>(null)
    const [other, setOther] = useState('')
    const options = aggregate?.revision_options || []

    return (
        <div className="panel stack">
            <h2>11. Quyết định sửa đổi</h2>
            <p className="muted">
                Vòng revise hiện tại: {reviseCount}/2. {aggregate?.can_finalize_early ? 'Không còn MAJOR - có thể finalize sớm.' : ''}
            </p>
            <ChoiceGroup 
                options={options}
                value={choice}
                otherText={other}
                onSelect={setChoice}
                onOtherText={setOther}
            />

            <div className="row">
                <button 
                    className="btn"
                    disabled={!choice || loading}
                    onClick={() => {
                        if(choice === 'finalize') onFinalize()
                            else onRevise(choice!, choice === 'E' ? other : undefined)
                    }}
                >
                    {loading ? 'Đang áp dụng...' : 'Áp dụng'}
                </button>

                <button
                    className="btn secondary"
                    disabled={loading}
                    onClick={onFinalize}
                >
                    Hoàn tất ngay
                </button>

                {diffs.length ? (
                    <button
                        className="btn secondary"
                        disabled={loading}
                        onClick={onRejudge}
                    >
                        Chạy lại 5 Judge
                    </button>
                ) : null}
            </div>

            {diffs.length ? (
                <>
                    <h3>Diff sau revise</h3>
                    <DiffView 
                        diffs={diffs}
                    />
                </>
            ) : null}
        </div>
    )
}
