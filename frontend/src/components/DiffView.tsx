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
                        <div>
                            <div className="muted">Trước</div>
                            <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem' }}>{d.before || '-'}</pre>
                        </div>
                        <div>
                            <div className="muted">Sau</div>
                            <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem' }}>{d.after || '-'}</pre>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    )
}
