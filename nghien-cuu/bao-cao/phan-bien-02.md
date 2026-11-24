# Phản biện đợt 2 — 4 chương 03/04/05/06 (soi số liệu)

Phạm vi: `bao-cao/03-co-so-ly-thuyet.md`, `04-thiet-ke-he-trong.md` → đúng tên `04-thiet-ke-he-thong.md`, `05-ket-qua-thao-luan.md`, `06-ket-luan.md`.
Phương pháp: từng con số được mở file nguồn để đối chiếu. Nguồn dùng:
`mo-hinh/dong-hoc-delta.md`, `mo-hinh/ket-qua/tom-tat-kiem-chung.json`, `tom-tat-do-nhay.json`,
`mo-phong/runs/2026-11-24-pid-v2-dung-nghi/` (KETQUA.md, output/metrics.json, output/quet-chu-ky.csv, config.json),
`mo-phong/runs/2026-11-18-thi-giac-hsv/` (KETQUA.md, output/metrics.json, output/robustness.csv, ket-qua/test-999/metrics-heldout.json, error_cases.csv),
`thiet-ke/thong-so-co-khi.md`, `thiet-ke/BOM.md`, `thiet-ke/README.md`, `firmware/uno-serial-servo/` (GHICHU.md, config.h, README.md),
`de-tai.md`, `tai-lieu/references.bib`, `tai-lieu/notes/*`, chương 1–2.
Không có mạng → không kiểm chứng được DOI; chỉ nêu những gì bib tự đánh dấu `[CẦN KIỂM CHỨNG]`.

## 1. Bảng lỗi

