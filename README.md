# Robot Delta 3 bậc tự do phân loại sản phẩm bằng thị giác máy tính

Thiết kế, mô phỏng và kiểm chứng hệ robot Delta ba bậc tự do tịnh tiến, dùng webcam
và Arduino Uno để nhận dạng màu – hình rồi gắp–thả sản phẩm tự động.

**Đơn vị thực hiện:** Khoa Cơ điện tử — Trường Đại học Điện lực · **Năm:** 2026
**Sinh viên thực hiện:** *[CẦN BỔ SUNG]* · **Giảng viên hướng dẫn:** *[CẦN BỔ SUNG]*

> **Trạng thái:** đang thực hiện. Nguyên mẫu **chưa có khung cơ khí hoàn chỉnh**; toàn bộ
> kết quả dưới đây là kết quả **mô phỏng** trên dữ liệu tổng hợp, chưa đo trên robot thật.

---

## Nội dung nghiên cứu

1. **Động học** — động học nghịch (IK) giải bằng biểu thức giải tích, động học thuận (FK)
   bằng phương pháp Newton–Raphson, kiểm chứng chéo vòng kín IK↔FK trên lưới điểm trong
   vùng làm việc.
2. **Quỹ đạo và điều khiển** — quỹ đạo gắp–thả đa thức bậc 5 có pha dừng, bộ điều khiển
   PID và PID cộng bù tiến (feedforward), đánh giá bằng mô phỏng vòng kín.
3. **Thị giác máy tính** — nhận dạng màu và hình bằng ngưỡng HSV kết hợp contour trong
   OpenCV, phân loại trên ảnh tổng hợp có kiểm soát nhiễu.
4. **Thiết kế cơ khí** — thông số hình học, dung sai chế tạo dẫn từ khảo sát độ nhạy
   Monte Carlo, BOM và bản vẽ sơ đồ.

## Thông số thiết kế chính

| Thông số | Ký hiệu | Giá trị | Đơn vị |
| --- | --- | --- | --- |
| Cạnh tam giác đế | `f` | 346,0 | mm |
| Bán kính ngoại tiếp đế | `Rb` | 199,76 | mm |
| Cạnh bàn di động | `e` | 115,0 | mm |
| Tay quay chủ động | `rf` | 200,0 | mm |
| Cánh tay (cẳng) | `re` | 400,0 | mm |
| Vùng làm việc | — | Ø300,0 × 150,0 | mm |
| Khoảng `z` làm việc | — | −425,0 … −275,0 | mm |
| Chiều cao mặt khớp đế | `H_base` | 550,0 | mm |
| Chu kỳ vận hành chọn | `T` | 0,32 | s |
| Mô-men đỉnh tại `T` | `τ` | 1,14 | N·m |
| Tốc độ góc đỉnh tại `T` | `ω` | 7,25 (~69,2 vòng/phút) | rad/s |
| Truyền động | — | stepper vòng kín + đai GT2 tỉ số 5:1 | — |

## Kết quả chính (mô phỏng)

| Nội dung | Kết quả |
| --- | --- |
| Sai số vòng kín IK↔FK, cực đại trên 1.859 điểm lưới | 1,583 × 10⁻¹³ mm |
| Sai số điểm cuối, dung sai ±0,2 mm (P95 / cực đại) | 0,402 mm / 0,689 mm |
| Ngân sách sai số sau hiệu chuẩn (P95 / cận trên giải tích) | 0,612 mm / 1,048 mm |
| Sai số bám, `T` = 0,50 s — PID thuần / PID + bù tiến | 1,137 mm / 0,186 mm |
| Chu kỳ danh định tại `T` = 0,32 s (ngân sách 1,8 s) | 1,506 s |
| Độ chính xác phân loại (75 vật tổng hợp, seed 999) | 97,33 % (KTC Wilson 95 %: 90,8 – 99,3 %) |

**Đọc kèm điều kiện:** chỉ tiêu sai số 1 mm **đạt theo thống kê** (P95 = 0,612 mm) nhưng
**không đạt theo worst-case** (1,048 mm). Trễ truyền thông Serial và trễ cơ cấu chấp hành
**chưa được đo**. Mục tiêu kiểm chứng trên vật thật **chưa đạt** — mọi số phân loại đo trên
ảnh tổng hợp.

## Cấu trúc kho lưu trữ

```
nghien-cuu/
├── de-tai.md              Đề cương: vấn đề, mục tiêu, phương pháp, kế hoạch
├── tai-lieu/              Ghi chú paper, references.bib, bảng so sánh
├── mo-hinh/               Dẫn giải toán, script kiểm tra (sympy/numpy)
├── mo-phong/
│   └── runs/<ngày>-<slug>/   Mỗi lần chạy: config.json, run.py, output/, figures/, KETQUA.md
├── firmware/
│   └── uno-serial-servo/  Firmware Arduino Uno + đo trễ Serial
├── thiet-ke/              Thông số cơ khí, BOM, bản vẽ sơ đồ (SVG/PNG)
├── du-lieu/               Dữ liệu đo, calibration, ảnh mẫu
├── bao-cao/               Báo cáo đầy đủ + từng chương, biên bản phản biện
├── nhat-ky/               Nhật ký theo ngày YYYY-MM-DD.md
└── cong-cu/               Script tiện ích
```

Báo cáo hoàn chỉnh: [`nghien-cuu/bao-cao/00-bao-cao-day-du.md`](nghien-cuu/bao-cao/00-bao-cao-day-du.md)

## Môi trường và cách chạy lại

**Yêu cầu**

| Thành phần | Phiên bản / ghi chú |
| --- | --- |
| Python | 3.12 — `numpy`, `scipy`, `sympy`, `matplotlib`, `opencv-python`, `pandas`, `pyserial` |
| MATLAB | tuỳ chọn, dùng để đối chiếu một số kết quả |
| Arduino IDE | nạp firmware cho Arduino Uno |

**Chạy một lần mô phỏng**

```bash
cd nghien-cuu/mo-phong/runs/<ngày>-<slug>
python run.py          # đọc config.json (tham số + seed + phiên bản thư viện)
```

Mỗi thư mục `runs/` là một lần chạy độc lập và tái lập được: `config.json` ghi tham số,
seed và phiên bản thư viện; `output/` chứa dữ liệu thô **không chỉnh tay**; `figures/`
chứa hình xuất bản sinh lại được từ script; `KETQUA.md` ghi mục tiêu, số liệu và nhận xét.

## Nguyên tắc làm việc

1. **Không sửa kết quả cũ** — muốn làm lại thì tạo lần chạy mới.
2. **Mọi số trong báo cáo phải truy được** về một file trong `output/` hoặc `du-lieu/`.
3. **Không bịa tài liệu** — mọi trích dẫn phải có DOI hoặc URL kiểm chứng được.
4. **Đơn vị SI** trong công thức và bảng; ghi rõ đơn vị ở tiêu đề cột.
5. Thiếu dữ liệu thì ghi `[CẦN BỔ SUNG]`, không suy diễn.

> Kết quả trong kho lưu trữ này là **bản nháp có hỗ trợ của AI**. Sinh viên chịu trách nhiệm
> tự kiểm chứng công thức, số liệu và kết luận trước khi đưa vào báo cáo nộp.
