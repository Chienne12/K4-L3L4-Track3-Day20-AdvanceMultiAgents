# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Phùng Trọng Chiến | 2A202602430 | Hoàn thiện harness và thực hiện thí nghiệm với hỗ trợ của Codex; kiểm tra và diễn giải kết quả. |

- OpenAI `gpt-4.1-mini`; base URL `https://api.openai.com/v1`; giữ các tên biến `AZURE_OPENAI_*` để cấu hình ChatOpenAI theo code có sẵn. Không dùng Azure service.
- `LAB_TEMPERATURE=0`, `recursion_limit=60`; Deep Agents 0.7.21; Python 3.12.15; Linux Docker trên máy Windows.
- 21 lần chạy tác vụ: 18 chính thức (6 tác vụ × 3 điều kiện) và 3 thử skill trước đóng băng. Curator gọi 1 lần, thử kết nối API thành công 1 lần. Chưa có giới hạn ngân sách tiền do người dùng chỉ định; token được ghi ở từng run.
- Tổng token các lần chạy tác vụ: 930,738. Không gồm token curator và câu thử kết nối vì các lệnh này không lưu usage.
- Kết quả kiểm tra code: 29/29 test đạt trong Docker; 27/29 trên Windows, hai test shell thiếu lệnh Linux `which` và `cat`.
- Commit giả thuyết: `1a8c6f9`; commit của tag `freeze`: `d49af2b115e4092b1bac3e5ae3552c7a6e44146c`. Giả thuyết được ghi trước khi chạy bất kỳ tác vụ đánh giá nào.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)


- H1 (subagents so với baseline): Dự đoán subagents không vượt baseline về điểm trung bình đánh giá và tốn nhiều token hơn. Trên tác vụ học, subagents đạt code 6/10, data 0/8, logs 0/9; baseline đạt 6/10, 5/8, 1/9. Trace data cho thấy agent chính dùng báo cáo general-purpose rồi ghi kết quả mà không kiểm chứng bằng shell. Thêm vai trò không bảo đảm quy trình được thực hiện tốt hơn.
- H2 (skills-auto so với baseline): Dự đoán skills-auto có điểm trung bình đánh giá cao nhất trong ba điều kiện nhờ hướng dẫn kiểm tra code, chuẩn hóa dữ liệu và xử lý log; tuy nhiên không dự đoán đạt toàn bộ check. Skill code nhắc type hints/changelog, skill logs nhắc chuẩn hóa service và sắp xếp; skill data chưa chỉ rõ meta, skill logs chưa chỉ rõ giá trị schema header. Đây là giả thuyết cho bộ skill của lab, không suy rộng từ kết quả skill do con người viết trong [SkillsBench](https://arxiv.org/abs/2602.12670).
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán mức tăng điểm của skills-auto so với baseline lớn hơn trên tác vụ học so với tác vụ đánh giá, vì skill được rút từ phản hồi học và chưa biết quy ước mới của đánh giá. [SkillEvolBench](https://arxiv.org/abs/2605.24117) ghi nhận cải thiện tại chỗ không bảo đảm chuyển thành skill bền vững trên frozen deployment; đây là căn cứ để kiểm tra khả năng tổng quát hóa thay vì giả định skill luôn giúp.

## 3. Làm quen Deep Agents

1. Công cụ mặc định: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. `execute` chạy lệnh shell trong sandbox, trả stdout/stderr và exit code; ở đây shell chạy trong Linux Docker.
2. `task` tạo subagent tạm thời. `general-purpose` có các công cụ như agent chính; mặc định chỉ nhận prompt giao việc, không nhận toàn bộ lịch sử hội thoại; trả một báo cáo cuối để agent chính tổng hợp.
3. `scripts/tour.py` in system prompt mặc định là `''`; mô tả công cụ vẫn chứa hướng dẫn hành vi:

   - `task`: “Launch multiple agents concurrently when their tasks are independent, using a single message with multiple tool calls.”
   - `execute`: “Use read_file rather than cat/head/tail.”

## 4. Đường cơ sở và phân loại lỗi

Phạm vi: chỉ ba tác vụ học của `baseline`. Bằng chứng lấy từ `results/baseline/<task>/run.json` và `trace.md`.

| Tác vụ | Check thất bại | Nhóm | Bằng chứng từ detail |
|---|---|---|---|
| code-learn | `rule_type_hints` | E | RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value. |
| code-learn | `rule_regression_tests` | E | RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass. |
| code-learn | `rule_changelog` | E | RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets). |
| data-learn | `rule_money_in_cents` | E | RULE: money values in answer.json are integer cents (1606.67 USD is written 160667). |
| data-learn | `rule_meta_block` | E | RULE: answer.json has an object `meta` = {"source": <input file name>, "rows_in": <number of data rows in the input file, duplicates included>, "rows_used": <number of distinct orders with a known amount>}. |
| data-learn | `rule_clean_csv` | E | RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order with a known amount; timestamp_utc as YYYY-MM-DDTHH:MM:SSZ (UTC); region in canonical spelling (North, South, East, West); amount in integer cents. |
| logs-learn | `entry_count` | D | wrong number of entries (got 20) |
| logs-learn | `timestamps_utc` | D | 8/25 timestamps match |
| logs-learn | `exception_fields` | D | 17 wrong `exception` values |
| logs-learn | `repeat_counts` | D | 17 wrong `repeat_count` values |
| logs-learn | `counts_by_service` | D | counts_by_service: wrong values |
| logs-learn | `rule_service_names` | E | RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service). |
| logs-learn | `rule_sorted_errors` | E | RULE: `errors` is sorted by service, then by timestamp_utc, ascending. |
| logs-learn | `rule_schema_header` | E | RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage". |

