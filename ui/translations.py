"""
Multilingual Translations Module
Hỗ trợ 4 ngôn ngữ: Tiếng Việt (vi), Tiếng Anh (en), Tiếng Trung (zh), Tiếng Nhật (ja)
Bao gồm tất cả các thành phần UI, phím tắt, menu, dialogs, và bộ thông báo lỗi xác thực trực quan.
"""

LANGUAGES = {
    "vi": "Tiếng Việt",
    "en": "English",
    "zh": "中文 (简体)",
    "ja": "日本語"
}

TRANSLATIONS = {
    # =========================================================================
    # APP & HEADER
    # =========================================================================
    "app_title": {
        "vi": "So sánh Chỉ thị Thao tác",
        "en": "SOP Comparison Tool",
        "zh": "作业指导书对比工具",
        "ja": "作業指導書比較ツール"
    },
    "header_title": {
        "vi": "📊 So sánh Chỉ thị Thao tác",
        "en": "📊 SOP Comparison Tool",
        "zh": "📊 作业指导书对比工具",
        "ja": "📊 作業指導書比較ツール"
    },
    "btn_help": {
        "vi": "📖 Hướng dẫn",
        "en": "📖 User Guide",
        "zh": "📖 使用说明",
        "ja": "📖 ユーザーガイド"
    },
    "help_title": {
        "vi": "Hướng dẫn sử dụng",
        "en": "User Guide",
        "zh": "使用说明",
        "ja": "ユーザーガイド"
    },
    "btn_close": {
        "vi": "Đóng",
        "en": "Close",
        "zh": "关闭",
        "ja": "閉じる"
    },

    # =========================================================================
    # CARD 1: FILE SELECTION & DOCUMENT MODES
    # =========================================================================
    "card_file_selection": {
        "vi": "1. Chọn File CTTT Cần So Sánh",
        "en": "1. Select SOP Files for Comparison",
        "zh": "1. 选择需要对比的作业指导书文件",
        "ja": "1. 比較する作業指導書ファイルの選択"
    },
    "doc_type_label": {
        "vi": "Loại tài liệu:",
        "en": "Document type:",
        "zh": "文档类型:",
        "ja": "ドキュメント種類:"
    },
    "mode_standard_cttt": {
        "vi": "1. CTTT thông thường (Sheet tab XANH LÁ)",
        "en": "1. Standard SOP (GREEN tab Sheet)",
        "zh": "1. 普通作业指导书 (绿色标签工作表)",
        "ja": "1. 通常の作業指導書 (緑色タブシート)"
    },
    "mode_dukc_cttt": {
        "vi": "2. CTTT thuộc Tờ Phát Hành ĐƯKC (Sheet hiển thị)",
        "en": "2. SOP in DUKC Release Form (Visible sheets)",
        "zh": "2. 应急应对发行表内的作业指导书 (可见工作表)",
        "ja": "2. 緊急対応発行票の作業指導書 (表示シート)"
    },
    "mode_dukc_other": {
        "vi": "3. Tờ Phát Hành ĐƯKC & Khác (Sheet 'Form')",
        "en": "3. DUKC Release Form & Others ('Form' Sheet)",
        "zh": "3. 应急应对发行表及其它 ('Form' 工作表)",
        "ja": "3. 緊急対応発行票・その他 ('Form' シート)"
    },
    "screen_mode_label": {
        "vi": "Chế độ màn hình:",
        "en": "Screen mode:",
        "zh": "屏幕模式:",
        "ja": "画面モード:"
    },
    "screen_pc": {
        "vi": "Màn hình PC",
        "en": "PC Screen",
        "zh": "PC 屏幕",
        "ja": "PC画面"
    },
    "screen_vps": {
        "vi": "VPS",
        "en": "VPS",
        "zh": "VPS",
        "ja": "VPS"
    },
    "screen_secondary": {
        "vi": "Màn hình phụ",
        "en": "Secondary Screen",
        "zh": "副屏",
        "ja": "サブ画面"
    },
    "lbl_cttt_new": {
        "vi": "CTTT mới:",
        "en": "New SOP:",
        "zh": "新作业指导书:",
        "ja": "新作業指導書:"
    },
    "lbl_selected_new": {
        "vi": "Đã chọn:",
        "en": "Selected:",
        "zh": "已选择:",
        "ja": "選択済:"
    },
    "btn_select_new": {
        "vi": "📂 Chọn CTTT Mới...",
        "en": "📂 Select New SOP...",
        "zh": "📂 选择新指导书...",
        "ja": "📂 新ファイル選択..."
    },
    "lbl_cttt_old": {
        "vi": "CTTT cũ:",
        "en": "Old SOP:",
        "zh": "旧作业指导书:",
        "ja": "旧作業指導書:"
    },
    "lbl_selected_old": {
        "vi": "Đã chọn:",
        "en": "Selected:",
        "zh": "已选择:",
        "ja": "選択済:"
    },
    "mode_custom": {
        "vi": "🛠️ 4. Tài liệu do người dùng chọn (Tùy chỉnh vùng & sheet)",
        "en": "🛠️ 4. Custom Document (User-defined range & sheets)",
        "zh": "🛠️ 4. 自定义文档 (用户自定义范围与工作表)",
        "ja": "🛠️ 4. ユーザー定義ドキュメント (範囲とシート指定)"
    },
    "btn_custom_config": {
        "vi": "⚙️ Thiết lập",
        "en": "⚙️ Settings",
        "zh": "⚙️ 设置",
        "ja": "⚙️ 設定"
    },
    "custom_dialog_title": {
        "vi": "Cấu hình So Sánh Tài Liệu Tùy Chỉnh",
        "en": "Custom Document Comparison Settings",
        "zh": "自定义文档对比设置",
        "ja": "カスタムドキュメント比較設定"
    },
    "custom_config_title": {
        "vi": "Cấu hình So Sánh Tài Liệu Tùy Chỉnh",
        "en": "Custom Document Comparison Settings",
        "zh": "自定义文档对比设置",
        "ja": "カスタムドキュメント比較設定"
    },
    "custom_range_group": {
        "vi": "2.1. Phạm vi vùng so sánh (Print Area):",
        "en": "2.1. Comparison Range (Print Area):",
        "zh": "2.1. 对比范围 (打印区域):",
        "ja": "2.1. 比較範囲 (印刷範囲):"
    },
    "custom_range_hint": {
        "vi": "Nhập dải ô (Ví dụ: A1:AT120, EX1:GR76, J2:BD76, A1:Z100...):",
        "en": "Enter cell range (e.g., A1:AT120, EX1:GR76, J2:BD76, A1:Z100...):",
        "zh": "输入单元格范围 (例如: A1:AT120, EX1:GR76, J2:BD76, A1:Z100...):",
        "ja": "セル範囲を入力 (例: A1:AT120, EX1:GR76, J2:BD76, A1:Z100...):"
    },
    "custom_presets_label": {
        "vi": "Gợi ý nhanh:",
        "en": "Quick presets:",
        "zh": "快速预设:",
        "ja": "クイックプリセット:"
    },
    "custom_sheet_group": {
        "vi": "2.2. Lựa chọn Sheet so sánh:",
        "en": "2.2. Sheet Selection Scope:",
        "zh": "2.2. 工作表对比范围选择:",
        "ja": "2.2. 比較シートの選択:"
    },
    "custom_sheet_all": {
        "vi": "Toàn bộ sheet (So sánh tất cả các sheet hiển thị có tên trùng khớp)",
        "en": "All sheets (Compare all matching visible sheets)",
        "zh": "全部工作表 (对比所有同名的可见工作表)",
        "ja": "全シート (名前が一致するすべての表示シートを比較)"
    },
    "custom_sheet_specified": {
        "vi": "Sheet chỉ định (Nhập danh sách tên sheet cần so sánh):",
        "en": "Specified sheets (Enter sheet names to compare):",
        "zh": "指定工作表 (输入需要对比的工作表名称):",
        "ja": "指定シート (比較するシート名を入力):"
    },
    "custom_sheet_specified_placeholder": {
        "vi": "Ví dụ: Form, Sheet1, Data (ngăn cách bằng dấu phẩy)",
        "en": "e.g., Form, Sheet1, Data (comma-separated)",
        "zh": "例如: Form, Sheet1, Data (逗号分隔)",
        "ja": "例: Form, Sheet1, Data (カンマ区切り)"
    },
    "custom_only_green": {
        "vi": "Chỉ so sánh các sheet có Tab màu xanh lá (Optional)",
        "en": "Only compare sheets with green tabs (Optional)",
        "zh": "仅对比绿色标签的工作表 (可选)",
        "ja": "緑色タブのシートのみを比較 (オプション)"
    },
    "btn_save_apply": {
        "vi": "💾 Lưu & Áp dụng",
        "en": "💾 Save & Apply",
        "zh": "💾 保存并应用",
        "ja": "💾 保存して適用"
    },
    "print_area_label": {
        "vi": "Phạm vi so sánh:",
        "en": "Compare Range:",
        "zh": "对比范围:",
        "ja": "比較範囲:"
    },
    "btn_select_old": {
        "vi": "📂 Chọn CTTT Cũ...",
        "en": "📂 Select Old SOP...",
        "zh": "📂 选择旧指导书...",
        "ja": "📂 旧ファイル選択..."
    },
    "lbl_result_path": {
        "vi": "Thư mục lưu kết quả (để trống sẽ lưu cùng thư mục với CTTT mới):",
        "en": "Result folder (leave blank to save in the same folder as new SOP):",
        "zh": "结果保存目录 (留空将保存在新作业指导书同级目录下):",
        "ja": "結果保存先フォルダ (空欄の場合は新ファイルと同じフォルダに保存):"
    },
    "btn_browse": {
        "vi": "Duyệt...",
        "en": "Browse...",
        "zh": "浏览...",
        "ja": "参照..."
    },
    "btn_check_order": {
        "vi": "🔍 Kiểm tra & Sắp xếp thứ tự các cặp CTTT",
        "en": "🔍 Check & Arrange SOP Pair Order",
        "zh": "🔍 检查并调整文件配对顺序",
        "ja": "🔍 ペアの順序確認・並べ替え"
    },

    # =========================================================================
    # WORKFLOW 5 STEPS & BADGES
    # =========================================================================
    "workflow_step_1": {
        "vi": "Bước 1 — Chọn loại tài liệu so sánh",
        "en": "Step 1 — Select document type",
        "zh": "步骤 1 — 选择对比文档类型",
        "ja": "手順 1 — ドキュメントの種類を選択"
    },
    "workflow_step_1_done": {
        "vi": "Bước 1 — Đã chọn loại tài liệu",
        "en": "Step 1 — Document type selected",
        "zh": "步骤 1 — 已选择文档类型",
        "ja": "手順 1 — ドキュメントの種類選択済"
    },
    "workflow_step_2": {
        "vi": "Bước 2 — Chọn CTTT mới",
        "en": "Step 2 — Select new SOP files",
        "zh": "步骤 2 — 选择新作业指导书",
        "ja": "手順 2 — 新作業指導書を選択"
    },
    "workflow_step_2_done": {
        "vi": "Bước 2 — Đã chọn CTTT mới",
        "en": "Step 2 — New SOP files selected",
        "zh": "步骤 2 — 已选择新作业指导书",
        "ja": "手順 2 — 新作業指導書選択済"
    },
    "workflow_step_3": {
        "vi": "Bước 3 — Chọn CTTT cũ",
        "en": "Step 3 — Select old SOP files",
        "zh": "步骤 3 — 选择旧作业指导书",
        "ja": "手順 3 — 旧作業指導書を選択"
    },
    "workflow_step_3_done": {
        "vi": "Bước 3 — Đã chọn CTTT cũ",
        "en": "Step 3 — Old SOP files selected",
        "zh": "步骤 3 — 已选择旧作业指导书",
        "ja": "手順 3 — 旧作業指導書選択済"
    },
    "workflow_step_3_error": {
        "vi": "Bước 3 — Số lượng file mới/cũ chưa khớp",
        "en": "Step 3 — File counts mismatch",
        "zh": "步骤 3 — 新旧文件数量不匹配",
        "ja": "手順 3 — 新旧ファイル数が不一致"
    },
    "workflow_step_4": {
        "vi": "Bước 4 — Kiểm tra & xác nhận cặp",
        "en": "Step 4 — Check & confirm pairs",
        "zh": "步骤 4 — 检查并确认配对",
        "ja": "手順 4 — ペアの確認と確定"
    },
    "workflow_step_4_done": {
        "vi": "Bước 4 — Đã xác nhận cặp",
        "en": "Step 4 — Pairs confirmed",
        "zh": "步骤 4 — 配对已确认",
        "ja": "手順 4 — ペア確認済"
    },
    "workflow_step_4_error": {
        "vi": "Bước 4 — Chọn đúng loại tài liệu hoặc thay file",
        "en": "Step 4 — Correct document type or replace files",
        "zh": "步骤 4 — 更正文档类型或替换文件",
        "ja": "手順 4 — ドキュメント種類の変更またはファイル差替え"
    },
    "workflow_step_5": {
        "vi": "Bước 5 — Bắt đầu so sánh",
        "en": "Step 5 — Start comparison",
        "zh": "步骤 5 — 开始对比",
        "ja": "手順 5 — 比較開始"
    },
    "workflow_step_5_ready": {
        "vi": "Bước 5 — Sẵn sàng bắt đầu so sánh",
        "en": "Step 5 — Ready to compare",
        "zh": "步骤 5 — 准备就绪，可开始对比",
        "ja": "手順 5 — 比較の準備が完了しました"
    },
    "workflow_step_5_running": {
        "vi": "Bước 5 — Đang chạy so sánh",
        "en": "Step 5 — Comparison in progress",
        "zh": "步骤 5 — 正在执行对比",
        "ja": "手順 5 — 比較を実行中"
    },

    # Workflow Guidance Messages
    "workflow_msg_1": {
        "vi": "Bước 1/5: Chọn loại tài liệu so sánh để mở khóa bước chọn file.",
        "en": "Step 1/5: Select document type to unlock file selection.",
        "zh": "步骤 1/5: 请先选择对比文档类型以解锁文件选择功能。",
        "ja": "手順 1/5: ドキュメントの種類を選択してファイル選択をアンロックしてください。"
    },
    "workflow_msg_2": {
        "vi": "Bước 2/5: Đã chọn loại tài liệu. Hãy chọn file CTTT mới.",
        "en": "Step 2/5: Document type selected. Please choose new SOP files.",
        "zh": "步骤 2/5: 文档类型已选定。请选择新版作业指导书文件。",
        "ja": "手順 2/5: ドキュメント種類が選択されました。新作業指導書ファイルを選択してください。"
    },
    "workflow_msg_3": {
        "vi": "Bước 3/5: Đã chọn file mới. Hãy chọn file CTTT cũ tương ứng.",
        "en": "Step 3/5: New files selected. Please choose corresponding old SOP files.",
        "zh": "步骤 3/5: 新文件已选择。请选择对应的旧版作业指导书文件。",
        "ja": "手順 3/5: 新ファイルが選択されました。対応する旧作業指導書ファイルを選択してください。"
    },
    "workflow_msg_count_mismatch": {
        "vi": "Bước 3/5 chưa hợp lệ: Số file mới ({new_count}) và file cũ ({old_count}) chưa bằng nhau.",
        "en": "Step 3/5 invalid: New files count ({new_count}) and old files count ({old_count}) do not match.",
        "zh": "步骤 3/5 未就绪: 新文件数量 ({new_count}) 与旧文件数量 ({old_count}) 不一致。",
        "ja": "手順 3/5 未完了: 新ファイル数 ({new_count}) と旧ファイル数 ({old_count}) が一致していません。"
    },
    "workflow_msg_confirm_prompt": {
        "vi": "Bước 4/5: Nhấn 'Kiểm tra & Sắp xếp thứ tự' để kiểm tra từng cặp rồi bấm 'Xác nhận & Lưu'.",
        "en": "Step 4/5: Click 'Check & Arrange SOP Pair Order' to verify pairs, then click 'Confirm & Save'.",
        "zh": "步骤 4/5: 点击 '检查并调整文件配对顺序' 核对各对文件，然后点击 '确认并保存'。",
        "ja": "手順 4/5:「ペアの順序確認・並べ替え」をクリックして確認し、「確定して保存」を押してください。"
    },
    "workflow_msg_validation_error": {
        "vi": "Bước 4/5 chưa hợp lệ: Loại tài liệu đã chọn không khớp với cấu trúc sheet trong file Excel.",
        "en": "Step 4/5 invalid: The selected document type does not match the sheet structure in the Excel files.",
        "zh": "步骤 4/5 未通过: 所选文档类型与Excel文件中的工作表结构不匹配。",
        "ja": "手順 4/5 無効: 選択したドキュメント種類がExcelファイルのシート構造と一致しません。"
    },
    "workflow_msg_processing": {
        "vi": "Bước 5/5: Đang chạy so sánh, vui lòng chờ trong giây lát...",
        "en": "Step 5/5: Comparison is running, please wait...",
        "zh": "步骤 5/5: 正在进行比对，请稍候...",
        "ja": "手順 5/5: 比較を実行中です。しばらくお待ちください..."
    },
    "workflow_msg_ready": {
        "vi": "✅ Đã hoàn tất 4 bước. Bạn có thể nhấn 'BẮT ĐẦU SO SÁNH'.",
        "en": "✅ All 4 steps completed. You can click 'START COMPARISON'.",
        "zh": "✅ 4个步骤已全部完成。您可以点击 '开始对比'。",
        "ja": "✅ 4つのステップが完了しました。「比較開始」をクリックできます。"
    },

    # Workflow Action Block Warning Dialog
    "workflow_err_title": {
        "vi": "Chưa thể tiếp tục",
        "en": "Cannot Proceed",
        "zh": "无法继续",
        "ja": "続行できません"
    },
    "workflow_err_step1": {
        "vi": "Bước 1 chưa hoàn tất: Vui lòng chọn loại tài liệu so sánh trước.",
        "en": "Step 1 incomplete: Please select document comparison type first.",
        "zh": "步骤 1 未完成: 请先选择对比文档类型。",
        "ja": "手順 1 未完了: 最初にドキュメントの比較種類を選択してください。"
    },
    "workflow_err_step2": {
        "vi": "Bước 2 chưa hoàn tất: Vui lòng chọn file CTTT mới.",
        "en": "Step 2 incomplete: Please select new SOP files.",
        "zh": "步骤 2 未完成: 请选择新作业指导书文件。",
        "ja": "手順 2 未完了: 新作業指導書ファイルを選択してください。"
    },
    "workflow_err_step3": {
        "vi": "Bước 3 chưa hoàn tất: Vui lòng chọn file CTTT cũ.",
        "en": "Step 3 incomplete: Please select old SOP files.",
        "zh": "步骤 3 未完成: 请选择旧作业指导书文件。",
        "ja": "手順 3 未完了: 旧作業指導書ファイルを選択してください。"
    },
    "workflow_err_mismatch": {
        "vi": "Số lượng file mới ({new_count}) và file cũ ({old_count}) chưa khớp nhau. Hãy bổ sung hoặc xóa bớt file.",
        "en": "New files count ({new_count}) and old files count ({old_count}) do not match. Please add or remove files.",
        "zh": "新文件数量 ({new_count}) 与旧文件数量 ({old_count}) 不一致。请补充或删除文件。",
        "ja": "新ファイル数 ({new_count}) と旧ファイル数 ({old_count}) が一致しません。ファイルを追加または削除してください。"
    },
    "workflow_err_confirm": {
        "vi": "Bạn chưa kiểm tra và xác nhận thứ tự các cặp CTTT. Vui lòng bấm 'Kiểm tra & Sắp xếp thứ tự'.",
        "en": "You have not verified and confirmed the SOP pair order. Please click 'Check & Arrange SOP Pair Order'.",
        "zh": "您尚未检查并确认文件配对顺序。请点击 '检查并调整文件配对顺序'。",
        "ja": "ペアの順序確認・確定が完了していません。「ペアの順序確認・並べ替え」をクリックしてください。"
    },

    # =========================================================================
    # FILE SELECTION DIALOGS (Append vs Replace)
    # =========================================================================
    "file_dialog_select_new": {
        "vi": "Chọn file CTTT mới",
        "en": "Select New SOP Files",
        "zh": "选择新作业指导书文件",
        "ja": "新作業指導書ファイルを選択"
    },
    "file_dialog_select_old": {
        "vi": "Chọn file CTTT cũ",
        "en": "Select Old SOP Files",
        "zh": "选择旧作业指导书文件",
        "ja": "旧作業指導書ファイルを選択"
    },
    "file_dialog_excel_filter": {
        "vi": "File Excel (*.xls, *.xlsx, *.xlsm)",
        "en": "Excel Files (*.xls, *.xlsx, *.xlsm)",
        "zh": "Excel 文件 (*.xls, *.xlsx, *.xlsm)",
        "ja": "Excelファイル (*.xls, *.xlsx, *.xlsm)"
    },
    "file_append_replace_title_new": {
        "vi": "Bổ sung hoặc Thay thế file CTTT mới",
        "en": "Append or Replace New SOP Files",
        "zh": "追加或替换新作业指导书文件",
        "ja": "新作業指導書ファイルの追加または置換"
    },
    "file_append_replace_msg_new": {
        "vi": "Hiện đang có {existing_count} file CTTT mới đã chọn trước đó.\nBạn vừa chọn thêm {selected_count} file.\n\n• [Yes / Có]: BỔ SUNG thêm vào danh sách hiện tại\n• [No / Không]: THAY THẾ toàn bộ danh sách bằng các file vừa chọn\n• [Cancel / Hủy]: Giữ nguyên danh sách hiện tại",
        "en": "{existing_count} new SOP files are already selected.\nYou just selected {selected_count} files.\n\n• [Yes]: APPEND to current list\n• [No]: REPLACE entire list with new selection\n• [Cancel]: Keep current list unchanged",
        "zh": "当前已选择 {existing_count} 个新作业指导书文件。\n您刚才又选择了 {selected_count} 个文件。\n\n• [是 / Yes]: 追加到当前列表中\n• [否 / No]: 用新选择的文件全部替换当前列表\n• [取消 / Cancel]: 保持现有列表不变",
        "ja": "現在 {existing_count} 個の新作業指導書ファイルが選択されています。\n新しく {selected_count} 個のファイルを選択しました。\n\n• [はい / Yes]: 現在のリストに追加\n• [いいえ / No]: 新しく選択したファイルですべて置換\n• [キャンセル]: 変更せず現在のリストを維持"
    },
    "file_append_replace_title_old": {
        "vi": "Bổ sung hoặc Thay thế file CTTT cũ",
        "en": "Append or Replace Old SOP Files",
        "zh": "追加或替换旧作业指导书文件",
        "ja": "旧作業指導書ファイルの追加または置換"
    },
    "file_append_replace_msg_old": {
        "vi": "Hiện đang có {existing_count} file CTTT cũ đã chọn trước đó.\nBạn vừa chọn thêm {selected_count} file.\n\n• [Yes / Có]: BỔ SUNG thêm vào danh sách hiện tại\n• [No / Không]: THAY THẾ toàn bộ danh sách bằng các file vừa chọn\n• [Cancel / Hủy]: Giữ nguyên danh sách hiện tại",
        "en": "{existing_count} old SOP files are already selected.\nYou just selected {selected_count} files.\n\n• [Yes]: APPEND to current list\n• [No]: REPLACE entire list with new selection\n• [Cancel]: Keep current list unchanged",
        "zh": "当前已选择 {existing_count} 个旧作业指导书文件。\n您刚才又选择了 {selected_count} 个文件。\n\n• [是 / Yes]: 追加到当前列表中\n• [否 / No]: 用新选择的文件全部替换当前列表\n• [取消 / Cancel]: 保持现有列表不变",
        "ja": "現在 {existing_count} 個の旧作業指導書ファイルが選択されています。\n新しく {selected_count} 個のファイルを選択しました。\n\n• [はい / Yes]: 現在のリストに追加\n• [いいえ / No]: 新しく選択したファイルですべて置換\n• [キャンセル]: 変更せず現在のリストを維持"
    },

    # =========================================================================
    # CHECK PAIR ORDER DIALOG
    # =========================================================================
    "check_order_window_title": {
        "vi": "Kiểm tra và Sắp xếp Thứ tự Cặp CTTT",
        "en": "Check and Arrange SOP Pair Order",
        "zh": "检查并调整文件配对顺序",
        "ja": "ペア順序の確認と並べ替え"
    },
    "check_order_hint": {
        "vi": "💡 Hướng dẫn: Kéo thả các dòng để điều chỉnh thứ tự ghép cặp (Dòng 1 Mới sẽ so sánh với Dòng 1 Cũ). Nhấn Delete để xóa dòng.",
        "en": "💡 Hint: Drag & drop rows to align matching pairs (Row 1 New compares with Row 1 Old). Press Delete to remove.",
        "zh": "💡 说明: 拖放列表行以对齐配对 (第1行新文件将与第1行旧文件进行对比)。按 Delete 键可删除选中项。",
        "ja": "💡 ヒント: 行をドラッグ＆ドロップして比較ペアを整列します (新行1と旧行1が比較されます)。Deleteキーで削除できます。"
    },
    "check_order_header_new": {
        "vi": "Danh sách CTTT Mới ({count} file)",
        "en": "New SOP Files ({count} files)",
        "zh": "新作业指导书列表 ({count} 个文件)",
        "ja": "新作業指導書一覧 ({count} ファイル)"
    },
    "check_order_header_old": {
        "vi": "Danh sách CTTT Cũ ({count} file)",
        "en": "Old SOP Files ({count} files)",
        "zh": "旧作业指导书列表 ({count} 个文件)",
        "ja": "旧作業指導書一覧 ({count} ファイル)"
    },
    "check_order_matched": {
        "vi": "✅ Số lượng đã khớp: {count} cặp file",
        "en": "✅ Counts matched: {count} file pairs",
        "zh": "✅ 数量已匹配: {count} 对文件",
        "ja": "✅ ファイル数が一致しています: {count} ペア"
    },
    "check_order_mismatched": {
        "vi": "⚠️ Chưa khớp: Mới có {new_count} file, Cũ có {old_count} file (Chênh lệch: {abs_diff} file)",
        "en": "⚠️ Mismatch: {new_count} new files, {old_count} old files (Diff: {abs_diff})",
        "zh": "⚠️ 数量不一致: 新文件 {new_count} 个, 旧文件 {old_count} 个 (相差: {abs_diff} 个)",
        "ja": "⚠️ 不一致: 新ファイル {new_count} 件, 旧ファイル {old_count} 件 (差: {abs_diff} 件)"
    },
    "check_order_btn_add_new": {
        "vi": "➕ Thêm file Mới",
        "en": "➕ Add New Files",
        "zh": "➕ 添加新文件",
        "ja": "➕ 新ファイル追加"
    },
    "check_order_btn_del_new": {
        "vi": "➖ Xóa file Mới",
        "en": "➖ Delete New File",
        "zh": "➖ 删除新文件",
        "ja": "➖ 新ファイル削除"
    },
    "check_order_btn_add_old": {
        "vi": "➕ Thêm file Cũ",
        "en": "➕ Add Old Files",
        "zh": "➕ 添加旧文件",
        "ja": "➕ 旧ファイル追加"
    },
    "check_order_btn_del_old": {
        "vi": "➖ Xóa file Cũ",
        "en": "➖ Delete Old File",
        "zh": "➖ 删除旧文件",
        "ja": "➖ 旧ファイル削除"
    },
    "check_order_btn_confirm": {
        "vi": "💾 Xác nhận & Lưu thứ tự",
        "en": "💾 Confirm & Save Order",
        "zh": "💾 确认并保存顺序",
        "ja": "💾 順序を確定して保存"
    },
    "check_order_btn_del_both": {
        "vi": "🗑️ Xóa cả 2 bên",
        "en": "🗑️ Delete Both Sides",
        "zh": "🗑️ 同时删除两侧",
        "ja": "🗑️ 両側を削除"
    },
    "check_order_btn_close": {
        "vi": "Đóng",
        "en": "Close",
        "zh": "关闭",
        "ja": "閉じる"
    },
    "check_order_warn_title": {
        "vi": "Số lượng file chưa bằng nhau",
        "en": "File Counts Mismatch",
        "zh": "文件数量不一致",
        "ja": "ファイル数が一致しません"
    },
    "check_order_warn_msg": {
        "vi": "Số file Mới ({new_count}) và Cũ ({old_count}) chưa bằng nhau.\nVui lòng bấm 'Thêm file' hoặc 'Xóa file' để cân bằng số lượng trước khi xác nhận.",
        "en": "New files ({new_count}) and Old files ({old_count}) do not match.\nPlease add or remove files to balance counts before confirming.",
        "zh": "新文件 ({new_count}) 与旧文件 ({old_count}) 数量不相等。\n请点击 '添加文件' 或 '删除文件' 调整一致后再确认。",
        "ja": "新ファイル ({new_count}) と旧ファイル ({old_count}) の数が一致しません。\n確定する前にファイルを追加または削除して数を合わせてください。"
    },
    "confirm_success_title": {
        "vi": "Đã xác nhận",
        "en": "Confirmed",
        "zh": "已确认",
        "ja": "確認完了"
    },
    "confirm_success_msg": {
        "vi": "Đã lưu và xác nhận {count} cặp file CTTT thành công. Bạn có thể bắt đầu so sánh!",
        "en": "Successfully confirmed {count} SOP file pairs. You can now start the comparison!",
        "zh": "已成功确认 {count} 对作业指导书文件。现在可以开始对比了！",
        "ja": "{count} ペアの作業指導書ファイルが正常に確認されました。比較を開始できます！"
    },

    # =========================================================================
    # RUN BUTTONS & LEGACY METHOD
    # =========================================================================
    "btn_run_main": {
        "vi": "🚀 BẮT ĐẦU SO SÁNH (PHƯƠNG PHÁP PDF KHUYÊN DÙNG)",
        "en": "🚀 START COMPARISON (RECOMMENDED PDF METHOD)",
        "zh": "🚀 开始对比 (推荐使用 PDF 方法)",
        "ja": "🚀 比較開始 (推奨 PDF 方式)"
    },
    "legacy_frame_title": {
        "vi": "Phương pháp dự phòng (Phiên bản cũ)",
        "en": "Fallback Method (Legacy Version)",
        "zh": "备用方法 (旧版本方式)",
        "ja": "代替方式 (レガシー旧版)"
    },
    "btn_legacy": {
        "vi": "⚡ BẮT ĐẦU SO SÁNH (PHƯƠNG PHÁP CŨ - CHỤP MÀN HÌNH)",
        "en": "⚡ START COMPARISON (LEGACY SCREENSHOT METHOD)",
        "zh": "⚡ 开始对比 (旧版截屏方式)",
        "ja": "⚡ 比較開始 (レガシー画面キャプチャ方式)"
    },
    "legacy_warning": {
        "vi": "⚠️ Lưu ý: Phương pháp cũ sẽ chiếm chuột/bàn phím và chụp ảnh màn hình. Không chạm vào máy tính khi đang chạy.",
        "en": "⚠️ Note: Legacy method controls mouse/keyboard and captures screen. Do not use computer while running.",
        "zh": "⚠️ 注意: 旧版方法将控制鼠标/键盘并截屏。运行期间请勿操作电脑。",
        "ja": "⚠️ 注意: 旧方式はマウス/キーボードを制御し画面キャプチャします。実行中はPCを操作しないでください。"
    },

    # =========================================================================
    # CARD 2: ADVANCED SETTINGS
    # =========================================================================
    "card_settings": {
        "vi": "2. Cài Đặt Nâng Cao",
        "en": "2. Advanced Settings",
        "zh": "2. 高级设置",
        "ja": "2. 詳細設定"
    },
    "chk_use_pdf": {
        "vi": "Sử dụng phương pháp so sánh PDF (Khuyên dùng)",
        "en": "Use PDF comparison method (Recommended)",
        "zh": "使用 PDF 对比方法 (推荐)",
        "ja": "PDF比較方式を使用 (推奨)"
    },
    "lbl_dpi": {
        "vi": "Độ phân giải PDF (DPI):",
        "en": "PDF Render DPI:",
        "zh": "PDF 渲染分辨率 (DPI):",
        "ja": "PDF描画解像度 (DPI):"
    },
    "lbl_zoom": {
        "vi": "Mức phóng to (%):",
        "en": "Zoom level (%):",
        "zh": "缩放级别 (%):",
        "ja": "拡大レベル (%):"
    },
    "lbl_goto": {
        "vi": "Ô di chuyển đến:",
        "en": "Go to cell address:",
        "zh": "跳转到单元格:",
        "ja": "移動先セル:"
    },
    "chk_auto_b": {
        "vi": "Tự động thêm 'b' vào barcode",
        "en": "Auto-append 'b' to barcode",
        "zh": "自动在条码后追加 'b'",
        "ja": "バーコードに自動で 'b' を追加"
    },
    "chk_suppress": {
        "vi": "Ẩn thông báo lỗi phụ trong quá trình chạy",
        "en": "Suppress non-critical error popups during processing",
        "zh": "运行过程中隐藏次要错误提示弹窗",
        "ja": "実行中の重要でないエラーポップアップを非表示"
    },
    "chk_save": {
        "vi": "Tự động lưu cấu hình người dùng",
        "en": "Auto-save user settings",
        "zh": "自动保存用户配置",
        "ja": "ユーザー設定を自動保存"
    },

    # =========================================================================
    # CARD 3: HIGHLIGHT & DIFF PARAMETERS
    # =========================================================================
    "card_highlight": {
        "vi": "3. Tùy Chỉnh Highlight Khác Biệt",
        "en": "3. Difference Highlight Customization",
        "zh": "3. 差异高亮自定义",
        "ja": "3. 差異ハイライトのカスタマイズ"
    },
    "btn_base_color": {
        "vi": "Màu Nền",
        "en": "Base Color",
        "zh": "底色",
        "ja": "背景色"
    },
    "btn_outline_color": {
        "vi": "Màu Viền",
        "en": "Outline Color",
        "zh": "边框颜色",
        "ja": "枠線色"
    },
    "btn_fill_color": {
        "vi": "Màu Tô",
        "en": "Fill Color",
        "zh": "填充颜色",
        "ja": "塗りつぶし色"
    },
    "lbl_opacity": {
        "vi": "Độ trong suốt (%):",
        "en": "Opacity (%):",
        "zh": "透明度 (%):",
        "ja": "不透明度 (%):"
    },
    "lbl_threshold": {
        "vi": "Ngưỡng phát hiện (0-255):",
        "en": "Detection threshold (0-255):",
        "zh": "检测阈值 (0-255):",
        "ja": "検出しきい値 (0-255):"
    },
    "lbl_dilate_size": {
        "vi": "Độ dày vùng tô (1-9):",
        "en": "Fill thickness (1-9):",
        "zh": "填充厚度 (1-9):",
        "ja": "塗りの太さ (1-9):"
    },
    "lbl_dilate_iter": {
        "vi": "Số lần mở rộng (1-3):",
        "en": "Expansion count (1-3):",
        "zh": "扩展次数 (1-3):",
        "ja": "拡張回数 (1-3):"
    },

    # =========================================================================
    # STATUS BAR & TOOLTIPS
    # =========================================================================
    "status_ready": {
        "vi": "Sẵn sàng",
        "en": "Ready",
        "zh": "就绪",
        "ja": "準備完了"
    },
    "status_version": {
        "vi": "Phiên bản {version} ({date})",
        "en": "Version {version} ({date})",
        "zh": "版本 {version} ({date})",
        "ja": "バージョン {version} ({date})"
    },
    "status_processing": {
        "vi": "🔄 Đang xử lý so sánh CTTT, vui lòng chờ...",
        "en": "🔄 Processing SOP comparison, please wait...",
        "zh": "🔄 正在处理作业指导书对比，请稍候...",
        "ja": "🔄 比較処理中、しばらくお待ちください..."
    },
    "status_complete": {
        "vi": "So sánh hoàn tất thành công!",
        "en": "Comparison completed successfully!",
        "zh": "对比处理圆满完成！",
        "ja": "比較処理が正常に完了しました！"
    },
    "status_error": {
        "vi": "Lỗi trong quá trình so sánh:",
        "en": "Error during comparison:",
        "zh": "对比过程中发生错误:",
        "ja": "比較中にエラーが発生しました:"
    },

    # =========================================================================
    # MENU BAR
    # =========================================================================
    "menu_file": {
        "vi": "Tệp",
        "en": "File",
        "zh": "文件",
        "ja": "ファイル"
    },
    "menu_select_new": {
        "vi": "Chọn CTTT mới",
        "en": "Select New SOP",
        "zh": "选择新作业指导书",
        "ja": "新作業指導書を選択"
    },
    "menu_select_old": {
        "vi": "Chọn CTTT cũ",
        "en": "Select Old SOP",
        "zh": "选择旧作业指导书",
        "ja": "旧作業指導書を選択"
    },
    "menu_select_result": {
        "vi": "Chọn thư mục kết quả",
        "en": "Select Result Folder",
        "zh": "选择结果保存目录",
        "ja": "結果保存フォルダを選択"
    },
    "menu_save_settings": {
        "vi": "Lưu cài đặt",
        "en": "Save Settings",
        "zh": "保存设置",
        "ja": "設定を保存"
    },
    "menu_exit": {
        "vi": "Thoát",
        "en": "Exit",
        "zh": "退出",
        "ja": "終了"
    },
    "menu_edit": {
        "vi": "Chỉnh sửa",
        "en": "Edit",
        "zh": "编辑",
        "ja": "編集"
    },
    "menu_check_order": {
        "vi": "Kiểm tra thứ tự file",
        "en": "Check File Order",
        "zh": "检查文件配对顺序",
        "ja": "ファイル順序確認"
    },
    "menu_start_compare": {
        "vi": "Bắt đầu so sánh",
        "en": "Start Comparison",
        "zh": "开始对比",
        "ja": "比較開始"
    },
    "menu_view": {
        "vi": "Xem",
        "en": "View",
        "zh": "查看",
        "ja": "表示"
    },
    "menu_open_result": {
        "vi": "Mở thư mục kết quả",
        "en": "Open Result Folder",
        "zh": "打开结果文件夹",
        "ja": "結果フォルダを開く"
    },
    "menu_help": {
        "vi": "Trợ giúp",
        "en": "Help",
        "zh": "帮助",
        "ja": "ヘルプ"
    },
    "menu_user_guide": {
        "vi": "Hướng dẫn sử dụng",
        "en": "User Guide",
        "zh": "使用说明",
        "ja": "ユーザーガイド"
    },
    "menu_shortcuts": {
        "vi": "Danh sách phím tắt",
        "en": "Shortcuts List",
        "zh": "快捷键列表",
        "ja": "ショートカット一覧"
    },
    "menu_check_updates": {
        "vi": "Kiểm tra cập nhật phần mềm",
        "en": "Check for Software Updates",
        "zh": "检查软件更新",
        "ja": "ソフトウェア更新を確認"
    },
    "menu_about": {
        "vi": "Thông tin ứng dụng",
        "en": "About App",
        "zh": "关于应用",
        "ja": "アプリについて"
    },
    "about_title": {
        "vi": "Thông tin ứng dụng",
        "en": "About Application",
        "zh": "关于应用",
        "ja": "アプリケーション情報"
    },
    "about_msg": {
        "vi": "📊 So sánh Chỉ thị Thao tác (CTTT)\nPhiên bản: {version}\nNgày cập nhật: {date}\n\nTác giả: Ban Cải Tiến Kỹ Thuật",
        "en": "📊 SOP Comparison Tool\nVersion: {version}\nRelease Date: {date}\n\nAuthor: Engineering Improvement Team",
        "zh": "📊 作业指导书对比工具 (CTTT)\n版本: {version}\n更新日期: {date}\n\n作者: 技术改善组",
        "ja": "📊 作業指導書比較ツール (CTTT)\nバージョン: {version}\n更新日: {date}\n\n作成者: 技術改善チーム"
    },

    # =========================================================================
    # SHORTCUTS LIST
    # =========================================================================
    "shortcuts_title": {
        "vi": "Phím tắt ứng dụng",
        "en": "Application Shortcuts",
        "zh": "应用快捷键",
        "ja": "アプリケーションショートカット"
    },
    "shortcuts_header": {
        "vi": "⌨️ DANH SÁCH PHÍM TẮT:\n\n",
        "en": "⌨️ SHORTCUTS LIST:\n\n",
        "zh": "⌨️ 快捷键列表:\n\n",
        "ja": "⌨️ ショートカット一覧:\n\n"
    },

    # =========================================================================
    # AUTO UPDATE NOTIFICATIONS
    # =========================================================================
    "update_title": {
        "vi": "Cập nhật phần mềm",
        "en": "Software Update",
        "zh": "软件更新",
        "ja": "ソフトウェア更新"
    },
    "update_no_release": {
        "vi": "Phần mềm đang ở phiên bản mới nhất ({version}). Không có bản cập nhật mới.",
        "en": "You are using the latest version ({version}). No newer release was found.",
        "zh": "您当前使用的是最新版本 ({version})。未发现新版本更新。",
        "ja": "最新バージョン ({version}) を使用しています。新しい更新はありません。"
    },
    "update_found_msg": {
        "vi": "🆕 Đã có phiên bản mới: {newest_ver}\n(Phiên bản hiện tại của bạn: {current_ver})\n\nBạn có muốn tải và cài đặt ngay bây giờ không?\n\nLưu ý: Ứng dụng sẽ tự động tải bộ cài đặt và khởi động lại sau khi nâng cấp.",
        "en": "🆕 New version available: {newest_ver}\n(Your current version: {current_ver})\n\nWould you like to download and install it now?\n\nNote: The application will download the installer and restart automatically.",
        "zh": "🆕 发现新版本: {newest_ver}\n(您当前的运行版本: {current_ver})\n\n您是否希望立即下载并安装？\n\n注意: 应用程序将自动下载安装包并在升级后重启。",
        "ja": "🆕 新しいバージョンがあります: {newest_ver}\n(現在のバージョン: {current_ver})\n\n今すぐダウンロードしてインストールしますか？\n\n注: インストーラーが自動ダウンロードされ、完了後に再起動します。"
    },
    "update_release_notes": {
        "vi": "\n\nNội dung cập nhật:\n{notes}",
        "en": "\n\nRelease Notes:\n{notes}",
        "zh": "\n\n更新说明:\n{notes}",
        "ja": "\n\nリリースノート:\n{notes}"
    },
    "update_status_downloading": {
        "vi": "🔄 Đang tải và kiểm tra bộ cài đặt cập nhật...",
        "en": "🔄 Downloading and verifying update installer...",
        "zh": "🔄 正在下载并验证更新安装包...",
        "ja": "🔄 更新インストーラーをダウンロード・検証中..."
    },
    "update_error_msg": {
        "vi": "Không thể kiểm tra hoặc cài đặt bản cập nhật:\n{error}\n\nVui lòng kiểm tra kết nối mạng nội bộ (LAN / SMB Share) hoặc thử lại sau.",
        "en": "Could not check or install update:\n{error}\n\nPlease verify local network connection (LAN / SMB Share) or try again later.",
        "zh": "无法检查或安装更新:\n{error}\n\n请检查局域网连接 (LAN / SMB 共享) 或稍后重试。",
        "ja": "更新の確認またはインストールができませんでした:\n{error}\n\n社内ネットワーク接続 (LAN / SMB共有) を確認して再試行してください。"
    },

    # =========================================================================
    # EXECUTION RESULTS & DIALOGS
    # =========================================================================
    "complete": {
        "vi": "Hoàn thành",
        "en": "Complete",
        "zh": "完成",
        "ja": "完了"
    },
    "complete_msg": {
        "vi": "Đã xử lý tất cả các cặp file CTTT cũ, mới thành công.",
        "en": "All old and new SOP file pairs have been processed successfully.",
        "zh": "已成功处理所有新旧作业指导书文件对。",
        "ja": "すべての新旧作業指導書ファイルペアが正常に処理されました。"
    },
    "time_elapsed": {
        "vi": "Thời gian thực hiện: {minutes} phút {seconds:.2f} giây.",
        "en": "Time elapsed: {minutes} min {seconds:.2f} sec.",
        "zh": "耗时: {minutes} 分 {seconds:.2f} 秒。",
        "ja": "所要時間: {minutes} 分 {seconds:.2f} 秒。"
    },
    "error": {
        "vi": "Lỗi",
        "en": "Error",
        "zh": "错误",
        "ja": "エラー"
    },
    "legacy_confirm_title": {
        "vi": "Xác nhận so sánh CTTT phiên bản cũ",
        "en": "Confirm Old Version SOP Comparison",
        "zh": "确认旧版作业指导书比较",
        "ja": "旧バージョン作業指導書比較の確認"
    },
    "legacy_confirm_msg": {
        "vi": "⚠️ PHƯƠNG PHÁP CỦA PHIÊN BẢN CŨ\n\nPhương pháp này sẽ:\n• Mở từng file Excel trực tiếp trên màn hình và chụp ảnh\n• Yêu cầu KHÔNG SỬ DỤNG máy tính trong suốt quá trình chạy\n• Đảm bảo đã lưu và đóng tất cả file Excel đang mở trước đó\n\nBạn có muốn tiếp tục không?",
        "en": "⚠️ LEGACY VERSION METHOD\n\nThis method will:\n• Open each Excel file visibly on screen and capture screenshots\n• Requires NOT USING the computer during the entire process\n• Ensure all existing Excel workbooks are saved and closed\n\nDo you want to continue?",
        "zh": "⚠️ 传统版本方法\n\n此方法将:\n• 在屏幕上直接打开每个Excel文件并截屏\n• 整个运行过程中请勿使用电脑\n• 确保在此之前已保存并关闭所有打开的Excel文件\n\n是否继续？",
        "ja": "⚠️ 旧バージョン方式\n\nこの方式は:\n• 各Excelファイルを画面上に直接開いてスクリーンショットを撮影します\n• 処理完了までパソコンを一切操作しないでください\n• 事前に開いているすべてのExcelファイルを保存して閉じてください\n\n続行しますか？"
    },
    "legacy_complete_title": {
        "vi": "Hoàn thành so sánh CTTT (Phiên bản cũ)",
        "en": "Old Version SOP Comparison Complete",
        "zh": "旧版作业指导书比较完成",
        "ja": "旧バージョン作業指導書比較完了"
    },
    "legacy_complete_msg": {
        "vi": "Đã xử lý tất cả các cặp file CTTT bằng phương pháp chụp màn hình cũ thành công.",
        "en": "All SOP file pairs have been processed using the legacy screenshot method.",
        "zh": "已使用旧版截屏方式成功处理所有作业指导书文件对。",
        "ja": "旧スクリーンショット方式ですべての作業指導書ファイルペアの処理が完了しました。"
    },

    # =========================================================================
    # SETTINGS NOTICES & RESULT FOLDER
    # =========================================================================
    "settings_saved_title": {
        "vi": "Đã lưu cài đặt",
        "en": "Settings Saved",
        "zh": "设置已保存",
        "ja": "設定保存完了"
    },
    "settings_saved_msg": {
        "vi": "Cài đặt của bạn đã được lưu thành công để sử dụng lại lần sau.",
        "en": "Your settings have been saved successfully for future use.",
        "zh": "您的设置已成功保存，下次将自动加载。",
        "ja": "設定が正常に保存されました。次回起動時にも適用されます。"
    },
    "notice_title": {
        "vi": "Thông báo",
        "en": "Notice",
        "zh": "通知",
        "ja": "通知"
    },
    "folder_not_found_msg": {
        "vi": "Không tìm thấy thư mục kết quả. Có thể thư mục đã bị di chuyển hoặc xóa.",
        "en": "Result folder not found. It may have been moved or deleted.",
        "zh": "未找到结果文件夹。该文件夹可能已被移动或删除。",
        "ja": "結果フォルダが見つかりません。移動または削除された可能性があります。"
    },
    "no_folder_selected_msg": {
        "vi": "Chưa có thư mục kết quả. Vui lòng chọn file CTTT hoặc chỉ định thư mục trước.",
        "en": "No result folder available. Please select SOP files or specify a folder first.",
        "zh": "没有可用的结果文件夹。请先选择作业指导书文件或指定保存目录。",
        "ja": "利用可能な結果フォルダがありません。先に作業指導書ファイルを選択するか保存先を指定してください。"
    },

    # =========================================================================
    # COLOR PICKER TITLES
    # =========================================================================
    "color_picker_base": {
        "vi": "Chọn Màu Nền So Sánh",
        "en": "Select Comparison Base Color",
        "zh": "选择对比底色",
        "ja": "比較背景色を選択"
    },
    "color_picker_outline": {
        "vi": "Chọn Màu Viền Vùng Khác Biệt",
        "en": "Select Difference Outline Color",
        "zh": "选择差异区域边框颜色",
        "ja": "差異領域の枠線色を選択"
    },
    "color_picker_fill": {
        "vi": "Chọn Màu Tô Highlight",
        "en": "Select Highlight Fill Color",
        "zh": "选择高亮填充颜色",
        "ja": "ハイライト塗りつぶし色を選択"
    },

    # =========================================================================
    # VALIDATION & DETAILED ACTIONABLE ERROR MESSAGES
    # =========================================================================
    "val_title_incompatible_mode": {
        "vi": "Loại tài liệu không phù hợp",
        "en": "Incompatible Document Type",
        "zh": "文档类型不匹配",
        "ja": "ドキュメントの種類が不一致"
    },
    "val_header_incompatible_mode": {
        "vi": "Loại tài liệu đã chọn không phù hợp với cấu trúc file Excel:\n\n",
        "en": "The selected document type does not match the actual Excel files:\n\n",
        "zh": "所选的对比文档类型与Excel文件结构不匹配:\n\n",
        "ja": "選択された比較ドキュメントの種類がExcelファイル構造と一致しません:\n\n"
    },
    "val_err_missing_new": {
        "vi": "Chưa chọn file CTTT mới.",
        "en": "New SOP files have not been selected.",
        "zh": "尚未选择新作业指导书文件。",
        "ja": "新作業指導書ファイルが選択されていません。"
    },
    "val_err_missing_old": {
        "vi": "Chưa chọn file CTTT cũ.",
        "en": "Old SOP files have not been selected.",
        "zh": "尚未选择旧作业指导书文件。",
        "ja": "旧作業指導書ファイルが選択されていません。"
    },
    "val_err_file_not_found": {
        "vi": "File không tồn tại trên ổ đĩa: {file_path}",
        "en": "File does not exist on disk: {file_path}",
        "zh": "磁盘上不存在该文件: {file_path}",
        "ja": "ファイルがディスク上に存在しません: {file_path}"
    },
    "val_err_not_excel": {
        "vi": "File không phải định dạng Excel hợp lệ (.xlsx, .xls, .xlsm): {ext}",
        "en": "File is not a valid Excel format (.xlsx, .xls, .xlsm): {ext}",
        "zh": "文件不是有效的Excel格式 (.xlsx, .xls, .xlsm): {ext}",
        "ja": "有効なExcelファイル形式ではありません (.xlsx, .xls, .xlsm): {ext}"
    },
    "val_err_permission": {
        "vi": "Không có quyền đọc file hoặc file đang bị khóa bởi ứng dụng khác: {file_path}",
        "en": "Permission denied or file is locked by another program: {file_path}",
        "zh": "无权限读取文件或文件正被其他程序占用锁定: {file_path}",
        "ja": "ファイルの読み取り権限がないか、他のアプリで開かれています: {file_path}"
    },
    "val_err_pair_read_structure": {
        "vi": "Cặp {pair_index}: Không thể đọc cấu trúc workbook ({error}).",
        "en": "Pair {pair_index}: Unable to read workbook structure ({error}).",
        "zh": "第 {pair_index} 对: 无法读取工作簿结构 ({error})。",
        "ja": "ペア {pair_index}: ワークブック構造を読み取れません ({error})。"
    },
    "val_err_dukc_missing_form": {
        "vi": "Cặp {pair_index}: Chế độ 'Tờ Phát Hành DUKC & Khác' yêu cầu sheet 'Form', nhưng không tìm thấy trong {missing}.\n👉 Hướng dẫn: Kiểm tra lại tên sheet trong file Excel hoặc chọn loại so sánh khác.",
        "en": "Pair {pair_index}: Mode 'DUKC Release Form & Others' requires sheet 'Form', but not found in {missing}.\n👉 Solution: Check sheet names in Excel or switch to another comparison mode.",
        "zh": "第 {pair_index} 对: '应急应对发行表及其它' 模式要求工作表名为 'Form'，但在 {missing} 中未找到。\n👉 解决方法: 检查Excel中的工作表名称或选择其他对比类型。",
        "ja": "ペア {pair_index}:「緊急対応発行票・その他」モードには 'Form' シートが必要ですが、{missing} に見つかりません。\n👉 解決策: Excel内のシート名を確認するか、別の比較モードを選択してください。"
    },
    "val_err_standard_has_form": {
        "vi": "Cặp {pair_index}: Cả hai file đều có sheet 'Form', không phù hợp với 'CTTT thông thường'.\n👉 Hướng dẫn: Hãy chuyển sang chọn chế độ '3. Tờ Phát Hành DUKC & Khác'.",
        "en": "Pair {pair_index}: Both files contain sheet 'Form', which is incompatible with 'Standard SOP'.\n👉 Solution: Please switch to mode '3. DUKC Release Form & Others'.",
        "zh": "第 {pair_index} 对: 两个文件都包含 'Form' 工作表，不适用于 '普通作业指导书'。\n👉 解决方法: 请切换为 '3. 应急应对发行表及其它' 模式。",
        "ja": "ペア {pair_index}: 両方のファイルに 'Form' シートがあり、「通常の作業指導書」には適合しません。\n👉 解決策:「3. 緊急対応発行票・その他」モードに切り替えてください。"
    },
    "val_err_standard_no_green": {
        "vi": "Cặp {pair_index}: File mới '{new_label}' không có sheet tab màu XANH dành cho CTTT tiêu chuẩn.{suggestion}",
        "en": "Pair {pair_index}: New file '{new_label}' has no GREEN tab sheet for standard SOP.{suggestion}",
        "zh": "第 {pair_index} 对: 新文件 '{new_label}' 中没有标准作业指导书所需的绿色标签工作表。{suggestion}",
        "ja": "ペア {pair_index}: 新ファイル '{new_label}' に標準作業指導書用の緑色タブシートがありません。{suggestion}"
    },
    "val_err_standard_no_common_green": {
        "vi": "Cặp {pair_index}: Không tìm thấy sheet tab màu xanh trùng tên giữa '{new_label}' và '{old_label}'.\n👉 Hướng dẫn: Đảm bảo cả hai file đều có sheet tab xanh với cùng tên gọi.",
        "en": "Pair {pair_index}: No matching green tab sheet name found between '{new_label}' and '{old_label}'.\n👉 Solution: Ensure both files contain green tab sheets with identical names.",
        "zh": "第 {pair_index} 对: 在 '{new_label}' 和 '{old_label}' 之间未找到同名的绿色标签工作表。\n👉 解决方法: 确保两个文件都具有相同名称的绿色标签工作表。",
        "ja": "ペア {pair_index}: '{new_label}' と '{old_label}' の間に同名の緑色タブシートが見つかりません。\n👉 解決策: 両方のファイルに同名の緑色タブシートがあることを確認してください。"
    },
    "val_err_dukc_cttt_has_form": {
        "vi": "Cặp {pair_index}: Cả hai file đều có sheet 'Form'. Có thể bạn đã chọn nhầm loại tài liệu; hãy dùng 'Tờ Phát Hành DUKC & Khác'.\n👉 Hướng dẫn: Hãy chuyển sang chọn chế độ '3. Tờ Phát Hành DUKC & Khác'.",
        "en": "Pair {pair_index}: Both files contain sheet 'Form'. You might have chosen the wrong document type.\n👉 Solution: Please switch to mode '3. DUKC Release Form & Others'.",
        "zh": "第 {pair_index} 对: 两个文件都包含 'Form' 工作表。您可能选错了文档类型。\n👉 解决方法: 请切换为 '3. 应急应对发行表及其它' 模式。",
        "ja": "ペア {pair_index}: 両方のファイルに 'Form' シートがあります。種類を誤って選択した可能性があります。\n👉 解決策:「3. 緊急対応発行票・その他」モードを選択してください。"
    },
    "val_err_dukc_cttt_no_common_visible": {
        "vi": "Cặp {pair_index}: Không tìm thấy sheet hiển thị trùng tên giữa '{new_label}' và '{old_label}'.\n👉 Hướng dẫn: Kiểm tra lại tên các sheet cần so sánh trong 2 file.",
        "en": "Pair {pair_index}: No matching visible sheet name found between '{new_label}' and '{old_label}'.\n👉 Solution: Verify the sheet names in both files.",
        "zh": "第 {pair_index} 对: 在 '{new_label}' 和 '{old_label}' 之间未找到同名的可见工作表。\n👉 解决方法: 请核对两个文件中需要比对的工作表名称。",
        "ja": "ペア {pair_index}: '{new_label}' と '{old_label}' の間に同名の表示シートが見つかりません。\n👉 解決策: 両ファイル内の比較対象シート名を確認してください。"
    },
    "val_suggestion_has_form": {
        "vi": "\n👉 Gợi ý: File có sheet 'Form', hãy chọn loại '3. Tờ Phát Hành DUKC & Khác'.",
        "en": "\n👉 Hint: The file has a 'Form' sheet, please select '3. DUKC Release Form & Others'.",
        "zh": "\n👉 提示: 文件包含 'Form' 工作表，请选择 '3. 应急应对发行表及其它' 类型。",
        "ja": "\n👉 ヒント: ファイルに 'Form' シートがあります。「3. 緊急対応発行票・その他」を選択してください。"
    },

    # =========================================================================
    # DPI & VALUE VALIDATION
    # =========================================================================
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
}


def get_text(key: str, lang: str = "vi", **kwargs) -> str:
    """
    Get translated text for a given key and language.
    Falls back to Vietnamese if key not found for the requested language.
    Supports str.format formatting with kwargs.
    """
    if key in TRANSLATIONS:
        template = TRANSLATIONS[key].get(lang, TRANSLATIONS[key].get("vi", key))
    else:
        template = key

    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


def get_language_name(lang_code: str) -> str:
    """Get the display name for a language code."""
    return LANGUAGES.get(lang_code, lang_code)


def get_available_languages() -> list:
    """Return list of available language codes."""
    return list(LANGUAGES.keys())
