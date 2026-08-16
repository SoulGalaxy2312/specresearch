type Props = {
    markdown: string
    loading: boolean
    onAssemble: () => void
    onStartJudges: () => void
}

export function SpecDraftStep({ markdown, loading, onAssemble, onStartJudges }: Props) {
    return (
        <div className="panel stack">
            <h2>9. Research spec draft</h2>
            {!markdown ? (
                <button className="btn" disabled={loading} onClick={onAssemble}>
                    {loading ? 'Đang ghép spec...' : 'Assemble spec'}
                </button>
            ) : (
                <>
                    <div className="markdown-preview">{markdown}</div>
                    <button className="btn" disabled={loading} onClick={onStartJudges}>
                        Chạy 5 Judge độc lập
                    </button>
                </>
            )}
        </div>
    )
}