# Phản biện hồ sơ NCKH — đợt kiểm tra trước khi viết chương kết quả

**Ngày:** 2026-11-24 · **Phạm vi:** toàn bộ hồ sơ hiện có trong `nghien-cuu/` (đề cương, tài liệu, mô hình động học + kết quả kiểm chứng, 2 run mô phỏng, thiết kế cơ khí, chương 1–2 báo cáo, firmware).
**Trọng tâm:** tính nhất quán số liệu và tính đứng vững của kết luận — không xét văn phong.
**Giới hạn:** không có mạng, không tự kiểm chứng DOI; mọi nghi vấn trích dẫn đánh dấu `[CẦN KIỂM CHỨNG]`.

---

## 1. Bảng lỗi

| Mức | Vị trí (file:mục) | Vấn đề | Cách sửa |
| --- | --- | --- | --- |
| **Chặn nộp** | `mo-phong/runs/2026-11-18-pid-quy-dao-bac5/run.py` (hàm `settling_overshoot`, dòng ~381–414) và `KETQUA.md` mục 3 | Định nghĩa overshoot và thời gian xác lập **sai về mặt đo lường**. Cửa sổ quan sát kéo dài `target_time + 0.15·T` — tức vào **giữa đoạn quỹ đạo tiếp theo** (giữa các đoạn không có thời gian dừng), nên `overshoot_mm` đo chủ yếu là khoảng cách robot **rời đi** khỏi điểm đích, không phải vọt lố. Kiểm chứng số: overshoot pick = 6,522 mm / quãng đường đoạn 1 (150 mm) = 4,348 % — đúng bằng con số trong bảng; nhưng 6,52 mm **lớn hơn max sai số bám toàn quỹ đạo 1,158 mm**, vô lý nếu cùng đo cùng đại lượng. `settled_at` rơi vào nhánh fallback "lần đầu tiên vào vùng tol" (vì robot rời đích làm `all(dist<=tol)` luôn sai), nên `settling_pick = 0,451 s` không phải thời gian xác lập chuẩn; ở run chu kỳ nhỏ nhất, `settling_place = 0,448 s` **trước cả** thời điểm quỹ đạo tới place (2×0,2321 = 0,464 s). Hệ quả: chỉ tiêu **"overshoot ≤ 5 %" của mục tiêu 2 chưa được chứng minh** bằng số đo đúng. | Sửa metric trước khi viết chương 5: định nghĩa overshoot trong cửa sổ kết thúc tại (hoặc trước) thời điểm đến đích, với quỹ đạo có thời gian dừng ngắn tại pick/place (thêm dwell 0,1–0,2 s); thời gian xác lập đo từ thời điểm đến đích. Chạy lại, cập nhật `metrics.json` + `KETQUA.md`. |
| **Chặn nộp** | `runs/2026-11-18-thi-giac-hsv/KETQUA.md` mục 2, 3, 4 | **Tập test seed 777 đã bị dùng một lần để chẩn đoán.** Mục 3 kể rõ: phiên bản đầu chạy trên 777 cho 84 %, phát hiện 12/25 vuông nhầm tam giác → thêm đặc trưng góc → chạy lại **cùng tập 777** → 100 %. Câu "Các tham số chọn dựa trên validation, áp dụng một lần duy nhất lên test" (mục 3 cuối) **mâu thuẫn với chính mục 3**. Con số "100 % trên held-out" không còn là ước lượng không chệch. | Khai báo trung thực: "100 % trên test, nhưng test đã từng dùng 1 lần để chẩn đoán lỗi; ước lượng không chệch cần tập test mới". Tốt nhất: sinh tập test mới (seed khác, không xem trước) và chạy đúng 1 lần. |
| **Chặn nộp** | `de-tai.md` mục tiêu 3 ↔ `runs/2026-11-18-thi-giac-hsv/*` | Mục tiêu 3 yêu cầu **≥ 120 vật thật**; mọi số liệu hiện có là **ảnh tổng hợp do nhóm tự sinh** (train 285 + val 75 + test 75 = 435 object, 0 vật thật), test chỉ 75 object < 120; webcam chỉ chạy thử (24,4 fps — thấp hơn cả yêu cầu ≥ 30 fps của đề cương). Chương kết quả không được viết "đạt ≥ 90 % trên ≥ 120 vật" từ dữ liệu này. | Trong chương 5 ghi rõ: mục tiêu 3 **chưa hoàn thành phần vật thật**; số hiện tại là kết quả trên bộ sinh + robustness nội bộ. Ưu tiên chụp ≥ 120 vật thật (tuần 7–8 theo kế hoạch). |
| **Chặn nộp** | `firmware/uno-serial-servo/README.md` (cảnh báo đầu file), `GHICHU.md` mục 1, `ket-qua/latency-dryrun-*.csv` | **Chưa có số đo trễ thật nào**: board chưa cắm, các CSV hiện có đều là dry-run (giả lập). Câu hỏi nghiên cứu 2 của `de-tai.md` (trễ thực của chuỗi camera→OpenCV→Arduino; chu kỳ tổng có đạt 1,8 s?) **chưa trả lời được**. Không được trích số dry-run làm số phần cứng. | Cắm board, chạy `do-tre-serial.py --n 500` thật, thay toàn bộ dry-run; nếu không kịp, chương 5 phải ghi "chưa đo được, số giả lập chỉ để kiểm tra script". |
| **Chặn nộp** | `de-tai.md` mục tiêu 2 ↔ `firmware/GHICHU.md` mục 1, 3 ↔ `KETQUA.md` (PID) mục 5 | **Ngân sách chu kỳ tự mâu thuẫn:** chu kỳ thuần 1,5 s + trễ servo cơ khí 0,18–0,37 s (110°, `[DATASHEET]` GHICHU) + grip 0,2–0,3 s (ước lượng `tong-quan.md` 7.1) + camera ~41 ms/frame (webcam thật) ≈ **1,93–2,22 s > 1,8 s**. Với chính các trễ mà repo tự ước lượng, mục tiêu "chu kỳ toàn hệ thống ≤ 1,8 s" **không thể đạt** nếu giữ 1,5 s chuyển động thuần. Con số này chưa bị ai chỉ ra, nhưng chương kết quả mà khẳng định "≤ 1,8 s" sẽ bị hội đồng bóc ngay. | Chốt lại trước khi viết: hoặc rút chu kỳ thuần (≤ 1,2 s), hoặc nới mục tiêu toàn hệ thống lên 2,0 s (đã có tiền lệ khuyến nghị 1,8–2,0 trong `tong-quan.md` 7.1), và lập **bảng phân rã chu kỳ** cộng từng thành phần trễ. |
| Nên sửa | `thiet-ke/thong-so-co-khi.md` mục 5.1–5.2, `BOM.md` mục 1.2, 2 | **Max = 0,689 mm là max mẫu Monte Carlo, không phải cận trên của hộp dung sai ±0,2 mm**, nhưng được dùng làm "trường hợp xấu nhất" trong tổng tuyến tính 0,957 mm. Cận trên giải tích xấp xỉ từ hệ số khuếch đại OAT: (1,16 + 2,52 + 0,97 + 0,97) × 0,2 = **1,12 mm** cho riêng 4 khâu — tức tổng tuyến tính "đúng nghĩa worst-case" có thể vượt 1 mm. Kết luận "đạt ≤ 1 mm theo mọi cách tính" phụ thuộc giả thiết không được nêu: ±0,2 mm thực sự đạt được (trong khi `de-tai.md` mục 4 ghi "không gia công cơ khí chính xác" và Phương án 3 dừng ở CAD+BOM). | Tính thêm tổng worst-case giải tích (tổng \|gain\|×δ) và ghi rõ 0,957 mm là ước lượng từ max mẫu; nêu giả thiết "phải đạt dung sai ±0,2 mm bằng đế CNC + đồ gá" làm điều kiện của kết luận. |
| Nên sửa | `thiet-ke/thong-so-co-khi.md` mục 5.2 | **Cách cộng RSS thiếu cơ sở xác suất:** e_mech P95 = 0,402 mm là phân vị của phân bố sai số **theo điểm trong vùng làm việc** (170 100 mẫu, tương quan chặt giữa các điểm và giữa 3 nhánh), không phải biến ngẫu nhiên độc lập với backlash/encoder/gốc. Backlash là sai số hệ thống theo chiều đảo chiều; e_home là hệ thống (được calib khử một phần). RSS của các phân vị như vậy không cho một mức tin cậy 95 % có nghĩa. | Tách 2 nhóm: hệ thống (cộng tuyến tính: backlash + e_home sau calib) và ngẫu nhiên (RSS: e_mech + e_enc), nêu giả thiết độc lập, và nêu cả 2 kết quả thay vì chọn cái đạt ngưỡng. |
| Nên sửa | `thiet-ke/thong-so-co-khi.md` mục 2 ↔ `runs/.../config.json` (`joint_model`) | **Mô phỏng PID không có trọng lực** (feed-forward = J·θ̈ + b·θ̇, mô hình quán tính–nhớt), nhưng `thiet-ke` mục 2 lập luận mô-men tĩnh Δτ_g = 0,196 N·m = 43 % τ_max và BOM chọn động cơ theo đó. Hai mô hình không nhất quán: số τ_max = 0,457 N·m dùng để tính k_τ = 5,42 **chưa bao gồm thành phần trọng lực** mà chính văn cho là đáng kể. | Cộng trọng lực (τ_g = m g r_f theo cấu hình) vào mô phỏng, hoặc ghi rõ trong cả hai file rằng τ_max hiện tại chưa gồm trọng lực và k_τ thực sẽ thấp hơn. |
| Nên sửa | `thiet-ke/thong-so-co-khi.md` mục 5.1 điểm 3 | e_enc dùng **0,063 mm (1 count)** trong tổng, trong khi chính văn ghi lượng tử hóa là ±0,5 count = ±0,031 mm. Chọn bảo thủ được, nhưng phải ghi rõ lý do, vì nó chiếm khác biệt giữa các cột RSS/Hybrid. | Ghi chú "dùng trọn bước 1 count như biên trên bảo thủ" ngay trong bảng. |
| Nên sửa | `thiet-ke/thong-so-co-khi.md` mục 5.1 | Số `Max_tk ≈ 0,520 mm`, `P95_tk ≈ 0,340 mm` (kịch bản đế CNC ±0,05 + cẳng tay ±0,10) **không có phép chạy nào trong `tom-tat-do-nhay.json` chứng minh** — JSON chỉ có 2 mức ±0,2 và ±0,5 đều-dạng. Số mới không truy nguyên được. | Chạy thêm kịch bản dung sai phân cấp theo bảng mục 4 (±0,05/±0,10/±0,15) trong `do-nhay-hinh-hoc.py`, lưu JSON mới, rồi mới trích. |
| Nên sửa | `mo-hinh/dong-hoc-delta.md` mục 6.5(c) ↔ `thiet-ke/*` | Dung sai **r_e không nhất quán giữa 4 chỗ**: đồ gá ±0,15 mm (dong-hoc 6.5c) vs ±0,10 mm + chênh trong cặp ≤ 0,05 mm (`thong-so` bảng mục 4) vs "độ lệch tương đối ≤ 0,03 mm" (`thong-so` mục 6.2) vs ±0,05 mm (`README` bước 1, `BOM` item 5). Hội đồng sẽ hỏi "vậy r_e dung sai bao nhiêu?". | Chốt 1 bộ số (ví dụ ±0,10 mm tuyệt đối, ≤ 0,05 mm trong cặp) và sửa đồng bộ cả 4 file. |
| Nên sửa | `BOM.md` mục 1.1 ("k_τ ≥ 2,0") ↔ mục "Quyết định thiết kế" (k_τ = 1,55 ở 0,696 s) ↔ `KETQUA.md` mục 5 | Bảng yêu cầu k_τ ≥ 2,0 nhưng phương án được chọn chỉ đạt **1,55** ở chu kỳ giới hạn 0,696 s; đồng thời chu kỳ 0,696 s này **vi phạm sai số xác lập 2,7/5,3 mm** (run tự ghi) — `thiet-ke` mục 2 và `BOM` trích τ = 1,636 N·m ở 0,696 s mà **không kèm cảnh báo** này. | Khi trích số liệu chu kỳ 0,696 s bắt buộc kèm "vi phạm chỉ tiêu xác lập, chỉ dùng để cận mô-men"; sửa tiêu chí k_τ thành "≥ 2,0 ở chu kỳ danh mục 1,5 s". |
| Nên sửa | `KETQUA.md` (thi-giac) mục 6 ↔ `output/metrics.json` | Số trễ không khớp giữa 2 nguồn: KETQUA ghi P95 = 4,27 ms, P99 = 5,20 ms; `metrics.json` ghi p95 = **4,12**, p99 = **4,73** (mean 3,41 khớp). | Chọn một nguồn (nên là metrics.json), sửa KETQUA; nêu rõ nguồn tính (timing_ms.csv hay tổng hợp). |
| Nên sửa | `KETQUA.md` (thi-giac) mục 5.5 ↔ `output/robustness.csv` | (a) Phép thử bóng đổ sau khi sửa lỗi "làm sáng" vẫn **quá nhẹ**: mean\|diff\| = 3,48/255 (~1,4 %) — bóng gần như không đổi ảnh; "88,9 % dưới bóng đổ" không phải bằng chứng bền với bóng thật. (b) Bảng KETQUA **bỏ cột precision của shadow = 78,57 %** (CSV có) — nhiều false positive dưới bóng; bỏ mất chỉ tiêu bất lợi là选择性 báo cáo. (c) Mỗi điều kiện chỉ 36 ảnh → 88,9 % = 4 sai/36; khoảng tin cậy rất rộng, không nên khẳng định %. | Tăng cường độ bóng (mean\|diff\| ≥ 20–30) và chạy lại; đưa đủ cột precision vào bảng; ghi khoảng tin cậy (Wilson) cho từng %. |
| Nên sửa | `bao-cao/02-tong-quan.md` mục 2.2 và 2.8 | Tuyên bố "đánh số theo thứ tự xuất hiện" nhưng **[4] xuất hiện trước [3]** (mục 2.2: "[4]" ở câu FK, "[3]" Vischer ở câu sau). Vi phạm chuẩn IEEE tự đặt. | Đổi số: Yang & Xiao thành [3], Vischer thành [4], cập nhật toàn bộ dẫn chiếu ở cả chương 1, 2. |
| Nên sửa | `tai-lieu/bang-so-sanh.md` "So sánh theo chỉ tiêu" | "Phân loại ≥ 90 % (**≥ 100 mẫu**)" — `de-tai.md` yêu cầu **≥ 120**. Sai lệch ngưỡng giữa 2 file chuẩn. | Sửa thành ≥ 120. |
| Nên sửa | `runs/.../config.json` (`encoder_counts_per_rev: 4096`) ↔ `BOM.md` (1 000 PPR → 4 000 cpr) | Encoder trong mô phỏng (4096 cpr) khác encoder trong BOM (4000 cpr). Khác biệt nhỏ (e_enc 0,0615 vs 0,0628 mm) nhưng hai hệ thống số nên dùng chung một thông số. | Thống nhất (theo BOM: 4000 cpr) hoặc nêu rõ hai kịch bản. |
| Nên sửa | `references.bib` (note Clavel1988, note PhuongHoai2023), `thiet-ke/*` nhiều chỗ | Các nhãn `[CẦN KIỂM CHỨNG]` chưa xử lý: (a) DOI Clavel 1988; (b) tên/thứ tự tác giả FME 2023; (c) độ giãn đai GT2 0,1 mm (thông số then chốt của phương án truyền động được chọn, không có datasheet); (d) quán tính rotor 0,002–0,004 kg·m²; (e) datasheet rod-end/ổ bi. Riêng (c) là **số đầu vào của kết luận ngân sách sai số** — không được để `[CẦN KIỂM CHỨNG]` tới ngày nộp. | Kiểm chứng qua Crossref/đọc toàn văn; với (c) phải đo hoặc trích datasheet đai cụ thể, nếu không phương án T2 mất căn cứ. |
| Góp ý | `mo-hinh/ket-qua/tom-tat-kiem-chung.json` ↔ `runs/.../config.json` | R_b/r_p/R lệch nhau ~1×10⁻⁵ mm giữa 2 file (199,7631931 vs 199,7632026). Vô hại về số nhưng cho thấy 2 đường tính khác nhau. | Quy về một hàm tính duy nhất (f/√3 chính xác) trong một module dùng chung. |
| Góp ý | `mo-hinh/dong-hoc-delta.md` mục 6.6 | Tiêu đề ghi "Giới hạn trần vùng làm việc (z > **−265** mm)" nhưng thân bài ghi "z > **−250** mm". | Thống nhất một giá trị, kèm cơ chế (θ vượt −40° tại z nào). |
| Góp ý | `mo-hinh/dong-hoc-delta.md` mục "Tài liệu tham khảo" | Liệt kê đủ 8 mục nhưng thân bài chỉ dẫn [1], [2]; mục [3]–[8] "trích mà không dùng" trong file này. | Chỉ liệt kê các mục thực dùng, hoặc dẫn thêm khi liên hệ (ví dụ [5] khi nói giới hạn PID tốc độ cao). |
| Góp ý | `thiet-ke/BOM.md` mục 2 | Khoảng giá tổng "6,410–9,270 triệu" không khớp tổng cột thấp/cao tính từ chính bảng (tôi cộng được 6,70–9,34 triệu); tổng điểm 7,860 triệu thì khớp. | Tính lại khoảng từ chính các dòng của bảng. |
| Góp ý | `runs/.../KETQUA.md` mục 4 | "Bộ tốt nhất: PID+FF_nhanh" — RMSE 0,0190 vs 0,0208 (can_bang) chênh 9 %, không đáng kể; nên nêu tiêu chí chọn và độ chênh để tránh cảm giác kết luận cưỡng ép. | Ghi "ba bộ PID+FF tương đương (RMSE 0,019–0,025 mm); chọn nhanh vì dư biên". |
| Góp ý | `runs/.../KETQUA.md` mục 2 | "Sai số xác lập" thực chất là **trung bình sai số 50 ms cuối trước khi tới đích** (`run.py` dòng 370–374) — là sai số bám cuối đoạn, không phải xác lập đứng yên (các đoạn không dừng). Định nghĩa phải nêu trong chương 5. | Đổi tên chỉ tiêu thành "sai số cuối đoạn (50 ms trước đích)" hoặc thêm dwell rồi đo đúng nghĩa. |
| Góp ý | `thiet-ke/BOM.md` mục 1.2 (kịch bản 3) | RSS 0,620 / tuyến tính 1,050 mm của bản tiết kiệm (AS5600 gắn trực tiếp) không kèm bảng thành phần — không đủ dữ kiện để tái lập. | Thêm bảng thành phần như mục 5.1 của `thong-so-co-khi.md`. |

