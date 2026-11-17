# Ket qua mo phong: Quy dao gap-tha bac 5 - PID vs PID+FF

**Run:** `2026-11-18-pid-quy-dao-bac5`  
**Ngay chay:** 2026-11-18  
**Seed:** 42  
**Python:** D:\Python312\python.exe  

## 1. Giai thieu mo phong

- Tham so hinh hoc: f=346 mm, e=115 mm, rf=200 mm, re=400 mm.
- Quy dao: da thuc bac 5, dung han tai cac diem moc (v=a=0).
- Cac diem moc (mm): Home (0,0,-350), Pick (100,-100,-400), Place (-100,100,-350), tro ve Home.
- Mo hinh khop: J=0.01 kg.m2, b=0.05 Nm.s/rad, tau_max=2 Nm, omega_max=10 rad/s.
- **Gia thiet quan trong:** Bo qua tuong tac cheo giua 3 khop; moi khop duoc dieu khien doc lap nhu he quan tinh-nhot. Day la gia thiet ly tuong hoa, can xem xet lai khi thiet ke dong luc hoc day du.
- Feed-forward = J*theta_ddot_ref + b*theta_dot_ref.
- Sai so bam duoc quy doi ve khong gian thao tac (mm) qua FK.

## 2. Cau hinh PID chinh

- Kp = 80.0, Ki = 5.0, Kd = 4.0
- Thoi gian moi doan T = 0.5 s; chu ky thuan = 1.500 s

## 3. Bang so sanh PID thuan va PID + Feed-forward

| Chi so | PID thuan | PID + Feed-forward |
| --- | --- | --- |
| Max sai so bam (mm) | 1.1581 | 0.0751 |
| RMSE sai so bam (mm) | 0.5046 | 0.0208 |
| Sai so xac lap tai Pick (mm) | 0.2912 | 0.3442 |
| Sai so xac lap tai Place (mm) | 0.5530 | 0.6522 |
| Overshoot Pick (%) | 4.3482 | 4.6752 |
| Overshoot Place (%) | 1.0103 | 1.0811 |
| Thoi gian xac lap Pick (s) | 0.4510 | 0.4550 |
| Thoi gian xac lap Place (s) | 0.9590 | 0.9640 |
| Mo-men cuc dai (Nm) | 0.4569 | 0.4389 |
| Van toc goc cuc dai (rad/s) | 4.6636 | 4.6402 |
| Vi pham tau_max | Khong | Khong |
| Vi pham omega_max | Khong | Khong |
| Chu ky thuan (s) | 1.5000 | 1.5000 |

## 4. Quet bo PID

Danh gia 3 bo PID thuan va 3 bo PID+FF voi tieu chi: overshoot <= 5% va sai so xac lap <= 1 mm.

| Bo PID | Kp | Ki | Kd | RMSE (mm) | Overshoot Pick (%) | Overshoot Place (%) | Dat tieu chi? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PID_bao_thu | 40.0 | 2.0 | 2.0 | 1.0052 | 3.97 | 0.86 | Co |
| PID+FF_bao_thu | 40.0 | 2.0 | 2.0 | 0.0248 | 4.67 | 1.08 | Co |
| PID_can_bang | 80.0 | 5.0 | 4.0 | 0.5046 | 4.35 | 1.01 | Co |
| PID+FF_can_bang | 80.0 | 5.0 | 4.0 | 0.0208 | 4.68 | 1.08 | Co |
| PID_nhanh | 160.0 | 10.0 | 8.0 | 0.2512 | 4.54 | 1.05 | Co |
| PID+FF_nhanh | 160.0 | 10.0 | 8.0 | 0.0190 | 4.68 | 1.08 | Co |

**Bo tot nhat:** PID+FF_nhanh voi Kp=160.0, Ki=10.0, Kd=8.0.

## 5. Chu ky nho nhat kha thi

- Tim kiem giam T_segment tu 2.0 s xuong 0.12 s.
- **T_segment nho nhat kha thi:** 0.2321 s
- **Chu ky thuan nho nhat:** 0.6962 s
- Tai chu ky nay: omega_max = 9.990 rad/s, tau_max = 1.636 Nm.
- Khong vi pham gioi han vat ly (omega_max, tau_max) tai chu ky nho nhat tim duoc.
- **Luu y:** tai chu ky cuc nhanh nay sai so xac lap tai Pick/Place len den ~2.7/5.3 mm, vuot nguong 1 mm, vi khong con thoi gian dung lai du. Day la gioi han do dong co/chuyen dong, chua phai dieu kien dat do chinh xac.

## 6. Nhan xet va di lech ky vong

- Chu ky mac dinh 1.50 s **dat** muc tieu <= 1.5 s.
- PID + FF giam RMSE sai so bam tu 0.505 mm xuong 0.021 mm so voi PID thuan, nho bu tru quan tinh/gia toc.
- Tat ca cau hinh deu khong vi pham tau_max (2.0 Nm) va omega_max (10.0 rad/s) o chu ky 1.50 s.
- Khi giam T, omega_max cham nguong ~10.0 rad/s truoc khi tau_max cham 2.0 Nm; do do **gioi han van toc goc** la rang buoc chinh can tro tang toc.
- Chu ky nho nhat tinh duoc 0.696 s la ly thuyet, dua tren J=0.01 kg.m2 gia dinh; tren phan cung thuc te J, ma sat va tai trong lon hon nen chu ky nho nhat thuc te se lon hon.
- **Khong co so do thuc nghiem trong run nay; moi so lieu deu tu mo phong.**
- Thoi gian kep tha vat, do tre camera/Serial va sai so hinh hoc chua duoc tinh den.
- Can kiem chung lai voi mo hinh dong luc hoc day du (co ma tran quan tinh, luc Coriolis, trong luc) khi co BOM chinh xac.

## 7. File ket qua

- `output/PID_thuan.csv` va `output/PID_plus_FF.csv`: du lieu tho thoi gian.
- `output/metrics.json`: cac chi so dinh luong tong hop (JSON).
- `figures/quy_dao_3d_va_xy.png`: quy dao 3D va hinh chieu xy.
- `figures/sai_so_bam_theo_thoi_gian.png`: sai so bam.
- `figures/mo_men_3_khop.png`: mo-men 3 khop.
- `figures/van_toc_goc_3_khop.png`: van toc goc 3 khop.
