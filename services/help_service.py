"""
Help Service - Hướng dẫn sử dụng và thông tin ứng dụng
"""

import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText


USER_GUIDE_BASIC = """CÁCH DÙNG NHANH:
1) Chọn loại màn hình (PC/VPS/Monitor).
2) Chọn file CTTT mới, sau đó chọn file CTTT cũ (số lượng và thứ tự phải khớp).
3) (Tuỳ chọn) Nhập thư mục kết quả nếu không muốn lưu ở cùng thư mục file.
4) Chọn phương pháp: PDF (chuẩn hơn, nhưng chậm hơn) hoặc Cut/Paste (nhanh).
5) Nếu dùng PDF: chỉnh DPI (50-300, mặc định 100). DPI cao = chất lượng tốt nhưng chậm.
6) Chỉnh màu highlight và các thông số: 'Độ dày vùng tô' (1-9) và 'Số lần nở' (1-3).
7) Nhấn nút: 'So sánh và tạo báo cáo'.

LƯU Ý QUAN TRỌNG:
- Đóng tất cả Excel trước khi chạy để tránh xung đột.
- File kết quả mặc định sẽ lưu cùng thư mục với file CTTT mới, tên: TongHopKetQua.xlsx
- Kiểm tra sheet: chỉ các sheet có tab màu XANH mới được xử lý.
- Mẹo: bắt đầu với độ dày = 1, nở = 1; tăng dần nếu cần mở rộng vùng highlight."""


USER_GUIDE_DETAILED = """HƯỚNG DẪN CHI TIẾT - SỬ DỤNG CÔNG CỤ SO SÁNH CTTT

═══════════════════════════════════════════════════════════
BƯỚC 1: CHUẨN BỊ
═══════════════════════════════════════════════════════════
• Đóng tất cả file Excel đang mở để tránh xung đột
• Đảm bảo các file CTTT có định dạng .xlsx, .xls hoặc .xlsm
• Sheet cần so sánh phải có tab màu XANH LÁ (mã màu: 5296274)

═══════════════════════════════════════════════════════════
BƯỚC 2: CHỌN FILE
═══════════════════════════════════════════════════════════
• Nhấn "Chọn file mới" để chọn các file CTTT mới (phiên bản mới)
• Nhấn "Chọn file cũ" để chọn các file CTTT cũ (phiên bản gốc)
• Số lượng file mới và cũ phải bằng nhau
• Thứ tự các file phải tương ứng (file mới 1 so với file cũ 1, ...)

═══════════════════════════════════════════════════════════
BƯỚC 3: CẤU HÌNH
═══════════════════════════════════════════════════════════
• Phương pháp PDF: Chính xác hơn, xuất PDF của cả 2 file rồi so sánh
• DPI: Độ phân giải (50-300). 100 là cân bằng giữa tốc độ và chất lượng
• Ngưỡng phát hiện: Càng thấp càng nhạy, phát hiện nhiều khác biệt hơn
• Độ dày vùng tô (1-9): Thay đổi kích thước vùng highlight
• Số lần nở (1-3): Mở rộng vùng highlight

═══════════════════════════════════════════════════════════
BƯỚC 4: SO SÁNH
═══════════════════════════════════════════════════════════
• Nhấn nút "So sánh" để bắt đầu quá trình
• Quá trình có thể mất vài phút tùy số lượng file và cài đặt DPI
• Kết quả sẽ được lưu vào thư mục kết quả đã chọn

═══════════════════════════════════════════════════════════
BƯỚC 5: XEM KẾT QUẢ
═══════════════════════════════════════════════════════════
• File TongHopKetQua.xlsx chứa bảng tổng hợp kết quả
• Các file comparison_*.pdf/png chứa ảnh so sánh chi tiết
• Cột "Trạng thái": OK = giống nhau, FAIL = có khác biệt
• Click vào link trong cột "Link Ảnh Sai Khác" để xem chi tiết

═══════════════════════════════════════════════════════════
XỬ LÝ LỖI THƯỜNG GẶP
═══════════════════════════════════════════════════════════
❌ "Không tìm thấy sheet màu xanh"
   → Kiểm tra sheet có tab màu xanh lá không (không phải màu khác)

❌ "Không xuất được PDF"
   → Đóng tất cả Excel đang mở
   → Kiểm tra file không bị khóa (readonly)
   → Thử chạy lại ứng dụng với quyền Administrator

❌ "Số lượng file không khớp"
   → Đảm bảo số file mới = số file cũ

❌ "Lỗi kết nối Excel"
   → Đóng tất cả Excel
   → Mở Task Manager, đóng các process EXCEL.EXE còn sót
   → Khởi động lại ứng dụng"""