### Phần còn thiếu để bảo vệ được (điểm 7 checklist)

1. **Số đo thật từ phần cứng:** trễ vòng Serial thật (board chưa cắm); trễ cơ khí servo; đặc tuyến xung–góc; deadband (GHICHU mục 7 liệt kê đủ — chưa làm mục nào).
2. **Dữ liệu vật thật:** ≥ 120 vật 3 màu × 3 hình; hiện 0 vật thật.
3. **Chương 3–6 của báo cáo:** mới có chương 1, 2.
4. **CAD thật:** `ban-ve-so-do.svg` là sơ đồ 2 hình chiếu, không phải mô hình CAD 3D như sản phẩm dự kiến trong `de-tai.md` mục 6.
5. **Toàn văn tài liệu:** 8 bài mới đọc abstract/metadata; các mục `[CẦN BỔ SUNG]` trong chương 2 (sai số hiệu chuẩn [3], sai số bám [5][6], phân rã 1,8 s [2]) chưa có số.
6. **Bảng phân rã chu kỳ toàn hệ thống:** mục tiêu 2 vế 2 chưa có bài chạy tổng hợp nào chứng minh.
7. Không đủ dữ kiện để đánh giá: số liệu "100 % dưới bóng đổ" *trước khi sửa* (không thấy file lưu kết quả cũ; chỉ có mô tả trong KETQUA và nhật ký — chấp nhận được vì có `check-degradations.py` và `robustness_errors.txt` làm bằng chứng quá trình).

