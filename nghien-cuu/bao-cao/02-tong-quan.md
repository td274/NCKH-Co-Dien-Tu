# Chương 2. Tổng quan nghiên cứu

> Bản nháp do AI soạn từ `tong-quan.md` và `references.bib`. Số liệu lấy từ metadata và tóm tắt (abstract). Sinh viên phải đọc toàn văn trước khi nộp.

## 2.1 Phạm vi và cách tổ chức

Chương này tổng hợp tám công trình trong giai đoạn 1988–2024. Bảy công trình có mã định danh số (DOI) đã kiểm chứng qua Crossref. Công trình [1] là bài hội nghị năm 1988 và chưa có DOI, nên cần đối chiếu kỷ yếu gốc. Các công trình được xếp thành ba nhóm theo bài toán cốt lõi: động học và hiệu chuẩn, điều khiển bám quỹ đạo, và tích hợp thị giác chi phí thấp.

## 2.2 Động học, hiệu chuẩn và giải số động học

Robot Delta là cơ cấu song song ba bậc tự do tịnh tiến. Ba khớp quay chủ động đặt trên đế cố định. Cơ cấu hình bình hành giữ bàn công tác chỉ tịnh tiến theo x, y, z [1]. Bài toán nền tảng gồm hai chiều. Động học nghịch (inverse kinematics — IK) ánh xạ tọa độ điểm cuối sang góc khớp. Động học thuận (forward kinematics — FK) ánh xạ ngược lại. Với IK, mỗi nhánh đưa về phương trình lượng giác và có nghiệm giải tích tường minh [1]. Với FK, hệ phương trình phi tuyến có nhiều nghiệm và khó rút gọn [3].

Hiệu chuẩn động học xử lý sai số hình học do chế tạo và lắp ráp, như chiều dài khâu và vị trí khớp đế. Vischer và Clavel (1998) xây dựng mô hình hiệu chuẩn cho robot Delta thực [4]. Tóm tắt của công trình này không nêu sai số vị trí trước và sau hiệu chuẩn tính bằng mm. [CẦN BỔ SUNG: sai số điểm cuối trước và sau hiệu chuẩn (mm) từ toàn văn [4]].

Yang và Xiao (2024) giải FK bằng phương pháp số kết hợp ràng buộc nghiệm. Nhóm tác giả dùng mô phỏng Monte Carlo để ước lượng vùng làm việc trên MATLAB [3]. Công trình không công bố sai số định lượng giữa nghiệm FK và IK. Nghiệm FK cũng không được kiểm chứng vòng kín trên toàn vùng làm việc.

## 2.3 Điều khiển bám quỹ đạo

Hai công trình áp dụng điều khiển kháng nhiễu chủ động (active disturbance rejection control — ADRC) cho robot Delta tốc độ cao. Ý tưởng chung là coi bất định mô hình, ma sát và tương tác giữa các nhánh là một nhiễu tổng hợp [5], [6]. Bộ quan sát trạng thái mở rộng (extended state observer — ESO) ước lượng nhiễu này để bù theo thời gian thực [5], [6].

Castañeda, Luviano-Juárez và Chairez (2015) đề xuất ADRC thích nghi dựa trên đầu ra. Phương pháp không cần đo vận tốc khớp và dùng bình phương tối thiểu trung bình (least mean squares — LMS) để xấp xỉ phần bất định [5]. Tác giả đối chiếu với PID có bù tiến và ADRC không thích nghi. Kết quả được báo cáo là tốt hơn ở cả thực nghiệm và mô phỏng với quỹ đạo nhanh gấp 5 lần [5]. Tóm tắt không nêu sai số bám cụ thể.

Liu và cộng sự (2020) dùng ADRC tuyến tính (linear ADRC — LADRC) để giải ghép ba khớp khi bám quỹ đạo số 8 xoắn ốc trong không gian ba chiều. Công trình chỉ có mô phỏng, với nhiễu nội và ngoại [6]. Tóm tắt mô tả kết quả là "nhanh và chính xác" nhưng không có số liệu [6].

