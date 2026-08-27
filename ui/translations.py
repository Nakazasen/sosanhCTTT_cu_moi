# -*- coding: utf-8 -*-
"""
Localization module for CTTT Comparison Tool
Supports: Vietnamese (vi), English (en), Chinese (zh), Japanese (ja)
"""

LANGUAGES = {
    "vi": "Tiếng Việt",
    "en": "English", 
    "zh": "中文",
    "ja": "日本語"
}

TRANSLATIONS = {
    # ========== APP TITLE ==========
    "app_title": {
        "vi": "Phần mềm so sánh CTTT cũ - mới",
        "en": "SOP Comparison Tool - Old vs New",
        "zh": "作业指导书对比工具 - 新旧版本",
        "ja": "作業指導書比較ツール - 新旧版"
    },
    
    # ========== HEADER ==========
    "header_warning": {
        "vi": "ĐỌC KỸ HƯỚNG DẪN SỬ DỤNG TRƯỚC KHI DÙNG",
        "en": "READ THE USER GUIDE CAREFULLY BEFORE USE",
        "zh": "使用前请仔细阅读使用说明",
        "ja": "使用前に必ずガイドをお読みください"
    },
    "btn_help": {
        "vi": "Hướng dẫn sử dụng cơ bản >>Bấm vào xem<<",
        "en": "Basic User Guide >>Click to view<<",
        "zh": "基本使用指南 >>点击查看<<",
        "ja": "基本ガイド >>クリックして表示<<"
    },
    
    # ========== SCREEN MODE ==========
    "screen_mode_label": {
        "vi": "Chọn loại màn hình sử dụng:",
        "en": "Select screen type:",
        "zh": "选择屏幕类型:",
        "ja": "画面タイプを選択:"
    },
    "screen_pc": {
        "vi": "Phiên bản dùng cho màn hình máy tính",
        "en": "Desktop screen version",
        "zh": "电脑屏幕版本",
        "ja": "デスクトップ画面版"
    },
    "screen_vps": {
        "vi": "VPS",
        "en": "VPS",
        "zh": "VPS",
        "ja": "VPS"
    },
    "screen_secondary": {
        "vi": "Màn hình phụ",
        "en": "Secondary monitor",
        "zh": "副屏",
        "ja": "サブモニター"
    },
    
    # ========== DOCUMENT COMPARISON MODE ==========
    "doc_type_label": {
        "vi": "Loại tài liệu so sánh:",
        "en": "Comparison Document Type:",
        "zh": "对比文档类型:",
        "ja": "比較ドキュメントの種類:"
    },
    "mode_standard_cttt": {
        "vi": "📘 1. CTTT thông thường có form từ EX...xanh (Vùng EX1:GR76)",
        "en": "📘 1. Standard SOP (Form from EX... green tab - Range EX1:GR76)",
        "zh": "📘 1. 普通作业指导书 (从EX起的表格...绿色标签 - 范围 EX1:GR76)",
        "ja": "📘 1. 通常の作業指導書 (EXからのフォーム...緑色タブ - 範囲 EX1:GR76)"
    },
    "mode_dukc_cttt": {
        "vi": "📑 2. CTTT Đính Kèm ĐƯKC (Vùng J2:BD76 - Nhiều sheet)",
        "en": "📑 2. SOP DUKC Attachment (Range J2:BD76 - Multi-sheet)",
        "zh": "📑 2. 应急应对附带作业指导书 (范围 J2:BD76 - 多工作表)",
        "ja": "📑 2. 緊急対応添付作業指導書 (範囲 J2:BD76 - 複数シート)"
    },
    "mode_dukc_other": {
        "vi": "📄 3. Tờ Phát Hành ĐƯKC & Khác (Vùng A1:AT120 - Nhiều sheet)",
        "en": "📄 3. DUKC Release Form & Others (Range A1:AT120 - Multi-sheet)",
        "zh": "📄 3. 应急应对发行表及其它 (范围 A1:AT120 - 多工作表)",
        "ja": "📄 3. 緊急対応発行票・その他 (範囲 A1:AT120 - 複数シート)"
    },
    "print_area_label": {
        "vi": "Phạm vi so sánh:",
        "en": "Compare Range:",
        "zh": "对比范围:",
        "ja": "比較範囲:"
    },

    # ========== FILE SELECTION ==========
    "new_files_label": {
        "vi": "1.1. Chọn các file chỉ thị thao tác mới:",
        "en": "1.1. Select new SOP files:",
        "zh": "1.1. 选择新的作业指导书文件:",
        "ja": "1.1. 新しい作業指導書ファイルを選択:"
    },
    "old_files_label": {
        "vi": "1.2. Chọn các File chỉ thị thao tác cũ:",
        "en": "1.2. Select old SOP files:",
        "zh": "1.2. 选择旧的作业指导书文件:",
        "ja": "1.2. 古い作業指導書ファイルを選択:"
    },
    "paste_folder_path": {
        "vi": "Dán đường dẫn thư mục:",
        "en": "Paste folder path:",
        "zh": "粘贴文件夹路径:",
        "ja": "フォルダパスを貼り付け:"
    },
    "selected_files": {
        "vi": "Các file đã chọn:",
        "en": "Selected files:",
        "zh": "已选择的文件:",
        "ja": "選択されたファイル:"
    },
    "btn_open_new": {
        "vi": "Mở CTTT mới",
        "en": "Open new SOP",
        "zh": "打开新作业指导书",
        "ja": "新作業指導書を開く"
    },
    "btn_open_old": {
        "vi": "Mở CTTT cũ",
        "en": "Open old SOP",
        "zh": "打开旧作业指导书",
        "ja": "旧作業指導書を開く"
    },
    
    # ========== RESULT PATH ==========
    "result_path_label": {
        "vi": "Đường dẫn lưu file kết quả (để trống nếu muốn lưu cùng thư mục với CTTT mới):",
        "en": "Result file save path (leave empty to save in same folder as new SOP):",
        "zh": "结果文件保存路径(留空则保存在新作业指导书同一文件夹):",
        "ja": "結果ファイル保存先(新作業指導書と同じフォルダに保存する場合は空欄):"
    },
    "btn_browse": {
        "vi": "Duyệt...",
        "en": "Browse...",
        "zh": "浏览...",
        "ja": "参照..."
    },
    
    # ========== BUTTONS ==========
    "btn_check_order": {
        "vi": "Kiểm tra trình tự lựa chọn các cặp CTTT",
        "en": "Check SOP pair selection order",
        "zh": "检查作业指导书配对选择顺序",
        "ja": "作業指導書ペア選択順序を確認"
    },
    "btn_run_main": {
        "vi": "2. BẮT ĐẦU SO SÁNH (PHƯƠNG PHÁP MỚI)",
        "en": "2. START COMPARISON (NEW METHOD)",
        "zh": "2. 开始对比 (新方法)",
        "ja": "2. 比較開始 (新方式)"
    },
    "btn_legacy": {
        "vi": "🖼️ Phương pháp chụp ảnh màn hình của phiên bản 6 (Chụp màn hình trực tiếp - giống phiên bản cũ)",
        "en": "🖼️ Screenshot method from version 6 (Direct screen capture - like old version)",
        "zh": "🖼️ 版本6的截图方法 (直接截屏 - 与旧版本相同)",
        "ja": "🖼️ バージョン6のスクリーンショット方式 (直接画面キャプチャ - 旧バージョンと同様)"
    },
    "legacy_warning": {
        "vi": "⚠️ Lưu ý: Phương pháp này sẽ mở Excel hiện hữu trên màn hình và chụp ảnh trực tiếp.\nKhông sử dụng máy tính trong quá trình chạy. Đảm bảo đã đóng tất cả Excel.",
        "en": "⚠️ Note: This method will open Excel on screen and capture directly.\nDo not use the computer during processing. Ensure all Excel files are closed.",
        "zh": "⚠️ 注意: 此方法将在屏幕上打开Excel并直接截图。\n处理过程中请勿使用电脑。确保已关闭所有Excel文件。",
        "ja": "⚠️ 注意: この方式は画面上でExcelを開き、直接キャプチャします。\n処理中はパソコンを使用しないでください。すべてのExcelファイルを閉じてください。"
    },
    
    # ========== SETTINGS ==========
    "zoom_label": {
        "vi": "3. Cài đặt mức độ phóng to tỷ lệ màn hình của file Excel:",
        "en": "3. Set Excel file screen zoom level:",
        "zh": "3. 设置Excel文件屏幕缩放比例:",
        "ja": "3. Excelファイルの画面ズームレベルを設定:"
    },
    "goto_label": {
        "vi": "4. Nhập ô địa chỉ mà con trỏ nhảy đến (Gợi ý: dùng A1):",
        "en": "4. Enter cell address for cursor to jump to (Hint: use A1):",
        "zh": "4. 输入光标跳转的单元格地址 (建议: 使用A1):",
        "ja": "4. カーソルのジャンプ先セルアドレスを入力 (ヒント: A1を使用):"
    },
    "auto_add_b": {
        "vi": "⚠️ Tự động điền b để phát cho barcode/ để so sánh CTTT cũ - mới không cần thêm b thủ công",
        "en": "⚠️ Auto-fill 'b' for barcode / compare old-new SOP without manual 'b' addition",
        "zh": "⚠️ 自动填充b用于条码 / 无需手动添加b即可比较新旧作业指导书",
        "ja": "⚠️ バーコード用に自動的に'b'を追加 / 手動で'b'を追加せずに新旧作業指導書を比較"
    },
    "suppress_error": {
        "vi": "🔇 Ẩn thông báo lỗi kết nối Excel (khuyến nghị bật để chạy mượt mà)",
        "en": "🔇 Hide Excel connection error messages (recommended for smooth operation)",
        "zh": "🔇 隐藏Excel连接错误消息 (建议开启以确保流畅运行)",
        "ja": "🔇 Excel接続エラーメッセージを非表示 (スムーズな動作のため推奨)"
    },
    "save_settings": {
        "vi": "💾 Lưu cài đặt của tôi để dùng lại lần sau",
        "en": "💾 Save my settings for next use",
        "zh": "💾 保存我的设置以供下次使用",
        "ja": "💾 次回使用のために設定を保存"
    },
    
    # ========== METHOD SELECTION ==========
    "method_label": {
        "vi": "4.5. Chọn phương pháp so sánh:",
        "en": "4.5. Select comparison method:",
        "zh": "4.5. 选择比较方法:",
        "ja": "4.5. 比較方法を選択:"
    },
    "use_pdf_method": {
        "vi": "Sử dụng phương pháp PDF",
        "en": "Use PDF method",
        "zh": "使用PDF方法",
        "ja": "PDF方式を使用"
    },
    "pdf_method_note": {
        "vi": "(Chính xác hơn nhưng chậm hơn)",
        "en": "(More accurate but slower)",
        "zh": "(更准确但更慢)",
        "ja": "(より正確だが遅い)"
    },
    "dpi_label": {
        "vi": "DPI render PDF:",
        "en": "PDF render DPI:",
        "zh": "PDF渲染DPI:",
        "ja": "PDF レンダリング DPI:"
    },
    
    # ========== HIGHLIGHT SETTINGS ==========
    "highlight_label": {
        "vi": "5. Thiết lập hiển thị so sánh:",
        "en": "5. Comparison display settings:",
        "zh": "5. 比较显示设置:",
        "ja": "5. 比較表示設定:"
    },
    "btn_base_color": {
        "vi": "Chọn Màu Nền",
        "en": "Select Base Color",
        "zh": "选择底色",
        "ja": "背景色を選択"
    },
    "btn_outline_color": {
        "vi": "Chọn Màu Viền",
        "en": "Select Outline Color",
        "zh": "选择边框颜色",
        "ja": "枠線色を選択"
    },
    "btn_fill_color": {
        "vi": "Chọn Màu Tô",
        "en": "Select Fill Color",
        "zh": "选择填充颜色",
        "ja": "塗りつぶし色を選択"
    },
    "opacity_label": {
        "vi": "Độ mờ màu nền (%):",
        "en": "Background opacity (%):",
        "zh": "背景透明度 (%):",
        "ja": "背景の不透明度 (%):"
    },
    "threshold_label": {
        "vi": "Ngưỡng phát hiện PDF (0-255):",
        "en": "PDF detection threshold (0-255):",
        "zh": "PDF检测阈值 (0-255):",
        "ja": "PDF検出しきい値 (0-255):"
    },
    "dilate_size_label": {
        "vi": "Độ dày vùng tô PDF (1-9):",
        "en": "PDF fill area thickness (1-9):",
        "zh": "PDF填充区域厚度 (1-9):",
        "ja": "PDF塗りつぶし領域の太さ (1-9):"
    },
    "dilate_iter_label": {
        "vi": "Số lần nở PDF (1-3):",
        "en": "PDF dilation iterations (1-3):",
        "zh": "PDF膨胀次数 (1-3):",
        "ja": "PDF膨張回数 (1-3):"
    },
    
    # ========== STATUS ==========
    "status_ready": {
        "vi": "Sẵn sàng",
        "en": "Ready",
        "zh": "就绪",
        "ja": "準備完了"
    },
    "status_complete": {
        "vi": "Hoàn thành!",
        "en": "Complete!",
        "zh": "完成!",
        "ja": "完了!"
    },
    "status_error": {
        "vi": "Lỗi:",
        "en": "Error:",
        "zh": "错误:",
        "ja": "エラー:"
    },
    
    # ========== DIALOGS ==========
    "missing_files": {
        "vi": "Thiếu file",
        "en": "Missing files",
        "zh": "缺少文件",
        "ja": "ファイルが不足"
    },
    "missing_files_msg": {
        "vi": "Vui lòng chọn cả file cũ và mới.",
        "en": "Please select both old and new files.",
        "zh": "请选择新旧文件。",
        "ja": "新旧両方のファイルを選択してください。"
    },
    "count_mismatch": {
        "vi": "Số lượng không khớp",
        "en": "Count mismatch",
        "zh": "数量不匹配",
        "ja": "数量が一致しません"
    },
    "complete": {
        "vi": "Hoàn thành",
        "en": "Complete",
        "zh": "完成",
        "ja": "完了"
    },
    "complete_msg": {
        "vi": "Đã xử lý tất cả các cặp file CTTT cũ, mới.",
        "en": "All old and new SOP file pairs have been processed.",
        "zh": "已处理所有新旧作业指导书文件对。",
        "ja": "すべての新旧作業指導書ファイルペアが処理されました。"
    },
    "time_elapsed": {
        "vi": "Thời gian thực hiện: {minutes} phút và {seconds:.2f} giây.",
        "en": "Time elapsed: {minutes} min and {seconds:.2f} sec.",
        "zh": "耗时: {minutes}分{seconds:.2f}秒。",
        "ja": "所要時間: {minutes}分{seconds:.2f}秒。"
    },
    "error": {
        "vi": "Lỗi",
        "en": "Error",
        "zh": "错误",
        "ja": "エラー"
    },
    
    # ========== LEGACY METHOD DIALOGS ==========
    "legacy_confirm_title": {
        "vi": "Xác nhận so sánh CTTT phiên bản cũ",
        "en": "Confirm old version SOP comparison",
        "zh": "确认旧版作业指导书比较",
        "ja": "旧バージョン作業指導書比較の確認"
    },
    "legacy_confirm_msg": {
        "vi": "⚠️ PHƯƠNG PHÁP CŨ\n\nPhương pháp này sẽ:\n• Đóng tất cả Excel đang mở\n• Mở từng file Excel và chụp ảnh màn hình\n• Yêu cầu KHÔNG SỬ DỤNG máy tính trong khi chụp ảnh\n\nBạn có muốn tiếp tục không?",
        "en": "⚠️ OLD METHOD\n\nThis method will:\n• Close all open Excel files\n• Open each Excel file and capture screenshots\n• Requires NOT USING the computer during capture\n\nDo you want to continue?",
        "zh": "⚠️ 旧方法\n\n此方法将:\n• 关闭所有打开的Excel文件\n• 打开每个Excel文件并截图\n• 截图期间请勿使用电脑\n\n是否继续?",
        "ja": "⚠️ 旧方式\n\nこの方式は:\n• 開いているすべてのExcelファイルを閉じます\n• 各Excelファイルを開いてスクリーンショットを撮ります\n• キャプチャ中はパソコンを使用しないでください\n\n続行しますか?"
    },
    "legacy_complete_title": {
        "vi": "Hoàn thành so sánh CTTT phiên bản cũ",
        "en": "Old version SOP comparison complete",
        "zh": "旧版作业指导书比较完成",
        "ja": "旧バージョン作業指導書比較完了"
    },
    "legacy_complete_msg": {
        "vi": "Đã xử lý tất cả các cặp file CTTT bằng phương pháp cũ.",
        "en": "All SOP file pairs processed using old method.",
        "zh": "已使用旧方法处理所有作业指导书文件对。",
        "ja": "旧方式ですべての作業指導書ファイルペアが処理されました。"
    },
    
    # ========== CHECK ORDER DIALOG ==========
    "check_order_title": {
        "vi": "Kiểm tra thứ tự các cặp CTTT",
        "en": "Check SOP pair order",
        "zh": "检查作业指导书配对顺序",
        "ja": "作業指導書ペア順序を確認"
    },
    "pair_list_label": {
        "vi": "Danh sách các cặp file CTTT (Mới - Cũ):",
        "en": "SOP file pairs list (New - Old):",
        "zh": "作业指导书文件配对列表 (新 - 旧):",
        "ja": "作業指導書ファイルペアリスト (新 - 旧):"
    },
    "drag_hint": {
        "vi": "(Kéo thả để sắp xếp lại thứ tự nếu chưa khớp)",
        "en": "(Drag and drop to reorder if not matching)",
        "zh": "(如不匹配,可拖放重新排序)",
        "ja": "(一致しない場合はドラッグ&ドロップで並べ替え)"
    },
    "new_files_list": {
        "vi": "File CTTT Mới:",
        "en": "New SOP Files:",
        "zh": "新作业指导书文件:",
        "ja": "新作業指導書ファイル:"
    },
    "old_files_list": {
        "vi": "File CTTT Cũ:",
        "en": "Old SOP Files:",
        "zh": "旧作业指导书文件:",
        "ja": "旧作業指導書ファイル:"
    },
    "btn_confirm": {
        "vi": "Xác nhận OK",
        "en": "Confirm OK",
        "zh": "确认",
        "ja": "確認OK"
    },
    "btn_close": {
        "vi": "Đóng",
        "en": "Close",
        "zh": "关闭",
        "ja": "閉じる"
    },
    
    # ========== HELP GUIDE ==========
    "help_title": {
        "vi": "Hướng dẫn sử dụng cơ bản",
        "en": "Basic User Guide",
        "zh": "基本使用指南",
        "ja": "基本ユーザーガイド"
    },
    "help_content": {
        "vi": """HƯỚNG DẪN SỬ DỤNG - PHẦN MỀM CÓ 3 CÁCH SO SÁNH:

1) PHƯƠNG PHÁP PDF (Nút chính - Có chọn PDF):
   - Tick chọn 'Sử dụng phương pháp PDF'.
   - Nhấn nút chính (số 2) màu xanh.
   - Ưu điểm: Chính xác nhất, không bị ảnh hưởng bởi thao tác máy tính.

2) PHƯƠNG PHÁP SCREENSHOT MỚI (Nút chính - Không chọn PDF):
   - Bỏ chọn 'Sử dụng phương pháp PDF'.
   - Nhấn nút chính (số 2) màu xanh.
   - Ưu điểm: Tốc độ nhanh, xử lý ngầm qua file tạm.

3) PHƯƠNG PHÁP CỦA PHIÊN BẢN CŨ (Nút Vàng):
   - Nhấn trực tiếp nút màu vàng '🖼️ chụp ảnh...'.
   - Ưu điểm: Giống hệt thao tác của phiên bản cũ, chụp trực tiếp màn hình.
   - Lưu ý: KHÔNG dùng máy tính khi đang chụp ảnh.

LƯU Ý CHUNG:
- Chỉ các sheet có tab màu XANH mới được xử lý.
- Đảm bảo số lượng file mới và cũ khớp nhau.
- Kiểm tra 'Chế độ màn hình' (PC/VPS) để ảnh chụp không bị lệch.""",

        "en": """USER GUIDE - SOFTWARE HAS 3 COMPARISON METHODS:

1) PDF METHOD (Main button - PDF selected):
   - Check 'Use PDF method'.
   - Click the main button (no. 2) in blue.
   - Advantage: Most accurate, not affected by computer operations.

2) NEW SCREENSHOT METHOD (Main button - PDF not selected):
   - Uncheck 'Use PDF method'.
   - Click the main button (no. 2) in blue.
   - Advantage: Fast speed, processes in background via temp files.

3) OLD VERSION METHOD (Yellow button):
   - Click the yellow button '🖼️ Screenshot...'.
   - Advantage: Same as old version, captures screen directly.
   - Note: Do NOT use computer during capture.

GENERAL NOTES:
- Only sheets with GREEN tabs will be processed.
- Ensure new and old file counts match.
- Check 'Screen mode' (PC/VPS) to prevent image misalignment.""",

        "zh": """使用指南 - 软件有3种比较方法:

1) PDF方法 (主按钮 - 选择PDF):
   - 勾选 '使用PDF方法'。
   - 点击蓝色主按钮 (编号2)。
   - 优点: 最准确,不受电脑操作影响。

2) 新截图方法 (主按钮 - 不选PDF):
   - 取消勾选 '使用PDF方法'。
   - 点击蓝色主按钮 (编号2)。
   - 优点: 速度快,通过临时文件在后台处理。

3) 旧版本方法 (黄色按钮):
   - 直接点击黄色按钮 '🖼️ 截图...'。
   - 优点: 与旧版本相同,直接截屏。
   - 注意: 截图期间请勿使用电脑。

一般注意事项:
- 只有绿色标签的工作表才会被处理。
- 确保新旧文件数量匹配。
- 检查 '屏幕模式' (PC/VPS) 以防止图像错位。""",

        "ja": """ユーザーガイド - ソフトウェアには3つの比較方法があります:

1) PDF方式 (メインボタン - PDF選択時):
   - 「PDF方式を使用」にチェック。
   - 青いメインボタン (番号2) をクリック。
   - 利点: 最も正確、パソコン操作の影響を受けない。

2) 新スクリーンショット方式 (メインボタン - PDF非選択時):
   - 「PDF方式を使用」のチェックを外す。
   - 青いメインボタン (番号2) をクリック。
   - 利点: 高速、一時ファイルでバックグラウンド処理。

3) 旧バージョン方式 (黄色ボタン):
   - 黄色ボタン「🖼️ スクリーンショット...」を直接クリック。
   - 利点: 旧バージョンと同じ、画面を直接キャプチャ。
   - 注意: キャプチャ中はパソコンを使用しないでください。

一般的な注意事項:
- 緑色のタブを持つシートのみが処理されます。
- 新旧ファイルの数が一致していることを確認。
- 「画面モード」(PC/VPS)を確認して画像のずれを防止。"""
    },
    
    # ========== MENU ==========
    "menu_file": {
        "vi": "File",
        "en": "File",
        "zh": "文件",
        "ja": "ファイル"
    },
    "menu_view": {
        "vi": "Xem",
        "en": "View",
        "zh": "查看",
        "ja": "表示"
    },
    "menu_help": {
        "vi": "Trợ giúp",
        "en": "Help",
        "zh": "帮助",
        "ja": "ヘルプ"
    },
    "menu_language": {
        "vi": "Ngôn ngữ",
        "en": "Language",
        "zh": "语言",
        "ja": "言語"
    },
    "menu_open_new": {
        "vi": "Mở file CTTT mới...",
        "en": "Open new SOP file...",
        "zh": "打开新作业指导书文件...",
        "ja": "新作業指導書ファイルを開く..."
    },
    "menu_open_old": {
        "vi": "Mở file CTTT cũ...",
        "en": "Open old SOP file...",
        "zh": "打开旧作业指导书文件...",
        "ja": "旧作業指導書ファイルを開く..."
    },
    
    # ========== LANGUAGE SELECTOR ==========
    "language_label": {
        "vi": "Ngôn ngữ:",
        "en": "Language:",
        "zh": "语言:",
        "ja": "言語:"
    },
    
    # ========== TOOLTIPS ==========
    "tooltip_auto_b": {
        "vi": "Tự động thêm tiền tố 'b' vào tên sheet để khớp các file barcode.",
        "en": "Automatically add 'b' prefix to sheet names to match barcode files.",
        "zh": "自动在工作表名称前添加'b'前缀以匹配条码文件。",
        "ja": "バーコードファイルに一致するようにシート名に'b'プレフィックスを自動追加。"
    },
    "tooltip_threshold": {
        "vi": "Giá trị càng thấp càng nhạy (bắt nhiều khác biệt hơn). Đề xuất: 20-40.",
        "en": "Lower value = more sensitive (catches more differences). Recommended: 20-40.",
        "zh": "值越低越敏感(捕捉更多差异)。建议: 20-40。",
        "ja": "値が低いほど敏感(より多くの違いを検出)。推奨: 20-40。"
    },
    "tooltip_dilate_size": {
        "vi": "Độ dày vùng tô (px): số lẻ 1-9. Số lớn hơn = vùng highlight rộng hơn.",
        "en": "Fill area thickness (px): odd number 1-9. Higher = wider highlight area.",
        "zh": "填充区域厚度(px): 奇数1-9。数值越大 = 高亮区域越宽。",
        "ja": "塗りつぶし領域の太さ(px): 奇数1-9。大きいほどハイライト領域が広い。"
    },
    "tooltip_dilate_iter": {
        "vi": "Số lần nở: số lần phóng to vùng highlight (1-3). Tăng số lần nở làm vùng tô lớn hơn.",
        "en": "Dilation count: times to expand highlight area (1-3). More iterations = larger fill.",
        "zh": "膨胀次数: 扩大高亮区域的次数(1-3)。次数越多 = 填充越大。",
        "ja": "膨張回数: ハイライト領域を拡大する回数(1-3)。回数が多いほど塗りつぶしが大きい。"
    },
    
    # ========== DPI VALIDATION ==========
    "dpi_min_warning": {
        "vi": "DPI tối thiểu là 50. Đã tự động điều chỉnh về 50.",
        "en": "Minimum DPI is 50. Auto-adjusted to 50.",
        "zh": "最小DPI为50。已自动调整为50。",
        "ja": "最小DPIは50です。50に自動調整されました。"
    },
    "dpi_max_warning": {
        "vi": "DPI tối đa là 300. Đã tự động điều chỉnh về 300.",
        "en": "Maximum DPI is 300. Auto-adjusted to 300.",
        "zh": "最大DPI为300。已自动调整为300。",
        "ja": "最大DPIは300です。300に自動調整されました。"
    },
    "dpi_invalid": {
        "vi": "DPI không hợp lệ",
        "en": "Invalid DPI",
        "zh": "无效的DPI",
        "ja": "無効なDPI"
    },
    "dpi_invalid_msg": {
        "vi": "Vui lòng nhập số nguyên từ 50 đến 300. Đã reset về 100.",
        "en": "Please enter an integer from 50 to 300. Reset to 100.",
        "zh": "请输入50到300之间的整数。已重置为100。",
        "ja": "50から300の整数を入力してください。100にリセットされました。"
    },
    
    # ========== COLOR LABELS ==========
    "base_color": {
        "vi": "Màu Nền:",
        "en": "Base Color:",
        "zh": "底色:",
        "ja": "背景色:"
    },
    "outline_color": {
        "vi": "Màu Viền:",
        "en": "Outline Color:",
        "zh": "边框颜色:",
        "ja": "枠線色:"
    },
    "fill_color": {
        "vi": "Màu Tô:",
        "en": "Fill Color:",
        "zh": "填充颜色:",
        "ja": "塗りつぶし色:"
    },
}


def get_text(key: str, lang: str = "vi") -> str:
    """
    Get translated text for a given key and language.
    Falls back to Vietnamese if key not found for the language.
    """
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(lang, TRANSLATIONS[key].get("vi", key))
    return key


def get_language_name(lang_code: str) -> str:
    """Get the display name for a language code."""
    return LANGUAGES.get(lang_code, lang_code)


def get_available_languages() -> list:
    """Return list of available language codes."""
    return list(LANGUAGES.keys())
