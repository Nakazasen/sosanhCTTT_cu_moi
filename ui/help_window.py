import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import logging
from ui.translations import get_text

class ModernHelpWindow(tk.Toplevel):
    def __init__(self, parent, current_lang="vi"):
        super().__init__(parent)
        self.current_lang = current_lang
        self.title(get_text("help_title", current_lang))
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Icon (if available in parent)
        if parent.iconbitmap():
            try:
                self.iconbitmap(parent.iconbitmap())
            except:
                pass
                
        # Main layout
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load assets path
        self.assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "help")
        
        # Build Tabs
        self.build_overview_tab()
        self.build_step1_tab()
        self.build_step2_tab()
        self.build_settings_tab()
        self.build_legacy_tab()
        
        # Close button
        btn_close = ttk.Button(self, text=get_text("btn_close", current_lang), command=self.destroy)
        btn_close.pack(pady=(0, 10), ipadx=20)

    def create_scrollable_tab(self, tab_title):
        """Create a tab frame with a scrollbar"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=tab_title)
        
        canvas = tk.Canvas(frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="White.TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        return scrollable_frame

    def add_section_title(self, parent, text):
        lbl = tk.Label(parent, text=text, font=("Segoe UI", 16, "bold"), fg="#1D4ED8", bg="white", anchor="w")
        lbl.pack(fill="x", padx=20, pady=(20, 10))
        
    def add_paragraph(self, parent, text):
        lbl = tk.Label(parent, text=text, font=("Segoe UI", 11), bg="white", justify="left", wraplength=780, anchor="w")
        lbl.pack(fill="x", padx=20, pady=5)
        
    def add_bullet_point(self, parent, text):
        lbl = tk.Label(parent, text=f"•  {text}", font=("Segoe UI", 11), bg="white", justify="left", wraplength=760, anchor="w")
        lbl.pack(fill="x", padx=40, pady=2)

    def add_image(self, parent, image_filename):
        """Load and display an image from assets/help"""
        img_path = os.path.join(self.assets_path, image_filename)
        if os.path.exists(img_path):
            try:
                # Load and resize logic could go here. For now, just load.
                pil_img = Image.open(img_path)
                # Resize if too wide
                base_width = 700
                if pil_img.width > base_width:
                    w_percent = (base_width / float(pil_img.width))
                    h_size = int((float(pil_img.height) * float(w_percent)))
                    pil_img = pil_img.resize((base_width, h_size), Image.Resampling.LANCZOS)
                
                tk_img = ImageTk.PhotoImage(pil_img)
                lbl = tk.Label(parent, image=tk_img, bg="white", bd=1, relief="solid")
                lbl.image = tk_img # Keep reference
                lbl.pack(pady=15)
            except Exception as e:
                logging.error(f"Failed to load help image {image_filename}: {e}")
                
    def build_overview_tab(self):
        titles = {
            "vi": "Tổng quan", "en": "Overview", "zh": "概览", "ja": "概要"
        }
        content = self.create_scrollable_tab(titles.get(self.current_lang, "Overview"))
        
        intro_texts = {
            "vi": "Phần mềm So sánh CTTT giúp tự động phát hiện sự khác biệt giữa hai phiên bản tài liệu (Cũ vs Mới).",
            "en": "The SOP Comparison Tool automatically detects differences between two document versions (Old vs New).",
            "zh": "SOP对比工具自动检测两个文档版本(旧与新)之间的差异。",
            "ja": "SOP比較ツールは、2つのドキュメントバージョン(新旧)間の違いを自動的に検出します。"
        }
        
        self.add_section_title(content, titles.get(self.current_lang, "Overview"))
        self.add_paragraph(content, intro_texts.get(self.current_lang, intro_texts["en"]))
        
        # Add placeholder for overview image
        self.add_image(content, "overview.png")

        methods_title = {
            "vi": "Các phương pháp so sánh", "en": "Comparison Methods", "zh": "比较方法", "ja": "比較方法"
        }
        self.add_section_title(content, methods_title.get(self.current_lang, "Comparison Methods"))
        
        methods = {
            "vi": [
                "Phương pháp PDF (Khuyên dùng): Chuyển đổi Excel sang PDF rồi so sánh. Độ chính xác cao nhất.",
                "Phương pháp Chụp màn hình (Nhanh): Chụp ảnh nội dung Excel dùng bộ nhớ đêm. Tốc độ nhanh.",
                "Phương pháp Phiên bản cũ (Trực tiếp): Giả lập thao tác giống phiên bản 6. Chậm nhưng quen thuộc."
            ],
            "en": [
                "PDF Method (Recommended): Converts Excel to PDF for comparison. Highest accuracy.",
                "Screenshot Method (Fast): Captures Excel content screenshots. High speed.",
                "Legacy Method (Old): Simulates version 6 user operations. Slow but familiar."
            ],
            "zh": [
                "PDF方法 (推荐): 将Excel转换为PDF进行对比。准确度最高。",
                "截图方法 (快速): 截取Excel内容进行对比。速度快。",
                "传统方法 (旧版): 模拟版本6用户操作。速度较慢但熟悉。"
            ],
            "ja": [
                "PDF方式 (推奨): ExcelをPDFに変換して比較。最も高精度。",
                "スクリーンショット方式 (高速): Excel内容をキャプチャして比較。高速。",
                "レガシー方式 (旧版): バージョン6の操作をシミュレート。遅いが慣れ親しんだ方式。"
            ]
        }
        
        current_methods = methods.get(self.current_lang, methods["en"])
        
        for m in current_methods:
            self.add_bullet_point(content, m)
            
    def build_step1_tab(self):
        titles = {
            "vi": "B1: Chọn File", "en": "S1: Select Files", "zh": "步骤1: 选择文件", "ja": "手順1: ファイル選択"
        }
        content = self.create_scrollable_tab(titles.get(self.current_lang, "S1: Select Files"))
        
        self.add_section_title(content, titles.get(self.current_lang, "S1: Select Files"))
        
        steps = {
            "vi": [
                "1. Chọn 'Chế độ màn hình' phù hợp (PC, VPS, hoặc Màn hình phụ).",
                "2. Nhấn nút 'Chọn CTTT Mới' để chọn file phiên bản mới.",
                "3. Nhấn nút 'Chọn CTTT Cũ' để chọn file phiên bản cũ.",
                "4. Kiểm tra danh sách file ở các ô text."
            ],
            "en": [
                "1. Select appropriate 'Screen mode' (PC, VPS, or Secondary Screen).",
                "2. Click 'Select New SOP' to open new version files.",
                "3. Click 'Select Old SOP' to open old version files.",
                "4. Verify the file lists in the text boxes."
            ],
            "zh": [
                "1. 选择合适的 '屏幕模式' (PC, VPS 或 副屏)。",
                "2. 点击 '选择新作业指导书' 打开新版本文件。",
                "3. 点击 '选择旧作业指导书' 打开旧版本文件。",
                "4. 检查文本框中的文件列表。"
            ],
            "ja": [
                "1. 適切な「画面モード」(PC, VPS, またはサブ画面)を選択します。",
                "2. 「新作業指導書選択」をクリックして新形式ファイルを開きます。",
                "3. 「旧作業指導書選択」をクリックして旧形式ファイルを開きます。",
                "4. テキストボックスのファイルリストを確認します。"
            ]
        }
        
        current_steps = steps.get(self.current_lang, steps["en"])
        
        for s in current_steps:
            self.add_paragraph(content, s)
            
        self.add_image(content, "step1_select.png")
        
        note = {
            "vi": "Lưu ý: Tên file hoặc cấu trúc folder nên giống nhau để phần mềm tự động ghép cặp chính xác. Nhấn 'Kiểm tra thứ tự' để xác nhận.",
            "en": "Note: Filenames or folder text should be similar for auto-matching. Click 'Check SOP pair order' to verify.",
            "zh": "注意: 文件名或文件夹结构应相似以便自动匹配。点击 '检查配对顺序' 进行确认。",
            "ja": "注: 自動マッチングのため、ファイル名やフォルダ構成は類似している必要があります。「ペア順序確認」をクリックして確認してください。"
        }
        
        tk.Label(content, text=f"💡 {note.get(self.current_lang, note['en'])}", 
                 fg="#D97706", bg="#FFFBEB", font=("Segoe UI", 10, "italic"), padx=10, pady=10).pack(fill="x", padx=20, pady=10)

    def build_step2_tab(self):
        titles = {
            "vi": "B2: Chạy so sánh", "en": "S2: Run Compare", "zh": "步骤2: 运行对比", "ja": "手順2: 比較実行"
        }
        content = self.create_scrollable_tab(titles.get(self.current_lang, "S2: Run Compare"))
        self.add_section_title(content, titles.get(self.current_lang, "S2: Run Compare"))
        
        run_inst = {
            "vi": "Sau khi chọn file xong, nhấn nút BẮT ĐẦU màu xanh lớn.",
            "en": "After selecting files, click the large blue START button.",
            "zh": "选择文件后，点击蓝色的大 '开始' 按钮。",
            "ja": "ファイル選択後、大きな青い「比較開始」ボタンをクリックします。"
        }
        self.add_paragraph(content, run_inst.get(self.current_lang, run_inst["en"]))
        self.add_image(content, "step2_run.png")
        
        res_titles = {"vi": "Kết quả", "en": "Results", "zh": "结果", "ja": "結果"}
        self.add_section_title(content, res_titles.get(self.current_lang, "Results"))
        
        res_inst = {
            "vi": "Kết quả sẽ được lưu vào thư mục bạn chọn (hoặc cùng thư mục với file mới).",
            "en": "Results are saved in your selected folder (or same folder as new file).",
            "zh": "结果将保存到您选择的文件夹 (或新文件所在文件夹)。",
            "ja": "結果は選択したフォルダ (または新しいファイルと同じフォルダ) に保存されます。"
        }
        self.add_paragraph(content, res_inst.get(self.current_lang, res_inst["en"]))
        self.add_image(content, "step2_result.png")

    def build_settings_tab(self):
        titles = {
            "vi": "Cài đặt", "en": "Settings", "zh": "设置", "ja": "設定"
        }
        content = self.create_scrollable_tab(titles.get(self.current_lang, "Settings"))
        self.add_section_title(content, titles.get(self.current_lang, "Settings"))
        
        settings = {
            "vi": [
                "Sử dụng phương pháp PDF: Tắt đi nếu bạn muốn chạy nhanh hơn, nhưng độ chính xác có thể giảm một chút.",
                "Tự động thêm 'b': Bật nếu file barcode của bạn không có hậu tố 'b' nhưng bạn muốn so sánh với file thường.",
                "Thiết lập Highlight: Bạn có thể thay đổi màu sắc vùng khác biệt (Đỏ, Vàng...) và độ đậm nhạt."
            ],
            "en": [
                "Use PDF Method: Uncheck for faster speed, but accuracy might slightly decrease.",
                "Auto-add 'b': Enable if your barcode files miss the 'b' suffix but you want to compare.",
                "Highlight Settings: Customize the difference color (Red, Yellow...) and opacity."
            ],
            "zh": [
                "使用PDF方法: 如果想运行得更快可取消勾选，但准确度可能会略有降低。",
                "自动添加 'b': 如果您的条码文件缺少 'b' 后缀但需要对比，请启用此项。",
                "高亮设置: 自定义差异颜色 (红, 黄...) 和透明度。"
            ],
            "ja": [
                "PDF方式を使用: 高速化したい場合はチェックを外しますが、精度が若干低下する可能性があります。",
                "自動的に 'b' を追加: バーコードファイルに 'b' 接尾辞がないが比較したい場合に有効にします。",
                "ハイライト設定: 差異の色 (赤、黄など) と不透明度をカスタマイズします。"
            ]
        }
        
        current = settings.get(self.current_lang, settings["en"])
        for s in current:
            self.add_bullet_point(content, s)
            
        self.add_image(content, "settings.png")

    def build_legacy_tab(self):
        titles = {
            "vi": "Chế độ (Phiên bản cũ)", "en": "Legacy Mode", "zh": "传统模式", "ja": "レガシーモード"
        }
        content = self.create_scrollable_tab(titles.get(self.current_lang, "Legacy Mode"))
        self.add_section_title(content, titles.get(self.current_lang, "Legacy Mode"))
        
        warn = {
            "vi": "⚠️ Chế độ này sẽ chiếm quyền điều khiển chuột và màn hình. KHÔNG chạm vào máy tính khi đang chạy.",
            "en": "⚠️ This mode takes control of mouse and screen. DO NOT touch the computer while running.",
            "zh": "⚠️ 此模式将控制鼠标和屏幕。运行期间请勿触碰电脑。",
            "ja": "⚠️ このモードはマウスと画面を制御します。実行中はコンピュータに触れないでください。"
        }
        
        tk.Label(content, text=warn.get(self.current_lang, warn['en']), fg="red", bg="#FEF2F2", font=("Segoe UI", 11, "bold"), padx=10, pady=10).pack(fill="x", padx=20)
        
        desc = {
            "vi": "Sử dụng nút màu vàng ở dưới cùng nếu phương pháp mới không hoạt động đúng với định dạng file đặc biệt của bạn.",
            "en": "Use the yellow button at the bottom if the new method fails with your specific file format.",
            "zh": "如果新方法无法正确处理您的特定文件格式，请使用底部的黄色按钮。",
            "ja": "新しい方法で特定のファイル形式が正しく処理されない場合は、下部の黄色いボタンを使用してください。"
        }
        self.add_paragraph(content, desc.get(self.current_lang, desc['en']))