Nhóm E chiếm 9/14 check thất bại của agent; nhóm D chiếm 5/14. Trong logs-learn, agent đọc log rồi viết JSON thủ công, không đọc README trong trace và không gọi execute để kiểm tra: đây còn là dấu hiệu của A (bỏ qua đặc tả) và B (không kiểm chứng), góp phần vào lỗi D. Đếm một nhóm chính cho mỗi check để tránh đếm trùng.

Code đạt 6/7 check kỹ thuật theo checker, data đạt 5/5, logs đạt 1/6. Bằng chứng này không hỗ trợ kết luận mọi tác vụ đều mắc lỗi kỹ thuật. Code baseline thực sự chạy pytest và sửa hàm dùng chung; chưa thấy bằng chứng đủ để quy lỗi nhóm C. Lời cuối logs nói đã chuyển UTC và cộng repeat_count, nhưng các check tương ứng không đạt; đây là sai lệch giữa tự báo cáo và kiểm chứng.

**Sai lệch môi trường, không xếp vào lỗi agent:** `tests_not_modified` của code-learn thất bại ngay từ file gốc. SHA256 bytes CRLF là `efb5e7650d4f03356e8353d209fbcfe81505ce2fd648bd558d5ada6e8b92ff19`; thay CRLF bằng LF cho hash `79e05f4cc2e62a4f606d210b0b08a2cc21777245bc2f6ad244a126e9a2aee00d`, đúng hash checker. Không sửa file tasks hay checker để đổi điểm. Bảng vẫn giữ điểm thô của grader; hạn chế này được tách khỏi phân loại lỗi.

## 5. Điều kiện subagents

Ba vai trò: `explore` đọc và báo cáo, `implementer` thực hiện thay đổi và chạy kiểm tra, `reviewer` kiểm tra độc lập. Phạm vi read-only của explore/reviewer được hướng dẫn bằng prompt, không phải khóa quyền ở backend.

| Tác vụ | Số lần gọi task | Vai trò thấy trong trace | Token | Giây |
|---|---:|---|---:|---:|
| code-eval | 0 | Không có tên trong phần trace được lưu | 50,049 | 24.8 |
| code-learn | 1 | implementer | 97,838 | 40.0 |
| data-eval | 1 | general-purpose | 25,514 | 21.7 |
| data-learn | 1 | general-purpose | 40,573 | 14.8 |
| logs-eval | 1 | general-purpose | 35,377 | 21.5 |
| logs-learn | 1 | general-purpose | 25,416 | 41.4 |

