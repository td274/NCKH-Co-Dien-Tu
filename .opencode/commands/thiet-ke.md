---
description: Thiết kế cơ khí, dung sai, BOM và bản vẽ từ kết quả mô phỏng
agent: co-khi
subagent: true
---

Thiết kế cơ khí cho: $ARGUMENTS

Đọc `nghien-cuu/mo-hinh/dong-hoc-delta.md`, `nghien-cuu/mo-hinh/ket-qua/` (bảng độ nhạy
sai số hình học), và `nghien-cuu/mo-phong/runs/*/output/metrics.json` (mô-men, vận tốc
cực đại thực tế trong mô phỏng).

Tạo trong `nghien-cuu/thiet-ke/`:
1. `thong-so-co-khi.md` — kích thước chốt, vật liệu, khớp, ổ bi, phương án gia công,
   **bảng dung sai từng chi tiết kèm lý do dẫn về kết quả độ nhạy**.
2. `BOM.md` — bảng linh kiện, thông số yêu cầu, số lượng, giá tham khảo VN, tổng kinh phí.
3. `ban-ve-so-do.svg` — sơ đồ có kích thước (đế, tay quay, cẳng, bàn di động, vùng làm việc).
4. `README.md` — trình tự lắp, điểm căn chỉnh, quy trình hiệu chuẩn sau lắp.

Bắt buộc:
- Chọn động cơ theo τ_max = 0,457 N·m và ω_max = 4,66 rad/s **kèm hệ số an toàn ≥ 2**;
  ghi rõ đã dùng hệ số nào.
- Dung sai khâu ≤ 0,2 mm (kết quả độ nhạy); nhấn mạnh khớp đế cần CNC liền khối vì
  khuếch đại sai số tới 3,4 mm/mm.
- Không bịa datasheet; thông số chưa có nguồn thì đánh dấu `[CẦN KIỂM CHỨNG]`.
