const COLORS: Record<string, string> = {
    CONFIRMED: 'CONFIRMED',
    PROPOSED: 'PROPOSED',
    MISSING: 'MISSING',
    AMBIGUOUS: 'AMBIGUOUS',
    UNSUPPORTED: 'UNSUPPORTED',
    CONFLICT: 'CONFLICT',
    MAJOR: 'MAJOR',
    MINOR: 'MINOR',
}

export function CardBadge({ status }: { status: string }) {
    const cls = COLORS[status] || 'PROPOSED'
    return <span className={`badge ${cls}`}>{status}</span>
}