Kết quả định tính của [5] cho thấy PID có bù tiến kém hơn ADRC thích nghi khi quỹ đạo nhanh hơn. Công trình [6] đưa ra nhận xét tương tự cho bài toán ba khớp ghép. Tuy nhiên, cả hai không cung cấp baseline PID định lượng trên quỹ đạo gắp–thả. [CẦN BỔ SUNG: chỉ số sai số bám (mm) và độ vọt lố (%) của PID và PID + bù tiến từ toàn văn [5], [6]].

## 2.4 Tích hợp thị giác và robot Delta chi phí thấp

Nhóm này dùng kiến trúc phân tán giá thấp. Một máy tính nhúng xử lý ảnh, và một vi điều khiển Arduino điều khiển khớp.

Vo và Le (2023) chuyển ảnh từ không gian BGR sang HSV, rồi phân ngưỡng để nhận ba màu. Hệ thống dẫn động bằng ba servo DC và dùng Raspberry Pi 4 để xử lý ảnh [2]. Công trình báo cáo độ chính xác 100 % cho màu đỏ và vàng, 97,5 % cho màu xanh lá, và thời gian phân loại trung bình 1,8 s/vật [2]. Tóm tắt không nêu số mẫu thử và điều kiện chiếu sáng.

Elassal và cộng sự (2024) lọc dải màu và dùng contour để xác định bounding box của vật. Tính IK chạy trên Arduino, còn Raspberry Pi làm bộ điều phối [7]. Tác giả kết luận hệ thống "hiệu quả và chính xác", nhưng không có số liệu định lượng [7].

Hoai và cộng sự (2023) xác định đồng thời tọa độ 3D và kích thước vật để điều chỉnh độ mở tay kẹp. Hệ thống dùng động cơ bước, Arduino Uno và khung chế tạo bằng cắt laser và in 3D [8]. Bài báo báo cáo "sai số nhỏ" nhưng không nêu giá trị tính bằng mm [8]. [CẦN KIỂM CHỨNG: thứ tự và tên tác giả [8] trên trang bìa; Crossref ghi tên chưa khớp chuẩn tên Việt].

**Bảng 2.1.** So sánh rút gọn tám công trình theo chỉ tiêu liên quan đề tài.

| Công trình | Phương pháp chính | Phần cứng / mô phỏng | Chỉ tiêu định lượng (theo tóm tắt) | Điểm còn thiếu |
| --- | --- | --- | --- | --- |
| [2] Vo & Le, 2023 | Ngưỡng HSV, 3 màu | 3 servo DC, Arduino, Raspberry Pi 4 | 100 %; 97,5 %; 1,8 s/vật | Cỡ mẫu, điều kiện sáng, định nghĩa chu kỳ |
| [4] Vischer & Clavel, 1998 | Hiệu chuẩn sai số hình học | Robot Delta thực | Không nêu | Sai số điểm cuối (mm) |
| [3] Yang & Xiao, 2024 | FK số + Monte Carlo | Mô phỏng MATLAB | Không nêu | Sai số IK↔FK; thông số hình học |
| [5] Castañeda, 2015 | ADRC thích nghi đầu ra + LMS | Delta thực + mô phỏng 5× | Định tính: tốt hơn PID + bù tiến | Sai số bám (mm), vọt lố (%) |
| [6] Liu, 2020 | LADRC giải ghép 3 khớp | Chỉ mô phỏng | Định tính: "nhanh và chính xác" | Sai số bám; thông số quỹ đạo |
| [7] Elassal, 2024 | Lọc màu + contour; IK trên Arduino | Raspberry Pi, Arduino, giác hút | Định tính: "hiệu quả và chính xác" | Độ chính xác gắp (%), sai số (mm) |
| [8] Hoai, 2023 | Tọa độ 3D + kích thước vật | Động cơ bước, Arduino Uno | Định tính: "sai số nhỏ" | Sai số (mm), chu kỳ (s) |

## 2.5 Xu hướng nghiên cứu

Từ tám công trình, có thể rút ra bốn xu hướng sau. Các nhận định này là suy luận của người viết từ dữ liệu trên.

