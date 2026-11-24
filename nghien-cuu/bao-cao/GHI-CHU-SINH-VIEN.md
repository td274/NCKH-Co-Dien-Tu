# Ghi chú cho sinh viên

*Phần này nằm ngoài thân báo cáo. Xoá trước khi nộp.*

Trước khi nộp, kiểm chứng các mục sau:

1. **Trang bìa và tóm tắt.** Điền tên khoa, họ tên, MSSV, lớp, giảng viên hướng dẫn. Đọc lại tóm tắt: phải nêu rõ mục tiêu 3 chưa đạt.
2. **Khối lượng đế (Bảng 4.2).** 6,2 kg kiểm được từ tấm 480 × 480 × 10 mm nhôm (2700 kg/m³). Con số 2,5–3 kg sau phay là **ước lượng**, cần cân thực tế sau gia công.
3. **Hệ số k_τ.** Đã thống nhất **2,23** (theo τ_yc = 1,136 N·m) ở cả Bảng 4.5 và Bảng 5.5.
4. **Dư ngân sách P95.** Đã thống nhất **0,26 s** (1,8 − 1,545 = 0,255, làm tròn lên).
5. **Bảng 4.7.** Có thể bổ sung hai lệnh phụ `P` và `S` nếu đề cập đến `config.h`. Hiện chưa thêm.
6. **Bảng 3.3.** Chưa ghi bộ lọc vi phân $\tau_d = 0{,}005$ s có trong `config.json`. Nên thêm một dòng.
7. **Hình 4.1.** Nội dung `ban-ve-so-do.svg` chưa được đối chiếu trong quá trình gộp. Mở file bằng trình duyệt, kiểm tra các kích thước khớp Bảng 4.1 và Bảng 4.3. Nếu SVG không hiển thị, xem hướng dẫn ngay dưới hình.
8. **Chạy lại lệnh tái lập.** Các lệnh trong Phụ lục B cần chạy thử để khẳng định số trong Bảng 5.4–5.5 và Bảng 5.8. Nếu lệnh khác với ghi chú, cập nhật Phụ lục B.
9. **Tham chiếu Hình/Bảng.** Hình 4.1 được dẫn trong mục 4.8. Hình 5.1–5.6 giữ nguyên số. Bảng và hình có dãy số riêng, nên không cần đổi số hình chương 5.
10. **Kiểm chứng tài liệu.** [1] (Clavel 1988) chưa có DOI; [8] cần đối chiếu tên tác giả với trang bìa. Mọi mục trong danh mục phải khớp `references.bib` và đúng IEEE. Không thêm tài liệu ngoài danh mục.
11. **Nhãn nguồn `[CẦN KIỂM CHỨNG]`** trong BOM (mô-men giữ, độ cứng đai, khe hở khớp cầu, cấp ổ bi, quán tính rotor) phải được xác nhận bằng datasheet trước khi viết "đạt" cho chỉ tiêu liên quan.
12. **Kết luận ≤ 1 mm.** Chỉ viết "đạt theo thống kê P95" hoặc "đạt có điều kiện". Không viết "đảm bảo ≤ 1 mm" vì cận trên giải tích là 1,048 mm.
13. **Trích dẫn nguyên văn.** Mục 5.6 (Elassal) đã dùng nguyên văn "proved the effectiveness and accuracy". Kiểm lại mọi cụm trong ngoặc kép với note nguồn.
14. **Các blockquote "Bản nháp"** đầu chương 1–4 là lời nhắc của AI. Xoá trước khi nộp.
15. **Đọc lại toàn văn** [2], [5], [6], [4] để điền các mục [CẦN BỔ SUNG] ở chương 2 (Phụ lục C, mục 3–5). Không suy ra số liệu từ tóm tắt.
