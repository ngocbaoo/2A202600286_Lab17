# Báo cáo Benchmark: Multi-Memory Agent

**Họ tên:** Tạ Bảo Ngọc

**MSSV:** 2A202600286

## 1. Tổng quan (Executive Summary)
Báo cáo này trình bày kết quả đánh giá hiệu suất của Agent tích hợp hệ thống đa bộ nhớ (Short-term, Long-term Redis, Episodic JSON, Semantic Chroma) so với Agent cơ bản không có bộ nhớ bổ trợ. Thử nghiệm được thực hiện trên 10 kịch bản hội thoại đa lượt với độ khó khác nhau.

### Chỉ số chính (Key Metrics)
| Chỉ số | Agent Có Bộ Nhớ (Session A) | Agent Không Bộ Nhớ (Session B) |
| :--- | :---: | :---: |
| **Độ liên quan trung bình (Relevance)** | **8.0 / 10** | 6.4 / 10 |
| **Sử dụng ngữ cảnh (Context Utilization)** | **6.6 / 10** | 1.2 / 10 |
| **Hiệu suất Token (Token Efficiency)** | 7.6 / 10 | 7.4 / 10 |
| **Độ trễ trung bình (Latency)** | ~9.6s | **~8.4s** |

---

## 2. Phân tích chi tiết từng kịch bản (Case-by-case Analysis)

### Kịch bản 1: User Preference Recall (Trung bình)
- **Kết quả**: Agent có bộ nhớ (A) đạt điểm Relevance cao hơn (6 vs 5) nhưng vẫn gặp khó khăn trong việc nhớ lại màu sắc yêu thích ở lượt cuối.
- **Nhận xét**: Bộ nhớ Long-term (Redis) đã lưu trữ thông tin nhưng việc truy xuất (Recall) cần được tối ưu hóa để đảm bảo độ chính xác tuyệt đối.

### Kịch bản 2: Semantic Fact Retrieval (Trung bình)
- **Kết quả**: Agent A thắng tuyệt đối (Relevance 10 vs 9, Context Utilization 9 vs 0).
- **Nhận xét**: Bộ nhớ Semantic (ChromaDB) hoạt động cực kỳ hiệu quả trong việc truy xuất kiến thức về các mô hình LLM mới (DeepSeek-V3).

### Kịch bản 3: Episodic Experience (Khó)
- **Kết quả**: Cả hai Agent đều gặp khó khăn trong việc nhớ lại chi tiết chuyến đi ban đầu.
- **Nhận xét**: Bộ nhớ Episodic (JSON) ghi lại lịch sử nhưng khả năng kết nối các tình tiết thay đổi trong quá khứ cần được cải thiện.

### Kịch bản 4: Context Window Stress (Khó)
- **Kết quả**: Agent A duy trì thông tin tốt hơn (Relevance 9 vs 5).
- **Nhận xét**: Hệ thống Context Management với cơ chế ưu tiên (Priority-based eviction) giúp Agent A không bị mất các thông tin quan trọng khi cửa sổ ngữ cảnh bị đầy.

### Kịch bản 5: Combined Memory (Khó)
- **Kết quả**: Agent A vượt trội (Relevance 10 vs 4).
- **Nhận xét**: Việc kết hợp thông tin từ nhiều nguồn (Tên người dùng từ Redis, Kiến thức từ Chroma) cho thấy sức mạnh của kiến trúc đa tầng.

### Kịch bản 6-10: Các trường hợp khác
- **Personal Preferences**: Agent A ghi điểm tuyệt đối nhờ nhớ được dị ứng đậu phộng của người dùng để đưa ra lời khuyên an toàn.
- **Multi-Step Reasoning**: Agent A kết hợp được hạn chót dự án và thời gian viết báo cáo để tính toán ngày bắt đầu chính xác.
- **Fact Verification**: Agent A sử dụng tốt thông tin đã cung cấp ở lượt trước để trả lời câu hỏi tiếp theo.

---

## 3. Phân tích hiệu năng bộ nhớ (Memory Analysis)

### Tỷ lệ Hit Rate (Memory Hit Rate)
- Tỷ lệ bộ nhớ được kích hoạt trung bình là **~33%**. 
- Các kịch bản về sự kiện thực tế (Semantic) và sở thích người dùng (Long-term) có tỷ lệ Hit Rate cao nhất.
- Bộ nhớ Episodic cần cơ chế định tuyến (Router) nhạy bén hơn để kích hoạt đúng lúc.

### Quản lý cửa sổ ngữ cảnh (Context Management)
- Cơ chế phân cấp 4 tầng (System > Query > Memory > Buffer) giúp bảo vệ các chỉ thị hệ thống và dữ liệu bộ nhớ quan trọng nhất.
- Token Efficiency của hai phiên bản tương đương nhau, cho thấy việc thêm bộ nhớ không làm lãng phí token một cách vô ích.

---

## 4. Kết luận và Đề xuất (Conclusion & Recommendations)

### Kết luận
Hệ thống **Multi-memory Agent** cải thiện đáng kể khả năng cá nhân hóa và ghi nhớ thông tin dài hạn của AI. Đặc biệt hiệu quả trong các nhiệm vụ yêu cầu:
1. Tuân thủ sở thích/ràng buộc của người dùng (An toàn thực phẩm, phong cách trả lời).
2. Truy xuất kiến thức chuyên sâu không nằm trong dữ liệu huấn luyện (RAG).
3. Suy luận đa bước dựa trên dữ liệu lịch sử.

### Đề xuất cải tiến
1. **Tối ưu hóa Router**: Cải thiện Prompt cho Memory Router để phân loại chính xác hơn các yêu cầu cần truy xuất Episodic memory.
2. **Giảm độ trễ**: Việc truy vấn đồng thời nhiều nguồn bộ nhớ làm tăng độ trễ ~1.2s. Có thể cân nhắc chạy truy vấn song song (Parallel retrieval).
3. **Refine Semantic Search**: Tinh chỉnh ngưỡng (Threshold) cho ChromaDB để tránh việc lấy ra các đoạn văn bản không liên quan nhưng có độ tương đồng vector cao.