1. **Chuyển sang nguyên mẫu chi phí thấp.** Ba công trình thực nghiệm gần nhất [2], [7], [8] dùng in 3D, cắt laser, động cơ bước hoặc servo DC phổ thông. Các hệ thống này kết hợp Raspberry Pi xử lý ảnh với Arduino điều khiển khớp.
2. **Ưu tiên thị giác cổ điển cho phân loại đơn giản.** Với sản phẩm có màu và hình dạng rõ, các nhóm [2], [7] chọn ngưỡng HSV và contour thay vì học sâu. Cách này chạy được trên Raspberry Pi mà không cần GPU.
3. **Giải số và mô phỏng Monte Carlo cho động học thuận.** [3] dùng nghiệm số và quét đám mây điểm để trực quan hóa vùng làm việc.
4. **ADRC cho bám quỹ đạo tốc độ cao.** Khi tốc độ hoặc độ phức tạp của quỹ đạo tăng, các nhóm [5], [6] chuyển sang ESO để bù nhiễu thay cho PID cố định hệ số.

## 2.6 Mâu thuẫn giữa các nhóm

Có ba điểm chưa thống nhất giữa các công trình.

**Thứ nhất**, độ phức tạp điều khiển và mức đơn giản của hệ thống thực tế. [5], [6] cho rằng cần mô hình động lực học và ADRC để bám quỹ đạo chính xác. Ngược lại, [2], [7], [8] chỉ dùng IK và điều khiển vị trí mức cơ bản, và vẫn báo cáo hiệu quả. Hai nhóm khác chế độ vận hành. Nhóm điều khiển xét bám quỹ đạo liên tục tốc độ cao. Nhóm thực nghiệm xét gắp–thả điểm đến điểm với vật nhẹ. Nguyên nhân này là nhận định của người viết.

**Thứ hai**, lựa chọn động cơ dẫn động. [8] dùng động cơ bước, còn [2] dùng servo DC. Động cơ bước đơn giản vì điều khiển góc bằng xung, nhưng có nguy cơ trượt bước và giới hạn tốc độ (nhận định của người viết). Servo DC có phản hồi vị trí vòng kín [2]. Chưa có công trình nào so sánh hai lựa chọn này trên cùng một điều kiện.

**Thứ ba**, định nghĩa chu kỳ. Đề cương đặt mục tiêu chu kỳ chuyển động thuần không vượt 1,5 s. Mốc thực nghiệm [2] là 1,8 s/vật. Theo người viết, con số này có thể bao gồm xử lý ảnh, truyền thông nối tiếp và thời gian đóng mở cơ cấu chấp hành. Tóm tắt của [2] không định nghĩa rõ thời gian đo. [CẦN BỔ SUNG: phân rã thời gian 1,8 s/vật từ toàn văn [2]].

## 2.7 Khoảng trống nghiên cứu

Phân tích tám công trình cho bốn khoảng trống. Mỗi khoảng trống dẫn đến một phần của đề tài.

**Khoảng trống 1: thiếu kiểm chứng chéo định lượng IK↔FK.** [3] giải FK và vẽ vùng làm việc nhưng không báo cáo sai số. Chưa có công trình nào trong tám bài đối chiếu vòng kín IK–FK trên toàn vùng làm việc. Robot song song nhạy với kỳ dị và đa nghiệm. Nếu sai số công thức hoặc chọn nhầm nhánh không được kiểm tra, mọi khâu điều khiển phía sau đều chịu ảnh hưởng. Đề tài đáp ứng khoảng trống này bằng đóng góp 1: nghiệm IK giải tích được đối chiếu với FK Newton–Raphson trên lưới điểm dày.

**Khoảng trống 2: thiếu chỉ tiêu dung sai chế tạo gắn với sai số điểm cuối.** [4] mô tả hiệu chuẩn sai số hình học nhưng tóm tắt không nêu mm. Tóm tắt của [3] không nêu sai số chế tạo. Người viết nhận định rằng cần một khảo sát độ nhạy để biết sai lệch chiều dài khâu cỡ bao nhiêu thì vượt ngưỡng 1 mm. Đề tài đáp ứng bằng đóng góp 2, dựa trên sai lệch ±0,2 mm.

