type Props = {
  idea: string
  setIdea: (v: string) => void
  onSubmit: () => void
  loading: boolean
}

export function IdeaStep({ idea, setIdea, onSubmit, loading }: Props) {
  return (
    <div className="panel stack">
      <h2>1. Nhập ý tưởng nghiên cứu</h2>
      <p className="muted">
        Mô tả ý tưởng còn mơ hồ. Hệ thống sẽ diễn giải lại trước khi viết proposal đầy đủ.
      </p>
      <textarea
        value={idea}
        onChange={(e) => setIdea(e.target.value)}
        placeholder="Ví dụ: Tôi muốn xây dựng phương pháp tự động tối ưu prompt nhiều vòng để giảm hallucination khi LLM trích xuất thông tin từ paper."
      />
      <div className="row">
        <button className="btn" disabled={!idea.trim() || loading} onClick={onSubmit}>
          {loading ? 'Đang lưu...' : 'Tiếp tục – Diễn giải lại'}
        </button>
      </div>
    </div>
  )
}