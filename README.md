# So sánh Chỉ thị Thao tác Cũ - Mới (sosanhCTTT)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Một ứng dụng Python mạnh mẽ giúp tự động hóa việc so sánh các Chỉ thị Thao tác (CTTT) cũ và mới, hỗ trợ xuất báo cáo PDF và xử lý dữ liệu Excel chuyên nghiệp.

## 🚀 Tính năng nổi bật

- **So sánh trực quan**: Phát hiện sự khác biệt giữa hai phiên bản CTTT bằng thuật toán xử lý ảnh và dữ liệu Excel.
- **Giao diện hiện đại**: UI được xây dựng với `tkinter` nhưng được tinh chỉnh theo phong cách hiện đại, dễ sử dụng.
- **Xuất báo cáo PDF**: Tự động chuyển đổi các bảng so sánh sang định dạng PDF chuyên nghiệp.
- **Lấy thông tin tự động**: Tự động nhận diện phiên bản và ngày cập nhật từ file thực thi (`.exe`).
- **Ghi log ẩn**: Tính năng logging thông minh giúp điều tra lỗi mà không làm gián đoạn trải nghiệm người dùng.
- **Xử lý file an toàn**: Cơ chế sanitize tên file nghiêm ngặt, tránh lỗi ký tự đặc biệt trên Windows.

## 🛠️ Công nghệ sử dụng

- **Ngôn ngữ**: Python 3.8+
- **Giao diện**: Tkinter (Custom Modern UI)
- **Xử lý dữ liệu**: Openpyxl, Pandas (nếu có)
- **Xử lý hình ảnh**: OpenCV / Pillow (cho việc so sánh hình ảnh/screenshot)
- **Đóng gói**: PyInstaller

## 📂 Cấu trúc dự án

```text
├── core/               # logic so sánh chính
├── services/           # Các dịch vụ bổ trợ (PDF, Excel, Settings,...)
├── ui/                 # Giao diện người dùng (Windows, Styles, Translations)
├── assets/             # Hình ảnh, icon, hướng dẫn sử dụng
├── tests/              # Unit tests đảm bảo chất lượng
├── main.py             # Điểm entry của ứng dụng
└── utils.py            # Các hàm tiện ích dùng chung
```

## ⚙️ Cài đặt & Sử dụng

### Chạy từ mã nguồn
1. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```
2. Chạy ứng dụng:
   ```bash
   python main.py
   ```

### Đóng gói EXE
Sử dụng PyInstaller để đóng gói:
```bash
pyinstaller --noconfirm --onefile --windowed --name "SosanhCTTT_phienban7.04" main.py
```

## 📝 Nhật ký thay đổi (Changelog)

Xem chi tiết tại [CHANGELOG.md](CHANGELOG.md).

## 🤝 Liên hệ

- **Tác giả**: Bùi Đức Vinh
- **GitHub**: [Nakazasen](https://github.com/Nakazasen)

---
*Phát triển bởi đội ngũ đam mê tự động hóa.*
