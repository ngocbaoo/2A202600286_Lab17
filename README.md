# Multi-Memory Agent with LangGraph (Lab 17)

Lab này triển khai một AI Agent nâng cao sử dụng kiến trúc Multi-memory stack được xây dựng trên nền tảng LangGraph. Hệ thống cho phép Agent ghi nhớ thông tin ngắn hạn, sở thích dài hạn, các tập hội thoại quá khứ và kiến thức thực tế thông qua các cơ sở dữ liệu chuyên biệt.

## Tính năng chính

### 1. Hệ thống đa tầng bộ nhớ (4-Layer Memory Stack)
- **Short-term Memory**: Quản lý hội thoại hiện tại (Conversation Buffer).
- **Long-term Profile (Redis)**: Lưu trữ hồ sơ người dùng, sở thích và thông tin cá nhân bền vững.
- **Episodic Memory (JSON)**: Ghi nhật ký các tập (episodes) hội thoại để truy xuất kinh nghiệm quá khứ.
- **Semantic Memory (ChromaDB)**: Truy xuất thông tin dựa trên ý nghĩa (RAG) sử dụng Vector Database.

### 2. Điều phối thông minh (Memory Router)
Sử dụng LLM (GPT-4o mini) để phân tích ý định của người dùng và quyết định tầng bộ nhớ nào cần được kích hoạt (ví dụ: truy vấn sở thích vs. truy vấn kiến thức thực tế).

### 3. Quản lý ngữ cảnh (Context Window Management)
Cơ chế phân cấp 4 cấp độ ưu tiên để quản lý token budget hiệu quả:
- **Cấp 1**: Chỉ thị hệ thống (System Prompt) - Ưu tiên cao nhất.
- **Cấp 2**: Câu hỏi hiện tại của người dùng.
- **Cấp 3**: Các thông tin truy xuất từ bộ nhớ (Profile, Semantic, Episodic).
- **Cấp 4**: Lịch sử hội thoại gần nhất (Buffer) - Sẽ bị cắt tỉa đầu tiên khi hết bộ nhớ.

---

## Cài đặt

1. **Yêu cầu hệ thống**: Python 3.9+ 
2. **Cài đặt thư viện**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Cấu hình môi trường**: 
   Tạo file `.env` từ mẫu và thêm `GITHUB_TOKEN` của bạn:
   ```env
   GITHUB_TOKEN=your_github_token_here
   AZURE_INFERENCE_ENDPOINT=https://models.inference.ai.azure.com
   AZURE_INFERENCE_MODEL=gpt-4o-mini
   ```

---

## Chạy Benchmark

Lab này bao gồm một bộ công cụ benchmark tự động so sánh Agent có bộ nhớ vs. không có bộ nhớ trên 11 kịch bản đa lượt (multi-turn):

```bash
python benchmark/run.py
```

Kết quả sẽ được lưu tại:
- `benchmark_results.csv`: Dữ liệu thô về độ trễ, hit rate và điểm số.
- `report/benchmark_report.md`: Báo cáo phân tích chi tiết.

---

## Cấu trúc thư mục
- `src/memory/`: Triển khai các backend bộ nhớ (Redis, Chroma, JSON).
- `src/agent/`: Logic điều hướng, quản lý ngữ cảnh và đồ thị LangGraph.
- `benchmark/`: Kịch bản kiểm thử và công cụ chạy benchmark.
- `report/`: Báo cáo đánh giá hiệu năng.
