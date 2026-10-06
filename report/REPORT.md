# Ghi chú thực hiện lab: Self evolving Agentic

## 1. Cấu hình đã dùng

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Phùng Trọng Chiến | 2A202602430 | Chạy thử và đọc kết quả ,promt|

- Dùng OpenAI `gpt-4.1-mini` tại `https://api.openai.com/v1`, giữ tên biến `.env` ban đầu.
- `LAB_TEMPERATURE=0`, `recursion_limit=60`; Deep Agents 0.7.21; Python 3.12.15; Linux Docker trên máy Windows.
- Đã chạy 18 lượt chính thức và 3 lượt thử skill. Curator chạy một lần; thử API trả về `OK`.
- Tổng token chạy bài: 930,738, chưa tính curator và câu thử API.
- Docker đạt 29/29 test. Windows chỉ đạt 27/29 vì thiếu lệnh `which` và `cat`.
- Đã lưu dự đoán trước khi đánh giá: commit `1a8c6f9`. Tag `freeze` ở commit `d49af2b`.

## 2. Dự đoán trước khi chạy đánh giá


- H1: Thêm subagent có thể tốn token hơn nhưng điểm chưa chắc cao hơn, vì agent chính vẫn cần kiểm tra lại kết quả.
- H2: Có skill hướng dẫn, agent có thể đạt điểm cao hơn baseline, nhưng vẫn có thể bỏ sót yêu cầu.
- H3: Skill có thể giúp bài đã học tốt hơn bài mới, vì nó được tạo từ lỗi của bài đã học.

## 3. Làm quen Deep Agents

1. Có 9 công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. Dùng `execute` để chạy lệnh và nhận kết quả cùng mã thoát.
2. Dùng `task` để giao việc. Subagent `general-purpose` có công cụ như agent chính, nhưng chỉ thấy nội dung được giao.
3. System prompt mặc định rỗng (`''`). Hướng dẫn vẫn nằm trong mô tả công cụ:

   - `task`: “Launch multiple agents concurrently when their tasks are independent, using a single message with multiple tool calls.”
   - `execute`: “Use read_file rather than cat/head/tail.”

## 4. Các lỗi thấy ở baseline

Các lỗi dưới đây lấy từ `run.json` và `trace.md` của ba bài học. E là lỗi quy ước; D là lỗi xử lý dữ liệu.

| Bài | Check lỗi | Nhóm | Nhận xét và trích ngắn từ detail |
|---|---|---|---|
| code-learn | `rule_type_hints` | E | Thiếu khai báo kiểu: “type annotations on all parameters and on the return value”. |
| code-learn | `rule_regression_tests` | E | Thiếu test kiểm tra lỗi đã sửa: “add tests/test_regressions.py”. |
| code-learn | `rule_changelog` | E | Thiếu ghi chú sửa lỗi: “record each fix in CHANGELOG.md”. |
| data-learn | `rule_money_in_cents` | E | Tiền chưa viết thành số nguyên cents: “integer cents”. |
| data-learn | `rule_meta_block` | E | Thiếu `meta` gồm `source`, `rows_in`, `rows_used`. |
| data-learn | `rule_clean_csv` | E | Chưa có file đúng yêu cầu: “write workspace/clean.csv”. |
| logs-learn | `entry_count` | D | Sai số bản ghi: “wrong number of entries (got 20)”. |
| logs-learn | `timestamps_utc` | D | Chỉ đúng 8/25 thời điểm: “8/25 timestamps match”. |
| logs-learn | `exception_fields` | D | Sai 17 giá trị: “17 wrong `exception` values”. |
| logs-learn | `repeat_counts` | D | Sai 17 giá trị: “17 wrong `repeat_count` values”. |
| logs-learn | `counts_by_service` | D | Tổng theo service sai: “counts_by_service: wrong values”. |
| logs-learn | `rule_service_names` | E | Tên service chưa đúng: “lower-case with '-' replaced by '_'”. |
| logs-learn | `rule_sorted_errors` | E | Chưa sắp xếp đúng: “sorted by service, then by timestamp_utc”. |
| logs-learn | `rule_schema_header` | E | Thiếu hoặc sai `schema_version: 2`, `generated_by: log-triage`. |

Lỗi quy ước nhiều nhất: 9/14; lỗi xử lý dữ liệu là 5/14. Ở logs-learn, agent viết JSON thủ công, không thấy đọc README hay kiểm tra lại. Đây còn là dấu hiệu bỏ qua yêu cầu (A) và không kiểm chứng (B).

Code đạt 6/7 check kỹ thuật, data đạt 5/5, logs chỉ đạt 1/6. Code sửa hàm dùng chung và chạy pytest, chưa thấy kiểu vá triệu chứng (C). Logs nói đã xử lý UTC và số lần lặp nhưng kết quả vẫn sai.