Ở code-learn, task chọn implementer và gửi các lỗi đã xác định, đường dẫn, yêu cầu giữ test, và yêu cầu theo quy ước Acme. Ở data-learn và logs-learn, task chọn general-purpose thay vì vai trò tự định nghĩa. Trong data-learn, agent chính ghi trực tiếp JSON từ báo cáo subagent mà không chạy kiểm chứng trong luồng chính; các check kỹ thuật đều thất bại. Phần việc bên trong subagent không nằm trong trace nên không kết luận subagent chưa dùng shell chỉ từ vết này.

Lời giao logs-learn chỉ nhắc “rules given by the user” thay vì sao chép đầy đủ định dạng JSON và mọi quy tắc, trong khi subagent mặc định không nhận hội thoại. Việc giao thiếu chi tiết là một rủi ro có bằng chứng trong prompt; chưa đủ dữ liệu để xác định đó là nguyên nhân duy nhất của điểm 0/9. Không có bằng chứng reviewer được dùng chỉ vì nó đã được khai báo.

## 6. Self-evolving: skill tự sinh

Curator gọi 1 lần từ các run baseline học, giữ 3 skill hợp lệ; không xóa skill, không chạy lại curator, không sửa tay nội dung. Kết quả thử lưu ở `results/skills-auto-dev/` trước chạy chính thức.

| Skill | Tổng quát và chất lượng | Độ dài thân | Description |
|---|---|---:|---|
| `enforce-code-quality-rules` | Checklist hữu ích cho bảo toàn test, type hints, regression test và changelog. Có gắn quy ước Acme (Unreleased/type hints), không bảo đảm phù hợp mọi dự án; chưa chỉ rõ tên test và định dạng bullet mà bot học yêu cầu. | 7 dòng | Use this skill to ensure code changes comply with project-specific quality rules before submission. |
| `normalize-and-clean-data-for-analysis` | Nêu chuẩn hóa, UTC, tiền cents, dedup và kiểm tra schema. Sentinel -999 là chi tiết gắn tác vụ học; giữ bản ghi đầu tiên không đúng cho mọi dữ liệu có bản cập nhật. Thiếu hướng dẫn cụ thể cho meta/rows_in/rows_used. | 9 dòng | Use this skill to preprocess raw data files for analysis by normalizing fields, parsing dates, removing duplicates, and handling missing values. |
| `parse-and-structure-logs-for-triage` | Trình tự parse log và traceback phù hợp tác vụ học; nhắc chuẩn hóa service, UTC và sort. Chỉ lọc ERROR/CRITICAL có thể không phù hợp log dùng mức lỗi khác; metadata chưa ghi giá trị bắt buộc. Tổng theo service chưa nói rõ phải dùng repeat_count. | 11 dòng | Use this skill to extract, normalize, and structure log entries for error triage and reporting according to strict formatting rules. |

Các description nêu tình huống kích hoạt, nhưng trong lần thử trước đóng băng cả ba tác vụ đều có skills_read=0. Không xem định dạng hợp lệ là bằng chứng nội dung đúng hoặc đã được agent sử dụng.

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

Lỗi chạy: không có error trong 18 run chính thức. Skill bị thay đổi trong sandbox: không có; tất cả skills_modified=false. Điểm thấp vẫn là kết quả hợp lệ của thí nghiệm, không chạy lại chỉ để chọn điểm cao.

## 8. Phân tích

**1. Hiệu quả theo vai trò.**

| Điều kiện | Điểm TB học | Điểm TB đánh giá | Chênh học so baseline | Chênh đánh giá so baseline |
|---|---:|---:|---:|---:|
| baseline | 0.4454 | 0.3263 | +0.0000 | +0.0000 |
| subagents | 0.2000 | 0.2522 | -0.2454 | -0.0741 |
| skills-auto | 0.3620 | 0.4003 | -0.0833 | +0.0741 |