---

## 2. Số liệu đã tự tính lại (để đối chiếu)

**Quy đổi backlash (r_f = 200 mm; 1 arcmin = π/10800 = 2,9089×10⁻⁴ rad):**
- 5 arcmin = 1,4544×10⁻³ rad × 200 mm = **0,291 mm** ✓ (bảng ghi 0,291)
- 10 arcmin = 2,9089×10⁻³ rad × 200 = **0,582 mm** ✓
- 15 arcmin = 4,3633×10⁻³ rad × 200 = **0,873 mm** ✓

**Encoder 1 000 PPR × 4 (quadrature) × 5:1 = 20 000 cpr tại khớp:**
- δθ = 2π/20 000 = 3,1416×10⁻⁴ rad; e_enc = 200 × 3,1416×10⁻⁴ = **0,0628 mm** ✓ (bảng 0,063)
- Truyền trực tiếp 1:1: 200 × 2π/4 000 = **0,314 mm** ✓

**Lệch gốc:** hệ số 200 × π/180 = 3,4907 mm/°; 0,1° → **0,349 mm** ✓; 0,03° → **0,105 mm** ✓.

**Ngân sách sai số — tái tính cả 5 kịch bản (công thức: RSS = √(0,402² + e_bl² + 0,063² + e_home²); Hybrid = e_bl + √(0,402² + 0,063² + e_home²); Linear = 0,689 + e_bl + 0,063 + e_home):**