Riêng `tests_not_modified` bị lệch hash do kiểu xuống dòng CRLF của file gốc trên Windows. Đổi sang LF khi tính hash thì khớp. Đây là lỗi môi trường; điểm trong bảng vẫn giữ nguyên.

## 5. Khi thêm subagent

Có ba vai trò: `explore` đọc file → `implementer` sửa code → `reviewer` kiểm tra. Explore và reviewer chỉ được nhắc không sửa file, chưa có cơ chế chặn.

| Tác vụ | Số lần gọi task | Vai trò thấy trong trace | Token | Giây |
|---|---:|---|---:|---:|
| code-eval | 0 | Không gọi subagent | 50,049 | 24.8 |
| code-learn | 1 | implementer | 97,838 | 40.0 |
| data-eval | 1 | general-purpose | 25,514 | 21.7 |
| data-learn | 1 | general-purpose | 40,573 | 14.8 |
| logs-eval | 1 | general-purpose | 35,377 | 21.5 |
| logs-learn | 1 | general-purpose | 25,416 | 41.4 |

Code-learn gọi implementer; data và logs gọi general-purpose. Data-learn lấy JSON của subagent rồi ghi luôn, không thấy agent chính kiểm tra lại, điểm là 0/8. Trace không có các bước bên trong subagent.

Logs-learn giao việc nhưng thiếu cấu trúc JSON và một số quy tắc. Subagent chỉ thấy lời giao nên có thể thiếu thông tin. Không thấy gọi reviewer.

## 6. Skill tạo từ các lỗi

Curator đọc lỗi baseline học → tạo 3 skill → chạy thử. Giữ nguyên nội dung skill; kết quả thử nằm ở `results/skills-auto-dev/`.

| Skill | Nhận xét | Độ dài | Khi nào dùng |
|---|---|---:|---|
| `enforce-code-quality-rules` | Nhắc giữ test, thêm kiểu dữ liệu, test lỗi đã sửa và changelog. Còn thiếu tên file test và cách viết changelog cụ thể; vài quy tắc chỉ hợp Acme. | 7 dòng | Kiểm tra quy ước khi sửa code. |
| `normalize-and-clean-data-for-analysis` | Có xử lý giờ, tiền và dữ liệu trùng. Còn gắn với giá trị -999 của bài học, thiếu meta; cách giữ bản ghi đầu tiên chưa hợp mọi dữ liệu. | 9 dòng | Làm sạch dữ liệu trước khi tính. |
| `parse-and-structure-logs-for-triage` | Có tách lỗi và sắp xếp log. Chỉ nhận ERROR/CRITICAL nên có thể bỏ sót mức lỗi khác; thiếu chi tiết về thông tin đầu file và số lần lặp. | 11 dòng | Đọc và xử lý log lỗi. |

Cả ba skill đều có mô tả khi nào dùng, nhưng agent không đọc nội dung trong các lượt thử (`skills_read=0`).

## 7. Kết quả so sánh

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 6/10 |
| data-learn | 5/8 | 0/8 | 3/8 |
| logs-learn | 1/9 | 0/9 | 1/9 |
| code-eval | 6/11 | 6/11 | 6/11 |
| data-eval | 3/9 | 1/9 | 5/9 |
| logs-eval | 1/10 | 1/10 | 1/10 |
| **Mean score - learning tasks** | 0.45 | 0.20 | 0.36 |
| **Mean score - evaluation tasks** | 0.33 | 0.25 | 0.40 |
| **Mean tokens per run** | 35,416 | 45,794 | 45,290 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

Thống kê từ `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     10/18         0/12          23,630      0/3
baseline      learn    12/18         0/9           47,203      0/3
subagents     eval      8/18         0/12          36,980      0/3
subagents     learn     6/18         0/9           54,609      0/3
skills-auto   eval     12/18         0/12          40,491      0/3
skills-auto   learn    10/18         0/9           50,090      0/3
```

18 lượt đều không lỗi API, không sửa skill. Giữ nguyên cả kết quả điểm thấp.

## 8. Nhận xét sau khi chạy

**1. Cách nào được điểm cao hơn?**

| Điều kiện | Điểm TB học | Điểm TB đánh giá | Chênh học so baseline | Chênh đánh giá so baseline |
|---|---:|---:|---:|---:|
| baseline | 0.4454 | 0.3263 | +0.0000 | +0.0000 |
| subagents | 0.2000 | 0.2522 | -0.2454 | -0.0741 |
| skills-auto | 0.3620 | 0.4003 | -0.0833 | +0.0741 |

H1 đúng ở lượt này: subagents tốn hơn nhưng điểm thấp hơn. H2 đúng về thứ hạng: skills-auto cao nhất trên bài đánh giá, nhưng chưa chắc nhờ skill. H3 không đúng: điểm học giảm, điểm đánh giá tăng. Chưa thấy kiểu chỉ tốt trên bài đã học; cần chạy thêm để kiểm tra.