H1 phù hợp kết quả: subagents có điểm đánh giá 0.2522, thấp hơn baseline 0.3263, và tốn nhiều token hơn. H2 phù hợp thứ hạng điểm thô: skills-auto đứng đầu đánh giá với 0.4003; chưa thể quy chênh lệch này cho nội dung skill vì không có run nào đọc skill. H3 không phù hợp kết quả: skills-auto giảm 0.0833 điểm trên học nhưng tăng 0.0741 trên đánh giá so baseline. Một lần chạy mỗi cấu hình chưa đủ xác định khác biệt có ý nghĩa thống kê; thí nghiệm này không cho thấy mẫu cải thiện học nhưng suy giảm đánh giá để kết luận quá khớp từ điểm số.

**2. Check kỹ thuật và quy ước mới.** Bảng breakdown tách `rule_` khỏi kỹ thuật. Tìm các tên rule xuất hiện ở eval nhưng không xuất hiện ở learn, rồi đếm trực tiếp từ run.json:

| Quy ước mới | baseline | subagents | skills-auto |
|---|---|---|---|
| `rule_sorted_keys_format` | 0/1 | 0/1 | 0/1 |
| `rule_source_line` | 0/1 | 0/1 | 0/1 |
| `rule_version_bump` | 0/1 | 0/1 | 0/1 |

**3. Cơ chế dùng skill.** Trong 6 run skills-auto chính thức, 0 run có đọc nội dung skill theo định nghĩa read_file trong luồng chính. Trên lần thử code-learn, trace bắt đầu bằng ls workspace/inventory và đọc source; không có read_file skills/.../SKILL.md. `rule_type_hints`, `rule_regression_tests`, `rule_changelog` vẫn thất bại dù skill code nhắc các hành vi này. Đây là ví dụ skill chưa được đọc, không phải bằng chứng skill đã được thực hiện mà sai.

Không có căn cứ để chọn một check và khẳng định skill trực tiếp giúp đạt khi không quan sát được đọc skill. Frontmatter được nạp vào prompt vẫn có thể ảnh hưởng model; chênh điểm hoặc token cũng có thể do nhiễu. Phân biệt “đã nạp danh sách skill” với “đã đọc và làm theo nội dung skill”.

**4. Chi phí.** Dùng điểm trung bình tất cả 6 tác vụ chia token trung bình, nhân 1 triệu để dễ đọc; đây là chỉ số điểm/token, không phải giá tiền API.

| Điều kiện | Token TB | Thời gian TB (giây) | Điểm TB trên 1 triệu token |
|---|---:|---:|---:|
| baseline | 35,416.7 | 21.3 | 10.894 |
| subagents | 45,794.5 | 27.4 | 4.937 |
| skills-auto | 45,290.8 | 29.3 | 8.416 |

Theo chỉ số này, `baseline` hiệu quả nhất trong số run đã đo. Đa tác tử chưa cho thấy lợi ích đủ bù chi phí: điểm học thấp hơn baseline và điểm đánh giá cũng thấp hơn; không suy rộng kết luận này cho mọi mô hình/tác vụ.

**5. Rò rỉ và quá khớp.** Curator lọc role=learn trước đọc trace; validator chặn eval markers; giả thuyết commit trước freeze; kết quả eval chỉ chạy sau freeze; skill giữ nguyên. Skill data còn sentinel -999, skill logs chỉ nhận ERROR/CRITICAL: có dấu hiệu gắn quy trình với dữ liệu học. Tuy nhiên agent không đọc nội dung skill trong các run đã quan sát nên chưa thể đo tác động nhân quả của các chi tiết này lên chuyển giao.

**6. Nhiễu với cùng bộ skill.** So sánh bản thử và bản chính thức; hash skill phải giống nhau:

| Tác vụ học | Trước đóng băng | Chính thức | Chênh điểm | Token thử / chính thức | Cùng hash |
|---|---:|---:|---:|---:|---|
| code-learn | 6/10 | 6/10 | +0.0000 | 66,370 / 73,210 | Có |
| data-learn | 5/8 | 3/8 | -0.2500 | 70,335 / 48,877 | Có |
| logs-learn | 1/9 | 1/9 | +0.0000 | 35,021 / 28,185 | Có |