| Kịch bản | RSS | Hybrid | Linear | Linear sau calib | Khớp bảng? |
| --- | --- | --- | --- | --- | --- |
| 15 arcmin | √1,0495 = 1,024 | 1,409 | 1,974 | 1,730 | ✓ tất cả |
| 10 arcmin | 0,791 | 1,118 | 1,683 | 1,439 | ✓ |
| 5 arcmin | 0,610 | 0,827 | 1,392 | 1,148 | ✓ |
| GT2 (e_bl = 0,100) | 0,545 | 0,636 | 1,201 | **0,957** ✓ | ✓ |
| Direct 1:1 | 0,618 | 0,638 (bảng 0,641) | 1,372 | 1,128 | ✓ (sai 0,003 mm do làm tròn) |

→ **Số học trong bảng ngân sách đúng.** Vấn đề nằm ở **ý nghĩa** của cách cộng (xem hàng "Nên sửa" tương ứng): 0,689 mm là max mẫu Monte Carlo chứ không phải cận trên hộp dung sai; cận trên xấp xỉ giải tích từ hệ số khuếch đại OAT là (1,16 + 2,52 + 0,97 + 0,97) × 0,2 = **1,12 mm** cho riêng 4 khâu.

**Động lực học (đối chiếu `thiet-ke` mục 2):**
- J_mech = ⅓ × 0,11 × 0,04 + (0,035 + ⅔×0,036 + ⅓×0,075) × 0,04 = 0,00147 + 0,00336 = **0,00483 kg·m²** ✓
- Δτ_g (100 g): 0,1 × 9,81 × 0,2 = **0,196 N·m**; 0,196/0,457 = **42,9 %** ✓ — nhưng mô phỏng PID **không có** thành phần này (xem lỗi "Nên sửa").
- k_τ: 2,48/0,457 = 5,43 (bảng 5,42); 2,53/0,457 = 5,53 (bảng 5,54); 2,53/1,636 = 1,546 (bảng 1,55) — khớp trong sai số làm tròn.