| Mức | Vị trí | Vấn đề | Cách sửa |
| --- | --- | --- | --- |
| Chặn nộp | `05-ket-qua-thao-luan.md` mục 5.2, đoạn sau Bảng 5.3 | Khẳng định **sai về nguồn**: "Cột 'tách nhóm hệ thống + ngẫu nhiên' trong `thong-so-co-khi.md` không được đưa vào bảng vì công thức ghi trong file không tái lập được các số của cột đó." Đã tính lại: 0,205 + √(0,402²+0,063²) = **0,612** và 0,205 + √(0,689²+0,063²) = **0,897** tái lập đúng các số ở Bảng 5.2b của `thong-so-co-khi.md` (dòng 198–199, 208). Tệ hơn: chương 4 (Bảng 4.6) dùng chính các số tách nhóm này và ghi "Các phép cộng được tính lại và khớp với bảng nguồn" — **hai chương tự mâu thuẫn**. | Xoá nhận định "không tái lập được"; đưa cột tách nhóm vào Bảng 5.3 (0,612 / 0,897) để khớp với Bảng 4.6 và kết luận của ch6 ("ngân sách 0,612 mm"). Ghi rõ đây là giả thiết độc lập giữa hai nhóm. |
| Nên sửa | `04-thiet-ke-he-thong.md` mục 4.2, đoạn "Quán tính" | "Mô phỏng dùng J = 0,01 kg·m², cao hơn khoảng 25–35 %." Sai số học: 0,01/0,0075 = **+33 %**, 0,01/0,0066 = **+52 %**. Lỗi có sẵn trong `thong-so-co-khi.md` mục 2 (dòng 77) nhưng báo cáo lặp lại như事实 đúng. | Viết lại "cao hơn ước tính khoảng 33–52 %" hoặc ghi rõ cơ sở của "25–35 %" (không tìm thấy cách tính nào cho ra dải đó). Sửa cả file nguồn nếu xác nhận. |
| Nên sửa | `05-ket-qua-thao-luan.md` Bảng 5.5, chú thích nguồn + Ghi chú biên tập cuối chương | "file KETQUA ghi 1,26 / 1,50 / 2,04 s **do làm tròn bỏ phần thị giác và truyền thông**" — sai. `KETQUA.md` mục 7 và mục 5 cộng **đủ** overhead 0,046 s (thị giác 3,41 + chờ khung 41,05 + Serial 2,0 ms; mục 5 viết rõ "cộng overhead 0,046 s thành 2,046 s"); `thong-so-co-khi.md` mục 1.1 cũng ghi "cộng trễ camera + truyền thông ⟹ 1,50 s". Khác biệt 1,26 so với 1,27 chỉ là cách làm tròn (1,2665). Ghi chú biên tập cuối ch5 lặp lại cùng nhận định sai. | Sửa chú thích thành "khác nhau do làm tròn/thu hẹp số chữ số, không phải do bỏ thành phần". Xoá dòng biên tập sai. |
| Nên sửa | `05-ket-qua-thao-luan.md` Bảng 5.9, dòng Elassal | Trích trong ngoặc kép: "effective and accurate" — note `tai-lieu/notes/elassal-2024-low-cost-delta-vision.md` (dòng 19) ghi nguyên văn abstract là **"proved the effectiveness and accuracy"**. Cụm trong ngoặc kép không phải nguyên văn. | Dùng nguyên văn "proved the effectiveness and accuracy" hoặc bỏ ngoặc kép, diễn giải tiếng Việt. |
| Nên sửa | `04-thiet-ke-he-thong.md` mục 4.3, đoạn "Mô-men động cơ và tốc độ" | "cần động cơ có ... tốc độ định mức ≥ 350 vòng/phút" — không tìm thấy yêu cầu này trong `BOM.md`. BOM mục 1.1 yêu cầu ω định mức trục khớp ≥ 10 rad/s ⟹ **động cơ ≥ 480 vòng/phút** (qua 5:1); số 350 chỉ xuất hiện trong BOM như một ví dụ "350 rpm dư tốc độ > 2,0×". 350 = 5 × 69,2 rpm là tốc độ **đỉnh tại điểm vận hành**, không phải định mức. | Ghi tách bạch: "tốc độ đỉnh yêu cầu ≈ 346 vòng/phút (tại điểm vận hành); yêu cầu định mức theo BOM mục 1.1 là ≥ 480 vòng/phút". |
| Nên sửa | `04-thiet-ke-he-thong.md` Bảng 4.2 (và nguồn `thong-so-co-khi.md` mục 2) | Khối lượng ước tính không có cách tính dẫn ra. Kiểm tra nhanh: tam giác đều cạnh 346 mm, dày 10 mm nhôm ≈ **1,4 kg**; tấm bao 480×480 mm (BOM dòng 1) dày 10 mm nhôm ≈ **6,2 kg**. Số "≈ 2,8 kg (nhôm) / ≈ 6,2 kg (thép)" trong file cho thấy nghi vấn nhãn nhôm/thép hoán đổi (6,2 kg trùng khối lượng **nhôm** của tấm 480×480×10). Không đủ dữ kiện để khẳng định sai, nhưng hiện không tái lập được. | Ghi rõ hình dạng tấm (tam giác / lục giác ngoại tiếp Ø500 mục 6 / bao 480×480) và cách tính khối lượng; kiểm tra lại nhãn vật liệu. J_eq và Δτ_g không phụ thuộc khối đế nên không ảnh hưởng kết luận mô-men, nhưng ảnh hưởng độ tin của mục 4.2. |
| Nên sửa | `03-co-so-ly-thuyet.md` mục 3.6, đoạn "Hạn chế của chuỗi thị giác" | "Ngưỡng cụ thể của các đặc trưng hình học ... nằm trong mã, không được ghi trong tài liệu tóm tắt" — không đúng hoàn toàn: `KETQUA.md` (thị giác) mục 3 ghi quy tắc góc đỉnh **"ít nhất 3 góc trong khoảng 70°–110°"**. Riêng ngưỡng circularity/solidity thì đúng là chỉ có trong mã. | Tách hai vế: góc đỉnh đã có ngưỡng ghi trong KETQUA.md; chỉ circularity/solidity cần `[CẦN BỔ SUNG]` từ `src/detect.py`. |
| Góp ý | `03-co-so-ly-thuyet.md` mục 3.2 | Trích trong ngoặc kép: "nhảy lên khoảng 10⁻¹⁰ mm" — nguyên văn `dong-hoc-delta.md` (dòng 166) là "nhảy lên **~**10⁻¹⁰ mm". Thêm chữ "khoảng" vào trong ngoặc kép là paraphrase. | Thay dấu ~ hoặc bỏ ngoặc kép. Ý nghĩa số học không đổi. |
| Góp ý | `04` Bảng 4.5 (k_τ = 2,22) vs `05` Bảng 5.5 (k_τ = 2,23) | Cùng đại lượng τ_ra/τ_yc nhưng hai cách làm tròn: 2,53/1,14 = 2,22; 2,53/1,136 = 2,23. Cả hai đều có nguồn (`BOM.md` mục 1.2 và `KETQUA.md` mục 7), nhưng hội đồng sẽ hỏi vì sao đổi số giữa hai chương. | Chọn một quy ước (khuyến nghị 2,23 theo giá trị chưa làm tròn 1,136, như `thong-so-co-khi.md` mục 1.1 đã ghi cả hai) và chú thích một lần. |
| Góp ý | `04` mục 4.5 ("dư ... 0,26 s (P95)") vs `05` Bảng 5.6 ("Dư 0,25 s") | 1,8 − 1,545 = 0,255 → hai chương làm tròn khác chiều. | Thống nhất một cách làm tròn, ví dụ "≈ 0,25–0,26 s". |
| Góp ý | `05-ket-qua-thao-luan.md` mục 5.5 | "Khoảng cách tâm **giữa hai dự đoán** là 0,0 px và 1,4 px" — trường `distance_px` trong `error_cases.csv` là khoảng cách GT↔dự đoán của từng ca sai; kết luận "cùng một vật" là diễn giải của file nguồn (`KETQUA.md` thị giác mục 5), chưa có minh hoạ trực quan kèm theo. | Nêu đúng nghĩa của `distance_px` và ghi rõ đây là suy diễn từ ca lỗi (hoặc kèm ảnh lỗi từ figures nếu có). |
| Góp ý | `04-thiet-ke-he-thong.md` mục 4.4 và ch4.5 | "quy trình hiệu chuẩn 9 điểm (thiết kế/README.md, **mục 4B**)" — `thiet-ke/README.md` chia mục "4. Quy trình Hiệu chuẩn Động học" với tiêu đề con "**Giai đoạn B**" (dòng 89, 129), không có nhãn "4B". (Lỗi nhãn có sẵn trong `thong-so-co-khi.md` mục 5.1.) | Sửa thành "README.md mục 4, Giai đoạn B". |
| Góp ý | `04-thiet-ke-he-thong.md` Bảng 4.7 | Chỉ liệt kê 2 lệnh `J`, `H`; `config.h` còn định nghĩa `P` (ping → `P,<micros>`) và `S` (trạng thái) không nhắc. | Thêm dòng "các lệnh phụ P, S (không dùng trong chu trình gắp–thả)" hoặc ghi "hai lệnh chính". |
| Góp ý | `05-ket-qua-thao-luan.md` mục 5.1, `[CẦN BỔ SUNG]` | Điểm còn treo có thể **đóng ngay**: đã kiểm `kiem-chung-ik-fk.py` dòng 271–315 — hàm phần dư của Newton–Raphson chỉ dùng ràng buộc hình học F = ‖p − C_i‖² − r_e², **không gọi lại công thức IK**. | Bổ sung xác nhận này vào văn bản và xoá `[CẦN BỔ SUNG]`. |
| Góp ý | `05-ket-qua-thao-luan.md` Bảng 5.3, chú thích nguồn | Dẫn "số học được tính lại trong `bao-cao/phan-bien-01.md` mục 2" — file phản biện không phải nguồn dữ liệu; số học nên tính lại trực tiếp và dẫn `thong-so-co-khi.md` Bảng 5.2a. | Bỏ dẫn tới file phản biện; tính lại và ghi "số học đã tính lại, khớp Bảng 5.2a". |
| Góp ý | `03-co-so-ly-thuyet.md` (3.11) và Bảng 3.3 | `config.json` có `tau_d_filter_s = 0,005` (lọc bộ vi phân) không nhắc trong mô hình PID. Ảnh hưởng nhỏ nhưng để tái lập đúng cần ghi. | Thêm một dòng vào Bảng 3.3. |

