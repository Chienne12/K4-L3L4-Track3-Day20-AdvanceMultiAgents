# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Phùng Trọng Chiến | 2A202602430 | Hoàn thiện harness và thực hiện thí nghiệm với sự hỗ trợ của Codex; kiểm tra và diễn giải kết quả. |

- Mô hình: OpenAI `gpt-4.1-mini`, base URL `https://api.openai.com/v1`; giữ tên biến `AZURE_OPENAI_*` của lab để cấu hình ChatOpenAI. `LAB_TEMPERATURE=0`, `recursion_limit=60`.
- Phiên bản Deep Agents: 0.7.21; Python 3.12.15; chạy trong container Linux Docker trên máy Windows.
- Kiểm tra ngoại tuyến: 29/29 test đạt trong Docker (12 provided, 9 agent, 6 runner, 2 curator).
- Số lần chạy tác vụ đã dùng / ngân sách: đang thực hiện 21 lần chạy tác vụ theo GUIDE (18 chính thức và 3 thử skill trước đóng băng), 1 lần curator và 1 lần thử API; không chạy phần mở rộng. Không có ngân sách tiền được chỉ định.
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): Dự đoán subagents không vượt baseline về điểm trung bình đánh giá và tốn nhiều token hơn. Trên tác vụ học, subagents đạt code 6/10, data 0/8, logs 0/9; baseline đạt 6/10, 5/8, 1/9. Trace data cho thấy agent chính dùng báo cáo general-purpose rồi ghi kết quả mà không kiểm chứng bằng shell. Thêm vai trò không bảo đảm quy trình được thực hiện tốt hơn.
- H2 (skills-auto so với baseline): Dự đoán skills-auto có điểm trung bình đánh giá cao nhất trong ba điều kiện nhờ hướng dẫn kiểm tra code, chuẩn hóa dữ liệu và xử lý log; tuy nhiên không dự đoán đạt toàn bộ check. Skill code nhắc type hints/changelog, skill logs nhắc chuẩn hóa service và sắp xếp; skill data chưa chỉ rõ meta, skill logs chưa chỉ rõ giá trị schema header. Đây là giả thuyết cho bộ skill của lab, không suy rộng từ kết quả skill do con người viết trong [SkillsBench](https://arxiv.org/abs/2602.12670).
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán mức tăng điểm của skills-auto so với baseline lớn hơn trên tác vụ học so với tác vụ đánh giá, vì skill được rút từ phản hồi học và chưa biết quy ước mới của đánh giá. [SkillEvolBench](https://arxiv.org/abs/2605.24117) ghi nhận cải thiện tại chỗ không bảo đảm chuyển thành skill bền vững trên frozen deployment; đây là căn cứ để kiểm tra khả năng tổng quát hóa thay vì giả định skill luôn giúp.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Công cụ mặc định: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. Công cụ `execute` chạy lệnh shell trong sandbox và trả stdout/stderr cùng mã thoát. Trong cấu hình thí nghiệm này shell chạy trong Linux Docker.
2. Công cụ `task` giao một nhiệm vụ nhiều bước cho subagent `general-purpose`, có các công cụ như agent chính. Mỗi lần gọi mặc định chỉ nhận prompt được giao, không tự nhận lịch sử hội thoại của agent chính, và trả một báo cáo cuối để agent chính tổng hợp.
3. System prompt mặc định quan sát bằng `scripts/tour.py` là chuỗi rỗng. Hướng dẫn hành vi vẫn xuất hiện trong mô tả công cụ:

   - `task`: “Launch multiple agents concurrently when their tasks are independent, using a single message with multiple tool calls.”
   - `execute`: “Use read_file rather than cat/head/tail.”

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| | | | |

Nhận xét: nhóm lỗi nào chiếm đa số? Skill có thể phòng ngừa nhóm đó không?

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc):
- Ảnh hưởng đến token và thời gian:

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do:

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| | | | |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