**Chu kỳ toàn hệ thống (tự cộng từ số trong repo):**
1,5 (thuần) + 0,041 (frame webcam thật) + 0,005 (trễ vòng Serial mean, `[ƯỚC LƯỢNG]`) + 0,18–0,37 (servo 110°, `[DATASHEET]`) + 0,2–0,3 (grip, ước lượng) = **1,93–2,22 s** → vượt mốc 1,8 s kể cả kịch bản tốt nhất.

**Overshoot PID (chứng minh lỗi metric):** 6,522/150 = 4,348 % ✓ khớp bảng; nhưng lý thuyết quỹ đạo bậc 5, tại t = đích + 0,15T (τ = 0,15), s(τ) = 10τ³−15τ⁴+6τ⁵ = 0,0266 → đoạn pick→place dài 287 mm đã đi được **≈ 7,6 mm** khỏi pick — đúng bậc độ lớn với "overshoot" 6,52 mm được báo cáo. Kết luận: con số đo **khoảng cách rời đích**, không phải vọt lố.

**Kiểm tra khác đã làm:** bảng 6.4/6.5 trong `dong-hoc-delta.md` khớp tuyệt đối với `tom-tat-kiem-chung.json` và `tom-tat-do-nhay.json` (cả OAT); ma trận nhầm lẫn train/val/test khớp giữa `metrics.json` và `metrics-heldout.json`; robustness.csv khớp bảng 5.5 của KETQUA (riêng cột precision bị bỏ); tổng tiền BOM cột đơn 7,860 triệu ✓; 1 859 = 11 × 169 điểm lưới ✓.

