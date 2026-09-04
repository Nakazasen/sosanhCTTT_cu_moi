"""
Modern Main Window UI
Giao diện hiện đại, chuyên nghiệp, hỗ trợ đa ngôn ngữ (vi, en, zh, ja)
và chuẩn hóa thông báo lỗi thân thiện, trực quan.
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
        self.wraplength = 240
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


class CustomModeConfigDialog(tk.Toplevel):
    """
    Hộp thoại cấu hình tùy chỉnh cho '4. Tài liệu do người dùng chọn'
    2.1. Phạm vi so sánh (Vùng từ bao nhiêu đến bao nhiêu)
    2.2. Toàn bộ sheet hay sheet chỉ định (+ lọc tab màu xanh)
    """
    def __init__(self, parent, settings_service, current_lang="vi", on_save_callback=None):
        super().__init__(parent)
        self.settings_service = settings_service
        self.current_lang = current_lang
        self.on_save_callback = on_save_callback

        self.title(get_text("custom_dialog_title", self.current_lang))
        self.geometry("540x470")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Load current settings
        cur_settings = self.settings_service.settings if self.settings_service else {}
        self.range_var = tk.StringVar(value=cur_settings.get(config.KEY_CUSTOM_PRINT_AREA, config.DEFAULT_CUSTOM_PRINT_AREA))
        self.sheet_mode_var = tk.StringVar(value=cur_settings.get(config.KEY_CUSTOM_SHEET_MODE, config.CUSTOM_SHEET_MODE_ALL))
        self.specified_sheets_var = tk.StringVar(value=cur_settings.get(config.KEY_CUSTOM_SPECIFIED_SHEETS, ""))
        self.only_green_var = tk.BooleanVar(value=cur_settings.get(config.KEY_CUSTOM_ONLY_GREEN, False))

        self._build_ui()
        self._center_window(parent)

    def _build_ui(self):
        container = ttk.Frame(self, padding=Spacing.LG)
        container.pack(fill="both", expand=True)

        # --- GROUP 1: Phạm vi so sánh (Range) ---
        grp_range = ttk.LabelFrame(container, text=f"  {get_text('custom_range_group', self.current_lang)}  ", padding=Spacing.MD)
        grp_range.pack(fill="x", pady=(0, Spacing.MD))

        row1 = ttk.Frame(grp_range)
        row1.pack(fill="x", pady=(0, Spacing.XS))

        ttk.Label(row1, text="Print Area:", font=Fonts.get("base", "bold")).pack(side="left", padx=(0, Spacing.SM))
        entry_range = ttk.Entry(row1, textvariable=self.range_var, width=28)
        entry_range.pack(side="left", fill="x", expand=True)

        ttk.Label(grp_range, text=get_text("custom_range_hint", self.current_lang), style="Muted.TLabel").pack(anchor="w", pady=(0, Spacing.SM))

        # Presets
        row_presets = ttk.Frame(grp_range)
        row_presets.pack(fill="x")
        ttk.Label(row_presets, text=f"{get_text('custom_presets_label', self.current_lang)}:").pack(side="left", padx=(0, Spacing.XS))

        presets = [
            ("A1:AT120", "A1:AT120"),
            ("EX1:GR76", "EX1:GR76"),
            ("J2:BD76", "J2:BD76"),
            ("A1:Z50", "A1:Z50"),
            ("A1:ZZ500", "A1:ZZ500")
        ]
        for label, val in presets:
            btn = ttk.Button(row_presets, text=label, width=9,
                             command=lambda v=val: self.range_var.set(v))
            btn.pack(side="left", padx=2)

        # --- GROUP 2: Phạm vi Sheet ---
        grp_sheets = ttk.LabelFrame(container, text=f"  {get_text('custom_sheet_group', self.current_lang)}  ", padding=Spacing.MD)
        grp_sheets.pack(fill="x", pady=(0, Spacing.MD))

        rb_all = ttk.Radiobutton(
            grp_sheets,
            text=get_text("custom_sheet_all", self.current_lang),
            variable=self.sheet_mode_var,
            value=config.CUSTOM_SHEET_MODE_ALL,
            command=self._on_sheet_mode_toggle
        )
        rb_all.pack(anchor="w", pady=(0, Spacing.XS))

        rb_spec = ttk.Radiobutton(
            grp_sheets,
            text=get_text("custom_sheet_specified", self.current_lang),
            variable=self.sheet_mode_var,
            value=config.CUSTOM_SHEET_MODE_SPECIFIED,
            command=self._on_sheet_mode_toggle
        )
        rb_spec.pack(anchor="w", pady=(0, Spacing.XS))

        self.entry_spec_sheets = ttk.Entry(
            grp_sheets,
            textvariable=self.specified_sheets_var,
            width=45
        )
        self.entry_spec_sheets.pack(fill="x", padx=(Spacing.LG, 0), pady=(0, Spacing.SM))

        chk_green = ttk.Checkbutton(
            grp_sheets,
            text=get_text("custom_only_green", self.current_lang),
            variable=self.only_green_var
        )
        chk_green.pack(anchor="w", pady=(Spacing.XS, 0))

        self._on_sheet_mode_toggle()

        # --- BUTTONS ---
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x", side="bottom", pady=(Spacing.SM, 0))

        btn_save = ttk.Button(
            btn_frame,
            text=f"💾 {get_text('btn_save_apply', self.current_lang)}",
            style="Primary.TButton",
            command=self._on_save
        )
        btn_save.pack(side="right", padx=(Spacing.SM, 0))

        btn_cancel = ttk.Button(
            btn_frame,
            text=get_text("cancel", self.current_lang),
            style="Secondary.TButton",
            command=self.destroy
        )
        btn_cancel.pack(side="right")

    def _on_sheet_mode_toggle(self):
        if self.sheet_mode_var.get() == config.CUSTOM_SHEET_MODE_SPECIFIED:
            self.entry_spec_sheets.config(state="normal")
        else:
            self.entry_spec_sheets.config(state="disabled")

    def _center_window(self, parent):
        self.update_idletasks()
        try:
            p_x = parent.winfo_rootx()
            p_y = parent.winfo_rooty()
            p_w = parent.winfo_width()
            p_h = parent.winfo_height()
            w = self.winfo_width()
            h = self.winfo_height()
            x = p_x + max(0, (p_w - w) // 2)
            y = p_y + max(0, (p_h - h) // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _on_save(self):
        area = self.range_var.get().strip().upper()
        if not area:
            area = config.DEFAULT_CUSTOM_PRINT_AREA

        sheet_mode = self.sheet_mode_var.get()
        spec_sheets = self.specified_sheets_var.get().strip()
        only_green = self.only_green_var.get()

        updated_settings = {
            config.KEY_CUSTOM_PRINT_AREA: area,
            config.KEY_CUSTOM_SHEET_MODE: sheet_mode,
            config.KEY_CUSTOM_SPECIFIED_SHEETS: spec_sheets,
            config.KEY_CUSTOM_ONLY_GREEN: only_green,
        }
        if self.settings_service:
            self.settings_service.save_settings(updated_settings)

        if self.on_save_callback:
            self.on_save_callback(updated_settings)

        self.destroy()


class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title(get_text("app_title", "vi"))
        
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
        
        # Document mode
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
        
        self.title_label = ttk.Label(
            header_frame, 
            text=get_text("header_title", self.current_lang),
            style="Header.TLabel"
        )
        self.title_label.pack(side="left")
        self.translatable_widgets["title"] = self.title_label
        
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
        lang_codes = list(LANGUAGES.keys())
        if self.current_lang in lang_codes:
            self.lang_combo.current(lang_codes.index(self.current_lang))
        else:
            self.lang_combo.current(0)
        self.lang_combo.pack(side="left")
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        self.help_btn = ttk.Button(
            header_frame, 
            text=get_text("btn_help", self.current_lang),
            command=self.show_help,
            style="Secondary.TButton"
        )
        self.help_btn.pack(side="right")
        self.translatable_widgets["help_btn"] = self.help_btn
        
        # ========== CONTENT (Scrollable) ==========
        self.canvas = tk.Canvas(main_container, bg=Colors.BG_MAIN, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="TFrame")
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        def _on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            if self.scrollable_frame.winfo_reqheight() <= self.canvas.winfo_height():
                self.scrollbar.grid_remove()
            else:
                self.scrollbar.grid()
        
        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        
        self.scrollable_frame.bind("<Configure>", _on_frame_configure)
        self.canvas.bind("<Configure>", _on_canvas_configure)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        self.scrollbar.grid_remove()
        
        content = self.scrollable_frame
        content.grid_columnconfigure(0, weight=1)
        
        row = 0
        
        # ==================== CARD 1: FILE SELECTION ====================
        self.file_card = ttk.LabelFrame(content, text=get_text("card_file_selection", self.current_lang), style="Card.TLabelframe", padding=Spacing.LG)
        self.file_card.grid(row=row, column=0, sticky="ew", pady=(0, Spacing.MD)); row += 1

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
                get_text("mode_dukc_other", self.current_lang),
                get_text("mode_custom", self.current_lang)
            ],
            state="readonly", 
            width=54
        )
        self.doc_mode_combo.set("")
        self.doc_mode_combo.pack(side="left", padx=(0, Spacing.XS))
        self.doc_mode_combo.bind("<<ComboboxSelected>>", self.on_doc_mode_change)

        self.btn_custom_config = ttk.Button(
            mode_frame,
            text=f"⚙️ {get_text('btn_custom_config', self.current_lang)}",
            command=self.open_custom_config_dialog,
            style="Secondary.TButton",
            state="disabled",
        )
        self.btn_custom_config.pack(side="left", padx=(0, Spacing.LG))

        self.lbl_screen_mode = ttk.Label(mode_frame, text=get_text("screen_mode_label", self.current_lang))
        self.lbl_screen_mode.pack(side="left", padx=(0, Spacing.SM))
        self.screen_combo = ttk.Combobox(
            mode_frame, 
            values=[
                get_text("screen_pc", self.current_lang),
                get_text("screen_vps", self.current_lang),
                get_text("screen_secondary", self.current_lang)
            ], 
            state="readonly", 
            width=16
        )
        self.screen_combo.current(0)
        self.screen_combo.pack(side="left")
        self.screen_combo.bind("<<ComboboxSelected>>", self.on_screen_mode_change)
        # New Files
        self.lbl_cttt_new = ttk.Label(self.file_card, text=get_text("lbl_cttt_new", self.current_lang))
        self.lbl_cttt_new.grid(row=1, column=0, sticky="w", padx=Spacing.SM)
        ttk.Entry(self.file_card, textvariable=self.new_dir_path).grid(row=1, column=1, sticky="ew", padx=Spacing.SM)
        self.lbl_selected_new = ttk.Label(self.file_card, text=get_text("lbl_selected_new", self.current_lang))
        self.lbl_selected_new.grid(row=1, column=2, sticky="e", padx=Spacing.SM)
        ttk.Entry(self.file_card, textvariable=self.new_files_display).grid(row=1, column=3, sticky="ew", padx=Spacing.SM)
        self.btn_select_new = ttk.Button(self.file_card, text=get_text("btn_select_new", self.current_lang), command=self.select_new_files, style="Primary.TButton")
        self.btn_select_new.grid(row=1, column=4, padx=Spacing.SM, pady=Spacing.SM)
        
        # Old Files
        self.lbl_cttt_old = ttk.Label(self.file_card, text=get_text("lbl_cttt_old", self.current_lang))
        self.lbl_cttt_old.grid(row=2, column=0, sticky="w", padx=Spacing.SM)
        ttk.Entry(self.file_card, textvariable=self.old_dir_path).grid(row=2, column=1, sticky="ew", padx=Spacing.SM)
        self.lbl_selected_old = ttk.Label(self.file_card, text=get_text("lbl_selected_old", self.current_lang))
        self.lbl_selected_old.grid(row=2, column=2, sticky="e", padx=Spacing.SM)
        ttk.Entry(self.file_card, textvariable=self.old_files_display).grid(row=2, column=3, sticky="ew", padx=Spacing.SM)
        self.btn_select_old = ttk.Button(self.file_card, text=get_text("btn_select_old", self.current_lang), command=self.select_old_files, style="Secondary.TButton")
        self.btn_select_old.grid(row=2, column=4, padx=Spacing.SM, pady=Spacing.SM)
        
        # Result Path
        self.lbl_result_path = ttk.Label(self.file_card, text=get_text("lbl_result_path", self.current_lang), style="Muted.TLabel")
        self.lbl_result_path.grid(row=3, column=0, columnspan=3, sticky="w", padx=Spacing.SM, pady=(Spacing.MD, 0))
        result_row = ttk.Frame(self.file_card); result_row.grid(row=4, column=0, columnspan=5, sticky="ew", padx=Spacing.SM)
        result_row.grid_columnconfigure(0, weight=1)
        ttk.Entry(result_row, textvariable=self.result_path).grid(row=0, column=0, sticky="ew")
        self.btn_browse = ttk.Button(result_row, text=get_text("btn_browse", self.current_lang), command=self.browse_result_folder, style="Secondary.TButton")
        self.btn_browse.grid(row=0, column=1, padx=(Spacing.SM, 0))
        
        # Check Order
        self.btn_check_order = ttk.Button(self.file_card, text=get_text("btn_check_order", self.current_lang), command=self.check_order, style="Secondary.TButton")
        self.btn_check_order.grid(row=5, column=0, columnspan=5, sticky="ew", pady=(Spacing.MD, 0))

        # Workflow step badges
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
            run_frame, text=get_text("btn_run_main", self.current_lang), command=self.run_comparison,
            font=Fonts.get("xl", "bold"), bg="#1D4ED8", fg="#FFFFFF",
            activebackground="#1E3A8A", activeforeground="#FFFFFF",
            height=2, cursor="hand2", relief="flat", bd=0
        )
        self.btn_run.grid(row=0, column=0, sticky="ew", ipady=Spacing.MD)
        
        # ==================== LEGACY SCREENSHOT BUTTON ====================
        self.legacy_frame = ttk.LabelFrame(content, text=get_text("legacy_frame_title", self.current_lang), style="Card.TLabelframe", padding=Spacing.SM)
        self.legacy_frame.grid(row=row, column=0, sticky="ew", pady=(0, Spacing.MD)); row += 1
        self.legacy_frame.grid_columnconfigure(0, weight=1)
        
        self.btn_legacy = tk.Button(
            self.legacy_frame, text=get_text("btn_legacy", self.current_lang), 
            command=self.run_legacy_comparison,
            font=Fonts.get("lg", "bold"), bg="#FFD700", fg="#000000",
            activebackground="#EAB308", activeforeground="#000000",
            height=2, cursor="hand2", relief="flat", bd=0
        )
        self.btn_legacy.pack(fill="x", padx=Spacing.SM, pady=(Spacing.SM, 0))
        
        self.lbl_legacy_warning = ttk.Label(
            self.legacy_frame, 
            text=get_text("legacy_warning", self.current_lang),
            style="Muted.TLabel", wraplength=800
        )
        self.lbl_legacy_warning.pack(anchor="w", padx=Spacing.SM, pady=Spacing.SM)
        
        # ==================== CARD 2: SETTINGS ====================
        self.settings_card = ttk.LabelFrame(content, text=get_text("card_settings", self.current_lang), style="Card.TLabelframe", padding=Spacing.LG)
        self.settings_card.grid(row=row, column=0, sticky="ew", pady=(0, Spacing.MD)); row += 1
        self.settings_card.grid_columnconfigure(1, weight=1)
        self.settings_card.grid_columnconfigure(3, weight=1)
        
        # Method
        method_frame = ttk.Frame(self.settings_card); method_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, Spacing.MD))
        self.chk_use_pdf = ttk.Checkbutton(method_frame, text=get_text("chk_use_pdf", self.current_lang), variable=self.use_pdf_method)
        self.chk_use_pdf.pack(side="left")
        self.lbl_dpi = ttk.Label(method_frame, text=get_text("lbl_dpi", self.current_lang))
        self.lbl_dpi.pack(side="left", padx=(Spacing.LG, Spacing.SM))
        dpi_entry = ttk.Entry(method_frame, textvariable=self.pdf_render_dpi, width=6); dpi_entry.pack(side="left")
        dpi_entry.bind('<FocusOut>', self.validate_dpi_input)
        ttk.Label(method_frame, text="(50-300)", style="Muted.TLabel").pack(side="left", padx=Spacing.SM)
        
        # Zoom & Goto
        self.lbl_zoom = ttk.Label(self.settings_card, text=get_text("lbl_zoom", self.current_lang))
        self.lbl_zoom.grid(row=1, column=0, sticky="w", pady=Spacing.SM)
        ttk.Entry(self.settings_card, textvariable=self.zoom_var, width=10).grid(row=1, column=1, sticky="w", padx=Spacing.SM)
        self.lbl_goto = ttk.Label(self.settings_card, text=get_text("lbl_goto", self.current_lang))
        self.lbl_goto.grid(row=1, column=2, sticky="e", padx=Spacing.SM)
        ttk.Entry(self.settings_card, textvariable=self.goto_address, width=10).grid(row=1, column=3, sticky="w")
        
        # Checkboxes
        check_frame = ttk.Frame(self.settings_card); check_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=Spacing.MD)
        self.chk_auto_b = ttk.Checkbutton(check_frame, text=get_text("chk_auto_b", self.current_lang), variable=self.auto_add_b)
        self.chk_auto_b.pack(side="left", padx=(0, Spacing.LG))
        self.chk_suppress = ttk.Checkbutton(check_frame, text=get_text("chk_suppress", self.current_lang), variable=self.suppress_error_popups)
        self.chk_suppress.pack(side="left", padx=(0, Spacing.LG))
        self.chk_save = ttk.Checkbutton(check_frame, text=get_text("chk_save", self.current_lang), variable=self.save_user_settings)
        self.chk_save.pack(side="left")
        
        # ==================== CARD 3: HIGHLIGHT ====================
        self.hl_card = ttk.LabelFrame(content, text=get_text("card_highlight", self.current_lang), style="Card.TLabelframe", padding=Spacing.LG)
        self.hl_card.grid(row=row, column=0, sticky="ew", pady=(0, Spacing.MD)); row += 1
        self.hl_card.grid_columnconfigure(1, weight=1)
        self.hl_card.grid_columnconfigure(3, weight=1)
        
        # Colors
        color_frame = ttk.Frame(self.hl_card); color_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, Spacing.MD))
        self.btn_base_color = tk.Button(color_frame, text=get_text("btn_base_color", self.current_lang), command=self.select_base_color, bg=Colors.SURFACE, relief="flat", padx=Spacing.MD, cursor="hand2")
        self.btn_base_color.pack(side="left", padx=(0, 4))
        self.base_color_label = tk.Label(color_frame, text=f"  {self.highlight_base_color}  ", bg=self.highlight_base_color, fg="white", relief="solid", bd=1)
        self.base_color_label.pack(side="left", padx=(0, Spacing.LG))
        
        self.btn_outline_color = tk.Button(color_frame, text=get_text("btn_outline_color", self.current_lang), command=self.select_outline_color, bg=Colors.SURFACE, relief="flat", padx=Spacing.MD, cursor="hand2")
        self.btn_outline_color.pack(side="left", padx=(0, 4))
        self.outline_color_label = tk.Label(color_frame, text=f"  {self.highlight_outline_color}  ", bg=self.highlight_outline_color, fg="white", relief="solid", bd=1)
        self.outline_color_label.pack(side="left", padx=(0, Spacing.LG))
        
        self.btn_fill_color = tk.Button(color_frame, text=get_text("btn_fill_color", self.current_lang), command=self.select_fill_color, bg=Colors.SURFACE, relief="flat", padx=Spacing.MD, cursor="hand2")
        self.btn_fill_color.pack(side="left", padx=(0, 4))
        self.fill_color_label = tk.Label(color_frame, text=f"  {self.highlight_fill_color}  ", bg=self.highlight_fill_color, fg="white", relief="solid", bd=1)
        self.fill_color_label.pack(side="left")
        
        # Parameters
        self.lbl_opacity = ttk.Label(self.hl_card, text=get_text("lbl_opacity", self.current_lang))
        self.lbl_opacity.grid(row=1, column=0, sticky="w")
        ttk.Scale(self.hl_card, from_=0, to=100, variable=self.highlight_fill_opacity, orient="horizontal").grid(row=1, column=1, sticky="ew", padx=Spacing.SM)
        self.lbl_threshold = ttk.Label(self.hl_card, text=get_text("lbl_threshold", self.current_lang))
        self.lbl_threshold.grid(row=1, column=2, sticky="e", padx=Spacing.SM)
        ttk.Entry(self.hl_card, textvariable=self.pdf_diff_threshold, width=8).grid(row=1, column=3, sticky="w")
        
        self.lbl_dilate_size = ttk.Label(self.hl_card, text=get_text("lbl_dilate_size", self.current_lang))
        self.lbl_dilate_size.grid(row=2, column=0, sticky="w", pady=Spacing.SM)
        ttk.Entry(self.hl_card, textvariable=self.pdf_dilate_size, width=8).grid(row=2, column=1, sticky="w", padx=Spacing.SM)
        self.lbl_dilate_iter = ttk.Label(self.hl_card, text=get_text("lbl_dilate_iter", self.current_lang))
        self.lbl_dilate_iter.grid(row=2, column=2, sticky="e", padx=Spacing.SM)
        ttk.Entry(self.hl_card, textvariable=self.pdf_dilate_iterations, width=8).grid(row=2, column=3, sticky="w")
        
        # ==================== STATUS BAR ====================
        status_frame = ttk.Frame(self.master, style="Surface.TFrame")
        status_frame.pack(side="bottom", fill="x")
        
        self.status_label = ttk.Label(status_frame, text="✅ " + get_text("status_ready", self.current_lang), style="TLabel")
        self.status_label.pack(side="left", padx=Spacing.LG, pady=Spacing.SM)
        
        self.status_version_label = ttk.Label(status_frame, text=get_text("status_version", self.current_lang, version=config.APP_VERSION, date=config.APP_DATE), style="Muted.TLabel")
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
        if hasattr(self, "btn_custom_config"):
            self.btn_custom_config.config(state="normal" if idx == 3 else "disabled")
        if idx == 1:
            self.doc_mode_var.set(config.DOC_MODE_DUKC_CTTT)
            self.print_area_var.set(config.PRINT_AREA_DUKC_CTTT)
        elif idx == 2:
            self.doc_mode_var.set(config.DOC_MODE_DUKC_OTHER)
            self.print_area_var.set(config.PRINT_AREA_DUKC_OTHER)
        elif idx == 3:
            self.doc_mode_var.set(config.DOC_MODE_CUSTOM)
            cur_area = (self.settings.get(config.KEY_CUSTOM_PRINT_AREA) if self.settings else None) or config.DEFAULT_CUSTOM_PRINT_AREA
            self.print_area_var.set(cur_area)
            self.open_custom_config_dialog()
        else:
            self.doc_mode_var.set(config.DOC_MODE_STANDARD_CTTT)
            self.print_area_var.set(config.PRINT_AREA_STANDARD_CTTT)
        self._invalidate_pair_confirmation()

    def open_custom_config_dialog(self):
        """Mở hộp thoại cấu hình cho chế độ 4: Tùy chỉnh vùng và sheet."""
        def on_save_callback(updated_settings):
            self.settings = self.settings_service.settings
            new_area = updated_settings.get(config.KEY_CUSTOM_PRINT_AREA, config.DEFAULT_CUSTOM_PRINT_AREA)
            self.print_area_var.set(new_area)
            self.update_status(f"Đã cập nhật chế độ Tùy chỉnh: Vùng {new_area}")

        CustomModeConfigDialog(
            self.master,
            self.settings_service,
            self.current_lang,
            on_save_callback,
        )

    def validate_dpi_input(self, event=None):
        """Validate và tự động điều chỉnh DPI input."""
        try:
            val = int(self.pdf_render_dpi.get())
            if val < ValidationService.DPI_MIN:
                self.pdf_render_dpi.set(ValidationService.DPI_MIN)
            elif val > ValidationService.DPI_MAX:
                self.pdf_render_dpi.set(ValidationService.DPI_MAX)
        except Exception:
            self.pdf_render_dpi.set(ValidationService.DPI_DEFAULT)

    def _invalidate_pair_confirmation(self):
        """Require confirmation again whenever inputs or document type change."""
        self.pairs_confirmed = False
        self.workflow_validation_error = None
        self._refresh_workflow_state()

    def _refresh_workflow_state(self):
        """Gate each action until the previous workflow step is complete."""
        if not hasattr(self, "btn_select_old"):
            return

        lang = self.current_lang
        has_doc_mode = bool(getattr(self, "doc_mode_selected", False))
        has_new = bool(self.new_files)
        has_old = bool(self.old_files)
        counts_match = has_new and has_old and len(self.new_files) == len(self.old_files)
        ready = has_doc_mode and counts_match and self.pairs_confirmed and not self.is_processing

        self.btn_select_new.config(state="normal" if has_doc_mode and not self.is_processing else "disabled")
        self.btn_select_old.config(state="normal" if has_doc_mode and has_new and not self.is_processing else "disabled")
        self.btn_check_order.config(state="normal" if counts_match and not self.is_processing else "disabled")
        self.btn_run.config(state="normal" if ready else "disabled")
        if hasattr(self, "btn_legacy"):
            self.btn_legacy.config(state="normal" if ready else "disabled")

        validation_error = getattr(self, "workflow_validation_error", None)
        if not has_doc_mode:
            message = get_text("workflow_msg_1", lang)
            step_states = [
                ("current", get_text("workflow_step_1", lang)),
                ("blocked", get_text("workflow_step_2", lang)),
                ("blocked", get_text("workflow_step_3", lang)),
                ("blocked", get_text("workflow_step_4", lang)),
                ("blocked", get_text("workflow_step_5", lang)),
            ]
        elif not has_new:
            message = get_text("workflow_msg_2", lang)
            step_states = [
                ("done", get_text("workflow_step_1_done", lang)),
                ("current", get_text("workflow_step_2", lang)),
                ("blocked", get_text("workflow_step_3", lang)),
                ("blocked", get_text("workflow_step_4", lang)),
                ("blocked", get_text("workflow_step_5", lang)),
            ]
        elif not has_old:
            message = get_text("workflow_msg_3", lang)
            step_states = [
                ("done", get_text("workflow_step_1_done", lang)),
                ("done", get_text("workflow_step_2_done", lang)),
                ("current", get_text("workflow_step_3", lang)),
                ("blocked", get_text("workflow_step_4", lang)),
                ("blocked", get_text("workflow_step_5", lang)),
            ]
        elif not counts_match:
            message = get_text("workflow_msg_count_mismatch", lang, new_count=len(self.new_files), old_count=len(self.old_files))
            step_states = [
                ("done", get_text("workflow_step_1_done", lang)),
                ("done", get_text("workflow_step_2_done", lang)),
                ("error", get_text("workflow_step_3_error", lang)),
                ("blocked", get_text("workflow_step_4", lang)),
                ("blocked", get_text("workflow_step_5", lang)),
            ]
        elif validation_error:
            message = get_text("workflow_msg_validation_error", lang)
            step_states = [
                ("done", get_text("workflow_step_1_done", lang)),
                ("done", get_text("workflow_step_2_done", lang)),
                ("done", get_text("workflow_step_3_done", lang)),
                ("error", get_text("workflow_step_4_error", lang)),
                ("blocked", get_text("workflow_step_5", lang)),
            ]
        elif not self.pairs_confirmed:
            message = get_text("workflow_msg_confirm_prompt", lang)
            step_states = [
                ("done", get_text("workflow_step_1_done", lang)),
                ("done", get_text("workflow_step_2_done", lang)),
                ("done", get_text("workflow_step_3_done", lang)),
                ("current", get_text("workflow_step_4", lang)),
                ("blocked", get_text("workflow_step_5", lang)),
            ]
        elif self.is_processing:
            message = get_text("workflow_msg_processing", lang)
            step_states = [
                ("done", get_text("workflow_step_1_done", lang)),
                ("done", get_text("workflow_step_2_done", lang)),
                ("done", get_text("workflow_step_3_done", lang)),
                ("done", get_text("workflow_step_4_done", lang)),
                ("current", get_text("workflow_step_5_running", lang)),
            ]
        else:
            message = get_text("workflow_msg_ready", lang)
            step_states = [
                ("done", get_text("workflow_step_1_done", lang)),
                ("done", get_text("workflow_step_2_done", lang)),
                ("done", get_text("workflow_step_3_done", lang)),
                ("done", get_text("workflow_step_4_done", lang)),
                ("done", get_text("workflow_step_5_ready", lang)),
            ]

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
        lang = self.current_lang
        if not getattr(self, "doc_mode_selected", False):
            message = get_text("workflow_err_step1", lang)
        elif not self.new_files:
            message = get_text("workflow_err_step2", lang)
        elif not self.old_files:
            message = get_text("workflow_err_step3", lang)
        elif len(self.new_files) != len(self.old_files):
            message = get_text("workflow_err_mismatch", lang, new_count=len(self.new_files), old_count=len(self.old_files))
        elif not self.pairs_confirmed:
            message = get_text("workflow_err_confirm", lang)
        else:
            return False
        messagebox.showwarning(get_text("workflow_err_title", lang), message, parent=self.master)
        return True

    def _validate_document_mode_selection(self):
        """Block an incompatible document mode before a background thread is started."""
        from services.validation_service import ValidationService

        is_valid, error_message = ValidationService.validate_document_mode(
            self.new_files,
            self.old_files,
            self.doc_mode_var.get(),
            settings=self.settings,
            lang=self.current_lang
        )
        if is_valid:
            self.workflow_validation_error = None
            self._refresh_workflow_state()
            return True

        self.workflow_validation_error = error_message
        self._refresh_workflow_state()
        messagebox.showerror(
            get_text("val_title_incompatible_mode", self.current_lang),
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
        lang = self.current_lang
        initial_dir = self.new_dir_path.get().strip()
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = os.getcwd()
        
        files = filedialog.askopenfilenames(
            initialdir=initial_dir,
            title=get_text("file_dialog_select_new", lang),
            filetypes=[(get_text("file_dialog_excel_filter", lang), "*.xls *.xlsx *.xlsm")]
        )
        
        if not files:
            return
            
        new_selected = list(files)
        
        if self.new_files and not append_only:
            ans = messagebox.askyesnocancel(
                get_text("file_append_replace_title_new", lang),
                get_text("file_append_replace_msg_new", lang, existing_count=len(self.new_files), selected_count=len(new_selected)),
                parent=self.master
            )
            
            if ans is None:
                return  # Cancel
            elif ans is True:
                # Append
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
                # Replace
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
        lang = self.current_lang
        initial_dir = self.old_dir_path.get().strip()
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = os.getcwd()
        
        files = filedialog.askopenfilenames(
            initialdir=initial_dir,
            title=get_text("file_dialog_select_old", lang),
            filetypes=[(get_text("file_dialog_excel_filter", lang), "*.xls *.xlsx *.xlsm")]
        )
        
        if not files:
            return
            
        new_selected = list(files)
        
        if self.old_files and not append_only:
            ans = messagebox.askyesnocancel(
                get_text("file_append_replace_title_old", lang),
                get_text("file_append_replace_msg_old", lang, existing_count=len(self.old_files), selected_count=len(new_selected)),
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
        folder = filedialog.askdirectory(title=get_text("menu_select_result", self.current_lang))
        if folder:
            self.result_path.set(folder)

    def show_help(self):
        ModernHelpWindow(self.master, self.current_lang)

    def check_order(self):
        if not self.new_files or not self.old_files or len(self.new_files) != len(self.old_files):
            self._show_workflow_error()
            return
        self.show_confirmation_dialog()

    def _show_confirmation_dialog_partial(self):
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

    def show_confirmation_dialog(self):
        """Hiển thị hộp thoại xác nhận thứ tự các cặp file CTTT để người dùng kiểm tra, bổ sung và sắp xếp lại"""
        lang = self.current_lang
        
        if not self.new_files and not self.old_files:
            messagebox.showwarning(
                get_text("workflow_err_title", lang), 
                get_text("workflow_err_step2", lang), 
                parent=self.master
            )
            return

        self.confirmation_window = tk.Toplevel(self.master)
        self.confirmation_window.title(get_text("check_order_window_title", lang))
        self.confirmation_window.geometry("860x560")
        self.confirmation_window.minsize(720, 460)
        self.confirmation_window.configure(bg=Colors.BG_MAIN)
        self.confirmation_window.transient(self.master)
        
        self.drag_data = {}
        
        # Header frame
        header_frame = ttk.Frame(self.confirmation_window, padding=Spacing.SM)
        header_frame.pack(fill="x", padx=Spacing.MD, pady=(Spacing.SM, 0))
        
        lbl_hint = ttk.Label(header_frame, text=get_text("check_order_hint", lang), style="Subheader.TLabel", wraplength=820)
        lbl_hint.pack(anchor="w")
        
        self.lbl_match_status = tk.Label(header_frame, font=Fonts.get("base", "bold"), anchor="w", pady=4)
        self.lbl_match_status.pack(fill="x")
        
        # Listboxes frame
        listbox_frame = ttk.Frame(self.confirmation_window)
        listbox_frame.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.SM)
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(1, weight=1)
        listbox_frame.grid_rowconfigure(1, weight=1)
        
        self.lbl_new_header = ttk.Label(listbox_frame, text="", font=Fonts.get("base", "bold"))
        self.lbl_new_header.grid(row=0, column=0, sticky="w", padx=Spacing.SM, pady=(0, 4))
        
        self.lbl_old_header = ttk.Label(listbox_frame, text="", font=Fonts.get("base", "bold"))
        self.lbl_old_header.grid(row=0, column=1, sticky="w", padx=Spacing.SM, pady=(0, 4))
        
        # Left container
        left_subframe = ttk.Frame(listbox_frame)
        left_subframe.grid(row=1, column=0, sticky="nsew", padx=Spacing.SM)
        left_subframe.grid_columnconfigure(0, weight=1)
        left_subframe.grid_rowconfigure(0, weight=1)
        
        self.new_files_listbox = tk.Listbox(left_subframe, selectmode=tk.SINGLE, font=Fonts.get("base"), exportselection=False)
        self.new_files_listbox.grid(row=0, column=0, sticky="nsew")
        new_scroll = ttk.Scrollbar(left_subframe, orient="vertical", command=self.new_files_listbox.yview)
        new_scroll.grid(row=0, column=1, sticky="ns")
        self.new_files_listbox.config(yscrollcommand=new_scroll.set)
        
        left_btn_frame = ttk.Frame(left_subframe)
        left_btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        
        def _add_more_new_files():
            self.select_new_files(append_only=True)
            _refresh_dialog_lists()
            
        def _del_selected_new_file():
            sel = self.new_files_listbox.curselection()
            idx = sel[0] if sel else self.new_files_listbox.index(tk.ACTIVE)
            if idx is not None and 0 <= idx < len(self.new_files):
                self.new_files.pop(idx)
                self._invalidate_pair_confirmation()
                _refresh_dialog_lists()
                if len(self.new_files) > 0:
                    new_idx = min(idx, len(self.new_files) - 1)
                    self.new_files_listbox.selection_set(new_idx)
                    self.new_files_listbox.activate(new_idx)
                
        ttk.Button(left_btn_frame, text=get_text("check_order_btn_add_new", lang), command=_add_more_new_files, style="Primary.TButton").pack(side="left", padx=(0, Spacing.XS))
        ttk.Button(left_btn_frame, text=get_text("check_order_btn_del_new", lang), command=_del_selected_new_file, style="Secondary.TButton").pack(side="left")
        
        # Right container
        right_subframe = ttk.Frame(listbox_frame)
        right_subframe.grid(row=1, column=1, sticky="nsew", padx=Spacing.SM)
        right_subframe.grid_columnconfigure(0, weight=1)
        right_subframe.grid_rowconfigure(0, weight=1)
        
        self.old_files_listbox = tk.Listbox(right_subframe, selectmode=tk.SINGLE, font=Fonts.get("base"), exportselection=False)
        self.old_files_listbox.grid(row=0, column=0, sticky="nsew")
        old_scroll = ttk.Scrollbar(right_subframe, orient="vertical", command=self.old_files_listbox.yview)
        old_scroll.grid(row=0, column=1, sticky="ns")
        self.old_files_listbox.config(yscrollcommand=old_scroll.set)
        
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
                
        ttk.Button(right_btn_frame, text=get_text("check_order_btn_add_old", lang), command=_add_more_old_files, style="Primary.TButton").pack(side="left", padx=(0, Spacing.XS))
        ttk.Button(right_btn_frame, text=get_text("check_order_btn_del_old", lang), command=_del_selected_old_file, style="Secondary.TButton").pack(side="left")
        
        def _refresh_dialog_lists():
            cur_new = self.new_files_listbox.curselection()
            cur_old = self.old_files_listbox.curselection()
            
            self.new_files_listbox.delete(0, tk.END)
            for f in self.new_files:
                self.new_files_listbox.insert(tk.END, os.path.basename(f))
                
            self.old_files_listbox.delete(0, tk.END)
            for f in self.old_files:
                self.old_files_listbox.insert(tk.END, os.path.basename(f))
                
            if cur_new and cur_new[0] < len(self.new_files):
                self.new_files_listbox.selection_set(cur_new[0])
            if cur_old and cur_old[0] < len(self.old_files):
                self.old_files_listbox.selection_set(cur_old[0])
                
            n_new = len(self.new_files)
            n_old = len(self.old_files)
            
            self.lbl_new_header.config(text=get_text("check_order_header_new", lang, count=n_new))
            self.lbl_old_header.config(text=get_text("check_order_header_old", lang, count=n_old))
            
            if n_new == n_old and n_new > 0:
                self.lbl_match_status.config(
                    text=get_text("check_order_matched", lang, count=n_new), 
                    fg="#16A34A"
                )
            else:
                self.lbl_match_status.config(
                    text=get_text("check_order_mismatched", lang, new_count=n_new, old_count=n_old), 
                    fg="#DC2626"
                )
            
            file_names_new = ', '.join([os.path.basename(f) for f in self.new_files])
            file_names_old = ', '.join([os.path.basename(f) for f in self.old_files])
            self.new_files_display.set(file_names_new)
            self.old_files_display.set(file_names_old)
            self._auto_save_settings()

        _refresh_dialog_lists()

        # Drag and Drop bindings
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

        # Buttons footer
        btn_frame = ttk.Frame(self.confirmation_window, padding=Spacing.SM)
        btn_frame.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)
        
        def _on_confirm_click():
            if len(self.new_files) != len(self.old_files):
                messagebox.showwarning(
                    get_text("check_order_warn_title", lang),
                    get_text("check_order_warn_msg", lang, new_count=len(self.new_files), old_count=len(self.old_files)),
                    parent=self.confirmation_window
                )
                return
            self.confirm_files()

        ttk.Button(btn_frame, text=get_text("check_order_btn_confirm", lang), command=_on_confirm_click, style="Primary.TButton").pack(side="left", padx=Spacing.SM)
        ttk.Button(btn_frame, text=get_text("check_order_btn_del_both", lang), command=lambda: (self.delete_selected_items(), _refresh_dialog_lists()), style="Secondary.TButton").pack(side="left", padx=Spacing.SM)
        ttk.Button(btn_frame, text=get_text("check_order_btn_close", lang), command=self.confirmation_window.destroy, style="Secondary.TButton").pack(side="right", padx=Spacing.SM)

    def on_drag_start(self, event):
        widget = event.widget
        self.drag_data["widget"] = widget
        self.drag_data["index"] = widget.nearest(event.y)
        self.drag_data["item"] = widget.get(self.drag_data["index"]) if self.drag_data["index"] >= 0 else None
        self.drag_data["moved"] = False

    def on_drag_motion(self, event):
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
        if self.drag_data.get("moved"):
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

        file_names_new = ', '.join([os.path.basename(f) for f in self.new_files])
        file_names_old = ', '.join([os.path.basename(f) for f in self.old_files])
        self.new_files_display.set(file_names_new)
        self.old_files_display.set(file_names_old)
        self._auto_save_settings()
        self._invalidate_pair_confirmation()

    def confirm_files(self):
        lang = self.current_lang
        if not self._validate_document_mode_selection():
            return False
        self.pairs_confirmed = True
        self._refresh_workflow_state()

        if hasattr(self, 'doc_mode_combo'):
            idx = self.doc_mode_combo.current()
            if idx == 1:
                self.doc_mode_var.set(config.DOC_MODE_DUKC_CTTT)
                self.print_area_var.set(config.PRINT_AREA_DUKC_CTTT)
            elif idx == 2:
                self.doc_mode_var.set(config.DOC_MODE_DUKC_OTHER)
                self.print_area_var.set(config.PRINT_AREA_DUKC_OTHER)
            elif idx == 3:
                self.doc_mode_var.set(config.DOC_MODE_CUSTOM)
                cur_area = (self.settings.get(config.KEY_CUSTOM_PRINT_AREA) if self.settings else None) or config.DEFAULT_CUSTOM_PRINT_AREA
                self.print_area_var.set(cur_area)
            else:
                self.doc_mode_var.set(config.DOC_MODE_STANDARD_CTTT)
                self.print_area_var.set(config.PRINT_AREA_STANDARD_CTTT)

        file_names_new = ', '.join([os.path.basename(f) for f in self.new_files])
        file_names_old = ', '.join([os.path.basename(f) for f in self.old_files])
        self.new_files_display.set(file_names_new)
        self.old_files_display.set(file_names_old)
        self._auto_save_settings()

        if hasattr(self, 'confirmation_window') and self.confirmation_window:
            try:
                self.confirmation_window.destroy()
            finally:
                self.confirmation_window = None

        messagebox.showinfo(
            get_text("confirm_success_title", lang),
            get_text("confirm_success_msg", lang, count=len(self.new_files)),
            parent=self.master
        )
        return True

    # ========== RUN COMPARISON ==========
    def run_comparison(self):
        if self.is_processing:
            utils.logger.warning("Comparison is already in progress, ignoring duplicate trigger.")
            return

        if self._show_workflow_error():
            return

        if not self._validate_document_mode_selection():
            return

        lang = self.current_lang
        
        if not self.new_files or not self.old_files:
            messagebox.showwarning(
                get_text("workflow_err_title", lang),
                get_text("workflow_err_step2", lang) if not self.new_files else get_text("workflow_err_step3", lang)
            )
            return
        
        if len(self.new_files) != len(self.old_files):
            messagebox.showerror(
                get_text("error", lang),
                get_text("workflow_err_mismatch", lang, new_count=len(self.new_files), old_count=len(self.old_files))
            )
            return
        
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
        self.update_status(get_text("status_processing", lang))
        
        thread = threading.Thread(target=self._run_thread, daemon=True)
        thread.start()

    def _run_thread(self):
        lang = self.current_lang
        try:
            settings = dict(self.settings) if self.settings else {}
            settings.update({
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
                "highlight_base_color": self.highlight_base_color,
                "highlight_outline_color": self.highlight_outline_color,
                "highlight_fill_color": self.highlight_fill_color,
                "highlight_fill_opacity": self.highlight_fill_opacity.get(),
                "pdf_diff_threshold": self.pdf_diff_threshold.get(),
                "pdf_dilate_size": self.pdf_dilate_size.get(),
                "pdf_dilate_iterations": self.pdf_dilate_iterations.get(),
            })
            
            self.comparator.use_pdf_method = self.use_pdf_method.get()
            
            elapsed_time = self.comparator.start_comparison(
                self.new_files,
                self.old_files,
                status_callback=self.update_status,
                settings=settings
            )
            
            if elapsed_time:
                minutes, seconds = divmod(elapsed_time, 60)
                time_msg = "\n" + get_text("time_elapsed", lang, minutes=int(minutes), seconds=seconds)
            else:
                time_msg = ""
            
            self.update_status("✅ " + get_text("status_complete", lang))
            messagebox.showinfo(
                get_text("complete", lang), 
                get_text("complete_msg", lang) + time_msg
            )
        except Exception as e:
            self.update_status(f"❌ {get_text('status_error', lang)} {e}")
            messagebox.showerror(get_text("error", lang), str(e))
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
        if self.is_processing:
            utils.logger.warning("Comparison is already in progress, ignoring duplicate legacy trigger.")
            return

        if self._show_workflow_error():
            return

        if not self._validate_document_mode_selection():
            return
        lang = self.current_lang
        
        if not self.new_files or not self.old_files:
            messagebox.showwarning(
                get_text("workflow_err_title", lang),
                get_text("workflow_err_step2", lang) if not self.new_files else get_text("workflow_err_step3", lang)
            )
            return
        
        if len(self.new_files) != len(self.old_files):
            messagebox.showerror(
                get_text("error", lang),
                get_text("workflow_err_mismatch", lang, new_count=len(self.new_files), old_count=len(self.old_files))
            )
            return
        
        confirm = messagebox.askyesno(
            get_text("legacy_confirm_title", lang),
            get_text("legacy_confirm_msg", lang)
        )
        
        if not confirm:
            return
        
        self.btn_run.config(state="disabled")
        self.btn_legacy.config(state="disabled")
        self.update_status(get_text("status_processing", lang))
        
        threading.Thread(target=self._run_legacy_thread, daemon=True).start()
    
    def _run_legacy_thread(self):
        lang = self.current_lang
        try:
            mode_idx = self.screen_combo.current() if hasattr(self, 'screen_combo') else -1
            if mode_idx == 1:
                screen_mode = "vps"
            elif mode_idx == 2:
                screen_mode = "monitor"
            else:
                screen_mode = "pc"
            
            settings = dict(self.settings) if self.settings else {}
            settings.update({
                "screen_mode": screen_mode,
                "zoom": self.zoom_var.get(),
                "goto_address": "EX1" if not self.goto_address.get().strip() or self.goto_address.get().strip().upper() in ["A1", ""] else self.goto_address.get().strip(),
                "output_folder": self.result_path.get().strip() or None,
                "highlight_fill_color": self.highlight_fill_color,
                "highlight_fill_opacity": self.highlight_fill_opacity.get(),
                "doc_mode": self.doc_mode_var.get(),
                "print_area": self.print_area_var.get(),
            })
            
            elapsed_time = self.comparator.start_legacy_comparison(
                self.new_files,
                self.old_files,
                status_callback=self.update_status,
                progress_callback=None,
                settings=settings
            )
            
            if elapsed_time:
                minutes, seconds = divmod(elapsed_time, 60)
                time_msg = "\n" + get_text("time_elapsed", lang, minutes=int(minutes), seconds=seconds)
            else:
                time_msg = ""
            
            self.update_status("✅ " + get_text("status_complete", lang))
            messagebox.showinfo(
                get_text("legacy_complete_title", lang), 
                get_text("legacy_complete_msg", lang) + time_msg
            )
            
        except Exception as e:
            self.update_status(f"❌ {get_text('status_error', lang)} {e}")
            messagebox.showerror(get_text("error", lang), str(e))
        finally:
            self.btn_run.config(state="normal")
            self.btn_legacy.config(state="normal")

    # ========== COLOR PICKERS ==========
    def select_base_color(self):
        color = colorchooser.askcolor(title=get_text("color_picker_base", self.current_lang), initialcolor=self.highlight_base_color)
        if color[1]:
            self.highlight_base_color = color[1]
            self.bg_color = color[1]
            self.base_color_label.config(text=f"  {color[1]}  ", bg=color[1])
            self._auto_save_settings()

    def select_outline_color(self):
        color = colorchooser.askcolor(title=get_text("color_picker_outline", self.current_lang), initialcolor=self.highlight_outline_color)
        if color[1]:
            self.highlight_outline_color = color[1]
            self.outline_color = color[1]
            self.outline_color_label.config(text=f"  {color[1]}  ", bg=color[1])
            self._auto_save_settings()

    def select_fill_color(self):
        color = colorchooser.askcolor(title=get_text("color_picker_fill", self.current_lang), initialcolor=self.highlight_fill_color)
        if color[1]:
            self.highlight_fill_color = color[1]
            self.fill_color_label.config(text=f"  {color[1]}  ", bg=color[1])
            self._auto_save_settings()



    # ========== SETTINGS AUTO SAVE ==========
    def _auto_save_settings(self):
        if hasattr(self, 'save_user_settings') and self.save_user_settings.get():
            try:
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
            except Exception as e:
                utils.logger.warning(f"Failed to auto-save settings: {e}")

    # ========== LANGUAGE CHANGE ==========
    def on_language_change(self, event=None):
        lang_idx = self.lang_combo.current()
        lang_codes = list(LANGUAGES.keys())
        if 0 <= lang_idx < len(lang_codes):
            new_lang = lang_codes[lang_idx]
            self.current_lang = new_lang
            self._refresh_all_ui_texts()
            self._auto_save_settings()
    
    def _refresh_all_ui_texts(self):
        """Cập nhật toàn bộ text trong UI khi thay đổi ngôn ngữ (hot-swap)"""
        lang = self.current_lang
        
        # Window Title
        self.master.title(get_text("app_title", lang))

        # ===== HEADER =====
        if hasattr(self, 'title_label'):
            self.title_label.config(text=get_text("header_title", lang))
        if hasattr(self, 'help_btn'):
            self.help_btn.config(text=get_text("btn_help", lang))
        
        # ===== CARD 1: FILE SELECTION =====
        if hasattr(self, 'file_card'):
            self.file_card.config(text=get_text("card_file_selection", lang))
        
        if hasattr(self, 'lbl_doc_mode'):
            self.lbl_doc_mode.config(text=get_text("doc_type_label", lang))
        if hasattr(self, 'doc_mode_combo'):
            curr_idx = self.doc_mode_combo.current()
            self.doc_mode_combo.config(values=[
                get_text("mode_standard_cttt", lang),
                get_text("mode_dukc_cttt", lang),
                get_text("mode_dukc_other", lang),
                get_text("mode_custom", lang),
            ])
            if curr_idx >= 0:
                self.doc_mode_combo.current(curr_idx)
        if hasattr(self, 'btn_custom_config'):
            self.btn_custom_config.config(text=f"⚙️ {get_text('btn_custom_config', lang)}")

        if hasattr(self, 'lbl_screen_mode'):
            self.lbl_screen_mode.config(text=get_text("screen_mode_label", lang))
        
        if hasattr(self, 'lbl_cttt_new'):
            self.lbl_cttt_new.config(text=get_text("lbl_cttt_new", lang))
        if hasattr(self, 'lbl_cttt_old'):
            self.lbl_cttt_old.config(text=get_text("lbl_cttt_old", lang))
        if hasattr(self, 'lbl_selected_new'):
            self.lbl_selected_new.config(text=get_text("lbl_selected_new", lang))
        if hasattr(self, 'lbl_selected_old'):
            self.lbl_selected_old.config(text=get_text("lbl_selected_old", lang))
        
        if hasattr(self, 'btn_select_new'):
            self.btn_select_new.config(text=get_text("btn_select_new", lang))
        if hasattr(self, 'btn_select_old'):
            self.btn_select_old.config(text=get_text("btn_select_old", lang))
        
        if hasattr(self, 'lbl_result_path'):
            self.lbl_result_path.config(text=get_text("lbl_result_path", lang))
        if hasattr(self, 'btn_browse'):
            self.btn_browse.config(text=get_text("btn_browse", lang))
        if hasattr(self, 'btn_check_order'):
            self.btn_check_order.config(text=get_text("btn_check_order", lang))
        
        # ===== RUN BUTTON & LEGACY =====
        if hasattr(self, 'btn_run'):
            self.btn_run.config(text=get_text("btn_run_main", lang))
        if hasattr(self, 'legacy_frame'):
            self.legacy_frame.config(text=get_text("legacy_frame_title", lang))
        if hasattr(self, 'btn_legacy'):
            self.btn_legacy.config(text=get_text("btn_legacy", lang))
        if hasattr(self, 'lbl_legacy_warning'):
            self.lbl_legacy_warning.config(text=get_text("legacy_warning", lang))

        # ===== CARD 2: SETTINGS =====
        if hasattr(self, 'settings_card'):
            self.settings_card.config(text=get_text("card_settings", lang))
        if hasattr(self, 'chk_use_pdf'):
            self.chk_use_pdf.config(text=get_text("chk_use_pdf", lang))
        if hasattr(self, 'lbl_dpi'):
            self.lbl_dpi.config(text=get_text("lbl_dpi", lang))
        if hasattr(self, 'lbl_zoom'):
            self.lbl_zoom.config(text=get_text("lbl_zoom", lang))
        if hasattr(self, 'lbl_goto'):
            self.lbl_goto.config(text=get_text("lbl_goto", lang))
        if hasattr(self, 'chk_auto_b'):
            self.chk_auto_b.config(text=get_text("chk_auto_b", lang))
        if hasattr(self, 'chk_suppress'):
            self.chk_suppress.config(text=get_text("chk_suppress", lang))
        if hasattr(self, 'chk_save'):
            self.chk_save.config(text=get_text("chk_save", lang))
        
        # ===== CARD 3: HIGHLIGHT =====
        if hasattr(self, 'hl_card'):
            self.hl_card.config(text=get_text("card_highlight", lang))
        if hasattr(self, 'btn_base_color'):
            self.btn_base_color.config(text=get_text("btn_base_color", lang))
        if hasattr(self, 'btn_outline_color'):
            self.btn_outline_color.config(text=get_text("btn_outline_color", lang))
        if hasattr(self, 'btn_fill_color'):
            self.btn_fill_color.config(text=get_text("btn_fill_color", lang))
        
        if hasattr(self, 'lbl_opacity'):
            self.lbl_opacity.config(text=get_text("lbl_opacity", lang))
        if hasattr(self, 'lbl_threshold'):
            self.lbl_threshold.config(text=get_text("lbl_threshold", lang))
        if hasattr(self, 'lbl_dilate_size'):
            self.lbl_dilate_size.config(text=get_text("lbl_dilate_size", lang))
        if hasattr(self, 'lbl_dilate_iter'):
            self.lbl_dilate_iter.config(text=get_text("lbl_dilate_iter", lang))
            
        # ===== STATUS BAR =====
        if hasattr(self, 'status_version_label'):
            self.status_version_label.config(
                text=get_text("status_version", lang, version=config.APP_VERSION, date=config.APP_DATE)
            )
        if hasattr(self, 'status_label') and not self.is_processing:
            self.status_label.config(text="✅ " + get_text("status_ready", lang))
            
        # ===== SCREEN COMBO =====
        if hasattr(self, 'screen_combo'):
            current_idx = self.screen_combo.current()
            self.screen_combo.config(values=[
                get_text("screen_pc", lang),
                get_text("screen_vps", lang),
                get_text("screen_secondary", lang)
            ])
            if current_idx >= 0:
                self.screen_combo.current(current_idx)

        # ===== REBUILD MENU & WORKFLOW BADGES =====
        self.create_menu_bar()
        self._refresh_workflow_state()

    # ========== MENU & PHÍM TẮT ==========
    def create_menu_bar(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        lang = self.current_lang
        
        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=get_text("menu_file", lang), menu=file_menu)
        file_menu.add_command(label=get_text("menu_select_new", lang), command=self.select_new_files, accelerator="Ctrl+N")
        file_menu.add_command(label=get_text("menu_select_old", lang), command=self.select_old_files, accelerator="Ctrl+Shift+O")
        file_menu.add_command(label=get_text("menu_select_result", lang), command=self.browse_result_folder, accelerator="Ctrl+R")
        file_menu.add_separator()
        file_menu.add_command(label=get_text("menu_save_settings", lang), command=self._auto_save_settings, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label=get_text("menu_exit", lang), command=self.master.quit, accelerator="Alt+F4")
        
        # Menu Edit
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=get_text("menu_edit", lang), menu=edit_menu)
        edit_menu.add_command(label=get_text("menu_check_order", lang), command=self.check_order, accelerator="Ctrl+K")
        edit_menu.add_separator()
        edit_menu.add_command(label=get_text("menu_start_compare", lang), command=self.run_comparison, accelerator="F5")
        
        # Menu View
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=get_text("menu_view", lang), menu=view_menu)
        view_menu.add_command(label=get_text("menu_open_result", lang), command=self._open_result_folder, accelerator="Ctrl+E")
        
        # Menu Help
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=get_text("menu_help", lang), menu=help_menu)
        help_menu.add_command(label=get_text("menu_user_guide", lang), command=self.show_help, accelerator="F1")
        help_menu.add_command(label=get_text("menu_shortcuts", lang), command=self._show_shortcuts)
        help_menu.add_command(label=get_text("menu_check_updates", lang), command=lambda: self._check_updates_in_background(manual=True))
        help_menu.add_separator()
        
        about_title = get_text("about_title", lang)
        about_msg = get_text("about_msg", lang, version=config.APP_VERSION, date=config.APP_DATE)
        help_menu.add_command(label=get_text("menu_about", lang), command=lambda: messagebox.showinfo(about_title, about_msg))
    
    def _show_shortcuts(self):
        lang = self.current_lang
        shortcuts_list = [
            "Ctrl+N / Ctrl+O     " + get_text("menu_select_new", lang),
            "Ctrl+Shift+O        " + get_text("menu_select_old", lang),
            "Ctrl+R              " + get_text("menu_select_result", lang),
            "Ctrl+S              " + get_text("menu_save_settings", lang),
            "Ctrl+K              " + get_text("menu_check_order", lang),
            "F5 / Ctrl+Enter     " + get_text("menu_start_compare", lang),
            "F6                  " + get_text("btn_legacy", lang),
            "Ctrl+E              " + get_text("menu_open_result", lang),
            "F1                  " + get_text("menu_user_guide", lang),
            "Escape              Unfocus",
            "Alt+F4              " + get_text("menu_exit", lang)
        ]
        msg = get_text("shortcuts_header", lang) + "\n".join(shortcuts_list)
        messagebox.showinfo(get_text("shortcuts_title", lang), msg)

    def bind_shortcuts(self):
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
        
        self.master.bind('<Control-Return>', lambda e: self.run_comparison())
        self.master.bind('<F5>', lambda e: self.run_comparison())
        self.master.bind('<F6>', lambda e: self.run_legacy_comparison())
        
        self.master.bind('<Control-k>', lambda e: self.check_order())
        self.master.bind('<Control-K>', lambda e: self.check_order())
        
        self.master.bind('<Control-e>', lambda e: self._open_result_folder())
        self.master.bind('<Control-E>', lambda e: self._open_result_folder())
        
        self.master.bind('<F1>', lambda e: self.show_help())
        self.master.bind('<Escape>', lambda e: self.master.focus_set())
    
    def _manual_save_settings(self):
        lang = self.current_lang
        self._auto_save_settings()
        messagebox.showinfo(
            get_text("settings_saved_title", lang),
            get_text("settings_saved_msg", lang)
        )
    
    def _open_result_folder(self):
        lang = self.current_lang
        result_path = self.result_path.get()
        if result_path and os.path.isdir(result_path):
            os.startfile(result_path)
        elif self.new_files:
            folder = os.path.dirname(self.new_files[0])
            if os.path.isdir(folder):
                os.startfile(folder)
            else:
                messagebox.showwarning(
                    get_text("notice_title", lang),
                    get_text("folder_not_found_msg", lang)
                )
        else:
            messagebox.showwarning(
                get_text("notice_title", lang),
                get_text("no_folder_selected_msg", lang)
            )

    # ========== AUTO UPDATE ==========
    def _check_updates_in_background(self, manual=False):
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
        lang = self.current_lang
        if not has_update:
            if manual:
                messagebox.showinfo(
                    get_text("update_title", lang),
                    get_text("update_no_release", lang, version=config.APP_VERSION)
                )
            return
        
        current_ver = config.APP_VERSION
        message = get_text("update_found_msg", lang, newest_ver=newest_ver, current_ver=current_ver)
        if candidate and hasattr(candidate, 'notes') and candidate.notes:
            message += get_text("update_release_notes", lang, notes=candidate.notes)
            
        if messagebox.askyesno(get_text("update_title", lang), message):
            self.update_status(get_text("update_status_downloading", lang))
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
            lang = self.current_lang
            messagebox.showwarning(
                get_text("update_title", lang),
                get_text("update_error_msg", lang, error=str(error))
            )


def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
