type Props = {
  markdown: string
  onExportJson: () => void
  onCopy: () => void
}

export function FinalStep({
  markdown,
  onExportJson,
  onCopy
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

        <button className="btn secondary" onClick={onExportJson}>
          Tải / xem JSON AST
        </button>
      </div>

      <div className="markdown-preview">{markdown}</div>
    </div>
  )
}