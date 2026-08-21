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
        Chuyển ý tưởng nghiên cứu mơ hồ thành research specification có bằng chứng, kế hoạch thí nghiệm và phản
        biện đa Judge. Mô tả ý tưởng còn mơ hồ bên dưới — hệ thống sẽ diễn giải lại trước khi viết proposal đầy đủ.
      </p>
      <textarea
        className="field-long"
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