ABOUT_TEXT = """SO SÁNH CTTT - Refactored Version

Phiên bản: 7.03 Refactored
Ngày cập nhật: 12/2024

Ứng dụng so sánh sai khác giữa các Chỉ thị thao tác (CTTT) mới và cũ.

Tính năng chính:
• So sánh bằng phương pháp PDF (chính xác cao)
• Highlight các vùng khác biệt với màu sắc tùy chỉnh
• Xuất báo cáo Excel với link đến ảnh so sánh
• Hỗ trợ so sánh nhiều cặp file cùng lúc
• Tự động lưu cài đặt người dùng

Yêu cầu hệ thống:
• Windows 10/11
• Microsoft Excel 2016 trở lên
• Python 3.8+ (nếu chạy từ source)

Thư viện cần thiết:
• PyMuPDF (pymupdf) - Render PDF
• PyPDF2 - Gộp PDF
• openpyxl - Tạo báo cáo Excel
• Pillow - Xử lý ảnh"""


class HelpService:
    """Service hiển thị hướng dẫn và thông tin ứng dụng."""
    
    @staticmethod
    def show_user_guide(parent=None, detailed=False):
        """
        Hiển thị hướng dẫn sử dụng.
        
        Args:
            parent: Parent window (tkinter)
            detailed: Nếu True, hiển thị hướng dẫn chi tiết
        """
        text = USER_GUIDE_DETAILED if detailed else USER_GUIDE_BASIC
        title = "Hướng dẫn chi tiết" if detailed else "Hướng dẫn sử dụng cơ bản"
        
        if parent:
            try:
                win = tk.Toplevel(parent)
                win.title(title)
                win.geometry("700x500" if detailed else "600x380")
                
                st = ScrolledText(win, wrap='word', font=("Consolas", 10))
                st.insert('1.0', text)
                st.configure(state='disabled')
                st.pack(fill='both', expand=True, padx=8, pady=8)
                
                tk.Button(win, text="Đóng", command=win.destroy, width=10).pack(pady=8)
                
                # Center window
                win.update_idletasks()
                win.lift()
                win.focus_set()
                
            except Exception:
                messagebox.showinfo(title, text)
        else:
            print(text)
    
    @staticmethod
    def show_about(parent=None):
        """Hiển thị thông tin ứng dụng."""
        if parent:
            try:
                win = tk.Toplevel(parent)
                win.title("Về ứng dụng")
                win.geometry("450x400")
                win.resizable(False, False)
                
                st = ScrolledText(win, wrap='word', font=("Arial", 10))
                st.insert('1.0', ABOUT_TEXT)
                st.configure(state='disabled')
                st.pack(fill='both', expand=True, padx=10, pady=10)
                
                tk.Button(win, text="Đóng", command=win.destroy, width=10).pack(pady=8)
                
            except Exception:
                messagebox.showinfo("Về ứng dụng", ABOUT_TEXT)
        else:
            print(ABOUT_TEXT)
    
    @staticmethod
    def show_shortcut_help(parent=None):
        """Hiển thị các phím tắt."""
        shortcuts = """PHÍM TẮT:

Ctrl+O      Mở file mới
Ctrl+Shift+O    Mở file cũ
Ctrl+R      Chọn thư mục kết quả
Ctrl+Enter  Bắt đầu so sánh
Ctrl+S      Lưu cài đặt
F1          Mở hướng dẫn
F5          Làm mới danh sách file
Escape      Hủy thao tác đang chạy"""
        
        if parent:
            messagebox.showinfo("Phím tắt", shortcuts)
        else:
            print(shortcuts)
    
    @staticmethod
    def show_library_status(parent=None):
        """Hiển thị trạng thái các thư viện."""
        from services.report_service import LibraryValidator
        
        results = LibraryValidator.check_all()
        
        lines = ["TRẠNG THÁI THƯ VIỆN\n"]
        lines.append("=" * 40)
        lines.append("\nBẮT BUỘC:")
        
        for lib, info in results['required'].items():
            status = "✅" if info['available'] else "❌"
            lines.append(f"  {status} {lib}: {info['description']}")
        
        lines.append("\nTÙY CHỌN:")
        for lib, info in results['optional'].items():
            status = "✅" if info['available'] else "⚠️"
            lines.append(f"  {status} {lib}: {info['description']}")
        
        lines.append("\n" + "=" * 40)
        msg, ok = LibraryValidator.get_status_message()
        lines.append(msg)
        
        if results['missing_optional']:
            lines.append("\nCài đặt thư viện thiếu:")
            lines.append("pip install " + " ".join(results['missing_optional']))
        
        text = "\n".join(lines)
        
        if parent:
            try:
                win = tk.Toplevel(parent)
                win.title("Trạng thái thư viện")
                win.geometry("500x350")
                
                st = ScrolledText(win, wrap='word', font=("Consolas", 10))
                st.insert('1.0', text)
                st.configure(state='disabled')
                st.pack(fill='both', expand=True, padx=8, pady=8)
                
                tk.Button(win, text="Đóng", command=win.destroy, width=10).pack(pady=8)
                
            except Exception:
                messagebox.showinfo("Trạng thái thư viện", text)
        else:
            print(text)