**2. Agent còn bỏ sót gì?** Cả ba cách đều trượt toàn bộ check quy ước (`rule_`), kể cả ba quy ước mới:

| Quy ước mới | baseline | subagents | skills-auto |
|---|---|---|---|
| `rule_sorted_keys_format` | 0/1 | 0/1 | 0/1 |
| `rule_source_line` | 0/1 | 0/1 | 0/1 |
| `rule_version_bump` | 0/1 | 0/1 | 0/1 |

**3. Agent có đọc skill không?** Cả 6 lượt đều không đọc nội dung skill. Ở lượt thử code-learn, agent vào đọc code luôn, bỏ qua `SKILL.md`. Các check về kiểu dữ liệu, test lỗi đã sửa và changelog vẫn trượt.

Chưa đủ bằng chứng để nói skill giúp một check đạt. Model vẫn thấy mô tả skill, nhưng điểm khác nhau cũng có thể do từng lượt chạy.

**4. Cách nào ít tốn hơn?** Cột cuối là điểm trung bình chia token trung bình, nhân 1 triệu.

| Điều kiện | Token TB | Thời gian TB (giây) | Điểm TB trên 1 triệu token |
|---|---:|---:|---:|
| baseline | 35,416.7 | 21.3 | 10.894 |
| subagents | 45,794.5 | 27.4 | 4.937 |
| skills-auto | 45,290.8 | 29.3 | 8.416 |

Baseline ít tốn token nhất và có điểm trên mỗi token tốt nhất. Với bộ bài này, thêm subagent chưa đáng chi phí.

**5. Skill có dùng được cho bài khác không?** Giá trị -999 và cách chỉ lọc ERROR/CRITICAL còn bám vào bài học. Chưa biết ảnh hưởng thực tế vì agent không đọc skill. Curator chỉ dùng bài học; skill được kiểm tra và giữ cố định trước khi chạy bài đánh giá.

**6. Chạy lại cùng skill có giống kết quả không?**

| Tác vụ học | Trước đóng băng | Chính thức | Chênh điểm | Token thử / chính thức | Cùng hash |
|---|---:|---:|---:|---:|---|
| code-learn | 6/10 | 6/10 | +0.0000 | 66,370 / 73,210 | Có |
| data-learn | 5/8 | 3/8 | -0.2500 | 70,335 / 48,877 | Có |
| logs-learn | 1/9 | 1/9 | +0.0000 | 35,021 / 28,185 | Có |

Cùng bộ skill, data-learn giảm từ 5/8 xuống 3/8. Code và logs giữ điểm nhưng token thay đổi. Đặt nhiệt độ 0 vẫn có thể cho kết quả khác nhau.

## 9. Những chỗ còn hạn chế

1. Chỉ có 6 bài nên chưa biết kết quả với bài khác thế nào.
2. Mỗi cách chạy chính thức một lần; điểm có thể thay đổi khi chạy lại.
3. Agent chưa đọc skill nên chưa biết nội dung skill giúp được bao nhiêu.


## 10. Việc nên làm tiếp

Code đã chạy được qua OpenAI và đạt 29 test. Tiếp theo nên tìm vì sao agent bỏ qua `SKILL.md`, rồi chạy lại vài lần để xem điểm có ổn định không.

## Phụ lục: lệnh và tài liệu

Các lệnh Python chạy trong `/lab` của container `lab-deepagents`:

```bash
python -m pytest -v --tb=short
python scripts/tour.py
python -c "from lab.model import make_model; print(make_model().invoke('Reply with OK').content)"
python -m lab.runner --condition baseline --tasks learn
python -m lab.runner --condition subagents --tasks learn
python -m lab.curator
python -m lab.runner --condition skills-auto --tasks learn
# Sao lưu results/skills-auto thành results/skills-auto-dev trên host.
git add <các file code, skill, kết quả học và báo cáo>
git commit -m hypotheses
git commit --allow-empty -m 'freeze skills'
git tag freeze
python -m lab.runner --condition baseline --tasks eval
python -m lab.runner --condition subagents --tasks eval
python -m lab.runner --condition skills-auto --tasks all
python scripts/verify_freeze.py
python -m lab.compare > report/table.md
python scripts/check_breakdown.py
```

Tạo commit và tag trên Windows, chạy kiểm tra trong Docker. `.env` không đưa vào Git. Ban đầu thiếu tên model; bổ sung cấu hình OpenAI thì API trả `OK`. Chưa làm phần mở rộng.

Kiểm tra freeze đã `OK`. Git trong Docker cần `safe.directory=/lab` và `core.autocrlf=true` để xử lý xuống dòng giống Windows.

- [SkillsBench](https://arxiv.org/abs/2602.12670): tham khảo cách so sánh có và không có skill.
- [SkillEvolBench](https://arxiv.org/abs/2605.24117): tham khảo việc áp dụng skill từ bài học sang bài mới.
- [OpenAI gpt-4.1-mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini): model đã dùng.