## 2. Bảng đối chiếu số

Quy ước: "khớp" = số trong báo cáo truy được về file nguồn (kể cả sau làm tròn hợp lý). Kiểm tra thêm số học khi có công thức.

| # | Số trong báo cáo (vị trí) | Giá trị file nguồn | Kết luận |
| --- | --- | --- | --- |
| 1 | Bảng 3.2/5.1: max sai số vòng kín FK giải tích 1,583×10⁻¹³ mm | `tom-tat-kiem-chung.json`: 1,5826458×10⁻¹³ | Khớp |
| 2 | Bảng 5.1: RMSE FK giải tích 6,907×10⁻¹⁴; FK NR 1,836×10⁻¹³; lệch 1,729×10⁻¹³; NR 5,73/6 vòng; 1 859/1 859 | JSON: 6,9066×10⁻¹⁴; 1,83585×10⁻¹³; 1,72883×10⁻¹³; 5,7348/6; 1859/1859 | Khớp |
| 3 | 1 859 điểm = 11 mặt cắt × 169 điểm | `dong-hoc-delta.md` dòng 345 (11 × (1 + 7×24)) | Khớp |
| 4 | (3.5) bậc hai sau thế nửa góc; Δ = E²+F²−G²; dạng Citardauq (3.6) | `dong-hoc-delta.md` (11)–(16), dòng 155–166; kiểm lại đại số: đúng (t₂ = (G+E)/(−F+√Δ) ≡ t₁) | Khớp |
| 5 | Đỉnh vận tốc 1,875·Δ/T; gia tốc 10/√3·Δ/T² ≈ 5,77 | Tính lại: s′(½)=30/16=1,875; s″max=5,7735 = 10/√3 | Khớp (đã sửa lỗi 10√3 của đợt 1) |
| 6 | e_backlash = r_f·δθ; 15 arcmin → 0,873; 10 → 0,582; 5 → 0,291 mm | `thong-so-co-khi.md` mục 5.1 (2,9089×10⁻⁴ rad/arcmin × 200 mm) | Khớp |
| 7 | e_enc = r_f·2π/N: 20 000 xung/vòng → 0,063 mm; 1:1 → 0,314 mm | `thong-so-co-khi.md` mục 5.1; tính lại 0,0628 / 0,3142 | Khớp |
| 8 | e_home = 3,491 mm/° × 0,03° = 0,105 mm; × 0,10° = 0,349 mm | File mục 5.1.4 (200×π/180 = 3,491) | Khớp |
| 9 | Cận trên giải tích 4 khâu ±0,2 mm = 1,123 mm | (1,1624+2,5168+0,9683+0,9679)×0,2 = 1,1231; `tom-tat-do-nhay.json` gains + file mục 5.1 | Khớp |
| 10 | Bảng 4.3: đóng góp 0,170/0,252/0,116/0,097/0,145; tổng 0,780 | Gains × dung sai; file mục 5.1 (0,170+0,465+0,145 = 0,780) | Khớp |
| 11 | Bảng 4.6: 0,205; 0,407; 0,612; 0,897; 0,957; 1,123; 1,048 | `thong-so-co-khi.md` Bảng 5.2a/5.2b; tính lại tất cả các phép cộng | Khớp |
| 12 | Bảng 5.2: toàn bộ phân vị 4 kịch bản (0,236…2,410; 31,57 %; 0,00 %) | `tom-tat-do-nhay.json` mc_*: khớp từng ô (1,506 mm ở P99 kịch bản ±0,5+đế trùng ngẫu nhiên với chu kỳ, đã kiểm là 1,50633) | Khớp |
| 13 | OAT: 3,40 / 2,52 / 1,16 / 0,97 / 0,97 mm/mm; P95 đơn lẻ r_e = 0,291 | JSON oat_sensitivity: 3,3976 / 2,5168 / 1,1624 / 0,9683 / 0,9679; P95 re 0,29108 | Khớp |
| 14 | Bảng 5.4: 1,137/0,186; RMSE 0,435/0,070; overshoot 0,202/0,134; 0,331/0,115; 0,168/0,058; cuối dwell 0,067/0,122/0,173; τ 0,453/0,455; ω 4,665/4,645 | `metrics.json` (run v2) main_comparison: khớp từng ô | Khớp |
| 15 | Bản cũ: overshoot 6,52 mm / 4,35 %, max_err 1,158 mm | `KETQUA.md` v2 mục 1 | Khớp |
| 16 | RMSE T=0,30: 0,0813 mm bật / 0,0001 mm tắt lượng tử hoá | `KETQUA.md` mục 6.2 | Khớp |
| 17 | Bảng 5.5: T=0,22 (10,53; 1,796); 0,24 (9,66; 1,542; 1,74; 1,46); 0,32 (7,25; 0,940; 1,14; 2,23); 0,50 (4,64; 0,450; 0,65; 3,92) | `quet-chu-ky.csv` + `KETQUA.md` mục 7 (k_τ 2,23 theo 1,136) | Khớp |
| 18 | Chú thích Bảng 5.5: "file KETQUA ghi 1,26/1,50/2,04 s **do bỏ phần thị giác và truyền thông**" | `KETQUA.md` mục 7 **gồm** overhead 0,046 s (mục 5: 2,046 s); khác nhau chỉ do làm tròn | **Lệch (mô tả nguồn sai)** |
| 19 | Bảng 4.9/5.6: tổng 1,506 s (danh định) / 1,545 s (P95); dư 0,29 s / 0,26 s (ch4) vs 0,25 s (ch5) | Tính lại: 0,96+0,5+0,00341+0,04105+0,002 = 1,5065; P95 = 1,5452; dư 0,294 / 0,255 | Khớp số; dư P95 nhất quán chưa đạt giữa 2 chương |
| 20 | Trễ UART: lệnh ≤20 byte → 1,5–1,7 ms; đáp ≤13 byte → 0,7–1,1 ms; CH340 1–4 ms; OS 1–15 ms; tổng 3–20 ms (~5 ms); servo 110° 0,18–0,37 s | `GHICHU.md` mục 1–3 (20×86,8 µs = 1,74 ms ≈ biên trên) | Khớp |
| 21 | 1 µs ≈ 0,09°; deadband 5–8 µs ≈ 0,5–0,7°; `micros()` bước 4 µs; bộ đệm 64 byte; kẹp [−30°,+80°] | `GHICHU.md` mục 4–5; `config.h` (SERIAL_RX_BUF, JOINT*_MIN/MAX_DEG) | Khớp |
| 22 | Bảng 4.5: T1 2,48 N·m, k_τ 2,18, 0,291, 0,063, "đạt 0,803 sau hiệu chuẩn", 4,8–7,2 triệu; T2 2,53, 2,22, ≈0/0,100; T3 1,50, 1,32, 0,020, 0,314 | `BOM.md` mục 1.2; `thong-so-co-khi.md` Bảng 5.2b dòng 3 (0,803 mm sau calib) | Khớp |
| 23 | Đàn hồi đai: F 4,7–7,7 N; L 120 mm; EA 45 000–73 000 N; ΔL ≈ 0,013 mm; r_f/R_80T = 7,855; → 0,100 mm | `thong-so-co-khi.md` mục 5.1.2 (7,855×0,0127 = 0,0998) — đã đánh dấu giả thiết `[CẦN KIỂM CHỨNG BẰNG ĐO]` ở cả nguồn | Khớp (cùng trạng thái giả thiết) |
| 24 | "cao hơn khoảng 25–35 %" (J = 0,01 so với 0,0066–0,0075) | Tính lại: +33 % ÷ +52 % | **Lệch (sai số học)** |
| 25 | Bảng 4.2: đế ≈ 2,8 kg (nhôm) / 6,2 kg (thép) | `thong-so-co-khi.md` mục 2 ghi đúng các số này, nhưng không có cách tính; kiểm nhanh tam giác 346/10 mm nhôm ≈ 1,4 kg, tấm 480×480×10 nhôm (BOM dòng 1) ≈ 6,2 kg | **Không tái lập được (nghi nhầm nhãn nhôm/thép)** |
| 26 | "tốc độ định mức ≥ 350 vòng/phút" | `BOM.md` mục 1.1 yêu cầu động cơ ≥ 480 vòng/phút (định mức trục khớp ≥ 10 rad/s); 350 rpm chỉ xuất hiện trong BOM như ví dụ dư tốc độ | **Không có nguồn trực tiếp** |
| 27 | Bảng 4.10: A 7 dòng 3,01–4,17; B 4 dòng 1,05–1,62; C 5 dòng 2,64–3,55; tổng 6,70–9,34; tham chiếu 7,86 triệu; động cơ 1,65–2,10; đế CNC 0,85–1,10; HIL ~0,42 triệu | Cộng lại từ 16 dòng `BOM.md`: 3,01–4,17 / 1,05–1,62 / 2,64–3,55 / 6,70–9,34 / 7,86 — **báo cáo đúng**, chú thích nhóm của BOM (2,86/2,79) mới là số sai | Khớp (báo cáo đúng hơn nguồn) |
| 28 | Thị giác seed 999: 60 ảnh, 75 vật; 97,33 % (73/75); CI 90,8–99,3; màu 75/75 CI 95,1–100; ma trận hình 26/2/0, 0/25/0, 0/0/22; màu 29/25/21; 2 ca đỏ-tròn→đỏ-vuông, 0,0 px và 1,4 px | `metrics-heldout.json` + `error_cases.csv` + `KETQUA.md` mục 4–5 | Khớp |
| 29 | Bảng 5.8: 8 điều kiện (100,0; 100,0; 94,4 (81,9–98,5); 100,0; 100,0; 91,7 (78,2–97,1); 77,8 (66,9–85,8); 80,6 (65,0–90,2)); mean|diff| 0/57,8/23,0/9,4/6,4/10,8/16,8/66,9; che khuất precision 97,3 | `robustness.csv`: khớp từng ô và từng CI; CIs kiểm lại bằng công thức Wilson — đúng | Khớp |
| 30 | Trễ thị giác 3,41/4,12 ms (273 mẫu); chờ khung 41,05/79,06 ms (24,4 fps) | `metrics.json` timing_ms; `KETQUA.md` mục 6–7 | Khớp |
| 31 | Bảng 5.9: Vo&Le 1,8 s/vật; 100 % đỏ/vàng, 97,5 % xanh; Hoai "small error" | `notes/vo-2023-*.md` (dòng 19); `notes/hoai-*.md` (dòng 20) | Khớp |
| 32 | Bảng 5.9: Elassal "effective and accurate" | note ghi nguyên văn "proved the effectiveness and accuracy" | **Không nguyên văn** |
| 33 | Trích "`nhảy lên khoảng 10⁻¹⁰ mm`" (ch3) | `dong-hoc-delta.md` dòng 166: "nhảy lên **~**10⁻¹⁰ mm" | Gần khớp; "khoảng" thêm vào trong ngoặc kép |
| 34 | Bảng 6.1: các kết quả đối chiếu mục tiêu (1,583×10⁻¹³; 0,402; 0,689; 1,048; 0,96; 0,134 %; 0 %; 1,506; 97,33; 3,41 ms) | Trùng các bảng 5.1–5.6 đã kiểm; mục tiêu 0,96 s/1,46 s khớp `de-tai.md` dòng 43–45 | Khớp |