**Khoảng trống 3: thiếu baseline PID trên quỹ đạo gắp–thả.** [5], [6] so sánh với ADRC và không công bố số liệu PID theo chỉ tiêu thống nhất. [2], [7] bỏ qua đáp ứng quá độ. Đề tài đáp ứng bằng PID và PID + bù tiến trên quỹ đạo bậc 5, đo chu kỳ và độ vọt lố theo định nghĩa rõ ràng. Chỉ tiêu overshoot ≤ 5 % và chu kỳ ≤ 1,5 s thuộc mục tiêu 2.

**Khoảng trống 4: thiếu thống kê phân loại và pipeline tái lập.** [2] chỉ phân loại ba màu và không nêu cỡ mẫu hoặc ma trận nhầm lẫn. [7], [8] không có số liệu phần trăm chính xác. Các công trình mô phỏng [3], [6] tách rời phần cứng thử nghiệm. Chưa có công trình nào nối liền tọa độ từ OpenCV, quỹ đạo, IK và điều khiển khớp trong cùng một bộ chỉ tiêu. Đề tài đáp ứng bằng mục tiêu 3 (≥ 120 vật, có ma trận nhầm lẫn) và đóng góp 3 (pipeline tái lập).

Bốn khoảng trống trên định hướng ba đóng góp của đề tài trong Chương 1. Đề tài không nhằm vượt trội về điều khiển nâng cao. Mục tiêu là làm cho từng bước của chuỗi gắp–phân loại có số đo kiểm chứng được.

## 2.8 Tài liệu tham khảo

Danh mục dưới đây đánh số theo thứ tự xuất hiện trong báo cáo, theo chuẩn IEEE. Các mục khớp với `references.bib`.

[1] R. Clavel, "Delta, a fast robot with parallel geometry," in *Proc. 18th Int. Symp. Industrial Robots*, 1988, pp. 91–100. [CẦN KIỂM CHỨNG: chưa có DOI trên Crossref; đối chiếu kỷ yếu gốc.]

[2] D. C. Vo and H. P. Le, "Design and development of a delta robot system to classify objects using image processing," *Int. J. Electr. Comput. Eng. (IJECE)*, vol. 13, no. 3, pp. 2669–2676, 2023, doi: 10.11591/ijece.v13i3.pp2669-2676.

[3] H. Yang and B. Xiao, "Kinematics analysis of Delta parallel robot based on numerical solutions method," in *Proc. Int. Conf. Artificial Intelligence and Digital Technology (ICAIDT)*, 2024, pp. 294–297, doi: 10.1109/ICAIDT62617.2024.00070.

[4] P. Vischer and R. Clavel, "Kinematic calibration of the parallel Delta robot," *Robotica*, vol. 16, no. 2, pp. 207–218, 1998, doi: 10.1017/S0263574798000538.

[5] L. A. Castañeda, A. Luviano-Juárez, and I. Chairez, "Robust trajectory tracking of a Delta robot through adaptive active disturbance rejection control," *IEEE Trans. Control Syst. Technol.*, vol. 23, no. 4, pp. 1387–1398, 2015, doi: 10.1109/TCST.2014.2367313.

[6] C. Liu, Y. Cheng, D. Liu, G. Cao, and I. Lee, "Research on a LADRC strategy for trajectory tracking control of Delta high-speed parallel robots," *Math. Problems Eng.*, vol. 2020, Art. no. 9681530, 2020, doi: 10.1155/2020/9681530.

[7] A. Elassal, M. Abdelaal, M. Osama, and H. Elhnidy, "Low-cost parallel delta robot for a pick-and-place application with the support of the vision system," *e-Prime – Adv. Electr. Eng., Electron. Energy*, vol. 8, Art. no. 100518, 2024, doi: 10.1016/j.prime.2024.100518.

[8] P. Hoai, V. Cong, and T. Hiep, "Design a low-cost delta robot arm for pick and place applications based on computer vision," *FME Transactions*, vol. 51, no. 1, pp. 99–108, 2023, doi: 10.5937/fme2301099p. [CẦN KIỂM CHỨNG: thứ tự và tên tác giả theo Crossref chưa khớp tên Việt; đối chiếu trang bìa.]
