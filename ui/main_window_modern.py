"""
Modern Main Window UI
Giao diện hiện đại, chuyên nghiệp và tối giản
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from core.comparator import Comparator
import config
import utils
from services.settings_service import SettingsService
from ui.modern_style import Colors, Fonts, Spacing, configure_styles
from ui.translations import get_text, LANGUAGES, get_available_languages
import threading
import os
from ui.help_window import ModernHelpWindow


class ToolTip:
    """create a tooltip for a given widget"""
    def __init__(self, widget, text='widget info'):
        self.waittime = 500
        self.wraplength = 180
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
        x, y, cx, cy = self.widget.bbox("insert") if self.widget.bbox("insert") else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       wraplength=self.wraplength, font=Fonts.get("sm"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
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
        self._refresh_workflow_state()
        
        # Logic
        self.comparator = Comparator()
        
        # Apply saved language settings
        self._refresh_all_ui_texts()
        
        # Auto-update check after 1 second (không chặn UI)
        self.master.after(1000, self._check_updates_in_background)

    def setup_variables(self):
        self.new_dir_path = tk.StringVar()
        self.new_files_display = tk.StringVar()
        self.old_dir_path = tk.StringVar()
        self.old_files_display = tk.StringVar()
        self.result_path = tk.StringVar()
        self.is_processing = False
        self.pairs_confirmed = False
        self.workflow_validation_error = None
        
        # Settings Variables
        self.zoom_var = tk.IntVar(value=self.settings.get("zoom_level", config.DEFAULT_ZOOM))
        self.goto_address = tk.StringVar(value=self.settings.get("goto_address", config.DEFAULT_GOTO_ADDRESS))
        self.auto_add_b = tk.BooleanVar(value=self.settings.get("auto_add_b", False))
        self.suppress_error_popups = tk.BooleanVar(value=self.settings.get("suppress_error", True))
        self.save_user_settings = tk.BooleanVar(value=self.settings.get("save_settings", True))
        self.use_pdf_method = tk.BooleanVar(value=self.settings.get("use_pdf_method", True))
        self.pdf_render_dpi = tk.IntVar(value=self.settings.get("pdf_dpi", config.DEFAULT_DPI))
        # Document mode is deliberately not restored as an active choice.  It is the
        # first workflow decision and must be made for each new comparison session.
        self.doc_mode_var = tk.StringVar(value="")
        self.print_area_var = tk.StringVar(value="")
        self.doc_mode_selected = False
        
        # Highlight Colors
        self.highlight_base_color = self.settings.get("highlight_base_color", config.HIGHLIGHT_BASE_COLOR)
        self.highlight_outline_color = self.settings.get("highlight_outline_color", config.HIGHLIGHT_OUTLINE_COLOR)
        self.highlight_fill_color = self.settings.get("highlight_fill_color", config.HIGHLIGHT_FILL_COLOR)
        
        # Highlight Settings
        self.highlight_fill_opacity = tk.IntVar(value=self.settings.get("highlight_fill_opacity", config.DEFAULT_FILL_OPACITY))
        self.pdf_diff_threshold = tk.IntVar(value=self.settings.get("pdf_diff_threshold", config.DEFAULT_DIFF_THRESHOLD))
        self.pdf_dilate_size = tk.IntVar(value=self.settings.get("pdf_dilate_size", config.DEFAULT_DILATE_SIZE))
        self.pdf_dilate_iterations = tk.IntVar(value=self.settings.get("pdf_dilate_iterations", config.DEFAULT_DILATE_ITERATIONS))
        
        # Screen Mode
        self.screen_mode = tk.StringVar(value=self.settings.get("screen_mode", "pc"))
        
        # Progress Bar references
        self.progress_bar = None
        self.progress_label = None
        
        # Legacy compatibility
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
        # ========== MODERN STYLE CONFIGURATION ==========
        configure_styles(self.master)
        
        # Window Configuration
        self.master.geometry("1100x750")
        self.master.configure(bg=Colors.BG_MAIN)
        self.master.minsize(900, 600)
        
        # ========== MENU BAR ==========
        self.create_menu_bar()
        
        # ========== KEYBOARD SHORTCUTS ==========
        self.bind_shortcuts()
        
        # ========== MAIN CONTAINER ==========
        main_container = ttk.Frame(self.master, style="TFrame")
        main_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.MD)
        
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        
        # ========== HEADER ==========
        header_frame = ttk.Frame(main_container, style="TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, Spacing.MD))
        
        title_label = ttk.Label(
            header_frame, 
            text=get_text("app_title", self.current_lang) if self.current_lang != "vi" else "📊 So sánh Chỉ thị Thao tác",
            style="Header.TLabel"
        )
        title_label.pack(side="left")
        self.translatable_widgets["title"] = title_label
        
        # LANGUAGE SELECTOR
        lang_frame = ttk.Frame(header_frame, style="TFrame")
        lang_frame.pack(side="right", padx=(0, Spacing.MD))
        
        ttk.Label(lang_frame, text="🌐", font=("Arial", 12)).pack(side="left", padx=(0, 4))
        
        self.lang_combo = ttk.Combobox(
            lang_frame, 
            values=list(LANGUAGES.values()), 
            state="readonly", 
            width=12
        )
        # Set current language in combo
        lang_codes = list(LANGUAGES.keys())
        lang_names = list(LANGUAGES.values())
        if self.current_lang in lang_codes:
            self.lang_combo.current(lang_codes.index(self.current_lang))
        else:
            self.lang_combo.current(0)
        self.lang_combo.pack(side="left")
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        help_btn = ttk.Button(
            header_frame, 
            text=get_text("btn_help", self.current_lang) if self.current_lang != "vi" else "📖 Hướng dẫn",
            command=self.show_help,
            style="Secondary.TButton"
        )
        help_btn.pack(side="right")
        self.translatable_widgets["help_btn"] = help_btn
        
        # ========== CONTENT (Scrollable) ==========
        self.canvas = tk.Canvas(main_container, bg=Colors.BG_MAIN, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="TFrame")
        
        # Tạo window trong canvas và lưu ID
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        def _on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Ẩn scrollbar nếu nội dung không cần cuộn
            if self.scrollable_frame.winfo_reqheight() <= self.canvas.winfo_height():
                self.scrollbar.grid_remove()
            else:
                self.scrollbar.grid()
        
        def _on_canvas_configure(event):
            # Mở rộng scrollable_frame chiếm hết chiều ngang canvas
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        
        self.scrollable_frame.bind("<Configure>", _on_frame_configure)
        self.canvas.bind("<Configure>", _on_canvas_configure)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Mouse wheel
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        self.scrollbar.grid_remove()  # Ẩn mặc định, sẽ hiện khi cần
        
        content = self.scrollable_frame
        content.grid_columnconfigure(0, weight=1)
        
        row = 0
        
        # ==================== CARD 1: FILE SELECTION ====================
        self.file_card = ttk.LabelFrame(content, text="  📁 Chọn Files CTTT  ", style="Card.TLabelframe", padding=Spacing.LG)
        self.file_card.grid(row=row, column=0, sticky="ew", pady=(0, Spacing.MD)); row += 1
        self.file_card.grid_columnconfigure(1, weight=1)
        self.file_card.grid_columnconfigure(3, weight=1)
        
        # Document Mode & Screen Mode
        mode_frame = ttk.Frame(self.file_card); mode_frame.grid(row=0, column=0, columnspan=5, sticky="ew", pady=(0, Spacing.MD))
        self.lbl_doc_mode = ttk.Label(mode_frame, text=get_text("doc_type_label", self.current_lang), font=Fonts.get("base", "bold"))
        self.lbl_doc_mode.pack(side="left", padx=(0, Spacing.SM))
        
        self.doc_mode_combo = ttk.Combobox(
            mode_frame, 
            values=[
                get_text("mode_standard_cttt", self.current_lang),
                get_text("mode_dukc_cttt", self.current_lang),
                get_text("mode_dukc_other", self.current_lang)
            ],
            state="readonly", 
            width=56
        )
        self.doc_mode_combo.set("")
            
        self.doc_mode_combo.pack(side="left", padx=(0, Spacing.LG))
        self.doc_mode_combo.bind("<<ComboboxSelected>>", self.on_doc_mode_change)

        self.lbl_screen_mode = ttk.Label(mode_frame, text=get_text("screen_mode_label", self.current_lang))
        self.lbl_screen_mode.pack(side="left", padx=(0, Spacing.SM))
        self.screen_combo = ttk.Combobox(mode_frame, values=["Màn hình PC", "VPS", "Màn hình phụ"], state="readonly", width=15)
        self.screen_combo.current(0)
        self.screen_combo.pack(side="left")
        self.screen_combo.bind("<<ComboboxSelected>>", self.on_screen_mode_change)
        
        # New Files
        self.lbl_cttt_new = ttk.Label(self.file_card, text="CTTT Mới:")
        self.lbl_cttt_new.grid(row=1, column=0, sticky="w", padx=Spacing.SM)
        ttk.Entry(self.file_card, textvariable=self.new_dir_path).grid(row=1, column=1, sticky="ew", padx=Spacing.SM)
        self.lbl_selected_new = ttk.Label(self.file_card, text="Đã chọn:")
        self.lbl_selected_new.grid(row=1, column=2, sticky="e", padx=Spacing.SM)
        ttk.Entry(self.file_card, textvariable=self.new_files_display).grid(row=1, column=3, sticky="ew", padx=Spacing.SM)
        self.btn_select_new = ttk.Button(self.file_card, text="📂 Chọn CTTT mới", command=self.select_new_files, style="Primary.TButton")
        self.btn_select_new.grid(row=1, column=4, padx=Spacing.SM, pady=Spacing.SM)
        
        # Old Files
        self.lbl_cttt_old = ttk.Label(self.file_card, text="CTTT Cũ:")
        self.lbl_cttt_old.grid(row=2, column=0, sticky="w", padx=Spacing.SM)
        ttk.Entry(self.file_card, textvariable=self.old_dir_path).grid(row=2, column=1, sticky="ew", padx=Spacing.SM)
        self.lbl_selected_old = ttk.Label(self.file_card, text="Đã chọn:")
        self.lbl_selected_old.grid(row=2, column=2, sticky="e", padx=Spacing.SM)
        ttk.Entry(self.file_card, textvariable=self.old_files_display).grid(row=2, column=3, sticky="ew", padx=Spacing.SM)
        self.btn_select_old = ttk.Button(self.file_card, text="📂 Chọn CTTT cũ", command=self.select_old_files, style="Secondary.TButton")
        self.btn_select_old.grid(row=2, column=4, padx=Spacing.SM, pady=Spacing.SM)
        
        # Result Path
        self.lbl_result_path = ttk.Label(self.file_card, text="Thư mục lưu kết quả (để trống = cùng thư mục CTTT mới):", style="Muted.TLabel")
        self.lbl_result_path.grid(row=3, column=0, columnspan=3, sticky="w", padx=Spacing.SM, pady=(Spacing.MD, 0))
        result_row = ttk.Frame(self.file_card); result_row.grid(row=4, column=0, columnspan=5, sticky="ew", padx=Spacing.SM)
        result_row.grid_columnconfigure(0, weight=1)
        ttk.Entry(result_row, textvariable=self.result_path).grid(row=0, column=0, sticky="ew")
        self.btn_browse = ttk.Button(result_row, text="Duyệt...", command=self.browse_result_folder, style="Secondary.TButton")
        self.btn_browse.grid(row=0, column=1, padx=(Spacing.SM, 0))
        
        # Check Order
        self.btn_check_order = ttk.Button(self.file_card, text="🔍 Kiểm tra thứ tự cặp CTTT", command=self.check_order, style="Secondary.TButton")
        self.btn_check_order.grid(row=5, column=0, columnspan=5, sticky="ew", pady=(Spacing.MD, 0))

        self.workflow_frame = tk.Frame(self.file_card, bg="#F8FAFC", highlightbackground="#E2E8F0", highlightthickness=1)
        self.workflow_frame.grid(row=6, column=0, columnspan=5, sticky="ew", padx=Spacing.SM, pady=(Spacing.SM, 0))
        self.workflow_frame.grid_columnconfigure(0, weight=1)
        self.workflow_step_labels = []
        for step_index in range(5):
            label = tk.Label(
                self.workflow_frame, anchor="w", font=Fonts.get("sm", "bold"), padx=10, pady=4
            )
            label.grid(row=step_index, column=0, sticky="ew", padx=4, pady=2)
            self.workflow_step_labels.append(label)

        self.lbl_workflow = ttk.Label(self.file_card, text="", style="Muted.TLabel", wraplength=900)
        self.lbl_workflow.grid(row=7, column=0, columnspan=5, sticky="w", padx=Spacing.SM, pady=(Spacing.XS, 0))
        
        # ==================== RUN BUTTON ====================
        run_frame = ttk.Frame(content); run_frame.grid(row=row, column=0, sticky="ew", pady=(0, Spacing.MD)); row += 1
        run_frame.grid_columnconfigure(0, weight=1)
        
        self.btn_run = tk.Button(
            run_frame, text="▶️  BẮT ĐẦU SO SÁNH(PHƯƠNG PHÁP MỚI BẢN TỪ VER 7 TRỞ LÊN(PDF/EXCEL))", command=self.run_comparison,
            font=Fonts.get("xl", "bold"), bg="#1D4ED8", fg="#FFFFFF",
            activebackground="#1E3A8A", activeforeground="#FFFFFF",
            height=2, cursor="hand2", relief="flat", bd=0
        )
        self.btn_run.grid(row=0, column=0, sticky="ew", ipady=Spacing.MD)
        
        # ==================== LEGACY SCREENSHOT BUTTON (NEW) ====================
        self.legacy_frame = ttk.LabelFrame(content, text="  🖼️ Phương pháp chụp ảnh màn hình của phiên bản 6 (Phiên bản cũ)  ", style="Card.TLabelframe", padding=Spacing.SM)
        self.legacy_frame.grid(row=row, column=0, sticky="ew", pady=(0, Spacing.MD)); row += 1
        self.legacy_frame.grid_columnconfigure(0, weight=1)
        
        self.btn_legacy = tk.Button(
            self.legacy_frame, text="📷 CHỤP MÀN HÌNH TRỰC TIẾP (Phiên bản 6)", 
            command=self.run_legacy_comparison,
            font=Fonts.get("lg", "bold"), bg="#FFD700", fg="#000000",
            activebackground="#EAB308", activeforeground="#000000",
            height=2, cursor="hand2", relief="flat", bd=0
        )
        self.btn_legacy.pack(fill="x", padx=Spacing.SM, pady=(Spacing.SM, 0))
        
        self.lbl_legacy_warning = ttk.Label(
            self.legacy_frame, 
            text="⚠️ Mở Excel trực tiếp trên màn hình, chụp ảnh và so sánh (giống phiên bản 6). Không sử dụng máy tính trong khi chạy!",
            style="Muted.TLabel", wraplength=800
        )
        self.lbl_legacy_warning.pack(anchor="w", padx=Spacing.SM, pady=Spacing.SM)
        
        # ==================== CARD 2: SETTINGS ====================
        self.settings_card = ttk.LabelFrame(content, text="  ⚙️ Cài đặt  ", style="Card.TLabelframe", padding=Spacing.LG)
        self.settings_card.grid(row=row, column=0, sticky="ew", pady=(0, Spacing.MD)); row += 1
        self.settings_card.grid_columnconfigure(1, weight=1)
        self.settings_card.grid_columnconfigure(3, weight=1)
        
        # Method
        method_frame = ttk.Frame(self.settings_card); method_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, Spacing.MD))
        self.chk_use_pdf = ttk.Checkbutton(method_frame, text="📄 Sử dụng phương pháp PDF (chính xác hơn)", variable=self.use_pdf_method)
        self.chk_use_pdf.pack(side="left")
        self.lbl_dpi = ttk.Label(method_frame, text="Độ phân giải:")
        self.lbl_dpi.pack(side="left", padx=(Spacing.LG, Spacing.SM))
        dpi_entry = ttk.Entry(method_frame, textvariable=self.pdf_render_dpi, width=6); dpi_entry.pack(side="left")
        dpi_entry.bind('<FocusOut>', self.validate_dpi_input)
        ttk.Label(method_frame, text="(50-300)", style="Muted.TLabel").pack(side="left", padx=Spacing.SM)
        
        # Zoom & Goto
        self.lbl_zoom = ttk.Label(self.settings_card, text="Mức phóng to:")
        self.lbl_zoom.grid(row=1, column=0, sticky="w", pady=Spacing.SM)
        ttk.Entry(self.settings_card, textvariable=self.zoom_var, width=10).grid(row=1, column=1, sticky="w", padx=Spacing.SM)
        self.lbl_goto = ttk.Label(self.settings_card, text="Di chuyển đến ô (Mặc định: EX1):")
        self.lbl_goto.grid(row=1, column=2, sticky="e", padx=Spacing.SM)
        ttk.Entry(self.settings_card, textvariable=self.goto_address, width=10).grid(row=1, column=3, sticky="w")
        
        # Checkboxes
        check_frame = ttk.Frame(self.settings_card); check_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=Spacing.MD)
        self.chk_auto_b = ttk.Checkbutton(check_frame, text="⚠️ Tự động thêm 'b' cho barcode", variable=self.auto_add_b)
        self.chk_auto_b.pack(side="left", padx=(0, Spacing.LG))
        self.chk_suppress = ttk.Checkbutton(check_frame, text="🔇 Ẩn thông báo lỗi", variable=self.suppress_error_popups)
        self.chk_suppress.pack(side="left", padx=(0, Spacing.LG))
        self.chk_save = ttk.Checkbutton(check_frame, text="💾 Lưu cài đặt", variable=self.save_user_settings)
        self.chk_save.pack(side="left")
        
        # ==================== CARD 3: HIGHLIGHT ====================
        self.hl_card = ttk.LabelFrame(content, text="  🎨 Thiết lập Highlight  ", style="Card.TLabelframe", padding=Spacing.LG)
        self.hl_card.grid(row=row, column=0, sticky="ew", pady=(0, Spacing.MD)); row += 1
        self.hl_card.grid_columnconfigure(1, weight=1)
        self.hl_card.grid_columnconfigure(3, weight=1)
        
        # Colors
        color_frame = ttk.Frame(self.hl_card); color_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, Spacing.MD))
        self.btn_base_color = tk.Button(color_frame, text="Màu Nền", command=self.select_base_color, bg=Colors.SURFACE, relief="flat", padx=Spacing.MD, cursor="hand2")
        self.btn_base_color.pack(side="left", padx=(0, 4))
        self.base_color_label = tk.Label(color_frame, text=f"  {self.highlight_base_color}  ", bg=self.highlight_base_color, fg="white", relief="solid", bd=1)
        self.base_color_label.pack(side="left", padx=(0, Spacing.LG))
        
        self.btn_outline_color = tk.Button(color_frame, text="Màu Viền", command=self.select_outline_color, bg=Colors.SURFACE, relief="flat", padx=Spacing.MD, cursor="hand2")
        self.btn_outline_color.pack(side="left", padx=(0, 4))
        self.outline_color_label = tk.Label(color_frame, text=f"  {self.highlight_outline_color}  ", bg=self.highlight_outline_color, fg="white", relief="solid", bd=1)
        self.outline_color_label.pack(side="left", padx=(0, Spacing.LG))
        
        self.btn_fill_color = tk.Button(color_frame, text="Màu Tô", command=self.select_fill_color, bg=Colors.SURFACE, relief="flat", padx=Spacing.MD, cursor="hand2")
        self.btn_fill_color.pack(side="left", padx=(0, 4))
        self.fill_color_label = tk.Label(color_frame, text=f"  {self.highlight_fill_color}  ", bg=self.highlight_fill_color, fg="white", relief="solid", bd=1)
        self.fill_color_label.pack(side="left")
        
        # Parameters
        self.lbl_opacity = ttk.Label(self.hl_card, text="Độ trong suốt (%):")
        self.lbl_opacity.grid(row=1, column=0, sticky="w")
        ttk.Scale(self.hl_card, from_=0, to=100, variable=self.highlight_fill_opacity, orient="horizontal").grid(row=1, column=1, sticky="ew", padx=Spacing.SM)
        self.lbl_threshold = ttk.Label(self.hl_card, text="Ngưỡng phát hiện (0-255):")
        self.lbl_threshold.grid(row=1, column=2, sticky="e", padx=Spacing.SM)
        ttk.Entry(self.hl_card, textvariable=self.pdf_diff_threshold, width=8).grid(row=1, column=3, sticky="w")
        
        self.lbl_dilate_size = ttk.Label(self.hl_card, text="Độ dày vùng tô (1-9):")
        self.lbl_dilate_size.grid(row=2, column=0, sticky="w", pady=Spacing.SM)
        ttk.Entry(self.hl_card, textvariable=self.pdf_dilate_size, width=8).grid(row=2, column=1, sticky="w", padx=Spacing.SM)
        self.lbl_dilate_iter = ttk.Label(self.hl_card, text="Số lần mở rộng (1-3):")
        self.lbl_dilate_iter.grid(row=2, column=2, sticky="e", padx=Spacing.SM)
        ttk.Entry(self.hl_card, textvariable=self.pdf_dilate_iterations, width=8).grid(row=2, column=3, sticky="w")
        
        # ==================== STATUS BAR ====================
        status_frame = ttk.Frame(self.master, style="Surface.TFrame")
        status_frame.pack(side="bottom", fill="x")
        
        self.status_label = ttk.Label(status_frame, text="✅ " + get_text("status_ready", self.current_lang), style="TLabel")
        self.status_label.pack(side="left", padx=Spacing.LG, pady=Spacing.SM)
        
        self.status_version_label = ttk.Label(status_frame, text=f"Phiên bản {config.APP_VERSION} | {config.APP_DATE}", style="Muted.TLabel")
        self.status_version_label.pack(side="right", padx=Spacing.LG, pady=Spacing.SM)

    def on_doc_mode_change(self, event=None):
        idx = self.doc_mode_combo.current()
        if idx < 0:
            self.doc_mode_selected = False
            self.doc_mode_var.set("")
            self.print_area_var.set("")
            self._invalidate_pair_confirmation()
            return
        self.doc_mode_selected = True
        if idx == 1:
            self.doc_mode_var.set(config.DOC_MODE_DUKC_CTTT)
            self.print_area_var.set(config.PRINT_AREA_DUKC_CTTT)
            self.update_status("Chế độ: CTTT Đính kèm ĐƯKC (Vùng in: J2:BD76)")
        elif idx == 2:
            self.doc_mode_var.set(config.DOC_MODE_DUKC_OTHER)
            self.print_area_var.set(config.PRINT_AREA_DUKC_OTHER)
            self.update_status("Chế độ: Tờ phát hành ĐƯKC & Khác (Vùng in: A1:AT120 - Sheet Form)")
        else:
            self.doc_mode_var.set(config.DOC_MODE_STANDARD_CTTT)
            self.print_area_var.set(config.PRINT_AREA_STANDARD_CTTT)
            self.update_status("Chế độ: CTTT thông thường có form từ EX...xanh (Vùng in: EX1:GR76)")
        self._invalidate_pair_confirmation()

    def _invalidate_pair_confirmation(self):
        """Require confirmation again whenever inputs or document type change."""
        self.pairs_confirmed = False
        self.workflow_validation_error = None
        self._refresh_workflow_state()

    def _refresh_workflow_state(self):
        """Gate each action until the previous workflow step is complete."""
        if not hasattr(self, "btn_select_old"):
            return

        has_doc_mode = bool(getattr(self, "doc_mode_selected", False))
        has_new = bool(self.new_files)
        has_old = bool(self.old_files)
        counts_match = has_new and has_old and len(self.new_files) == len(self.old_files)
        ready = has_doc_mode and counts_match and self.pairs_confirmed and not self.is_processing

        self.btn_select_new.config(state="normal" if has_doc_mode and not self.is_processing else "disabled")
        self.btn_select_old.config(state="normal" if has_doc_mode and has_new and not self.is_processing else "disabled")
        self.btn_check_order.config(state="normal" if counts_match and not self.is_processing else "disabled")
        self.btn_run.config(state="normal" if ready else "disabled")
        self.btn_legacy.config(state="normal" if ready else "disabled")

        validation_error = getattr(self, "workflow_validation_error", None)
        if not has_doc_mode:
            message = "Bước 1/5: Chọn loại tài liệu so sánh để mở khóa bước chọn file."
            step_states = [("current", "Bước 1 — Chọn loại tài liệu so sánh"), ("blocked", "Bước 2 — Chọn CTTT mới"), ("blocked", "Bước 3 — Chọn CTTT cũ"), ("blocked", "Bước 4 — Kiểm tra & xác nhận cặp"), ("blocked", "Bước 5 — Bắt đầu so sánh")]
        elif not has_new:
            message = "Bước 2/5: Đã chọn loại tài liệu. Hãy chọn file CTTT mới."
            step_states = [("done", "Bước 1 — Đã chọn loại tài liệu"), ("current", "Bước 2 — Chọn CTTT mới"), ("blocked", "Bước 3 — Chọn CTTT cũ"), ("blocked", "Bước 4 — Kiểm tra & xác nhận cặp"), ("blocked", "Bước 5 — Bắt đầu so sánh")]
        elif not has_old:
            message = "Bước 3/5: Đã chọn file mới. Hãy chọn file CTTT cũ tương ứng."
            step_states = [("done", "Bước 1 — Đã chọn loại tài liệu"), ("done", "Bước 2 — Đã chọn CTTT mới"), ("current", "Bước 3 — Chọn CTTT cũ"), ("blocked", "Bước 4 — Kiểm tra & xác nhận cặp"), ("blocked", "Bước 5 — Bắt đầu so sánh")]
        elif not counts_match:
            message = (
                f"Bước 3/5 chưa hợp lệ: số file mới ({len(self.new_files)}) và "
                f"file cũ ({len(self.old_files)}) chưa bằng nhau."
            )
            step_states = [("done", "Bước 1 — Đã chọn loại tài liệu"), ("done", "Bước 2 — Đã chọn CTTT mới"), ("error", "Bước 3 — Số lượng file mới/cũ chưa khớp"), ("blocked", "Bước 4 — Kiểm tra & xác nhận cặp"), ("blocked", "Bước 5 — Bắt đầu so sánh")]
        elif validation_error:
            message = "Bước 4/5 chưa hợp lệ: loại tài liệu đã chọn không khớp với form trong file."
            step_states = [("done", "Bước 1 — Đã chọn loại tài liệu"), ("done", "Bước 2 — Đã chọn CTTT mới"), ("done", "Bước 3 — Đã chọn CTTT cũ"), ("error", "Bước 4 — Chọn đúng loại tài liệu hoặc thay file"), ("blocked", "Bước 5 — Bắt đầu so sánh")]
        elif not self.pairs_confirmed:
            message = "Bước 4/5: Kiểm tra thứ tự từng cặp rồi bấm 'Xác nhận & Lưu'."
            step_states = [("done", "Bước 1 — Đã chọn loại tài liệu"), ("done", "Bước 2 — Đã chọn CTTT mới"), ("done", "Bước 3 — Đã chọn CTTT cũ"), ("current", "Bước 4 — Kiểm tra & xác nhận cặp"), ("blocked", "Bước 5 — Bắt đầu so sánh")]
        elif self.is_processing:
            message = "Bước 5/5: Đang chạy so sánh, vui lòng chờ hoàn tất."
            step_states = [("done", "Bước 1 — Đã chọn loại tài liệu"), ("done", "Bước 2 — Đã chọn CTTT mới"), ("done", "Bước 3 — Đã chọn CTTT cũ"), ("done", "Bước 4 — Đã xác nhận cặp"), ("current", "Bước 5 — Đang chạy so sánh")]
        else:
            message = "✅ Đã hoàn tất 4 bước. Bạn có thể bắt đầu so sánh."
            step_states = [("done", "Bước 1 — Đã chọn loại tài liệu"), ("done", "Bước 2 — Đã chọn CTTT mới"), ("done", "Bước 3 — Đã chọn CTTT cũ"), ("done", "Bước 4 — Đã xác nhận cặp"), ("done", "Bước 5 — Sẵn sàng bắt đầu so sánh")]

        self.lbl_workflow.config(text=message)
        palette = {
            "done": ("●", "#166534", "#DCFCE7"),
            "current": ("●", "#C2410C", "#FFEDD5"),
            "error": ("●", "#B91C1C", "#FEE2E2"),
            "blocked": ("○", "#6B7280", "#F3F4F6"),
        }
        for label, (state, text) in zip(getattr(self, "workflow_step_labels", []), step_states):
            icon, foreground, background = palette[state]
            label.config(text=f"{icon}  {text}", fg=foreground, bg=background)

    def _show_workflow_error(self):
        if not getattr(self, "doc_mode_selected", False):
            message = "Bước 1 chưa hoàn tất: vui lòng chọn loại tài liệu so sánh."
        elif not self.new_files:
            message = "Bước 2 chưa hoàn tất: vui lòng chọn file CTTT mới."
        elif not self.old_files:
            message = "Bước 3 chưa hoàn tất: vui lòng chọn file CTTT cũ."
        elif len(self.new_files) != len(self.old_files):
            message = "Số lượng file mới và cũ chưa khớp. Hãy bổ sung hoặc xóa file trước."
        elif not self.pairs_confirmed:
            message = "Bạn chưa kiểm tra và xác nhận thứ tự các cặp CTTT."
        else:
            return False
        messagebox.showwarning("Chưa thể tiếp tục", message, parent=self.master)
        return True

    def _validate_document_mode_selection(self):
        """Block an incompatible document mode before a background thread is started."""
        from services.validation_service import ValidationService

        is_valid, error_message = ValidationService.validate_document_mode(
            self.new_files,
            self.old_files,
            self.doc_mode_var.get(),
        )
        if is_valid:
            self.workflow_validation_error = None
            self._refresh_workflow_state()
            return True

        self.workflow_validation_error = error_message
        self._refresh_workflow_state()
        messagebox.showerror(
            "Loại tài liệu không phù hợp",
            error_message,
            parent=self.master,
        )
        return False
            
    def on_screen_mode_change(self, event=None):
        mode_idx = self.screen_combo.current()
        modes = ["pc", "vps", "monitor"]
        if 0 <= mode_idx < len(modes):
            self.screen_mode.set(modes[mode_idx])

    # ========== FILE SELECTION METHODS ==========
    def select_new_files(self, append_only=False):
        initial_dir = self.new_dir_path.get().strip()
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = os.getcwd()
        
        title_texts = {"vi": "Chọn file CTTT mới", "en": "Select new CTTT files", "zh": "选择新CTTT文件", "ja": "新CTTTファイルを選択"}
        filetype_texts = {"vi": "File Excel", "en": "Excel Files", "zh": "Excel文件", "ja": "Excelファイル"}
        
        files = filedialog.askopenfilenames(
            initialdir=initial_dir,
            title=title_texts.get(self.current_lang, title_texts["vi"]),
            filetypes=[(filetype_texts.get(self.current_lang, filetype_texts["vi"]), "*.xls *.xlsx *.xlsm")]
        )
        
        if not files:
            return
            
        new_selected = list(files)
        
        # Nếu trước đó đã có file trong danh sách và không phải chế độ ép buộc bổ sung
        if self.new_files and not append_only:
            dialog_titles = {
                "vi": "Bổ sung hoặc Thay thế file CTTT mới",
                "en": "Append or Replace New CTTT Files",
                "zh": "追加或替换新CTTT文件",
                "ja": "新CTTTファイルの追加または置換"
            }
            dialog_msgs = {
                "vi": f"Hiện đang có {len(self.new_files)} file CTTT mới đã chọn trước đó.\n"
                      f"Bạn vừa chọn {len(new_selected)} file.\n\n"
                      f"• [Có / Yes]: BỔ SUNG thêm vào danh sách (giữ file cũ, thêm file mới)\n"
                      f"• [Không / No]: THAY THẾ toàn bộ bằng danh sách mới\n"
                      f"• [Hủy / Cancel]: Giữ nguyên danh sách hiện tại",
                "en": f"{len(self.new_files)} new CTTT files already selected.\n"
                      f"You just selected {len(new_selected)} files.\n\n"
                      f"• [Yes]: APPEND to current list (keep old, add new)\n"
                      f"• [No]: REPLACE all with new files\n"
                      f"• [Cancel]: Keep current list",
                "zh": f"当前已选择 {len(self.new_files)} 个新CTTT文件。\n"
                      f"您刚刚选择了 {len(new_selected)} 个文件。\n\n"
                      f"• [是 / Yes]: 追加到当前列表\n"
                      f"• [否 / No]: 用新文件全部替换\n"
                      f"• [取消 / Cancel]: 保持不变",
                "ja": f"現在 {len(self.new_files)} 個の新CTTTファイルが選択されています。\n"
                      f"新しく {len(new_selected)} 個のファイルを選択しました。\n\n"
                      f"• [はい / Yes]: 現在のリストに追加\n"
                      f"• [いいえ / No]: 新規ファイルですべて置換\n"
                      f"• [キャンセル]: 変更しない"
            }
            
            ans = messagebox.askyesnocancel(
                dialog_titles.get(self.current_lang, dialog_titles["vi"]),
                dialog_msgs.get(self.current_lang, dialog_msgs["vi"]),
                parent=self.master
            )
            
            if ans is None:
                return  # Cancel
            elif ans is True:
                # Bổ sung - loại bỏ trùng lặp
                existing = {os.path.normcase(os.path.normpath(f)) for f in self.new_files}
                added_count = 0
                for f in new_selected:
                    norm = os.path.normcase(os.path.normpath(f))
                    if norm not in existing:
                        self.new_files.append(f)
                        existing.add(norm)
                        added_count += 1
                utils.logger.info(f"Appended {added_count} files to new_files. Total: {len(self.new_files)}")
            else:
                # Thay thế
                self.new_files = new_selected
        else:
            if append_only and self.new_files:
                existing = {os.path.normcase(os.path.normpath(f)) for f in self.new_files}
                for f in new_selected:
                    norm = os.path.normcase(os.path.normpath(f))
                    if norm not in existing:
                        self.new_files.append(f)
                        existing.add(norm)
            else:
                self.new_files = new_selected
        
        if self.new_files:
            self.new_dir_path.set(os.path.dirname(self.new_files[0]))
            file_names = ', '.join([os.path.basename(f) for f in self.new_files])
            self.new_files_display.set(file_names)
            self._auto_save_settings()
            self._invalidate_pair_confirmation()

    def select_old_files(self, append_only=False):
        initial_dir = self.old_dir_path.get().strip()
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = os.getcwd()
        
        title_texts = {"vi": "Chọn file CTTT cũ", "en": "Select old CTTT files", "zh": "选择旧CTTT文件", "ja": "旧CTTTファイルを選択"}
        filetype_texts = {"vi": "File Excel", "en": "Excel Files", "zh": "Excel文件", "ja": "Excelファイル"}
        
        files = filedialog.askopenfilenames(
            initialdir=initial_dir,
            title=title_texts.get(self.current_lang, title_texts["vi"]),
            filetypes=[(filetype_texts.get(self.current_lang, filetype_texts["vi"]), "*.xls *.xlsx *.xlsm")]
        )
        
        if not files:
            return
            
        new_selected = list(files)
        
        if self.old_files and not append_only:
            dialog_titles = {
                "vi": "Bổ sung hoặc Thay thế file CTTT cũ",
                "en": "Append or Replace Old CTTT Files",
                "zh": "追加或替换旧CTTT文件",
                "ja": "旧CTTTファイルの追加または置換"
            }
            dialog_msgs = {
                "vi": f"Hiện đang có {len(self.old_files)} file CTTT cũ trong danh sách.\n"
                      f"Bạn vừa chọn {len(new_selected)} file.\n\n"
                      f"• [Có / Yes]: BỔ SUNG thêm vào danh sách (giữ file cũ, thêm file mới)\n"
                      f"• [Không / No]: THAY THẾ toàn bộ bằng danh sách mới\n"
                      f"• [Hủy / Cancel]: Giữ nguyên danh sách hiện tại",
                "en": f"{len(self.old_files)} old CTTT files already selected.\n"
                      f"You just selected {len(new_selected)} files.\n\n"
                      f"• [Yes]: APPEND to current list (keep old, add new)\n"
                      f"• [No]: REPLACE all with new files\n"
                      f"• [Cancel]: Keep current list",
                "zh": f"当前已选择 {len(self.old_files)} 个旧CTTT文件。\n"
                      f"您刚刚选择了 {len(new_selected)} 个文件。\n\n"
                      f"• [是 / Yes]: 追加到当前列表\n"
                      f"• [否 / No]: 用新文件全部替换\n"
                      f"• [取消 / Cancel]: 保持不变",
                "ja": f"現在 {len(self.old_files)} 個の旧CTTTファイルが選択されています。\n"
                      f"新しく {len(new_selected)} 個のファイルを選択しました。\n\n"
                      f"• [はい / Yes]: 現在のリストに追加\n"
                      f"• [いいえ / No]: 新規ファイルですべて置換\n"
                      f"• [キャンセル]: 変更しない"
            }
            
            ans = messagebox.askyesnocancel(
                dialog_titles.get(self.current_lang, dialog_titles["vi"]),
                dialog_msgs.get(self.current_lang, dialog_msgs["vi"]),
                parent=self.master
            )
            
            if ans is None:
                return
            elif ans is True:
                existing = {os.path.normcase(os.path.normpath(f)) for f in self.old_files}
                added_count = 0
                for f in new_selected:
                    norm = os.path.normcase(os.path.normpath(f))
                    if norm not in existing:
                        self.old_files.append(f)
                        existing.add(norm)
                        added_count += 1
                utils.logger.info(f"Appended {added_count} files to old_files. Total: {len(self.old_files)}")
            else:
                self.old_files = new_selected
        else:
            if append_only and self.old_files:
                existing = {os.path.normcase(os.path.normpath(f)) for f in self.old_files}
                for f in new_selected:
                    norm = os.path.normcase(os.path.normpath(f))
                    if norm not in existing:
                        self.old_files.append(f)
                        existing.add(norm)
            else:
                self.old_files = new_selected
                
        if self.old_files:
            self.old_dir_path.set(os.path.dirname(self.old_files[0]))
            file_names = ', '.join([os.path.basename(f) for f in self.old_files])
            self.old_files_display.set(file_names)
            self._auto_save_settings()
            self._invalidate_pair_confirmation()

    def browse_result_folder(self):
        title_texts = {"vi": "Chọn thư mục lưu kết quả", "en": "Select result folder", "zh": "选择结果文件夹", "ja": "結果フォルダを選択"}
        folder = filedialog.askdirectory(title=title_texts.get(self.current_lang, title_texts["vi"]))
        if folder:
            self.result_path.set(folder)

    def show_help(self):
        ModernHelpWindow(self.master, self.current_lang)

    def check_order(self):
        if not self.new_files or not self.old_files or len(self.new_files) != len(self.old_files):
            self._show_workflow_error()
            return
        self.show_confirmation_dialog()

    def show_confirmation_dialog(self):
        """Hiển thị hộp thoại xác nhận thứ tự các cặp file CTTT để người dùng kiểm tra, bổ sung và sắp xếp lại"""
        lang = self.current_lang
        
        if not self.new_files and not self.old_files:
            warning_titles = {"vi": "Chưa chọn file", "en": "No files selected", "zh": "未选择文件", "ja": "ファイル未選択"}
            missing_files_msgs = {
                "vi": "Bạn cần chọn file CTTT trước khi kiểm tra.",
                "en": "Please select CTTT files before checking.",
                "zh": "请先选择CTTT文件再进行检查。",
                "ja": "確認する前にCTTTファイルを選択してください。"
            }
            messagebox.showwarning(warning_titles.get(lang, warning_titles["vi"]), missing_files_msgs.get(lang, missing_files_msgs["vi"]), parent=self.master)
            return

        # Dialog texts
        dialog_titles = {"vi": "🔍 Kiểm tra & Sắp xếp các cặp CTTT", "en": "🔍 Check & Reorder CTTT pairs", "zh": "🔍 检查并排序CTTT配对", "ja": "🔍 CTTTペアの確認と並べ替え"}
        hint_texts = {"vi": "💡 Kéo thả từng dòng để đổi thứ tự đối ứng. Dùng nút '➕ Thêm' để chọn bổ sung nếu bị thiếu file!", 
                      "en": "💡 Drag & drop to reorder pairs. Use '➕ Add' to append missing files!", 
                      "zh": "💡 拖放以重新排序。使用 '➕ 添加' 按钮补充缺少的文件！", 
                      "ja": "💡 ドラッグ＆ドロップで並べ替え。'➕ 追加' ボタンで不足ファイルを追加できます！"}
        confirm_btn_texts = {"vi": "✅ Xác nhận & Lưu", "en": "✅ Confirm & Save", "zh": "✅ 确认并保存", "ja": "✅ 確認して保存"}
        delete_selected_texts = {"vi": "🗑️ Xóa cả 2 mục đang chọn", "en": "🗑️ Delete both selected", "zh": "🗑️ 删除两个选中项", "ja": "🗑️ 両方の選択項目を削除"}
        close_btn_texts = {"vi": "❌ Đóng", "en": "❌ Close", "zh": "❌ 关闭", "ja": "❌ 閉じる"}
        add_new_texts = {"vi": "➕ Thêm CTTT Mới", "en": "➕ Add New CTTT", "zh": "➕ 添加新CTTT", "ja": "➕ 新CTTT追加"}
        add_old_texts = {"vi": "➕ Thêm CTTT Cũ", "en": "➕ Add Old CTTT", "zh": "➕ 添加旧CTTT", "ja": "➕ 旧CTTT追加"}
        del_new_texts = {"vi": "🗑️ Xóa file chọn", "en": "🗑️ Delete selected", "zh": "🗑️ 删除选中项", "ja": "🗑️ 選択項目を削除"}
        del_old_texts = {"vi": "🗑️ Xóa file chọn", "en": "🗑️ Delete selected", "zh": "🗑️ 删除选中项", "ja": "🗑️ 選択項目を削除"}

        # Tạo cửa sổ con để hiển thị danh sách file
        self.confirmation_window = tk.Toplevel(self.master)
        self.confirmation_window.title(dialog_titles.get(lang, dialog_titles["vi"]))
        self.confirmation_window.geometry("860x560")
        self.confirmation_window.minsize(720, 460)
        self.confirmation_window.configure(bg=Colors.BG_MAIN)
        self.confirmation_window.transient(self.master)
        
        # Khởi tạo drag data
        self.drag_data = {}
        
        # Header frame
        header_frame = ttk.Frame(self.confirmation_window, padding=Spacing.SM)
        header_frame.pack(fill="x", padx=Spacing.MD, pady=(Spacing.SM, 0))
        
        lbl_hint = ttk.Label(header_frame, text=hint_texts.get(lang, hint_texts["vi"]), style="Subheader.TLabel", wraplength=820)
        lbl_hint.pack(anchor="w")
        
        # Match status label
        self.lbl_match_status = tk.Label(header_frame, font=Fonts.get("base", "bold"), anchor="w", pady=4)
        self.lbl_match_status.pack(fill="x")
        
        # Tạo khung chứa 2 cột song song
        listbox_frame = ttk.Frame(self.confirmation_window)
        listbox_frame.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.SM)
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(1, weight=1)
        listbox_frame.grid_rowconfigure(1, weight=1)
        
        # Header labels
        self.lbl_new_header = ttk.Label(listbox_frame, text=f"📂 CTTT Mới ({len(self.new_files)} file)", font=Fonts.get("base", "bold"))
        self.lbl_new_header.grid(row=0, column=0, sticky="w", padx=Spacing.SM, pady=(0, 4))
        
        self.lbl_old_header = ttk.Label(listbox_frame, text=f"📂 CTTT Cũ ({len(self.old_files)} file)", font=Fonts.get("base", "bold"))
        self.lbl_old_header.grid(row=0, column=1, sticky="w", padx=Spacing.SM, pady=(0, 4))
        
        # Left container with scrollbar
        left_subframe = ttk.Frame(listbox_frame)
        left_subframe.grid(row=1, column=0, sticky="nsew", padx=Spacing.SM)
        left_subframe.grid_columnconfigure(0, weight=1)
        left_subframe.grid_rowconfigure(0, weight=1)
        
        self.new_files_listbox = tk.Listbox(left_subframe, selectmode=tk.SINGLE, font=Fonts.get("base"), exportselection=False)
        self.new_files_listbox.grid(row=0, column=0, sticky="nsew")
        new_scroll = ttk.Scrollbar(left_subframe, orient="vertical", command=self.new_files_listbox.yview)
        new_scroll.grid(row=0, column=1, sticky="ns")
        self.new_files_listbox.config(yscrollcommand=new_scroll.set)
        
        # Left sub buttons (Thêm / Xóa)
        left_btn_frame = ttk.Frame(left_subframe)
        left_btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        
        def _add_more_new_files():
            self.select_new_files(append_only=True)
            _refresh_dialog_lists()
            
        def _del_selected_new_file():
            sel = self.new_files_listbox.curselection()
            idx = None
            if sel and len(sel) > 0:
                idx = sel[0]
            else:
                active = self.new_files_listbox.index(tk.ACTIVE)
                if active is not None and 0 <= active < len(self.new_files):
                    idx = active
            
            if idx is not None and 0 <= idx < len(self.new_files):
                self.new_files.pop(idx)
                self._invalidate_pair_confirmation()
                _refresh_dialog_lists()
                if len(self.new_files) > 0:
                    new_idx = min(idx, len(self.new_files) - 1)
                    self.new_files_listbox.selection_set(new_idx)
                    self.new_files_listbox.activate(new_idx)
                
        ttk.Button(left_btn_frame, text=add_new_texts.get(lang, add_new_texts["vi"]), command=_add_more_new_files, style="Primary.TButton").pack(side="left", padx=(0, Spacing.XS))
        ttk.Button(left_btn_frame, text=del_new_texts.get(lang, del_new_texts["vi"]), command=_del_selected_new_file, style="Secondary.TButton").pack(side="left")
        
        # Right container with scrollbar
        right_subframe = ttk.Frame(listbox_frame)
        right_subframe.grid(row=1, column=1, sticky="nsew", padx=Spacing.SM)
        right_subframe.grid_columnconfigure(0, weight=1)
        right_subframe.grid_rowconfigure(0, weight=1)
        
        self.old_files_listbox = tk.Listbox(right_subframe, selectmode=tk.SINGLE, font=Fonts.get("base"), exportselection=False)
        self.old_files_listbox.grid(row=0, column=0, sticky="nsew")
        old_scroll = ttk.Scrollbar(right_subframe, orient="vertical", command=self.old_files_listbox.yview)
        old_scroll.grid(row=0, column=1, sticky="ns")
        self.old_files_listbox.config(yscrollcommand=old_scroll.set)
        
        # Right sub buttons (Thêm / Xóa)
        right_btn_frame = ttk.Frame(right_subframe)
        right_btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        
        def _add_more_old_files():
            self.select_old_files(append_only=True)
            _refresh_dialog_lists()
            
        def _del_selected_old_file():
            sel = self.old_files_listbox.curselection()
            idx = None
            if sel and len(sel) > 0:
                idx = sel[0]
            else:
                active = self.old_files_listbox.index(tk.ACTIVE)
                if active is not None and 0 <= active < len(self.old_files):
                    idx = active
                    
            if idx is not None and 0 <= idx < len(self.old_files):
                self.old_files.pop(idx)
                self._invalidate_pair_confirmation()
                _refresh_dialog_lists()
                if len(self.old_files) > 0:
                    new_idx = min(idx, len(self.old_files) - 1)
                    self.old_files_listbox.selection_set(new_idx)
                    self.old_files_listbox.activate(new_idx)
                
        ttk.Button(right_btn_frame, text=add_old_texts.get(lang, add_old_texts["vi"]), command=_add_more_old_files, style="Primary.TButton").pack(side="left", padx=(0, Spacing.XS))
        ttk.Button(right_btn_frame, text=del_old_texts.get(lang, del_old_texts["vi"]), command=_del_selected_old_file, style="Secondary.TButton").pack(side="left")
        
        # Helper to refresh dialog lists and match label
        def _refresh_dialog_lists():
            # Save selections before refresh
            cur_new = self.new_files_listbox.curselection()
            cur_old = self.old_files_listbox.curselection()
            
            self.new_files_listbox.delete(0, tk.END)
            for f in self.new_files:
                self.new_files_listbox.insert(tk.END, os.path.basename(f))
                
            self.old_files_listbox.delete(0, tk.END)
            for f in self.old_files:
                self.old_files_listbox.insert(tk.END, os.path.basename(f))
                
            # Restore selections if valid
            if cur_new and cur_new[0] < len(self.new_files):
                self.new_files_listbox.selection_set(cur_new[0])
            if cur_old and cur_old[0] < len(self.old_files):
                self.old_files_listbox.selection_set(cur_old[0])
                
            n_new = len(self.new_files)
            n_old = len(self.old_files)
            
            new_title = {"vi": f"📂 CTTT Mới ({n_new} file)", "en": f"📂 New CTTT ({n_new} files)", "zh": f"📂 新CTTT ({n_new} 文件)", "ja": f"📂 新CTTT ({n_new} 件)"}
            old_title = {"vi": f"📂 CTTT Cũ ({n_old} file)", "en": f"📂 Old CTTT ({n_old} files)", "zh": f"📂 旧CTTT ({n_old} 文件)", "ja": f"📂 旧CTTT ({n_old} 件)"}
            
            self.lbl_new_header.config(text=new_title.get(lang, new_title["vi"]))
            self.lbl_old_header.config(text=old_title.get(lang, old_title["vi"]))
            
            if n_new == n_old and n_new > 0:
                match_txt = {"vi": f"✅ Khớp số lượng: {n_new} cặp file CTTT (Đủ điều kiện so sánh)",
                             "en": f"✅ Count matched: {n_new} CTTT file pairs (Ready to compare)",
                             "zh": f"✅ 数量匹配: {n_new} 对CTTT文件 (准备就绪)",
                             "ja": f"✅ ファイル数一致: {n_new} ペア (比較可能)"}
                self.lbl_match_status.config(text=match_txt.get(lang, match_txt["vi"]), fg="#16A34A")
            else:
                diff_txt = {"vi": f"⚠️ CHƯA KHỚP SỐ LƯỢNG: CTTT Mới ({n_new} file) ≠ CTTT Cũ ({n_old} file). Bấm '➕ Thêm' để chọn bù hoặc '🗑️ Xóa' để cân bằng!",
                            "en": f"⚠️ COUNT MISMATCH: New ({n_new}) ≠ Old ({n_old}). Click '➕ Add' or '🗑️ Delete' to balance!",
                            "zh": f"⚠️ 数量不匹配: 新 ({n_new}) ≠ 旧 ({n_old})。请点击 '➕ 添加' 或 '🗑️ 删除' 进行平衡！",
                            "ja": f"⚠️ ファイル数不一致: 新 ({n_new}) ≠ 旧 ({n_old})。'➕ 追加' または '🗑️ 削除' で数を揃えてください！"}
                self.lbl_match_status.config(text=diff_txt.get(lang, diff_txt["vi"]), fg="#DC2626")
            
            # Cập nhật hiển thị ngoài main window
            file_names_new = ', '.join([os.path.basename(f) for f in self.new_files])
            file_names_old = ', '.join([os.path.basename(f) for f in self.old_files])
            self.new_files_display.set(file_names_new)
            self.old_files_display.set(file_names_old)
            self._auto_save_settings()

        # Load initial items
        _refresh_dialog_lists()

        # Gán sự kiện kéo thả cho cả 2 listbox
        self.new_files_listbox.bind("<Button-1>", self.on_drag_start)
        self.new_files_listbox.bind("<B1-Motion>", self.on_drag_motion)
        self.new_files_listbox.bind("<ButtonRelease-1>", self.on_drag_release)
        self.new_files_listbox.bind("<Delete>", lambda e: _del_selected_new_file())
        self.new_files_listbox.bind("<BackSpace>", lambda e: _del_selected_new_file())

        self.old_files_listbox.bind("<Button-1>", self.on_drag_start)
        self.old_files_listbox.bind("<B1-Motion>", self.on_drag_motion)
        self.old_files_listbox.bind("<ButtonRelease-1>", self.on_drag_release)
        self.old_files_listbox.bind("<Delete>", lambda e: _del_selected_old_file())
        self.old_files_listbox.bind("<BackSpace>", lambda e: _del_selected_old_file())

        # Tạo nút xác nhận và xóa ở chân dialog
        btn_frame = ttk.Frame(self.confirmation_window, padding=Spacing.SM)
        btn_frame.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)
        
        def _on_confirm_click():
            if len(self.new_files) != len(self.old_files):
                warn_titles = {"vi": "Số lượng chưa khớp", "en": "Count mismatch", "zh": "数量不匹配", "ja": "数が一致しません"}
                warn_msgs = {
                    "vi": f"Số lượng file chưa khớp nhau!\nCTTT Mới: {len(self.new_files)} file\nCTTT Cũ: {len(self.old_files)} file\n\nVui lòng bấm '➕ Thêm' để chọn bổ sung file còn thiếu hoặc '🗑️ Xóa' bớt file thừa trước khi xác nhận!",
                    "en": f"File count does not match!\nNew: {len(self.new_files)}, Old: {len(self.old_files)}\n\nPlease click '➕ Add' to append missing files or '🗑️ Delete' to balance before confirming!",
                    "zh": f"文件数量不匹配！\n新: {len(self.new_files)}, 旧: {len(self.old_files)}\n\n请在确认前点击 '➕ 添加' 补充文件或 '🗑️ 删除' 平衡数量！",
                    "ja": f"ファイル数が一致していません！\n新: {len(self.new_files)}, 旧: {len(self.old_files)}\n\n確認前に '➕ 追加' で不足ファイルを追加するか '🗑️ 削除' で数を揃えてください！"
                }
                messagebox.showwarning(warn_titles.get(lang, warn_titles["vi"]), warn_msgs.get(lang, warn_msgs["vi"]), parent=self.confirmation_window)
                return
            self.confirm_files()

        ttk.Button(btn_frame, text=confirm_btn_texts.get(lang, confirm_btn_texts["vi"]), command=_on_confirm_click, style="Primary.TButton").pack(side="left", padx=Spacing.SM)
        ttk.Button(btn_frame, text=delete_selected_texts.get(lang, delete_selected_texts["vi"]), command=lambda: (self.delete_selected_items(), _refresh_dialog_lists()), style="Secondary.TButton").pack(side="left", padx=Spacing.SM)
        ttk.Button(btn_frame, text=close_btn_texts.get(lang, close_btn_texts["vi"]), command=self.confirmation_window.destroy, style="Secondary.TButton").pack(side="right", padx=Spacing.SM)

    def on_drag_start(self, event):
        """Xử lý sự kiện bắt đầu kéo thả trong listbox"""
        widget = event.widget
        self.drag_data["widget"] = widget
        self.drag_data["index"] = widget.nearest(event.y)
        self.drag_data["item"] = widget.get(self.drag_data["index"]) if self.drag_data["index"] >= 0 else None
        self.drag_data["moved"] = False

    def on_drag_motion(self, event):
        """Xử lý sự kiện kéo thả trong listbox, cho phép sắp xếp lại thứ tự file"""
        widget = event.widget
        if not self.drag_data.get("widget") or widget != self.drag_data.get("widget"):
            return
        index = widget.nearest(event.y)
        old_index = self.drag_data.get("index")
        
        target_list = self.new_files if widget == self.new_files_listbox else self.old_files
        
        if old_index is not None and index != old_index and 0 <= old_index < len(target_list) and 0 <= index < len(target_list):
            widget.delete(old_index)
            widget.insert(index, self.drag_data["item"])
            widget.selection_clear(0, tk.END)
            widget.selection_set(index)
            target_list.insert(index, target_list.pop(old_index))
            self.drag_data["index"] = index
            self.drag_data["moved"] = True

    def on_drag_release(self, event):
        """Xử lý sự kiện thả chuột, kết thúc quá trình kéo thả"""
        if self.drag_data.get("moved"):
            # Update main window display text
            file_names_new = ', '.join([os.path.basename(f) for f in self.new_files])
            file_names_old = ', '.join([os.path.basename(f) for f in self.old_files])
            self.new_files_display.set(file_names_new)
            self.old_files_display.set(file_names_old)
            self._auto_save_settings()
            self._invalidate_pair_confirmation()
        self.drag_data["item"] = None
        self.drag_data["index"] = None
        self.drag_data["widget"] = None
        self.drag_data["moved"] = False

    def delete_selected_items(self):
        """Xóa các mục được chọn khỏi cả hai listbox và danh sách file tương ứng"""
        selected_new_index = self.new_files_listbox.curselection()
        selected_old_index = self.old_files_listbox.curselection()

        if not selected_new_index:
            active_new = self.new_files_listbox.index(tk.ACTIVE)
            if active_new is not None and 0 <= active_new < len(self.new_files):
                selected_new_index = (active_new,)

        if not selected_old_index:
            active_old = self.old_files_listbox.index(tk.ACTIVE)
            if active_old is not None and 0 <= active_old < len(self.old_files):
                selected_old_index = (active_old,)

        if selected_new_index:
            selected_index = selected_new_index[0]
            if selected_index < len(self.new_files):
                self.new_files.pop(selected_index)
            
        if selected_old_index:
            selected_index = selected_old_index[0]
            if selected_index < len(self.old_files):
                self.old_files.pop(selected_index)

        # Cập nhật hiển thị tên file trong các entry sau khi xóa
        file_names_new = ', '.join([os.path.basename(f) for f in self.new_files])
        file_names_old = ', '.join([os.path.basename(f) for f in self.old_files])
        self.new_files_display.set(file_names_new)
        self.old_files_display.set(file_names_old)
        self._auto_save_settings()
        self._invalidate_pair_confirmation()

    def confirm_files(self):
        """Xác nhận và áp dụng thứ tự file đã sắp xếp, đóng cửa sổ xác nhận"""
        lang = self.current_lang
        if not self._validate_document_mode_selection():
            return False
        self.pairs_confirmed = True
        self._refresh_workflow_state()

        # Sync doc_mode_var and print_area_var from combo
        if hasattr(self, 'doc_mode_combo'):
            idx = self.doc_mode_combo.current()
            if idx == 1:
                self.doc_mode_var.set(config.DOC_MODE_DUKC_CTTT)
                self.print_area_var.set(config.PRINT_AREA_DUKC_CTTT)
            elif idx == 2:
                self.doc_mode_var.set(config.DOC_MODE_DUKC_OTHER)
                self.print_area_var.set(config.PRINT_AREA_DUKC_OTHER)
            else:
                self.doc_mode_var.set(config.DOC_MODE_STANDARD_CTTT)
                self.print_area_var.set(config.PRINT_AREA_STANDARD_CTTT)

        # Cập nhật hiển thị tên file trong các entry chính
        file_names_new = ', '.join([os.path.basename(f) for f in self.new_files])
        file_names_old = ', '.join([os.path.basename(f) for f in self.old_files])
        self.new_files_display.set(file_names_new)
        self.old_files_display.set(file_names_old)
        self._auto_save_settings()

        # Close the ordering dialog immediately after a successful save. Keeping
        # it alive until after showinfo makes the UI appear as if confirm did not work.
        if hasattr(self, 'confirmation_window') and self.confirmation_window:
            try:
                self.confirmation_window.destroy()
            finally:
                self.confirmation_window = None

        confirm_titles = {"vi": "Xác nhận", "en": "Confirmed", "zh": "已确认", "ja": "確認済み"}
        confirm_msgs = {
            "vi": f"Đã xác nhận {len(self.new_files)} cặp CTTT.",
            "en": f"Confirmed {len(self.new_files)} CTTT pairs.",
            "zh": f"已确认 {len(self.new_files)} 对CTTT文件。",
            "ja": f"{len(self.new_files)} 件のCTTTペアを確認しました。"
        }
        messagebox.showinfo(confirm_titles.get(lang, confirm_titles["vi"]), confirm_msgs.get(lang, confirm_msgs["vi"]), parent=self.master)
        return True

    # ========== RUN COMPARISON ==========
    def run_comparison(self):
        if self.is_processing:
            utils.logger.warning("Comparison is already in progress, ignoring duplicate trigger.")
            return

        # This guard also covers F5/Ctrl+Enter and the menu command, which do not
        # respect a disabled button state.
        if self._show_workflow_error():
            return

        if not self._validate_document_mode_selection():
            return

        lang = self.current_lang
        
        # Warning/Error messages translations
        warning_titles = {"vi": "Thiếu dữ liệu", "en": "Missing data", "zh": "缺少数据", "ja": "データ不足"}
        warning_msgs = {
            "vi": "Vui lòng chọn đủ file CTTT mới và cũ!",
            "en": "Please select both new and old CTTT files!",
            "zh": "请选择新旧CTTT文件！",
            "ja": "新旧CTTTファイルを両方選択してください！"
        }
        error_titles = {"vi": "Lỗi", "en": "Error", "zh": "错误", "ja": "エラー"}
        mismatch_msgs = {
            "vi": f"Số lượng file không khớp!\nMới: {len(self.new_files)}, Cũ: {len(self.old_files)}",
            "en": f"File count mismatch!\nNew: {len(self.new_files)}, Old: {len(self.old_files)}",
            "zh": f"文件数量不匹配！\n新: {len(self.new_files)}, 旧: {len(self.old_files)}",
            "ja": f"ファイル数が一致しません！\n新: {len(self.new_files)}, 旧: {len(self.old_files)}"
        }
        processing_texts = {"vi": "🔄 Đang xử lý...", "en": "🔄 Processing...", "zh": "🔄 处理中...", "ja": "🔄 処理中..."}
        
        if not self.new_files or not self.old_files:
            messagebox.showwarning(warning_titles.get(lang, warning_titles["vi"]), warning_msgs.get(lang, warning_msgs["vi"]))
            return
        
        if len(self.new_files) != len(self.old_files):
            messagebox.showerror(error_titles.get(lang, error_titles["vi"]), mismatch_msgs.get(lang, mismatch_msgs["vi"]))
            return
        
        # Save Settings before running (Critical - matches legacy behavior)
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
                "doc_mode": self.doc_mode_var.get(),
                "print_area": self.print_area_var.get(),
            })
        
        self.is_processing = True
        self.btn_run.config(state="disabled")
        if hasattr(self, 'btn_legacy'):
            self.btn_legacy.config(state="disabled")
        self.update_status(processing_texts.get(lang, processing_texts["vi"]))
        
        thread = threading.Thread(target=self._run_thread, daemon=True)
        thread.start()

    def _run_thread(self):
        try:
            # Collect all settings to pass to comparator (Critical - from Gap Analysis)
            settings = {
                # Core settings (use both key names for compatibility)
                "dpi": self.pdf_render_dpi.get(),
                "pdf_dpi": self.pdf_render_dpi.get(),
                "zoom": self.zoom_var.get(),
                "zoom_level": self.zoom_var.get(),
                "goto_address": self.goto_address.get(),
                "auto_add_b": self.auto_add_b.get(),
                "output_folder": self.result_path.get().strip() or None,
                "suppress_error": self.suppress_error_popups.get(),
                "use_pdf_method": self.use_pdf_method.get(),
                "doc_mode": self.doc_mode_var.get(),
                "print_area": self.print_area_var.get(),
                
                # Highlight Colors (Critical - was missing)
                "highlight_base_color": self.highlight_base_color,
                "highlight_outline_color": self.highlight_outline_color,
                "highlight_fill_color": self.highlight_fill_color,
                
                # Highlight Settings
                "highlight_fill_opacity": self.highlight_fill_opacity.get(),
                "pdf_diff_threshold": self.pdf_diff_threshold.get(),
                "pdf_dilate_size": self.pdf_dilate_size.get(),
                "pdf_dilate_iterations": self.pdf_dilate_iterations.get(),
            }
            
            self.comparator.use_pdf_method = self.use_pdf_method.get()
            
            elapsed_time = self.comparator.start_comparison(
                self.new_files,
                self.old_files,
                status_callback=self.update_status,
                settings=settings
            )
            
            if elapsed_time:
                minutes, seconds = divmod(elapsed_time, 60)
                time_msg = f"\nThời gian: {int(minutes)} phút {seconds:.2f} giây"
            else:
                time_msg = ""
            
            self.update_status("✅ " + get_text("status_complete", self.current_lang))
            messagebox.showinfo(
                get_text("complete", self.current_lang), 
                get_text("complete_msg", self.current_lang) + time_msg
            )
        except Exception as e:
            self.update_status(f"❌ {get_text('status_error', self.current_lang)} {e}")
            messagebox.showerror(get_text("error", self.current_lang), str(e))
        finally:
            self.is_processing = False
            self.btn_run.config(state="normal")
            if hasattr(self, 'btn_legacy'):
                self.btn_legacy.config(state="normal")

    def update_status(self, msg):
        if len(msg) > 100:
            msg = msg[:97] + "..."
        self.status_label.config(text=msg)
        self.master.update_idletasks()
    
    # ========== LEGACY SCREENSHOT METHOD ==========
    def run_legacy_comparison(self):
        """Chạy phương pháp Legacy Screenshot (giống phiên bản cũ)"""
        if self.is_processing:
            utils.logger.warning("Comparison is already in progress, ignoring duplicate legacy trigger.")
            return

        if self._show_workflow_error():
            return

        if not self._validate_document_mode_selection():
            return

        lang = self.current_lang
        
        # Translations
        warning_titles = {"vi": "Thiếu dữ liệu", "en": "Missing data", "zh": "缺少数据", "ja": "データ不足"}
        warning_msgs = {
            "vi": "Vui lòng chọn đủ file CTTT mới và cũ!",
            "en": "Please select both new and old CTTT files!",
            "zh": "请选择新旧CTTT文件！",
            "ja": "新旧CTTTファイルを両方選択してください！"
        }
        error_titles = {"vi": "Lỗi", "en": "Error", "zh": "错误", "ja": "エラー"}
        mismatch_msgs = {
            "vi": f"Số file mới ({len(self.new_files)}) và cũ ({len(self.old_files)}) không khớp.",
            "en": f"New ({len(self.new_files)}) and old ({len(self.old_files)}) file count do not match.",
            "zh": f"新文件({len(self.new_files)})和旧文件({len(self.old_files)})数量不匹配。",
            "ja": f"新ファイル({len(self.new_files)})と旧ファイル({len(self.old_files)})の数が一致しません。"
        }
        starting_texts = {"vi": "🔄 Đang khởi động...", "en": "🔄 Starting...", "zh": "🔄 启动中...", "ja": "🔄 起動中..."}
        
        if not self.new_files or not self.old_files:
            messagebox.showwarning(warning_titles.get(lang, warning_titles["vi"]), warning_msgs.get(lang, warning_msgs["vi"]))
            return
        
        if len(self.new_files) != len(self.old_files):
            messagebox.showerror(error_titles.get(lang, error_titles["vi"]), mismatch_msgs.get(lang, mismatch_msgs["vi"]))
            return
        
        # Cảnh báo người dùng
        confirm = messagebox.askyesno(
            get_text("legacy_confirm_title", self.current_lang),
            get_text("legacy_confirm_msg", self.current_lang)
        )
        
        if not confirm:
            return
        
        # Disable buttons
        self.btn_run.config(state="disabled")
        self.btn_legacy.config(state="disabled")
        self.update_status(starting_texts.get(lang, starting_texts["vi"]))
        
        # Run in thread
        threading.Thread(target=self._run_legacy_thread, daemon=True).start()
    
    def _run_legacy_thread(self):
        """Thread chạy Legacy comparison"""
        try:
            # Get screen mode from combobox
            mode_text = self.screen_combo.get()
            if "VPS" in mode_text:
                screen_mode = "vps"
            elif "phụ" in mode_text:
                screen_mode = "monitor"
            else:
                screen_mode = "pc"
            
            # Collect settings
            settings = {
                "screen_mode": screen_mode,
                "zoom": self.zoom_var.get(),
                "goto_address": "EX1" if not self.goto_address.get().strip() or self.goto_address.get().strip().upper() in ["A1", ""] else self.goto_address.get().strip(),
                "output_folder": self.result_path.get().strip() or None,
                "highlight_fill_color": self.highlight_fill_color,
                "highlight_fill_opacity": self.highlight_fill_opacity.get(),
                "doc_mode": self.doc_mode_var.get(),
                "print_area": self.print_area_var.get(),
            }
            
            # Run legacy comparison
            elapsed_time = self.comparator.start_legacy_comparison(
                self.new_files,
                self.old_files,
                status_callback=self.update_status,
                progress_callback=None,
                settings=settings
            )
            
            # Show result
            if elapsed_time:
                minutes, seconds = divmod(elapsed_time, 60)
                time_msg = f"\nThời gian: {int(minutes)} phút {seconds:.2f} giây"
            else:
                time_msg = ""
            
            self.update_status("✅ " + get_text("status_complete", self.current_lang))
            messagebox.showinfo(
                get_text("legacy_complete_title", self.current_lang), 
                get_text("legacy_complete_msg", self.current_lang) + time_msg
            )
            
        except Exception as e:
            self.update_status(f"❌ {get_text('status_error', self.current_lang)} {e}")
            messagebox.showerror(get_text("error", self.current_lang), str(e))
        finally:
            self.btn_run.config(state="normal")
            self.btn_legacy.config(state="normal")


    # ========== COLOR PICKERS ==========
    def select_base_color(self):
        color = colorchooser.askcolor(title="Chọn Màu Nền", initialcolor=self.highlight_base_color)
        if color[1]:
            self.highlight_base_color = color[1]
            self.bg_color = color[1]
            self.base_color_label.config(text=f"  {color[1]}  ", bg=color[1])
            self._auto_save_settings()

    def select_outline_color(self):
        color = colorchooser.askcolor(title="Chọn Màu Viền", initialcolor=self.highlight_outline_color)
        if color[1]:
            self.highlight_outline_color = color[1]
            self.outline_color = color[1]
            self.outline_color_label.config(text=f"  {color[1]}  ", bg=color[1])
            self._auto_save_settings()

    def select_fill_color(self):
        color = colorchooser.askcolor(title="Chọn Màu Tô", initialcolor=self.highlight_fill_color)
        if color[1]:
            self.highlight_fill_color = color[1]
            self.fill_color_label.config(text=f"  {color[1]}  ", bg=color[1])
            self._auto_save_settings()

    def validate_dpi_input(self, event=None):
        try:
            val = self.pdf_render_dpi.get()
            if val < 50:
                self.pdf_render_dpi.set(50)
            elif val > 300:
                self.pdf_render_dpi.set(300)
        except:
            self.pdf_render_dpi.set(100)

    def on_screen_mode_change(self, event=None):
        idx = self.screen_combo.current()
        if idx == 0:  # PC
            self.zoom_var.set(46)
        elif idx == 1:  # VPS
            self.zoom_var.set(100)
        else:  # Secondary
            self.zoom_var.set(60)
        self._auto_save_settings()

    # ========== SETTINGS ==========
    def _auto_save_settings(self):
        if not self.save_user_settings.get():
            return
        
        current_settings = {
            "zoom_level": self.zoom_var.get(),
            "goto_address": self.goto_address.get(),
            "auto_add_b": self.auto_add_b.get(),
            "suppress_error": self.suppress_error_popups.get(),
            "use_pdf_method": self.use_pdf_method.get(),
            "pdf_dpi": self.pdf_render_dpi.get(),
            "highlight_base_color": self.highlight_base_color,
            "highlight_outline_color": self.highlight_outline_color,
            "highlight_fill_color": self.highlight_fill_color,
            "highlight_fill_opacity": self.highlight_fill_opacity.get(),
            "pdf_diff_threshold": self.pdf_diff_threshold.get(),
            "pdf_dilate_size": self.pdf_dilate_size.get(),
            "pdf_dilate_iterations": self.pdf_dilate_iterations.get(),
            "save_settings": True,
            "language": self.current_lang,
        }
        self.settings_service.save_settings(current_settings)
    
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
            
            # Refresh all UI texts dynamically
            self._refresh_all_ui_texts()
            
            # Show confirmation
            confirmations = {
                "vi": "✅ Đã chuyển sang Tiếng Việt",
                "en": "✅ Switched to English",
                "zh": "✅ 已切换到中文",
                "ja": "✅ 日本語に切り替えました"
            }
            messagebox.showinfo(
                get_text("menu_language", self.current_lang),
                confirmations.get(new_lang, "Language changed")
            )
    
    def _refresh_all_ui_texts(self):
        """Cập nhật toàn bộ text trong UI khi thay đổi ngôn ngữ (hot-swap)"""
        lang = self.current_lang
        
        # Window Title
        self.master.title(get_text("app_title", lang))

        # ===== HEADER =====
        if hasattr(self, 'translatable_widgets'):
            title = self.translatable_widgets.get("title")
            if title:
                title.config(text=get_text("app_title", lang) if lang != "vi" else "📊 So sánh Chỉ thị Thao tác")
            
            help_btn = self.translatable_widgets.get("help_btn")
            if help_btn:
                help_btn.config(text=get_text("btn_help", lang) if lang != "vi" else "📖 Hướng dẫn")
        
        # ===== CARD 1: FILE SELECTION =====
        # Card titles - using LabelFrame text property
        file_card_texts = {
            "vi": "  📁 Chọn Files CTTT  ",
            "en": "  📁 Select SOP Files  ",
            "zh": "  📁 选择作业指导书文件  ",
            "ja": "  📁 作業指導書ファイルを選択  "
        }
        if hasattr(self, 'file_card'):
            self.file_card.config(text=file_card_texts.get(lang, file_card_texts["vi"]))
        
        # Document mode
        if hasattr(self, 'lbl_doc_mode'):
            self.lbl_doc_mode.config(text=get_text("doc_type_label", lang))
        if hasattr(self, 'doc_mode_combo'):
            curr_idx = self.doc_mode_combo.current()
            self.doc_mode_combo.config(values=[
                get_text("mode_standard_cttt", lang),
                get_text("mode_dukc_cttt", lang),
                get_text("mode_dukc_other", lang)
            ])
            if curr_idx >= 0:
                self.doc_mode_combo.current(curr_idx)

        # Screen mode label
        screen_mode_texts = {"vi": "Chế độ màn hình:", "en": "Screen mode:", "zh": "屏幕模式:", "ja": "画面モード:"}
        if hasattr(self, 'lbl_screen_mode'):
            self.lbl_screen_mode.config(text=screen_mode_texts.get(lang, screen_mode_texts["vi"]))
        
        # CTTT labels
        cttt_new_texts = {"vi": "CTTT Mới:", "en": "New SOP:", "zh": "新作业指导书:", "ja": "新作業指導書:"}
        cttt_old_texts = {"vi": "CTTT Cũ:", "en": "Old SOP:", "zh": "旧作业指导书:", "ja": "旧作業指導書:"}
        selected_texts = {"vi": "Đã chọn:", "en": "Selected:", "zh": "已选择:", "ja": "選択済:"}
        
        if hasattr(self, 'lbl_cttt_new'):
            self.lbl_cttt_new.config(text=cttt_new_texts.get(lang, cttt_new_texts["vi"]))
        if hasattr(self, 'lbl_cttt_old'):
            self.lbl_cttt_old.config(text=cttt_old_texts.get(lang, cttt_old_texts["vi"]))
        if hasattr(self, 'lbl_selected_new'):
            self.lbl_selected_new.config(text=selected_texts.get(lang, selected_texts["vi"]))
        if hasattr(self, 'lbl_selected_old'):
            self.lbl_selected_old.config(text=selected_texts.get(lang, selected_texts["vi"]))
        
        # Buttons
        btn_new_texts = {"vi": "📂 Chọn CTTT mới", "en": "📂 Select New SOP", "zh": "📂 选择新作业指导书", "ja": "📂 新作業指導書を選択"}
        btn_old_texts = {"vi": "📂 Chọn CTTT cũ", "en": "📂 Select Old SOP", "zh": "📂 选择旧作业指导书", "ja": "📂 旧作業指導書を選択"}
        
        if hasattr(self, 'btn_select_new'):
            self.btn_select_new.config(text=btn_new_texts.get(lang, btn_new_texts["vi"]))
        if hasattr(self, 'btn_select_old'):
            self.btn_select_old.config(text=btn_old_texts.get(lang, btn_old_texts["vi"]))
        
        # Result path
        result_texts = {
            "vi": "Thư mục lưu kết quả (để trống = cùng thư mục CTTT mới):",
            "en": "Result folder (empty = same as new SOP folder):",
            "zh": "结果文件夹（留空 = 与新作业指导书同文件夹）:",
            "ja": "結果フォルダ（空欄 = 新作業指導書と同じ）:"
        }
        if hasattr(self, 'lbl_result_path'):
            self.lbl_result_path.config(text=result_texts.get(lang, result_texts["vi"]))
        
        browse_texts = {"vi": "Duyệt...", "en": "Browse...", "zh": "浏览...", "ja": "参照..."}
        if hasattr(self, 'btn_browse'):
            self.btn_browse.config(text=browse_texts.get(lang, browse_texts["vi"]))
        
        check_order_texts = {"vi": "🔍 Kiểm tra thứ tự cặp CTTT", "en": "🔍 Check SOP pair order", "zh": "🔍 检查作业指导书配对顺序", "ja": "🔍 作業指導書ペア順序確認"}
        if hasattr(self, 'btn_check_order'):
            self.btn_check_order.config(text=check_order_texts.get(lang, check_order_texts["vi"]))
        
        # ===== RUN BUTTON =====
        run_texts = {
            "vi": "▶️  BẮT ĐẦU SO SÁNH(PHƯƠNG PHÁP MỚI BẢN TỪ VER 7 TRỞ LÊN(PDF/EXCEL))",
            "en": "▶️  START COMPARISON (NEW METHOD - VER 7+ PDF/EXCEL)",
            "zh": "▶️  开始对比（新方法 - VER 7+ PDF/EXCEL）",
            "ja": "▶️  比較開始（新方式 - VER 7+ PDF/EXCEL）"
        }
        if hasattr(self, 'btn_run'):
            self.btn_run.config(text=run_texts.get(lang, run_texts["vi"]))
        
        # Legacy button
        legacy_texts = {
            "vi": "📷 CHỤP MÀN HÌNH TRỰC TIẾP (Phiên bản 6)",
            "en": "📷 DIRECT SCREENSHOT (Version 6)",
            "zh": "📷 直接截屏（版本6）",
            "ja": "📷 直接スクリーンショット（バージョン6）"
        }
        if hasattr(self, 'btn_legacy'):
            self.btn_legacy.config(text=legacy_texts.get(lang, legacy_texts["vi"]))
        
        legacy_warning_texts = {
            "vi": "⚠️ Mở Excel trực tiếp trên màn hình, chụp ảnh và so sánh (giống phiên bản 6). Không sử dụng máy tính trong khi chạy!",
            "en": "⚠️ Opens Excel directly on screen, captures and compares (like version 6). Do not use computer while running!",
            "zh": "⚠️ 直接在屏幕上打开Excel，截图并比较（与版本6相同）。运行时请勿使用电脑！",
            "ja": "⚠️ 画面上でExcelを直接開き、キャプチャして比較（バージョン6と同様）。実行中はPCを使用しないでください！"
        }
        if hasattr(self, 'lbl_legacy_warning'):
            self.lbl_legacy_warning.config(text=legacy_warning_texts.get(lang, legacy_warning_texts["vi"]))
        
        # Legacy Frame Title
        legacy_frame_titles = {
            "vi": "  🖼️ Phương pháp chụp ảnh màn hình của phiên bản 6 (Phiên bản cũ)  ",
            "en": "  🖼️ Screenshot Method of Version 6 (Legacy Version)  ",
            "zh": "  🖼️ 版本6的截图方法（旧版本）  ",
            "ja": "  🖼️ バージョン6のスクリーンショット方法（旧バージョン）  "
        }
        if hasattr(self, 'legacy_frame'):
            self.legacy_frame.config(text=legacy_frame_titles.get(lang, legacy_frame_titles["vi"]))

        # ===== CARD 2: SETTINGS =====
        settings_card_texts = {"vi": "  ⚙️ Cài đặt  ", "en": "  ⚙️ Settings  ", "zh": "  ⚙️ 设置  ", "ja": "  ⚙️ 設定  "}
        if hasattr(self, 'settings_card'):
            self.settings_card.config(text=settings_card_texts.get(lang, settings_card_texts["vi"]))
        
        pdf_method_texts = {
            "vi": "📄 Sử dụng phương pháp PDF (chính xác hơn)",
            "en": "📄 Use PDF method (more accurate)",
            "zh": "📄 使用PDF方法（更准确）",
            "ja": "📄 PDF方式を使用（より正確）"
        }
        if hasattr(self, 'chk_use_pdf'):
            self.chk_use_pdf.config(text=pdf_method_texts.get(lang, pdf_method_texts["vi"]))
        
        dpi_texts = {"vi": "Độ phân giải:", "en": "Resolution:", "zh": "分辨率:", "ja": "解像度:"}
        if hasattr(self, 'lbl_dpi'):
            self.lbl_dpi.config(text=dpi_texts.get(lang, dpi_texts["vi"]))
        
        zoom_texts = {"vi": "Mức phóng to:", "en": "Zoom level:", "zh": "缩放级别:", "ja": "ズームレベル:"}
        if hasattr(self, 'lbl_zoom'):
            self.lbl_zoom.config(text=zoom_texts.get(lang, zoom_texts["vi"]))
        
        goto_texts = {
            "vi": "Di chuyển đến ô (Mặc định: EX1):",
            "en": "Go to cell (Default: EX1):",
            "zh": "跳转到单元格 (默认: EX1):",
            "ja": "セルへ移動 (デフォルト: EX1):"
        }
        if hasattr(self, 'lbl_goto'):
            self.lbl_goto.config(text=goto_texts.get(lang, goto_texts["vi"]))
        
        auto_b_texts = {"vi": "⚠️ Tự động thêm 'b' cho barcode", "en": "⚠️ Auto-add 'b' for barcode", "zh": "⚠️ 自动添加'b'用于条码", "ja": "⚠️ バーコード用に'b'を自動追加"}
        suppress_texts = {"vi": "🔇 Ẩn thông báo lỗi", "en": "🔇 Hide error messages", "zh": "🔇 隐藏错误消息", "ja": "🔇 エラーメッセージを非表示"}
        save_texts = {"vi": "💾 Lưu cài đặt", "en": "💾 Save settings", "zh": "💾 保存设置", "ja": "💾 設定を保存"}
        
        if hasattr(self, 'chk_auto_b'):
            self.chk_auto_b.config(text=auto_b_texts.get(lang, auto_b_texts["vi"]))
        if hasattr(self, 'chk_suppress'):
            self.chk_suppress.config(text=suppress_texts.get(lang, suppress_texts["vi"]))
        if hasattr(self, 'chk_save'):
            self.chk_save.config(text=save_texts.get(lang, save_texts["vi"]))
        
        # ===== CARD 3: HIGHLIGHT =====
        hl_card_texts = {"vi": "  🎨 Thiết lập Highlight  ", "en": "  🎨 Highlight Settings  ", "zh": "  🎨 高亮设置  ", "ja": "  🎨 ハイライト設定  "}
        if hasattr(self, 'hl_card'):
            self.hl_card.config(text=hl_card_texts.get(lang, hl_card_texts["vi"]))
        
        base_color_texts = {"vi": "Màu Nền", "en": "Base Color", "zh": "底色", "ja": "背景色"}
        outline_color_texts = {"vi": "Màu Viền", "en": "Outline", "zh": "边框色", "ja": "枠線色"}
        fill_color_texts = {"vi": "Màu Tô", "en": "Fill Color", "zh": "填充色", "ja": "塗り色"}
        
        if hasattr(self, 'btn_base_color'):
            self.btn_base_color.config(text=base_color_texts.get(lang, base_color_texts["vi"]))
        if hasattr(self, 'btn_outline_color'):
            self.btn_outline_color.config(text=outline_color_texts.get(lang, outline_color_texts["vi"]))
        if hasattr(self, 'btn_fill_color'):
            self.btn_fill_color.config(text=fill_color_texts.get(lang, fill_color_texts["vi"]))
        
        opacity_texts = {"vi": "Độ trong suốt (%):", "en": "Opacity (%):", "zh": "透明度 (%):", "ja": "不透明度 (%):"}
        threshold_texts = {"vi": "Ngưỡng phát hiện (0-255):", "en": "Detection threshold (0-255):", "zh": "检测阈值 (0-255):", "ja": "検出しきい値 (0-255):"}
        dilate_size_texts = {"vi": "Độ dày vùng tô (1-9):", "en": "Fill thickness (1-9):", "zh": "填充厚度 (1-9):", "ja": "塗りの太さ (1-9):"}
        dilate_iter_texts = {"vi": "Số lần mở rộng (1-3):", "en": "Expansion count (1-3):", "zh": "扩展次数 (1-3):", "ja": "拡張回数 (1-3):"}
        
        if hasattr(self, 'lbl_opacity'):
            self.lbl_opacity.config(text=opacity_texts.get(lang, opacity_texts["vi"]))
        if hasattr(self, 'lbl_threshold'):
            self.lbl_threshold.config(text=threshold_texts.get(lang, threshold_texts["vi"]))
        if hasattr(self, 'lbl_dilate_size'):
            self.lbl_dilate_size.config(text=dilate_size_texts.get(lang, dilate_size_texts["vi"]))
        if hasattr(self, 'lbl_dilate_iter'):
            self.lbl_dilate_iter.config(text=dilate_iter_texts.get(lang, dilate_iter_texts["vi"]))
            
        # ===== STATUS BAR VERSION =====
        if hasattr(self, 'status_version_label'):
            ver_text = f"Version {config.APP_VERSION} | {config.APP_DATE}"
            if lang == "vi":
                ver_text = f"Phiên bản {config.APP_VERSION} | {config.APP_DATE}"
            elif lang == "zh":
                ver_text = f"版本 {config.APP_VERSION} | {config.APP_DATE}"
            elif lang == "ja":
                ver_text = f"バージョン {config.APP_VERSION} | {config.APP_DATE}"
            self.status_version_label.config(text=ver_text)
        

        
        # ===== STATUS BAR =====
        if hasattr(self, 'status_label'):
            self.status_label.config(text="✅ " + get_text("status_ready", lang))
            
        # ===== REBUILD MENU =====
        self.create_menu_bar()
        
        # ===== UPDATE COMBOBOXES =====
        if hasattr(self, 'screen_combo'):
            current_idx = self.screen_combo.current()
            screen_options = {
                "vi": ["Màn hình PC", "VPS", "Màn hình phụ"],
                "en": ["PC Screen", "VPS", "Secondary Screen"],
                "zh": ["PC屏幕", "VPS", "副屏"],
                "ja": ["PC画面", "VPS", "サブ画面"]
            }
            self.screen_combo.config(values=screen_options.get(lang, screen_options["vi"]))
            if current_idx >= 0:
                self.screen_combo.current(current_idx)


    # ========== MENU & PHÍM TẮT ==========
    def create_menu_bar(self):
        """Khởi tạo và cập nhật thanh menu đa ngôn ngữ"""
        # Xóa menu cũ nếu có (mặc dù tk.Tk tự handle việc replace, nhưng tốt nhất là tạo mới)
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        lang = self.current_lang
        
        # Translations
        menu_titles = {
            "vi": {"file": "Tệp", "edit": "Chỉnh sửa", "view": "Xem", "help": "Trợ giúp"},
            "en": {"file": "File", "edit": "Edit", "view": "View", "help": "Help"},
            "zh": {"file": "文件", "edit": "编辑", "view": "查看", "help": "帮助"},
            "ja": {"file": "ファイル", "edit": "編集", "view": "表示", "help": "ヘルプ"}
        }
        titles = menu_titles.get(lang, menu_titles["vi"])
        
        file_items = {
            "vi": ["Chọn CTTT mới", "Chọn CTTT cũ", "Chọn thư mục kết quả", "Lưu cài đặt", "Thoát"],
            "en": ["Select New SOP", "Select Old SOP", "Select Result Folder", "Save Settings", "Exit"],
            "zh": ["选择新作业指导书", "选择旧作业指导书", "选择结果文件夹", "保存设置", "退出"],
            "ja": ["新作業指導書選択", "旧作業指導書選択", "結果フォルダ選択", "設定保存", "終了"]
        }
        f_items = file_items.get(lang, file_items["vi"])
        
        edit_items = {
            "vi": ["Kiểm tra thứ tự file", "Bắt đầu so sánh"],
            "en": ["Check File Order", "Start Comparison"],
            "zh": ["检查文件顺序", "开始对比"],
            "ja": ["ファイル順序確認", "比較開始"]
        }
        e_items = edit_items.get(lang, edit_items["vi"])
        
        view_items = {
            "vi": ["Mở thư mục kết quả"],
            "en": ["Open Result Folder"],
            "zh": ["打开结果文件夹"],
            "ja": ["結果フォルダを開く"]
        }
        v_items = view_items.get(lang, view_items["vi"])
        
        help_items = {
            "vi": ["Hướng dẫn sử dụng", "Danh sách phím tắt", "Thông tin ứng dụng"],
            "en": ["User Guide", "Shortcuts List", "About App"],
            "zh": ["使用说明", "快捷键列表", "关于应用"],
            "ja": ["ユーザーガイド", "ショートカット一覧", "アプリについて"]
        }
        h_items = help_items.get(lang, help_items["vi"])
        
        # Menu Tệp
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=titles["file"], menu=file_menu)
        file_menu.add_command(label=f_items[0], command=self.select_new_files, accelerator="Ctrl+N")
        file_menu.add_command(label=f_items[1], command=self.select_old_files, accelerator="Ctrl+Shift+O")
        file_menu.add_command(label=f_items[2], command=self.browse_result_folder, accelerator="Ctrl+R")
        file_menu.add_separator()
        file_menu.add_command(label=f_items[3], command=self._auto_save_settings, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label=f_items[4], command=self.master.quit, accelerator="Alt+F4")
        
        # Menu Chỉnh sửa
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=titles["edit"], menu=edit_menu)
        edit_menu.add_command(label=e_items[0], command=self.check_order, accelerator="Ctrl+K")
        edit_menu.add_separator()
        edit_menu.add_command(label=e_items[1], command=self.run_comparison, accelerator="F5")
        
        # Menu Xem
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=titles["view"], menu=view_menu)
        view_menu.add_command(label=v_items[0], command=self._open_result_folder, accelerator="Ctrl+E")
        
        # Menu Trợ giúp
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=titles["help"], menu=help_menu)
        help_menu.add_command(label=h_items[0], command=self.show_help, accelerator="F1")
        help_menu.add_command(label=h_items[1], command=self._show_shortcuts)
        help_menu.add_command(label="Check for updates", command=lambda: self._check_updates_in_background(manual=True))
        help_menu.add_separator()
        
        about_title = h_items[2]
        about_msg = f"So sánh CTTT\nVersion {config.APP_VERSION}\nDate: {config.APP_DATE}"
        if lang == "vi":
            about_msg = f"So sánh CTTT\nPhiên bản {config.APP_VERSION}\nNgày: {config.APP_DATE}"
        elif lang == "zh":
             about_msg = f"CTTT比对工具\n版本 {config.APP_VERSION}\n日期: {config.APP_DATE}"
        elif lang == "ja":
             about_msg = f"CTTT比較ツール\nバージョン {config.APP_VERSION}\n日付: {config.APP_DATE}"
             
        help_menu.add_command(label=h_items[2], command=lambda: messagebox.showinfo(about_title, about_msg))
    
    def _show_shortcuts(self):
        """Hiển thị danh sách phím tắt"""
        lang = self.current_lang
        
        title = {
            "vi": "PHÍM TẮT:\n\n",
            "en": "SHORTCUTS:\n\n",
            "zh": "快捷键:\n\n",
            "ja": "ショートカット:\n\n"
        }
        
        shortcuts_list = {
            "vi": [
                "Ctrl+N / Ctrl+O     Chọn file CTTT mới",
                "Ctrl+Shift+O        Chọn file CTTT cũ",
                "Ctrl+R              Chọn thư mục kết quả",
                "Ctrl+S              Lưu cài đặt",
                "Ctrl+K              Kiểm tra thứ tự file",
                "F5 / Ctrl+Enter     Bắt đầu so sánh",
                "F6                  Chạy phương pháp Legacy",
                "Ctrl+E              Mở thư mục kết quả",
                "F1                  Hướng dẫn sử dụng",
                "Escape              Hủy focus",
                "Alt+F4              Thoát"
            ],
            "en": [
                "Ctrl+N / Ctrl+O     Select new SOP",
                "Ctrl+Shift+O        Select old SOP",
                "Ctrl+R              Select result folder",
                "Ctrl+S              Save settings",
                "Ctrl+K              Check file order",
                "F5 / Ctrl+Enter     Start comparison",
                "F6                  Run Legacy method",
                "Ctrl+E              Open result folder",
                "F1                  User Guide",
                "Escape              Unfocus",
                "Alt+F4              Exit"
            ],
            "zh": [
                "Ctrl+N / Ctrl+O     选择新作业指导书",
                "Ctrl+Shift+O        选择旧作业指导书",
                "Ctrl+R              选择结果文件夹",
                "Ctrl+S              保存设置",
                "Ctrl+K              检查文件顺序",
                "F5 / Ctrl+Enter     开始对比",
                "F6                  运行传统方法",
                "Ctrl+E              打开结果文件夹",
                "F1                  使用说明",
                "Escape              取消焦点",
                "Alt+F4              退出"
            ],
            "ja": [
                "Ctrl+N / Ctrl+O     新作業指導書選択",
                "Ctrl+Shift+O        旧作業指導書選択",
                "Ctrl+R              結果フォルダ選択",
                "Ctrl+S              設定保存",
                "Ctrl+K              ファイル順序確認",
                "F5 / Ctrl+Enter     比較開始",
                "F6                  レガシー方式実行",
                "Ctrl+E              結果フォルダを開く",
                "F1                  ユーザーガイド",
                "Escape              フォーカス解除",
                "Alt+F4              終了"
            ]
        }
        
        msg = title.get(lang, title["vi"]) + "\n".join(shortcuts_list.get(lang, shortcuts_list["vi"]))
        dialog_title = {"vi": "Phím tắt", "en": "Shortcuts", "zh": "快捷键", "ja": "ショートカット"}
        messagebox.showinfo(dialog_title.get(lang, dialog_title["vi"]), msg)

    def bind_shortcuts(self):
        """Gắn phím tắt cho các chức năng chính"""
        # File operations
        self.master.bind('<Control-n>', lambda e: self.select_new_files())
        self.master.bind('<Control-N>', lambda e: self.select_new_files())
        self.master.bind('<Control-o>', lambda e: self.select_new_files())
        self.master.bind('<Control-O>', lambda e: self.select_new_files())
        self.master.bind('<Control-Shift-o>', lambda e: self.select_old_files())
        self.master.bind('<Control-Shift-O>', lambda e: self.select_old_files())
        self.master.bind('<Control-r>', lambda e: self.browse_result_folder())
        self.master.bind('<Control-R>', lambda e: self.browse_result_folder())
        self.master.bind('<Control-s>', lambda e: self._manual_save_settings())
        self.master.bind('<Control-S>', lambda e: self._manual_save_settings())
        
        # Run comparison
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
    
    def _manual_save_settings(self):
        """Lưu cài đặt thủ công"""
        lang = self.current_lang
        self._auto_save_settings()
        
        titles = {"vi": "Đã lưu", "en": "Saved", "zh": "已保存", "ja": "保存済み"}
        msgs = {"vi": "Cài đặt đã được lưu thành công.", "en": "Settings saved successfully.", "zh": "设置已成功保存。", "ja": "設定が正常に保存されました。"}
        messagebox.showinfo(titles.get(lang, titles["vi"]), msgs.get(lang, msgs["vi"]))
    
    def _open_result_folder(self):
        """Mở thư mục kết quả trong Explorer"""
        lang = self.current_lang
        titles = {"vi": "Thông báo", "en": "Notice", "zh": "通知", "ja": "通知"}
        not_found_msgs = {"vi": "Không tìm thấy thư mục kết quả.", "en": "Result folder not found.", "zh": "未找到结果文件夹。", "ja": "結果フォルダが見つかりません。"}
        no_folder_msgs = {"vi": "Chưa có thư mục kết quả.", "en": "No result folder available.", "zh": "没有可用的结果文件夹。", "ja": "結果フォルダがありません。"}
        
        result_path = self.result_path.get()
        if result_path and os.path.isdir(result_path):
            os.startfile(result_path)
        elif self.new_files:
            folder = os.path.dirname(self.new_files[0])
            if os.path.isdir(folder):
                os.startfile(folder)
            else:
                messagebox.showwarning(titles.get(lang, titles["vi"]), not_found_msgs.get(lang, not_found_msgs["vi"]))
        else:
            messagebox.showwarning(titles.get(lang, titles["vi"]), no_folder_msgs.get(lang, no_folder_msgs["vi"]))

    # ========== AUTO UPDATE ==========
    def _legacy_check_for_updates(self):
        """Kiểm tra phiên bản mới từ server"""
        try:
            from services.update_service import check_for_update, perform_update, get_current_version
            
            has_update, newest_ver, newest_file = check_for_update()
            
            if has_update:
                current_ver = get_current_version()
                lang = self.current_lang
                
                titles = {"vi": "Cập nhật phần mềm", "en": "Software Update", "zh": "软件更新", "ja": "ソフトウェア更新"}
                msgs = {
                    "vi": f"🆕 Đã có phiên bản mới: {newest_ver}\n(Phiên bản hiện tại: {current_ver})\n\nBạn có muốn cập nhật ngay không?\n\nLưu ý: Ứng dụng sẽ tự động đóng và khởi động lại.",
                    "en": f"🆕 New version available: {newest_ver}\n(Current version: {current_ver})\n\nDo you want to update now?\n\nNote: The app will restart automatically.",
                    "zh": f"🆕 有新版本可用: {newest_ver}\n(当前版本: {current_ver})\n\n您想立即更新吗？\n\n注意：应用程序将自动重启。",
                    "ja": f"🆕 新しいバージョンがあります: {newest_ver}\n(現在のバージョン: {current_ver})\n\n今すぐ更新しますか？\n\n注：アプリは自動的に再起動します。"
                }
                
                result = messagebox.askyesno(
                    titles.get(lang, titles["vi"]),
                    msgs.get(lang, msgs["vi"])
                )
                
                if result:
                    self.update_status("🔄 Đang cập nhật phần mềm...")
                    perform_update(newest_file, callback_on_start=self.master.destroy)
            else:
                # Log nhưng không hiển thị thông báo
                import logging
                logging.info("Phần mềm đang ở phiên bản mới nhất.")
                
        except Exception as e:
            # Không hiển thị lỗi cho user, chỉ log
            import logging
            logging.warning(f"Không thể kiểm tra update: {e}")
    def _check_updates_in_background(self, manual=False):
        """Run all LAN catalog access away from Tkinter's event loop.

        There is intentionally no short probe timeout. SMB can take several
        seconds to establish a connection; timing out early causes real updates
        to be missed. A disconnected share can only delay this daemon worker,
        never the application UI.
        """
        def worker():
            try:
                from services.update_service import check_for_update
                result = check_for_update()
                self.master.after(0, lambda: self._show_update_candidate(result, manual))
            except Exception as exc:
                self.master.after(0, lambda: self._show_update_error(exc, manual))

        threading.Thread(target=worker, name="sosanh-cttt-update-check", daemon=True).start()

    def _show_update_candidate(self, result, manual):
        has_update, newest_ver, candidate = result
        if not has_update:
            if manual:
                messagebox.showinfo("Software update", "No newer release was found.")
            return
        message = f"New version {newest_ver} is available.\n\nInstall it now?"
        if candidate.notes:
            message += f"\n\nRelease notes:\n{candidate.notes}"
        if messagebox.askyesno("Software update", message):
            self.update_status("Downloading and verifying update installer...")
            threading.Thread(
                target=self._download_update_installer,
                args=(candidate,),
                name="sosanh-cttt-update-download",
                daemon=True,
            ).start()

    def _download_update_installer(self, candidate):
        try:
            from services.release_update_service import download_installer
            installer = download_installer(candidate)
            self.master.after(0, lambda: self._launch_verified_installer(installer))
        except Exception as exc:
            self.master.after(0, lambda: self._show_update_error(exc, True))

    def _launch_verified_installer(self, installer):
        import subprocess
        self.master.destroy()
        subprocess.Popen([str(installer), "/SP-", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"], close_fds=True)

    def _show_update_error(self, error, manual):
        import logging
        logging.warning("Update check/install failed: %s", error)
        if manual:
            messagebox.showwarning("Software update", f"Could not check or install the update:\n{error}")


def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