Chênh lệch cùng bộ skill chỉ là ước lượng biến thiên từ hai run trên mỗi tác vụ học; không thay thế việc lặp lại nhiều lần trên đánh giá. Temperature=0 không bảo đảm chuỗi gọi công cụ hay kết quả tuyệt đối giống nhau.

## 9. Hạn chế và tính hợp lệ

1. Chỉ 3 tác vụ cho mỗi vai trò, cùng bộ quy ước do lab thiết kế: kết quả có thể phụ thuộc mạnh vào cấu trúc bài, không đại diện công việc ngoài thực tế.
2. Mỗi cấu hình chính thức chạy 1 lần; so sánh nhiễu chỉ có 2 run học skills-auto: chưa có khoảng tin cậy hoặc kiểm định ý nghĩa.
3. Chỉ dùng một model gpt-4.1-mini và nhiệt độ 0: kết quả không nói được các model khác sẽ chọn subagent/đọc skill như thế nào.
4. Skill được nạp nhưng chưa quan sát đọc nội dung; không tách được ảnh hưởng frontmatter, nội dung skill và nhiễu. Cần đo invocation trước khi kết luận chất lượng skill.
5. File gốc Windows có CRLF gây lệch hash checker bảo toàn test; giữ điểm thô và ghi nhận sai lệch môi trường, không coi đó là hành vi sửa test của agent.
6. Trace chỉ có luồng chính, mỗi khối rút còn tối đa 1500 ký tự; sandbox bị xóa sau chạy. Không có toàn bộ log bên trong subagent hay bản output gốc để kiểm tra thủ công lại mọi bước.

## 10. Kết luận

Harness hoàn thiện và đạt 29 test ngoại tuyến; API OpenAI chạy thành công với cấu hình tên biến có sẵn. Thí nghiệm có đủ 18 run chính thức và 3 run thử skill được lưu riêng. Đa tác tử không cải thiện điểm trong những run này; có skill chưa đủ bảo đảm model đọc và làm theo. Chênh điểm phải được diễn giải cùng token, trace và sai lệch môi trường, không coi là bằng chứng nhân quả từ một lần chạy. Bước tiếp theo nên kiểm tra cơ chế đọc skill và lặp nhiều run trước khi mở rộng số tác vụ.

## Phụ lục: lệnh và tài liệu

Các lệnh Python bên dưới chạy từ thư mục /lab trong container, dùng cùng image lab-deepagents:

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

Commit/tag được tạo bằng Git trên host Windows; kiểm tra freeze chạy Linux để băm đường dẫn cùng hệ điều hành với runner. Các file .env không được commit. Lần gọi thử đầu tiên trước cấu hình model dừng ở validation DeepSeek, chưa gọi API; sau đó đặt base URL và model OpenAI và nhận OK. Không thực hiện thử thách mở rộng.

Kiểm tra cuối: `verify_freeze.py` báo `checked 6 runs of skill conditions: OK`. Khi gọi Git trong container đặt `safe.directory=/lab` và `core.autocrlf=true` giống host Windows; nếu thiếu cấu hình thứ hai, README có CRLF sẽ bị báo khác dù nội dung skill không đổi. Lần kiểm tra đầu đã gặp khác biệt này, sau đó chỉ đồng bộ cấu hình Git, không sửa file skill. Xem [REPRODUCE.md](REPRODUCE.md) để chạy các lệnh kiểm tra từ PowerShell.

- [SkillsBench](https://arxiv.org/abs/2602.12670): căn cứ cho đánh giá cặp có/không skill và tránh suy rộng lợi ích của skill curated sang skill tự sinh.
- [SkillEvolBench](https://arxiv.org/abs/2605.24117): căn cứ cho giả thuyết chuyển giao không ổn định từ học sang frozen deployment.
- [OpenAI gpt-4.1-mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini): model sử dụng cho thí nghiệm.
