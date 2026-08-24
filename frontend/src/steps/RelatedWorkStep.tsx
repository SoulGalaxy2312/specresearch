import { useState } from 'react'
import { CardBadge } from '../components/CardBadge'
import type { RelatedWorkEntry, SourceRef } from '../lib/types'

type Props = {
    status: string
    sources: SourceRef[]
    relatedWork: RelatedWorkEntry[]
    loading: boolean
    onFetch: () => void
    onAddManual: (payload: { title: string; url?: string; abstract?: string }) => void
    onContinue: () => void
}

export function RelatedWorkStep({
    status,
    sources,
    relatedWork,
    loading,
    onFetch,
    onAddManual,
    onContinue,
}: Props) {
    const [title, setTitle] = useState('')
    const [url, setUrl] = useState('')
    const [abstract, setAbstract] = useState('')
    const byId: Record<string, SourceRef> = Object.fromEntries(sources.map((s) => [s.id, s]))

    return (
        <div className="panel stack">
            <h2>4. Nghiên cứu công trình liên quan</h2>
            <p className="muted">Metadata-only qua OpenAlex. Mọi nhận định gắn source cụ thể.</p>
            {!relatedWork.length ? (
                <button className="btn" disabled={loading} onClick={onFetch}>
                    {loading ? 'Đang tìm...' : 'Tìm related work'}
                </button>
            ) : (
                <>
                    {status === 'DEGRADED' ? (
                        <div className="error">Retrieval degraded - bạn có thể thêm paper thủ công.</div>
                    ) : null}
                    <div className="table-scroll">
                        <table>
                            <thead>
                                <tr>
                                    <th>Nghiên cứu</th>
                                    <th>Đã làm gì?</th>
                                    <th>Feedback</th>
                                    <th>Điểm mở</th>
                                    <th>Support</th>
                                </tr>
                            </thead>
                            <tbody>
                                {relatedWork.map((e) => {
                                    const source = byId[e.source_id]
                                    return (
                                        <tr key={e.id}>
                                            <td>
                                                <div>{source?.title || e.source_id}</div>
                                                <div className="source-meta">
                                                    {source?.year || 'Không rõ năm'}
                                                    {source?.doi_url ? (
                                                        <>
                                                            {' · '}
                                                            <a href={source.doi_url} target="_blank" rel="noreferrer">
                                                                Mở nguồn
                                                            </a>
                                                        </>
                                                    ) : null}
                                                </div>
                                            </td>
                                            <td>{e.did_what}</td>
                                            <td>{e.feedback_used}</td>
                                            <td>{e.open_point}</td>
                                            <td>
                                                <CardBadge
                                                    status={
                                                        e.support_label === 'SUPPORTS'
                                                            ? 'CONFIRMED'
                                                            : e.support_label === 'NOT'
                                                              ? 'UNSUPPORTED'
                                                              : 'AMBIGUOUS'
                                                    }
                                                />
                                                {e.support_label}
                                            </td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>
                    </div>

                    <div className="manual-source-form">
                        <h3>Thêm paper thủ công</h3>
                        <label className="stack">
                            <span className="field-label">Tiêu đề paper</span>
                            <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} />
                        </label>
                        <label className="stack">
                            <span className="field-label">URL hoặc DOI</span>
                            <input type="url" value={url} onChange={(e) => setUrl(e.target.value)} />
                        </label>
                        <label className="stack">
                            <span className="field-label">Abstract (không bắt buộc)</span>
                            <textarea
                                className="field-long"
                                value={abstract}
                                onChange={(e) => setAbstract(e.target.value)}
                            />
                        </label>
                        <button
                            className="btn secondary"
                            disabled={!title.trim() || loading}
                            onClick={() => {
                                onAddManual({ title, url, abstract })
                                setTitle('')
                                setUrl('')
                                setAbstract('')
                            }}
                        >
                            Thêm paper
                        </button>
                    </div>

                    <button className="btn" onClick={onContinue}>
                        Tiếp tục - Research gap
                    </button>
                </>
            )}
        </div>
    )
}
