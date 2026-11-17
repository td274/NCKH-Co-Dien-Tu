# Thư mục nghiên cứu

Toàn bộ sản phẩm NCKH nằm ở đây. Mỗi thư mục con thuộc về một subagent — không ghi
chéo sang thư mục của agent khác.

| Thư mục | Chứa gì | Agent |
| --- | --- | --- |
| `de-tai.md` | Đề cương đang dùng | `nckh` |
| `tai-lieu/` | `notes/` (mỗi paper một file), `bang-so-sanh.md`, `references.bib` | `literature` |
| `mo-hinh/` | Dẫn giải toán + script kiểm tra (sympy/numpy) | `modeling` |
| `mo-phong/` | `src/` dùng chung + `runs/<ngày>-<slug>/` cho từng lần chạy | `simulation` |
| `firmware/` | Một project PlatformIO cho mỗi board | `firmware` |
| `du-lieu/` | CSV đo thực nghiệm, file calibration | `simulation` |
| `bao-cao/` | Báo cáo Markdown/LaTeX, slide, hình xuất bản | `writer` |
| `nhat-ky/` | `YYYY-MM-DD.md` — nhật ký từng phiên | `nckh` |

## Cấu trúc một lần chạy mô phỏng

```
mo-phong/runs/2026-11-17-pid-kenh-1/
├── config.json     # tham số + seed + phiên bản
├── run.py          # python run.py là chạy lại được
├── output/         # CSV thô, không chỉnh tay
├── figures/        # PNG/PDF 300 dpi
└── KETQUA.md       # mục tiêu, số liệu, nhận xét, bất thường
```

## Nguyên tắc

1. Không sửa kết quả cũ; làm lại thì tạo run mới.
2. Mọi số trong báo cáo phải truy được về một file trong `output/` hoặc `du-lieu/`.
3. Thiếu dữ liệu thì ghi `[CẦN BỔ SUNG]`, không suy diễn.
