import { useState } from "react";
import { CardBadge } from "../components/CardBadge";
import type { RelatedWorkEntry, SourceRef } from "../lib/types";

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
                    <div style={{ overflowX: 'auto' }}>
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
                                    const s= byId[e.source_id]
                                    return (
                                        <tr key={e.id}>
                                            <td>
                                                <div>{s?.title || e.source_id}</div>
                                                <div className="muted">
                                                    {s?.year || ''} {s?.doi_url ? `. ${s.doi_url}` : ''}
                                                </div>
                                            </td>
                                            <td>{e.did_what}</td>
                                            <td>{e.feedback_used}</td>
                                            <td>{e.open_point}</td>
                                            <td>
                                                <CardBadge status={e.support_label === 'SUPPORTS' ? 'CONFIRMED' : e.support_label === 'NOT' ? 'UNSUPPORTED' : 'AMBIGUOUS'} />
                                                {e.support_label}
                                            </td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>
                    </div>

                    <div>
                        <h3>Thêm paper thủ công</h3>
                        <input type="text" placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
                        <input type="url" placeholder="URL" value={url} onChange={(e) => setUrl(e.target.value)} />
                        <textarea placeholder="Abstract (optional)" value={abstract} onChange={(e) => setAbstract(e.target.value)} />
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
