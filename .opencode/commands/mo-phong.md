---
description: Viết và chạy một kịch bản mô phỏng
agent: simulation
subagent: true
---

Chạy mô phỏng cho kịch bản: $ARGUMENTS

Đọc mô hình trong `nghien-cuu/mo-hinh/` và đề cương. Tạo lần chạy mới theo cấu trúc
`nghien-cuu/mo-phong/runs/<ngày>-<slug>/` với `config.json`, `run.py`, `output/`,
`figures/`, `KETQUA.md`.

Bắt buộc:
- Seed cố định, ghi phiên bản thư viện.
- Hình 300 dpi, có đơn vị trục và legend.
- Nhận xét định lượng so với chỉ tiêu trong đề cương (không viết "khá tốt").
- Nêu rõ chỗ lệch kỳ vọng và 2–3 hướng chỉnh nếu không đạt.

Trả về tóm tắt ≤ 200 từ kèm đường dẫn `KETQUA.md`.
