import type { DiffItem } from '../lib/types'

export function DiffView({ diffs }: { diffs: DiffItem[] }) {
    if (!diffs?.length) {
        return <p className="muted">Không có thay đổi trong section nào.</p>
    }

    return (
        <div className="stack">
            {diffs.map((d) => (
                <div className="diff-block" key={d.section}>
                    <h4>{d.section}</h4>
                    <div className="card-grid two">
                        <div className="diff-column">
                            <div className="diff-label">Trước</div>
                            <pre className="diff-content">{d.before || '—'}</pre>
                        </div>
                        <div className="diff-column">
                            <div className="diff-label">Sau</div>
                            <pre className="diff-content">{d.after || '—'}</pre>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    )
}