Con số **không tìm thấy nguồn trực tiếp**: 1 (tốc độ định mức ≥ 350 vòng/phút, mục 4.3 — xem lỗi #5 bảng lỗi). Con số truy được nguồn nhưng **không tái lập được từ dữ kiện nguồn**: 1 (2,8 kg đế — mục 4.2). Các phần còn lại của 4 chương đều truy được về file.

## 3. Kiểm tra mức báo cáo

- **Trích dẫn [1]–[8]**: thứ tự xuất hiện — [1], [2] (ch1), [3], [4] (2.2), [5], [6] (2.3), [7], [8] (2.4) — liên tục và đúng chuẩn IEEE. Ch3–6 chỉ dùng lại các số đã xuất hiện, không phá thứ tự. Không có mục trích mà không dùng, không có dùng mà không trích. `references.bib` khớp danh mục ở ch2.2.8; hai mục `[CẦN KIỂM CHỨNG]` (Clavel 1988 không có DOI; Hoai 2023 tên tác giả) đã được báo cáo ghi nhận đúng.
- **Bảng/hình**: đánh số liên tục (3.1–3.4, 4.1–4.10, 5.1–5.9, 6.1); mọi bảng/hình được nhắc trong văn bản đều tồn tại; 6 file hình được dẫn (`ban-do-sai-so-xy.png`, `do-nhay-sai-so-hinh-hoc.png`, `sai_so_va_dwell.png`, `quet_chu_ky.png`, `confusion_shape_test_999.png` + ma trận màu, `robustness-bar.png`) đều có trên đĩa. Hình 5.1 khớp mô tả z = −350 mm của `dong-hoc-delta.md` dòng 363.
- **Nhất quán ch4↔ch5↔ch6**: tổng sai số 0,612/0,897/0,957/1,048/1,123/1,391 dùng thống nhất ở cả 3 chương (trừ chỗ ch5 tuyên bố sai "không tái lập được"); chu kỳ 1,506 s thống nhất (Bảng 5.5 ghi 1,51 là làm tròn, có chú thích); overshoot 0,134 %/0 % và accuracy 97,33 % thống nhất. Hai điểm không nhất quán nhỏ: k_τ 2,22/2,23 và dư P95 0,26/0,25 (bảng lỗi).
- **Khẳng định vượt bằng chứng**: không phát hiện. Các câu nhạy cảm đều được giới hạn đúng: "đạt ≤ 1 mm" đặt trong điều kiện (a)(b) và cận trên 1,048 được nêu thẳng (ch4.4, ch6.1); "đạt trong mô phỏng" cho mục tiêu 2; mục tiêu 3 ghi rõ **Chưa đạt**; trễ Serial/servo đánh dấu dry-run/chưa đo ở cả 3 chương. Ghi chú biên tập cuối ch5 (xoá trước khi nộp) và các `[CẦN BỔ SUNG]` là đúng chỗ — trừ nhận định sai về "tách nhóm" và "làm tròn bỏ thị giác" nêu ở bảng lỗi.
- **Toán**: (3.5)–(3.6), biệt thức, Citardauq, đỉnh bậc 5, hai công thức quy đổi sai số, tổng RSS/tuyến tính — đều kiểm lại đúng, đơn vị hai vế nhất quán (Bảng 3.1 ghi mm² cho E,F,G; mm⁴ cho Δ — đúng chiều).

## 4. Ba câu hỏi hội đồng có thể hỏi

**Câu 1. "Báo cáo vừa nói 'đạt ≤ 1 mm' vừa nói cận trên giải tích 1,048 mm. Kết luận cuối cùng về chỉ tiêu sai số là gì?"**
Gợi ý trả lời: chỉ tiêu đạt theo ước lượng thống kê P95 (0,612 mm sau hiệu chuẩn, tách nhóm hệ thống/ngẫu nhiên) và theo tuyến tính trên cực đại mẫu Monte Carlo (0,957 mm); **không** đạt theo cận trên giải tích (1,048 mm với dung sai phân cấp, 1,391 mm với ±0,2 mm đồng đều). Kết luận có điều kiện: đế CNC ±0,05 mm, đồ gá cẳng tay, hiệu chuẩn gốc 0,03°, đàn hồi đai ≤ 0,10 mm — tất cả chưa đo. Mọi số đều ở Bảng 4.6/5.3.

**Câu 2. "Độ chính xác 97,33 % đo trên ảnh do nhóm tự sinh — vì sao xem đó là kết quả của mục tiêu 3, và sai lẫy ở đâu?"**
Gợi ý trả lời: không xem là đạt mục tiêu 3 — Bảng 6.1 ghi **Chưa đạt** (0 vật thật). 97,33 % (73/75) trên seed 999 chỉ là bằng chứng pipeline hoạt động; CI 95 % là 90,8–99,3 %; seed 777 đã dùng để chẩn đoán nên bị loại khỏi bằng chứng; che khuất chỉ đạt 77,8 %. Lộ trình vật thật ~0,42 triệu VNĐ đã có trong BOM mục 4.

**Câu 3. "Chu kỳ 1,506 s chỉ dư ngân sách 0,29 s mà cả trễ Serial (2 ms dry-run), pha dừng (0,25 s danh định) lẫn thời gian bám của stepper đều chưa đo. Rủi ro vượt 1,8 s cỡ nào?"**
Gợi ý trả lời: nếu theo thiết kế stepper vòng kín + đai GT2, sai lệch vị trí là sai số bám đã nằm trong ngân sách 0,612 mm, không cộng thêm trễ; cấu hình HIL servo 0,18–0,37 s chỉ dùng để đo trễ truyền thông (nếu tính theo HIL, tổng 1,69–1,88 s sẽ vượt ở đầu trên — báo cáo đã nêu). Việc đo bắt buộc: `do-tre-serial.py` n ≥ 500 (mean/P95/P99) và đo thời gian bám của stepper thật trước khi chốt chu kỳ.
