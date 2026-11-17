---
name: Trích dẫn IEEE
description: Kiểm chứng và định dạng tài liệu tham khảo theo IEEE, quản lý references.bib, tránh citation ảo
---

# Trích dẫn IEEE và chống citation ảo

## 1. Kiểm chứng trước khi ghi

Không bao giờ đưa một tài liệu vào `references.bib` chỉ vì "nghe hợp lý". Quy trình:

1. Nếu đã có DOI, kiểm tra bằng Crossref:

```
https://api.crossref.org/works/<DOI>
```

2. Nếu chỉ có tên bài, tìm bằng:

```
https://api.crossref.org/works?query.bibliographic=<tên bài>&rows=5
```

3. Đối chiếu 4 trường: **tên bài, tác giả đầu, năm, tạp chí/hội nghị**. Lệch một trường
   là phải kiểm tra lại.
4. Không tìm thấy DOI: ghi URL + ngày truy cập. Vẫn không chắc tài liệu tồn tại → ghi
   `[CẦN KIỂM CHỨNG]` và nói rõ với người dùng.

Dấu hiệu citation ảo: DOI không resolve, tạp chí không tồn tại, số trang vô lý, tác giả
không có công trình nào khác, tiêu đề quá chung chung.

## 2. Định dạng BibTeX

```bibtex
@article{Nguyen2024PID,
  author  = {Nguyen, Van A. and Tran, Thi B.},
  title   = {Tên bài báo tiếng Anh},
  journal = {Tên tạp chí},
  year    = {2024},
  volume  = {12},
  number  = {3},
  pages   = {45--58},
  doi     = {10.xxxx/xxxxx},
}

@inproceedings{Tran2023Robot,
  author    = {Tran, Van C.},
  title     = {Tên báo cáo hội nghị},
  booktitle = {Proceedings of ...},
  year      = {2023},
  pages     = {1--6},
  doi       = {10.xxxx/xxxxx},
}
```

Khoá trích dẫn: `TacGiaNamTuKhoa`, không dấu, không khoảng trắng (ví dụ `Bui2025Arm`).

## 3. Định dạng IEEE trong báo cáo

- Bài báo: `[1] A. V. Nguyen and T. B. Tran, "Title of paper," Journal Name, vol. 12, no. 3, pp. 45–58, 2024, doi: 10.xxxx/xxxxx.`
- Hội nghị: `[2] V. C. Tran, "Title," in Proc. Conf. Name, City, Country, 2023, pp. 1–6.`
- Sách: `[3] R. C. Dorf and R. H. Bishop, Modern Control Systems, 13th ed. Pearson, 2017.`
- Web: `[4] Author/Org, "Title," Year. [Online]. Available: URL. [Accessed: 17-Nov-2026].`

Đánh số theo thứ tự xuất hiện trong văn bản. Mỗi mục trong danh mục phải được trích ít
nhất một lần; mỗi trích dẫn trong văn bản phải có trong danh mục.

## 4. Với tài liệu tiếng Việt

Tạp chí trong nước: ghi rõ tên tạp chí, số, trang, năm; nếu có DOI/URL thì thêm.
Luận văn/luận án: ghi bậc, trường, năm. Không dùng tài liệu không truy nguyên được nguồn.
