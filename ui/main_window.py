import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from core.comparator import Comparator
import config
from services.settings_service import SettingsService
from ui.modern_style import Colors, Fonts, Spacing, configure_styles, create_card_frame
from ui.translations import get_text, LANGUAGES, get_available_languages
import threading
import os

class ToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title(config.APP_TITLE)
        
        # Settings Service
        self.settings_service = SettingsService()
        self.settings = self.settings_service.settings

        # Variables
        self.setup_variables()
        
        # UI Setup
        self.create_widgets()
        
        # Logic
        self.comparator = Comparator()

    def setup_variables(self):
        self.new_dir_path = tk.StringVar()
        self.new_files_display = tk.StringVar()
        self.old_dir_path = tk.StringVar()
        self.old_files_display = tk.StringVar()
        self.result_path = tk.StringVar()
        self.is_processing = False
        
        # Settings Variables
        self.zoom_var = tk.IntVar(value=self.settings.get("zoom_level", config.DEFAULT_ZOOM))
        self.goto_address = tk.StringVar(value=self.settings.get("goto_address", config.DEFAULT_GOTO_ADDRESS))
        self.auto_add_b = tk.BooleanVar(value=self.settings.get("auto_add_b", False))
        self.suppress_error_popups = tk.BooleanVar(value=self.settings.get("suppress_error", True))
        self.save_user_settings = tk.BooleanVar(value=self.settings.get("save_settings", True))
        self.use_pdf_method = tk.BooleanVar(value=self.settings.get("use_pdf_method", True))
        self.pdf_render_dpi = tk.IntVar(value=self.settings.get("pdf_dpi", config.DEFAULT_DPI))
        
        # Highlight Colors (Critical - missing from original refactor)
        self.highlight_base_color = self.settings.get("highlight_base_color", config.HIGHLIGHT_BASE_COLOR)
        self.highlight_outline_color = self.settings.get("highlight_outline_color", config.HIGHLIGHT_OUTLINE_COLOR)
        self.highlight_fill_color = self.settings.get("highlight_fill_color", config.HIGHLIGHT_FILL_COLOR)
        
        # Highlight Settings (Critical - missing from original refactor)
        self.highlight_fill_opacity = tk.IntVar(value=self.settings.get("highlight_fill_opacity", config.DEFAULT_FILL_OPACITY))
        self.pdf_diff_threshold = tk.IntVar(value=self.settings.get("pdf_diff_threshold", config.DEFAULT_DIFF_THRESHOLD))
        self.pdf_dilate_size = tk.IntVar(value=self.settings.get("pdf_dilate_size", config.DEFAULT_DILATE_SIZE))
        self.pdf_dilate_iterations = tk.IntVar(value=self.settings.get("pdf_dilate_iterations", config.DEFAULT_DILATE_ITERATIONS))
        
        # Screen Mode (Critical - missing from original refactor)
        self.screen_mode = tk.StringVar(value=self.settings.get("screen_mode", "pc"))
        
        # Progress Bar references
        self.progress_bar = None
        self.progress_label = None
        
        # Drag-drop data for file ordering dialog
        self.drag_data = {}
        
        # Legacy compatibility aliases
        self.bg_color = self.highlight_base_color
        self.outline_color = self.highlight_outline_color
        
        # Lists
        self.new_files = []
        self.old_files = []
        
        # Language Settings
        self.current_lang = self.settings.get("language", "vi")
        
        # Widget references for language updates
        self.translatable_widgets = {}

    def create_widgets(self):
        # Resize Window
        self.master.geometry("1200x650")
        
        # ========== MENU BAR ==========
        self.create_menu_bar()
        
        # ========== KEYBOARD SHORTCUTS ==========
        self.bind_shortcuts()

        # Scrollable Layout
        self.canvas = tk.Canvas(self.master)
        self.scrollbar = tk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(5,0), pady=5)
        self.scrollbar.pack(side="right", fill="y", padx=(0,5), pady=5)

        parent = self.scrollable_frame
        
        # Grid Configuration
        for i in [1, 3]: parent.grid_columnconfigure(i, weight=1)
        
        row = 0
        
        # HEADER
        lbl_header = tk.Label(parent, text=get_text("header_warning", self.current_lang), fg="red", font=("Arial", 16, "bold"))
        lbl_header.grid(row=row, column=0, columnspan=5, pady=(5, 3), sticky="ew")
        self.translatable_widgets["header_warning"] = lbl_header
        row += 1
        
        btn_help = tk.Button(parent, text=get_text("btn_help", self.current_lang), command=self.show_help)
        btn_help.grid(row=row, column=0, columnspan=5, pady=3, sticky="ew")
        self.translatable_widgets["btn_help"] = btn_help
        row += 1
        
        # LANGUAGE SELECTOR
        lang_frame = tk.Frame(parent, bg="#e3f2fd", relief="ridge", bd=1)
        lang_frame.grid(row=row, column=0, columnspan=5, sticky="ew", padx=5, pady=5)
        
        tk.Label(lang_frame, text="🌐", font=("Arial", 14), bg="#e3f2fd").pack(side="left", padx=(10, 5))
        lbl_lang = tk.Label(lang_frame, text=get_text("language_label", self.current_lang), bg="#e3f2fd", font=("Arial", 10, "bold"))
        lbl_lang.pack(side="left", padx=5)
        self.translatable_widgets["language_label"] = lbl_lang
        
        self.lang_combo = ttk.Combobox(lang_frame, values=list(LANGUAGES.values()), state="readonly", width=15)
        # Set current language in combo
        lang_codes = list(LANGUAGES.keys())
        lang_names = list(LANGUAGES.values())
        if self.current_lang in lang_codes:
            self.lang_combo.current(lang_codes.index(self.current_lang))
        else:
            self.lang_combo.current(0)
        self.lang_combo.pack(side="left", padx=5, pady=5)
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        row += 1

        # Screen Selection
        tk.Label(parent, text="Chọn loại màn hình sử dụng:").grid(row=row, column=0, sticky="w", padx=5)
        self.screen_combo = ttk.Combobox(parent, values=["Phiên bản dùng cho màn hình máy tính", "VPS", "Màn hình phụ"], state="readonly", width=30)
        self.screen_combo.current(0)
        self.screen_combo.grid(row=row, column=1, columnspan=2, sticky="ew", padx=5)
        self.screen_combo.bind("<<ComboboxSelected>>", self.on_screen_mode_change)  # Critical - was missing
        row += 1

        # 1.1 NEW FILES
        tk.Label(parent, text="1.1. Chọn các file chỉ thị thao tác mới:").grid(row=row, column=0, sticky="w", padx=5, columnspan=5)
        row += 1
        
        tk.Label(parent, text="Dán đường dẫn thư mục:").grid(row=row, column=0, sticky="e", padx=5)
        tk.Entry(parent, textvariable=self.new_dir_path, width=35).grid(row=row, column=1, sticky="ew", padx=2)
        
        tk.Label(parent, text="Các file đã chọn:").grid(row=row, column=2, sticky="e", padx=5)
        tk.Entry(parent, textvariable=self.new_files_display, width=35).grid(row=row, column=3, sticky="ew", padx=2)
        
        tk.Button(parent, text="Mở CTTT mới", command=self.select_new_files, width=16).grid(row=row, column=4, pady=3, padx=5, sticky="ew")
        row += 1

        # 1.2 OLD FILES
        tk.Label(parent, text="1.2. Chọn các File chỉ thị thao tác cũ:").grid(row=row, column=0, sticky="w", padx=5, columnspan=5)
        row += 1
        
        tk.Label(parent, text="Dán đường dẫn thư mục:").grid(row=row, column=0, sticky="e", padx=5)
        tk.Entry(parent, textvariable=self.old_dir_path, width=35).grid(row=row, column=1, sticky="ew", padx=2)
        
        tk.Label(parent, text="Các file đã chọn:").grid(row=row, column=2, sticky="e", padx=5)
        tk.Entry(parent, textvariable=self.old_files_display, width=35).grid(row=row, column=3, sticky="ew", padx=2)
        
        tk.Button(parent, text="Mở CTTT cũ", command=self.select_old_files, width=16).grid(row=row, column=4, pady=5, padx=5, sticky="ew")
        row += 1

        # RESULT PATH
        tk.Label(parent, text="Đường dẫn lưu file kết quả (để trống nếu muốn lưu cùng thư mục với CTTT mới):").grid(row=row, column=0, columnspan=2, sticky="w", padx=5)
        row += 1
        tk.Entry(parent, textvariable=self.result_path, width=50).grid(row=row, column=0, columnspan=4, sticky="ew", padx=5)
        tk.Button(parent, text="Duyệt...", command=self.browse_result_folder, width=12).grid(row=row, column=4, pady=5, padx=5, sticky="w")
        row += 1

        # CHECK ORDER BTN
        tk.Button(parent, text="Kiểm tra trình tự lựa chọn các cặp CTTT", command=self.check_order).grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")
        row += 1

        # MASTER RUN BTN
        self.btn_run = tk.Button(parent, text="2. BẮT ĐẦU SO SÁNH (PHƯƠNG PHÁP MỚI)", 
                               command=self.run_comparison, height=2, 
                               bg="#1D4ED8", fg="#FFFFFF", font=("Arial", 12, "bold"))
        self.btn_run.grid(row=row, column=0, columnspan=5, pady=5, padx=5, sticky="ew")
        row += 1

        # LEGACY SCREENSHOT BTN (NEW)
        legacy_frame = tk.Frame(parent, bg="#fff8dc", relief="groove", bd=2)
        legacy_frame.grid(row=row, column=0, columnspan=5, pady=5, padx=5, sticky="ew")
        
        self.btn_legacy = tk.Button(legacy_frame, 
            text="🖼️ Phương pháp chụp ảnh màn hình của phiên bản 6 (Chụp màn hình trực tiếp - giống phiên bản cũ)", 
            command=self.run_legacy_comparison, 
            height=2, bg="#ffd700", fg="black",
            font=("Arial", 12, "bold"))
        self.btn_legacy.pack(fill="x", padx=5, pady=5)
        
        tk.Label(legacy_frame, 
            text="⚠️ Lưu ý: Phương pháp này sẽ mở Excel hiện hữu trên màn hình và chụp ảnh trực tiếp.\n"
                 "Không sử dụng máy tính trong quá trình chạy. Đảm bảo đã đóng tất cả Excel.",
            bg="#fff8dc", fg="#8B4513", font=("Arial", 8)).pack(anchor="w", padx=5, pady=(0,5))
        row += 1

        # 3. SETTINGS: Zoom
        tk.Label(parent, text="3. Cài đặt mức độ phóng to tỷ lệ màn hình của file Excel:").grid(row=row, column=0, columnspan=2, sticky="w", padx=5)
        row += 1
        tk.Entry(parent, textvariable=self.zoom_var).grid(row=row, column=0, columnspan=5, sticky="ew", padx=5)

        row += 1
        
        # 4. Settings: Goto
        tk.Label(parent, text="4. Nhập ô địa chỉ mà con trỏ nhảy đến (Gợi ý: dùng A1):").grid(row=row, column=0, columnspan=2, sticky="w", padx=5)
        row += 1
        tk.Entry(parent, textvariable=self.goto_address).grid(row=row, column=0, columnspan=5, sticky="ew", padx=5)
        row += 1

        # AUTO ADD B (Yellow Highlight)
        hl_frame = tk.Frame(parent, bg="#fff3cd", relief="ridge", bd=2)
        hl_frame.grid(row=row, column=0, columnspan=5, sticky="ew", padx=5, pady=5)
        
        cb_auto_b = tk.Checkbutton(hl_frame, text="⚠️ Tự động điền b để phát cho barcode/ để so sánh CTTT cũ - mới không cần thêm b thủ công", variable=self.auto_add_b, bg="#fff3cd", font=("Arial", 9, "bold"))
        cb_auto_b.pack(anchor="w", padx=10, pady=5)
        ToolTip(cb_auto_b, "Tự động thêm tiền tố 'b' vào tên sheet để khớp các file barcode.")
        row += 1

        # SUPPRESS ERROR
        suppress_frame = tk.Frame(parent, bg="#f0f0f0", relief="ridge", bd=1)
        suppress_frame.grid(row=row, column=0, columnspan=5, sticky="ew", padx=5, pady=3)
        cb_suppress = tk.Checkbutton(suppress_frame, text="🔇 Ẩn thông báo lỗi kết nối Excel (khuyến nghị bật để chạy mượt mà)", variable=self.suppress_error_popups, bg="#f0f0f0")
        cb_suppress.pack(anchor="w", padx=10, pady=3)
        row += 1

        # SAVE SETTINGS
        save_frame = tk.Frame(parent, bg="#e8f5e9", relief="ridge", bd=1)
        save_frame.grid(row=row, column=0, columnspan=5, sticky="ew", padx=5, pady=3)
        cb_save = tk.Checkbutton(save_frame, text="💾 Lưu cài đặt của tôi để dùng lại lần sau", variable=self.save_user_settings, bg="#e8f5e9", font=("Arial", 9, "bold"))
        cb_save.pack(anchor="w", padx=10, pady=5)
        row += 1

        # 4.5 METHOD
        tk.Label(parent, text="4.5. Chọn phương pháp so sánh:").grid(row=row, column=0, columnspan=2, sticky="w", padx=5)
        row += 1
        
        method_frame = tk.Frame(parent)
        method_frame.grid(row=row, column=0, columnspan=5, sticky="ew", padx=5)
        tk.Checkbutton(method_frame, text="Sử dụng phương pháp PDF", variable=self.use_pdf_method).pack(side="left")
        tk.Label(method_frame, text="(Chính xác hơn nhưng chậm hơn)", fg="gray").pack(side="left", padx=5)
        row += 1
        
        # Method Settings
        pdf_set_frame = tk.Frame(parent, bg="#e8f4fd", relief="ridge", bd=1)
        pdf_set_frame.grid(row=row, column=0, columnspan=5, sticky="ew", padx=15, pady=3)
        tk.Label(pdf_set_frame, text="DPI render PDF:", bg="#e8f4fd").grid(row=0, column=0, padx=5)
        dpi_entry = tk.Entry(pdf_set_frame, textvariable=self.pdf_render_dpi, width=10, justify="center")
        dpi_entry.grid(row=0, column=1, padx=5)
        dpi_entry.bind('<FocusOut>', self.validate_dpi_input)
        dpi_entry.bind('<Return>', self.validate_dpi_input)
        tk.Label(pdf_set_frame, text="(50-300)", bg="#e8f4fd", fg="#666").grid(row=0, column=2, padx=5)
        row += 1
        
        # ========== SECTION 5: HIGHLIGHT SETTINGS (Critical - was missing) ==========
        tk.Label(parent, text="5. Thiết lập hiển thị so sánh:").grid(row=row, column=0, columnspan=2, sticky="w", padx=5)
        row += 1
        
        # Row 1: Color Pickers - Base and Outline
        tk.Button(parent, text="Chọn Màu Nền", command=self.select_base_color).grid(row=row, column=0, pady=2, padx=5, sticky="ew")
        self.base_color_label = tk.Label(parent, text=f"Màu Nền: {self.highlight_base_color}", bg=self.highlight_base_color, fg="white")
        self.base_color_label.grid(row=row, column=1, pady=2, padx=5, sticky="ew")
        
        tk.Button(parent, text="Chọn Màu Viền", command=self.select_outline_color).grid(row=row, column=2, pady=2, padx=5, sticky="ew")
        self.outline_color_label = tk.Label(parent, text=f"Màu Viền: {self.highlight_outline_color}", bg=self.highlight_outline_color, fg="white")
        self.outline_color_label.grid(row=row, column=3, pady=2, padx=5, sticky="ew")
        row += 1
        
        # Row 2: Fill Color and Opacity Slider
        tk.Button(parent, text="Chọn Màu Tô", command=self.select_fill_color).grid(row=row, column=0, pady=2, padx=5, sticky="ew")
        self.fill_color_label = tk.Label(parent, text=f"Màu Tô: {self.highlight_fill_color}", bg=self.highlight_fill_color, fg="white")
        self.fill_color_label.grid(row=row, column=1, pady=2, padx=5, sticky="ew")
        
        tk.Label(parent, text="Độ mờ màu nền (%):").grid(row=row, column=2, sticky="w", padx=5)
        opacity_frame = tk.Frame(parent)
        opacity_frame.grid(row=row, column=3, sticky="ew", padx=5)
        opacity_slider = tk.Scale(opacity_frame, from_=0, to=100, orient='horizontal', variable=self.highlight_fill_opacity, length=120)
        opacity_slider.pack(side="left")
        tk.Entry(opacity_frame, textvariable=self.highlight_fill_opacity, width=5).pack(side="left", padx=(5,0))
        row += 1
        
        # Row 3: PDF Advanced Parameters
        lbl_thr = tk.Label(parent, text="Ngưỡng phát hiện PDF (0-255):")
        lbl_thr.grid(row=row, column=0, sticky="w", padx=5)
        tk.Entry(parent, textvariable=self.pdf_diff_threshold, width=12).grid(row=row, column=1, sticky="w", padx=5)
        ToolTip(lbl_thr, "Giá trị càng thấp càng nhạy (bắt nhiều khác biệt hơn). Đề xuất: 20-40.")
        
        lbl_sz = tk.Label(parent, text="Độ dày vùng tô PDF (1-9):")
        lbl_sz.grid(row=row, column=2, sticky="w", padx=5)
        tk.Entry(parent, textvariable=self.pdf_dilate_size, width=12).grid(row=row, column=3, sticky="w", padx=5)
        ToolTip(lbl_sz, "Độ dày vùng tô (px): số lẻ 1-9. Số lớn hơn = vùng highlight rộng hơn.")
        row += 1
        
        # Row 4: Dilate Iterations
        lbl_it = tk.Label(parent, text="Số lần nở PDF (1-3):")
        lbl_it.grid(row=row, column=0, sticky="w", padx=5)
        tk.Entry(parent, textvariable=self.pdf_dilate_iterations, width=12).grid(row=row, column=1, sticky="w", padx=5)
        ToolTip(lbl_it, "Số lần nở: số lần phóng to vùng highlight (1-3). Tăng số lần nở làm vùng tô lớn hơn.")
        row += 1
        
        # STATUS BAR
        self.status_label = ttk.Label(self.master, text="Sẵn sàng")
        self.status_label.pack(side="bottom", fill="x")

    def select_new_files(self):
        initial_dir = self.new_dir_path.get().strip()
        if initial_dir and os.path.exists(initial_dir):
            initial_dir = os.path.normpath(initial_dir)
        else:
            initial_dir = "/"
            
        files = filedialog.askopenfilenames(
            initialdir=initial_dir,
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if files:
            # Sort alphabetically by default to help with pairing
            self.new_files = sorted(list(files))
            
            # Display filenames
            display_text = ", ".join([os.path.basename(f) for f in self.new_files])
            self.new_files_display.set(display_text)
            
            self.new_dir_path.set(os.path.dirname(files[0]))

    def select_old_files(self):
        initial_dir = self.old_dir_path.get().strip()
        if initial_dir and os.path.exists(initial_dir):
            initial_dir = os.path.normpath(initial_dir)
        else:
            initial_dir = "/"

        files = filedialog.askopenfilenames(
            initialdir=initial_dir,
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if files:
            # Sort alphabetically by default
            self.old_files = sorted(list(files))
            
            # Display filenames
            display_text = ", ".join([os.path.basename(f) for f in self.old_files])
            self.old_files_display.set(display_text)
            
            self.old_dir_path.set(os.path.dirname(files[0]))

    def browse_result_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.result_path.set(folder)

    def show_help(self):
        """Hiển thị hướng dẫn sử dụng chi tiết trong cửa sổ riêng"""
        guide_text = get_text("help_content", self.current_lang)

        try:
            from tkinter.scrolledtext import ScrolledText
            win = tk.Toplevel(self.master)
            win.title(get_text("help_title", self.current_lang))
            win.geometry("650x420")
            st = ScrolledText(win, wrap='word', font=("Arial", 10))
            st.insert('1.0', guide_text)
            st.configure(state='disabled')
            st.pack(fill='both', expand=True, padx=8, pady=8)
            tk.Button(win, text=get_text("btn_close", self.current_lang), command=win.destroy).pack(pady=6)
        except Exception:
            messagebox.showinfo(get_text("help_title", self.current_lang), guide_text)

    def check_order(self):
        """Hiển thị dialog kiểm tra và sắp xếp thứ tự file"""
        self.show_confirmation_dialog()
    
    def show_confirmation_dialog(self):
        """Hiển thị hộp thoại xác nhận thứ tự các cặp file CTTT"""
        if not self.new_files or not self.old_files:
            messagebox.showwarning("Thiếu file", "Vui lòng chọn file CTTT mới và cũ trước.")
            return
        
        if len(self.new_files) != len(self.old_files):
            messagebox.showwarning("Số lượng không khớp", 
                f"Số file mới ({len(self.new_files)}) khác số file cũ ({len(self.old_files)}).\n"
                "Vui lòng chọn lại để số lượng khớp nhau.")
            return
        
        # Create dialog window
        dialog = tk.Toplevel(self.master)
        dialog.title("Kiểm tra thứ tự các cặp CTTT")
        dialog.geometry("700x400")
        dialog.transient(self.master)
        
        tk.Label(dialog, text="Danh sách các cặp file CTTT (Mới - Cũ):", font=("Arial", 11, "bold")).pack(pady=(10, 0))
        tk.Label(dialog, text="(Kéo thả để sắp xếp lại thứ tự nếu chưa khớp)", fg="blue", font=("Arial", 9, "italic")).pack(pady=(0, 10))
        
        # Frame for listboxes
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # New files listbox
        tk.Label(list_frame, text="File CTTT Mới:").grid(row=0, column=0, sticky="w")
        new_lb = tk.Listbox(list_frame, width=40, height=12)
        new_lb.grid(row=1, column=0, padx=5, pady=5)
        for f in self.new_files:
            new_lb.insert(tk.END, os.path.basename(f))
        self._enable_drag_drop(new_lb, self.new_files) # Enable Drag-Drop
        
        # Arrow label
        tk.Label(list_frame, text="↔", font=("Arial", 16)).grid(row=1, column=1)
        
        # Old files listbox  
        tk.Label(list_frame, text="File CTTT Cũ:").grid(row=0, column=2, sticky="w")
        old_lb = tk.Listbox(list_frame, width=40, height=12)
        old_lb.grid(row=1, column=2, padx=5, pady=5)
        for f in self.old_files:
            old_lb.insert(tk.END, os.path.basename(f))
        self._enable_drag_drop(old_lb, self.old_files) # Enable Drag-Drop
        
        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Xác nhận OK", command=dialog.destroy, width=15).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Đóng", command=dialog.destroy, width=15).pack(side="right", padx=10)

    def run_comparison(self):
        if self.is_processing:
            return

        if not self.new_files or not self.old_files:
            messagebox.showwarning("Thiếu file", "Vui lòng chọn cả file cũ và mới.")
            return
            
        # Save Settings
        if self.save_user_settings.get():
            self.settings_service.save_settings({
                "zoom_level": self.zoom_var.get(),
                "goto_address": self.goto_address.get(),
                "auto_add_b": self.auto_add_b.get(),
                "suppress_error": self.suppress_error_popups.get(),
                "save_settings": True,
                "use_pdf_method": self.use_pdf_method.get(),
                "pdf_dpi": self.pdf_render_dpi.get()
            })

        self.is_processing = True
        self.btn_run.config(state="disabled")
        if hasattr(self, 'btn_legacy'):
            self.btn_legacy.config(state="disabled")
        threading.Thread(target=self._run_thread, daemon=True).start()

    def _run_thread(self):
        try:
            # Collect all settings to pass to comparator (Critical - from Gap Analysis)
            settings = {
                # Core settings
                "dpi": self.pdf_render_dpi.get(),
                "zoom": self.zoom_var.get(),
                "auto_add_b": self.auto_add_b.get(),
                "output_folder": self.result_path.get() if self.result_path.get() else None,
                "suppress_error": self.suppress_error_popups.get(),
                "use_pdf_method": self.use_pdf_method.get(),
                
                # Highlight Colors (Critical - new)
                "highlight_base_color": self.highlight_base_color,
                "highlight_outline_color": self.highlight_outline_color,
                "highlight_fill_color": self.highlight_fill_color,
                
                # Highlight Settings (Critical - new)
                "highlight_fill_opacity": self.highlight_fill_opacity.get(),
                "pdf_diff_threshold": self.pdf_diff_threshold.get(),
                "pdf_dilate_size": self.pdf_dilate_size.get(),
                "pdf_dilate_iterations": self.pdf_dilate_iterations.get(),
            }
            
            # Update comparator's use_pdf_method flag from current UI state
            self.comparator.use_pdf_method = self.use_pdf_method.get()
            
            elapsed_time = self.comparator.start_comparison(
                self.new_files, 
                self.old_files, 
                status_callback=self.update_status,
                settings=settings
            )
            
            # Calculate minutes and seconds for display
            if elapsed_time:
                minutes, seconds = divmod(elapsed_time, 60)
                time_msg = f"\nThời gian thực hiện: {int(minutes)} phút và {seconds:.2f} giây."
            else:
                time_msg = ""
            
            self.update_status("Hoành thành!")
            messagebox.showinfo("Hoàn thành", f"Đã xử lý tất cả các cặp file CTTT cũ, mới.{time_msg}")
        except Exception as e:
            self.update_status(f"Lỗi: {e}")
            messagebox.showerror("Lỗi", str(e))
        finally:
            self.is_processing = False
            self.btn_run.config(state="normal")
            if hasattr(self, 'btn_legacy'):
                self.btn_legacy.config(state="normal")
            
    def update_status(self, msg):
        # Truncate long messages to prevent layout distortion
        if len(msg) > 100:
            msg = msg[:97] + "..."
        self.status_label.config(text=msg)
        self.master.update_idletasks()
    
    # ========== LEGACY SCREENSHOT METHOD ==========
    def run_legacy_comparison(self):
        """Chạy phương pháp Legacy Screenshot (giống phiên bản cũ)"""
        if self.is_processing:
            return

        if not self.new_files or not self.old_files:
            messagebox.showwarning("Thiếu file", "Vui lòng chọn cả file cũ và mới.")
            return
        
        if len(self.new_files) != len(self.old_files):
            messagebox.showerror("Lỗi", 
                f"Số file mới ({len(self.new_files)}) và cũ ({len(self.old_files)}) không khớp.")
            return
        
        # Cảnh báo người dùng
        confirm = messagebox.askyesno("Xác nhận so sánh CTTT phiên bản cũ",
            "⚠️ PHƯƠNG PHÁP CŨ\n\n"
            "Phương pháp này sẽ:\n"
            "• Đóng tất cả Excel đang mở\n"
            "• Mở từng file Excel và chụp ảnh màn hình\n"
            "• Yêu cầu KHÔNG SỬ DỤNG máy tính trong khi chụp ảnh\n\n"
            "Bạn có muốn tiếp tục không?")
        
        if not confirm:
            return
        
        # Disable buttons & set processing flag
        self.is_processing = True
        self.btn_run.config(state="disabled")
        if hasattr(self, 'btn_legacy'):
            self.btn_legacy.config(state="disabled")
        
        # Run in thread
        threading.Thread(target=self._run_legacy_thread, daemon=True).start()
    
    def _run_legacy_thread(self):
        """Thread chạy Legacy comparison"""
        try:
            # Collect settings
            settings = {
                "screen_mode": self.screen_mode.get(),
                "zoom": self.zoom_var.get(),
                "goto_address": self.goto_address.get(),
                "output_folder": self.result_path.get() if self.result_path.get() else None,
                "highlight_fill_color": self.highlight_fill_color,
                "highlight_fill_opacity": self.highlight_fill_opacity.get(),
            }
            
            # Create progress callback
            def progress_callback(value):
                self.master.after(0, lambda: self.update_progress(value))
            
            # Create progress bar
            self.master.after(0, self.create_progress_bar)
            
            # Run legacy comparison
            elapsed_time = self.comparator.start_legacy_comparison(
                self.new_files,
                self.old_files,
                status_callback=self.update_status,
                progress_callback=progress_callback,
                settings=settings
            )
            
            # Remove progress bar
            self.master.after(0, self.remove_progress_bar)
            
            # Show result
            if elapsed_time:
                minutes, seconds = divmod(elapsed_time, 60)
                time_msg = f"\nThời gian thực hiện: {int(minutes)} phút và {seconds:.2f} giây."
            else:
                time_msg = ""
            
            self.update_status("Hoàn thành!")
            messagebox.showinfo("Hoàn thành so sánh CTTT phiên bản cũ", 
                f"Đã xử lý tất cả các cặp file CTTT bằng phương pháp cũ.{time_msg}")
            
        except Exception as e:
            self.update_status(f"Lỗi: {e}")
            messagebox.showerror("Lỗi", str(e))
        finally:
            self.is_processing = False
            self.btn_run.config(state="normal")
            if hasattr(self, 'btn_legacy'):
                self.btn_legacy.config(state="normal")


    # ========== COLOR PICKER METHODS (Critical - was missing) ==========
    def select_base_color(self):
        """Mở color chooser để chọn màu nền highlight và cập nhật label"""
        color = colorchooser.askcolor(title="Chọn Màu Nền", initialcolor=self.highlight_base_color)
        if color[1]:
            self.highlight_base_color = color[1]
            self.bg_color = color[1]  # Legacy alias
            self.base_color_label.config(text=f"Màu Nền: {color[1]}", bg=color[1])
            self._auto_save_settings()
    
    def select_outline_color(self):
        """Mở color chooser để chọn màu viền highlight và cập nhật label"""
        color = colorchooser.askcolor(title="Chọn Màu Viền", initialcolor=self.highlight_outline_color)
        if color[1]:
            self.highlight_outline_color = color[1]
            self.outline_color = color[1]  # Legacy alias
            self.outline_color_label.config(text=f"Màu Viền: {color[1]}", bg=color[1])
            self._auto_save_settings()
    
    def select_fill_color(self):
        """Mở color chooser để chọn màu tô highlight và cập nhật label"""
        color = colorchooser.askcolor(title="Chọn Màu Tô", initialcolor=self.highlight_fill_color)
        if color[1]:
            self.highlight_fill_color = color[1]
            self.fill_color_label.config(text=f"Màu Tô: {color[1]}", bg=color[1])
            self._auto_save_settings()

    # ========== VALIDATION METHODS (Critical - was missing) ==========
    def validate_dpi_input(self, event=None):
        """Validation cho DPI input - đảm bảo giá trị trong khoảng 50-300"""
        try:
            current_value = self.pdf_render_dpi.get()
            if current_value < 50:
                self.pdf_render_dpi.set(50)
                messagebox.showwarning("DPI không hợp lệ", "DPI tối thiểu là 50. Đã tự động điều chỉnh về 50.")
            elif current_value > 300:
                self.pdf_render_dpi.set(300)
                messagebox.showwarning("DPI không hợp lệ", "DPI tối đa là 300. Đã tự động điều chỉnh về 300.")
            self._auto_save_settings()
        except Exception:
            self.pdf_render_dpi.set(100)
            messagebox.showerror("DPI không hợp lệ", "Vui lòng nhập số nguyên từ 50 đến 300. Đã reset về 100.")

    # ========== SCREEN MODE METHODS (Critical - was missing) ==========
    def on_screen_mode_change(self, event=None):
        """Xử lý sự kiện thay đổi chế độ màn hình và cập nhật zoom level tương ứng"""
        selected = self.screen_combo.get()
        if "VPS" in selected:
            self.screen_mode.set("vps")
            self.zoom_var.set(100)  # VPS thường cần zoom cao hơn
        elif "phụ" in selected or "Màn hình phụ" in selected:
            self.screen_mode.set("monitor")
            self.zoom_var.set(80)
        else:
            self.screen_mode.set("pc")
            self.zoom_var.set(config.DEFAULT_ZOOM)
        self._auto_save_settings()
    
    # ========== LANGUAGE METHODS ==========
    def on_language_change(self, event=None):
        """Xử lý sự kiện thay đổi ngôn ngữ giao diện"""
        selected_name = self.lang_combo.get()
        
        # Find language code from name
        lang_codes = list(LANGUAGES.keys())
        lang_names = list(LANGUAGES.values())
        
        if selected_name in lang_names:
            new_lang = lang_codes[lang_names.index(selected_name)]
        else:
            new_lang = "vi"
        
        if new_lang != self.current_lang:
            self.current_lang = new_lang
            self._auto_save_settings()
            
            # Update app title
            self.master.title(get_text("app_title", self.current_lang))
            
            # Update translatable widgets
            self._update_ui_language()
            
            # Show confirmation
            confirmations = {
                "vi": "Đã chuyển sang Tiếng Việt",
                "en": "Switched to English",
                "zh": "已切换到中文",
                "ja": "日本語に切り替えました"
            }
            messagebox.showinfo(
                get_text("menu_language", self.current_lang),
                confirmations.get(new_lang, "Language changed")
            )
    
    def _update_ui_language(self):
        """Cập nhật text cho các widget đã đăng ký"""
        for key, widget in self.translatable_widgets.items():
            try:
                new_text = get_text(key, self.current_lang)
                if hasattr(widget, 'config'):
                    widget.config(text=new_text)
            except Exception:
                pass  # Skip if widget was destroyed
        
        # Update status bar
        if hasattr(self, 'status_label'):
            self.status_label.config(text=get_text("status_ready", self.current_lang))

    # ========== PROGRESS BAR METHODS (Critical - was missing) ==========
    def create_progress_bar(self):
        """Tạo và hiển thị thanh tiến trình và label trạng thái"""
        if self.progress_bar is None:
            progress_frame = tk.Frame(self.master)
            progress_frame.pack(side="bottom", fill="x", before=self.status_label)
            
            self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
            self.progress_bar.pack(side="left", fill="x", expand=True, padx=5, pady=2)
            
            self.progress_label = tk.Label(progress_frame, text="0%", width=6)
            self.progress_label.pack(side="right", padx=5)
    
    def update_progress(self, value):
        """Cập nhật giá trị thanh tiến trình và label phần trăm"""
        if self.progress_bar:
            self.progress_bar['value'] = value
            if self.progress_label:
                self.progress_label.config(text=f"{int(value)}%")
            self.master.update_idletasks()
    
    def remove_progress_bar(self):
        """Ẩn và xóa thanh tiến trình và các label liên quan"""
        if self.progress_bar:
            parent = self.progress_bar.master
            self.progress_bar.destroy()
            self.progress_bar = None
            if self.progress_label:
                self.progress_label.destroy()
                self.progress_label = None
            parent.destroy()

    # ========== DRAG & DROP METHODS ==========
    def _enable_drag_drop(self, listbox, target_list):
        """Enable drag and drop reordering for a listbox"""
        listbox.bind('<Button-1>', lambda e: self._on_drag_start(e, listbox))
        listbox.bind('<B1-Motion>', lambda e: self._on_drag_motion(e, listbox, target_list))
        # listbox.bind('<ButtonRelease-1>', lambda e: self._on_drag_stop(e))

    def _on_drag_start(self, event, listbox):
        widget = event.widget
        # Get index under mouse
        try:
            index = widget.nearest(event.y)
            self.drag_data = {"index": index, "widget": widget}
        except Exception:
            self.drag_data = None

    def _on_drag_motion(self, event, listbox, target_list):
        if not self.drag_data:
            return
            
        widget = self.drag_data.get("widget")
        if not widget or widget != listbox:
            return
            
        # Get current index under mouse
        new_index = widget.nearest(event.y)
        
        # If moved
        if new_index != self.drag_data["index"]:
            # Swap in Listbox Visual
            old_index = self.drag_data["index"]
            
            # Get text of moving item
            text = widget.get(old_index)
            
            # Delete and Re-insert
            widget.delete(old_index)
            widget.insert(new_index, text)
            widget.selection_clear(0, tk.END)
            widget.selection_set(new_index)
            
            # Swap in Underlying Data List (Sync immediately)
            # This works because new_files/old_files are mutable lists
            if 0 <= old_index < len(target_list) and 0 <= new_index < len(target_list):
                target_list[old_index], target_list[new_index] = target_list[new_index], target_list[old_index]
            
            # Update current index
            self.drag_data["index"] = new_index
            
    # ========== HELPER METHODS ==========
    def _auto_save_settings(self):
        """Tự động lưu cài đặt nếu checkbox lưu cài đặt được bật"""
        if self.save_user_settings.get():
            self.settings_service.save_settings({
                "zoom_level": self.zoom_var.get(),
                "goto_address": self.goto_address.get(),
                "auto_add_b": self.auto_add_b.get(),
                "suppress_error": self.suppress_error_popups.get(),
                "save_settings": True,
                "use_pdf_method": self.use_pdf_method.get(),
                "pdf_dpi": self.pdf_render_dpi.get(),
                "highlight_base_color": self.highlight_base_color,
                "highlight_outline_color": self.highlight_outline_color,
                "highlight_fill_color": self.highlight_fill_color,
                "highlight_fill_opacity": self.highlight_fill_opacity.get(),
                "pdf_diff_threshold": self.pdf_diff_threshold.get(),
                "pdf_dilate_size": self.pdf_dilate_size.get(),
                "pdf_dilate_iterations": self.pdf_dilate_iterations.get(),
                "screen_mode": self.screen_mode.get(),
                "language": self.current_lang,
            })

    # ========== MENU BAR METHODS ==========
    def create_menu_bar(self):
        """Tạo menu bar với các menu File, View, Help"""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        # ===== FILE MENU =====
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        file_menu.add_command(label="Mở file CTTT mới...", command=self.select_new_files, accelerator="Ctrl+O")
        file_menu.add_command(label="Mở file CTTT cũ...", command=self.select_old_files, accelerator="Ctrl+Shift+O")
        file_menu.add_separator()
        file_menu.add_command(label="Chọn thư mục kết quả...", command=self.browse_result_folder, accelerator="Ctrl+R")
        file_menu.add_separator()
        file_menu.add_command(label="Lưu cài đặt", command=self._manual_save_settings, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self._on_close, accelerator="Alt+F4")
        
        # ===== EDIT MENU =====
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Chỉnh sửa", menu=edit_menu)
        
        edit_menu.add_command(label="Kiểm tra thứ tự file", command=self.check_order, accelerator="Ctrl+K")
        edit_menu.add_separator()
        edit_menu.add_command(label="Chọn màu nền", command=self.select_base_color)
        edit_menu.add_command(label="Chọn màu viền", command=self.select_outline_color)
        edit_menu.add_command(label="Chọn màu tô", command=self.select_fill_color)
        edit_menu.add_separator()
        edit_menu.add_command(label="Reset cài đặt mặc định", command=self._reset_to_defaults)
        
        # ===== VIEW MENU =====
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Xem", menu=view_menu)
        
        view_menu.add_command(label="Kiểm tra thư viện", command=self._show_library_status)
        view_menu.add_separator()
        view_menu.add_command(label="Mở thư mục kết quả", command=self._open_result_folder, accelerator="Ctrl+E")
        
        # ===== RUN MENU =====
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Chạy", menu=run_menu)
        
        run_menu.add_command(label="Bắt đầu so sánh", command=self.run_comparison, accelerator="Ctrl+Enter")
        
        # ===== HELP MENU =====
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Trợ giúp", menu=help_menu)
        
        help_menu.add_command(label="Hướng dẫn cơ bản", command=self.show_help, accelerator="F1")
        help_menu.add_command(label="Hướng dẫn chi tiết", command=self._show_detailed_help)
        help_menu.add_separator()
        help_menu.add_command(label="Phím tắt", command=self._show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="Về ứng dụng", command=self._show_about)
    
    def bind_shortcuts(self):
        """Gắn phím tắt cho các chức năng chính"""
        # File operations
        self.master.bind('<Control-o>', lambda e: self.select_new_files())
        self.master.bind('<Control-O>', lambda e: self.select_new_files())
        self.master.bind('<Control-Shift-o>', lambda e: self.select_old_files())
        self.master.bind('<Control-Shift-O>', lambda e: self.select_old_files())
        self.master.bind('<Control-r>', lambda e: self.browse_result_folder())
        self.master.bind('<Control-R>', lambda e: self.browse_result_folder())
        self.master.bind('<Control-s>', lambda e: self._manual_save_settings())
        self.master.bind('<Control-S>', lambda e: self._manual_save_settings())
        
        # Run
        self.master.bind('<Control-Return>', lambda e: self.run_comparison())
        self.master.bind('<F5>', lambda e: self.run_comparison())
        self.master.bind('<F6>', lambda e: self.run_legacy_comparison())  # Legacy (Phiên bản 6)
        
        # Edit
        self.master.bind('<Control-k>', lambda e: self.check_order())
        self.master.bind('<Control-K>', lambda e: self.check_order())
        
        # View
        self.master.bind('<Control-e>', lambda e: self._open_result_folder())
        self.master.bind('<Control-E>', lambda e: self._open_result_folder())
        
        # Help
        self.master.bind('<F1>', lambda e: self.show_help())
        
        # Escape to cancel/close dialogs
        self.master.bind('<Escape>', lambda e: self.master.focus_set())

    # ========== MENU COMMAND HANDLERS ==========
    def _manual_save_settings(self):
        """Lưu cài đặt thủ công"""
        self._auto_save_settings()
        messagebox.showinfo("Đã lưu", "Cài đặt đã được lưu thành công.")
    
    def _on_close(self):
        """Xử lý khi đóng ứng dụng"""
        if self.save_user_settings.get():
            self._auto_save_settings()
        self.master.quit()
    
    def _reset_to_defaults(self):
        """Reset tất cả cài đặt về mặc định"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn reset tất cả cài đặt về mặc định?"):
            self.zoom_var.set(config.DEFAULT_ZOOM)
            self.goto_address.set(config.DEFAULT_GOTO_ADDRESS)
            self.pdf_render_dpi.set(config.DEFAULT_DPI)
            self.pdf_diff_threshold.set(config.DEFAULT_DIFF_THRESHOLD)
            self.pdf_dilate_size.set(config.DEFAULT_DILATE_SIZE)
            self.pdf_dilate_iterations.set(config.DEFAULT_DILATE_ITERATIONS)
            self.highlight_fill_opacity.set(config.DEFAULT_FILL_OPACITY)
            self.highlight_base_color = config.HIGHLIGHT_BASE_COLOR
            self.highlight_outline_color = config.HIGHLIGHT_OUTLINE_COLOR
            self.highlight_fill_color = config.HIGHLIGHT_FILL_COLOR
            self.base_color_label.config(text=f"Màu Nền: {self.highlight_base_color}", bg=self.highlight_base_color)
            self.outline_color_label.config(text=f"Màu Viền: {self.highlight_outline_color}", bg=self.highlight_outline_color)
            self.fill_color_label.config(text=f"Màu Tô: {self.highlight_fill_color}", bg=self.highlight_fill_color)
            messagebox.showinfo("Đã reset", "Tất cả cài đặt đã được reset về mặc định.")
    
    def _show_library_status(self):
        """Hiển thị trạng thái thư viện"""
        try:
            from services.help_service import HelpService
            HelpService.show_library_status(self.master)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị trạng thái thư viện: {e}")
    
    def _open_result_folder(self):
        """Mở thư mục kết quả trong Explorer"""
        result_path = self.result_path.get()
        if result_path and os.path.isdir(result_path):
            os.startfile(result_path)
        elif self.new_files:
            # Fallback: mở thư mục chứa file mới đầu tiên
            folder = os.path.dirname(self.new_files[0])
            if os.path.isdir(folder):
                os.startfile(folder)
            else:
                messagebox.showwarning("Thông báo", "Không tìm thấy thư mục kết quả.")
        else:
            messagebox.showwarning("Thông báo", "Chưa có thư mục kết quả. Vui lòng chọn file hoặc thư mục trước.")
    
    def _show_detailed_help(self):
        """Hiển thị hướng dẫn chi tiết"""
        try:
            from services.help_service import HelpService
            HelpService.show_user_guide(self.master, detailed=True)
        except Exception:
            self.show_help()
    
    def _show_shortcuts(self):
        """Hiển thị danh sách phím tắt"""
        shortcuts = """PHÍM TẮT:

Ctrl+O          Mở file CTTT mới
Ctrl+Shift+O    Mở file CTTT cũ
Ctrl+R          Chọn thư mục kết quả
Ctrl+S          Lưu cài đặt
Ctrl+K          Kiểm tra thứ tự file
Ctrl+Enter      Bắt đầu so sánh
Ctrl+E          Mở thư mục kết quả
F1              Hướng dẫn sử dụng
Escape          Hủy focus
Alt+F4          Thoát"""
        messagebox.showinfo("Phím tắt", shortcuts)
    
    def _show_about(self):
        """Hiển thị thông tin ứng dụng"""
        try:
            from services.help_service import HelpService
            HelpService.show_about(self.master)
        except Exception:
            about = f"""SO SÁNH CTTT cũ và CTTT mới v7.04 (Tác giả: Bùi Đức Vinh)

Ứng dụng so sánh sai khác giữa các Chỉ thị thao tác (CTTT).

Tính năng:
• So sánh PDF với highlight màu
• Xuất báo cáo Excel
• Tự động lưu cài đặt"""
            messagebox.showinfo("Về ứng dụng", about)