---

## 3. Ba câu hỏi hội đồng có thể hỏi + gợi ý trả lời

**Câu 1. "Sai số vòng kín 10⁻¹³ mm của anh là con số vô nghĩa về mặt vật lý. Vậy trên robot thật, anh khẳng định đạt bao nhiêu mm và căn cứ đâu?"**
Gợi ý trả lời: Con số 10⁻¹³ mm chỉ chứng minh cặp hàm IK/FK là nghịch đảo đúng trong mã nguồn — đúng như nhật ký 18/11 đã ghi "không chứng minh độ chính xác vật lý". Độ chính xác thật được ước lượng bằng ngân sách sai số: Monte Carlo dung sai ±0,2 mm cho P95 = 0,514 mm (kèm lệch khớp đế), cộng backlash truyền đai ~0,1 mm và encoder 0,063 mm, cho tổng Hybrid ~0,64 mm. Điều kiện để con số này đứng: dung sai ±0,2 mm thực sự đạt được bằng đế CNC và đồ gá — điều kiện này phải được nêu rõ, và con số cuối cùng chỉ chốt được bằng đo trên khung thật (quy trình 9 điểm chuẩn trong `thiet-ke/README.md` mục 4).

**Câu 2. "Anh báo cáo 100 % trên tập held-out, nhưng dữ liệu là ảnh anh tự sinh. Giá trị khoa học của con số này là gì?"**
Gợi ý trả lời: Phải trả lời thẳng: 100 % chỉ đúng cho ảnh tổng hợp do chính bộ sinh của nhóm tạo ra, và tập test 777 đã từng bị dùng một lần để chẩn đoán lỗi (84 % → sửa → chạy lại), nên nó không còn là ước lượng hoàn toàn không chệch. Phép thử độ bền của chính nhóm cho thấy khi kết hợp nhiều suy giảm, độ chính xác rơi còn 61,1 % — tức pipeline chưa bền với điều kiện thật. Vì vậy mục tiêu 3 của đề cương (≥ 90 % trên ≥ 120 vật thật) **chưa hoàn thành**; con số hiện tại chỉ có giá trị kiểm chứng logic thuật toán và định hướng hiệu chỉnh ngưỡng.

**Câu 3. "Mốc đối chiếu của anh là 1,8 s/vật của Vo & Le (2023). Hệ thống của anh đạt bao nhiêu và trễ thật đo được bao nhiêu?"**
Gợi ý trả lời: Mô phỏng cho chu kỳ chuyển động thuần 1,5 s (quỹ đạo bậc 5, ω_max 4,66 < 10 rad/s, τ_max 0,457 < 2 N·m). Phần trễ thật: board Arduino chưa cắm nên chỉ có dry-run (3–20 ms, giả lập — phải nói rõ); trễ servo cơ khí 0,18–0,37 s theo datasheet. Cộng các thành phần theo bảng phân rã (chưa có — việc cần làm tiếp) cho thấy chu kỳ toàn hệ thống ước khoảng 1,9–2,2 s, **vượt** mốc 1,8 s nếu giữ 1,5 s thuần; do đó phải rút quỹ đạo hoặc đối chiếu với dải 1,8–2,0 s mà tổng quan đã khuyến nghị, và báo cáo trung thực điều này thay vì khẳng định đạt.

---

*Phản biện này chỉ nêu lỗi có dẫn chứng trong file; không sửa bất kỳ file nào ngoài `phan-bien-01.md`.*
