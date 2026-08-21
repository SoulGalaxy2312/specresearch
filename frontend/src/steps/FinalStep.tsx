import { DiffView } from '../components/DiffView'
import type { DiffItem, VersionSummary } from '../lib/types'

type Props = {
  markdown: string
  onExportJson: () => void
  onCopy: () => void
  versions: VersionSummary[]
  selectedVersionId: string | null
  versionDiff: DiffItem[]
  loading: boolean
  onLoadVersions: () => void
  onSelectVersion: (versionId: string) => void
}

export function FinalStep({
  markdown,
  onExportJson,
  onCopy,
  versions,
  selectedVersionId,
  versionDiff,
  loading,
  onLoadVersions,
  onSelectVersion,
}: Props) {
  return (
    <div className="panel stack">
      <h2>12. Bản spec cuối</h2>

      <p className="muted">
        Xuất Markdown hoặc JSON Spec AST.
      </p>

      <div className="row">
        <button className="btn" onClick={onCopy}>
          Copy Markdown
        </button>

        <button className="btn secondary" disabled={loading} onClick={onExportJson}>
          Tải / xem JSON AST
        </button>
      </div>

      <div className="markdown-preview">{markdown}</div>

      <h3>Lịch sử phiên bản</h3>
      {versions.length ? (
        <div className="row">
          {versions.map((v) => (
            <button
              key={v.id}
              className={`version-pill ${v.id === selectedVersionId ? 'selected' : ''}`}
              disabled={loading}
              onClick={() => onSelectVersion(v.id)}
            >
              v{v.version_no} · {v.label}
            </button>
          ))}
        </div>
      ) : (
        <button className="btn secondary" disabled={loading} onClick={onLoadVersions}>
          {loading ? 'Đang tải...' : 'Xem lịch sử phiên bản'}
        </button>
      )}

      {selectedVersionId ? (
        <>
          <div className="muted">So với phiên bản trước đó:</div>
          <DiffView diffs={versionDiff} />
        </>
      ) : null}
    </div>
  )
}
