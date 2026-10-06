# Kiểm tra kết quả từ PowerShell

Chạy trong thư mục gốc project. Docker Desktop cần đang chạy.

```powershell
docker build -t lab-deepagents .
docker run --rm -v "${PWD}:/lab" lab-deepagents python -m pytest -v
```

Kết quả mong đợi: `29 passed`.

Kiểm tra bộ skill đã đóng băng, dùng cùng cấu hình xuống dòng Git với host Windows:

```powershell
docker run --rm -e GIT_CONFIG_COUNT=2 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0=/lab -e GIT_CONFIG_KEY_1=core.autocrlf -e GIT_CONFIG_VALUE_1=true -v "${PWD}:/lab" lab-deepagents python scripts/verify_freeze.py
```

Kết quả mong đợi: `checked 6 runs of skill conditions: OK`.

Xem bảng và thống kê từ các run đã lưu; các lệnh này không gọi API:

```powershell
docker run --rm -v "${PWD}:/lab" lab-deepagents python -m lab.compare
docker run --rm -e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0=/lab -v "${PWD}:/lab" lab-deepagents python scripts/check_breakdown.py
```

API đã cấu hình trong `.env`: `AZURE_OPENAI_ENDPOINT=https://api.openai.com/v1`, `AZURE_OPENAI_DEPLOYMENT_MODEL=gpt-4.1-mini`, `AZURE_OPENAI_KEY` giữ key OpenAI hiện có, `LAB_TEMPERATURE=0`. Tên biến Azure chỉ là tên cấu hình của lab; request gửi đến OpenAI trực tiếp. Không commit `.env`.

Nếu muốn chạy lại để đo nhiễu, ghi vào thư mục riêng để giữ kết quả chính thức:

```powershell
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents python -m lab.runner --condition baseline --tasks all --results results-repeat
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents python -m lab.runner --condition subagents --tasks all --results results-repeat
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents python -m lab.runner --condition skills-auto --tasks all --results results-repeat
```

Các lệnh chạy lại có sử dụng token API. Giữ nguyên bộ skill và không chạy curator sau freeze nếu đang tái lập thí nghiệm chính thức. Báo cáo hiện tại chỉ sử dụng `results/`; `results/skills-auto-dev/` là bản thử trước đóng băng để so sánh nhiễu.
