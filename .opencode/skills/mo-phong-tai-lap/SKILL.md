---
name: Mô phỏng tái lập
description: Checklist để mọi kết quả mô phỏng cơ điện tử chạy lại được và số liệu trong báo cáo truy nguyên được
---

# Mô phỏng tái lập được

## Checklist trước khi báo "đã có kết quả"

- [ ] Chạy được bằng một lệnh duy nhất: `python run.py` (hoặc `pio run`).
- [ ] `config.json` chứa toàn bộ tham số: vật lý, bộ điều khiển, thời gian mô phỏng, bước
      tích phân, seed ngẫu nhiên.
- [ ] Phiên bản môi trường được ghi: Python/Octave/MATLAB + thư viện chính.
- [ ] Không phụ thuộc đường dẫn tuyệt đối hay file nằm ngoài repo.
- [ ] Dữ liệu thô trong `output/` không bị chỉnh tay.
- [ ] Hình trong `figures/` sinh ra từ script, không qua PowerPoint.
- [ ] `KETQUA.md` nêu: mục tiêu thí nghiệm, thông số, kết quả định lượng, nhận xét,
      điều bất thường.

## Bẫy thường gặp trong mô phỏng cơ điện tử

| Bẫy | Cách tránh |
| --- | --- |
| Bước tích phân quá lớn làm hệ "ổn định giả" | Giảm bước 10×, kiểm tra kết quả không đổi |
| Bão hoà PWM/điện áp bị bỏ qua | Thêm `clip(u, -u_max, u_max)` và mô phỏng lại |
| Trễ cảm biến/truyền thông bỏ qua | Thêm khối trễ, so sánh |
| Nhiễu encoder không mô phỏng | Thêm nhiễu lượng tử hoá theo CPR thực |
| Chỉ chạy 1 điều kiện | Chạy lưới tham số, báo cáo miền hoạt động |
| So sánh với "đáp ứng lý tưởng" tự định nghĩa | So sánh với chỉ tiêu trong đề cương hoặc số liệu công bố |

## Khi kết quả khác kỳ vọng

1. Kiểm tra đơn vị trước (rad vs độ, N vs kgf, rad/s vs vòng/phút).
2. Kiểm tra dấu và chiều trong mô hình (động học nghịch, ma trận Jacobian).
3. Chạy lại với bước nhỏ hơn và seed khác.
4. Nếu vẫn lệch: ghi vào `KETQUA.md` là phát hiện, không giấu. Sai lệch có giải thích
   là nội dung khoa học; sai lệch bị che đi là lỗi.
