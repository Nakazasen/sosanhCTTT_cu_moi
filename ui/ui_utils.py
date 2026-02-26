"""
UI Utilities - Các widget và helper UI 

Bao gồm:
- ToolTip: Hiển thị tooltip khi hover
- DragDropListbox: Listbox hỗ trợ drag-drop
- StatusBar: Thanh trạng thái
- ProgressDialog: Dialog hiển thị tiến trình
"""

import tkinter as tk
from tkinter import ttk


class ToolTip:
    """
    Tạo tooltip hover cho các widget.
    
    Sử dụng:
        tooltip = ToolTip(button, "Nội dung tooltip")
    """
    
    def __init__(self, widget, text, delay=500, wraplength=300):
        """
        Args:
            widget: Widget cần gắn tooltip
            text: Nội dung tooltip
            delay: Thời gian delay trước khi hiện tooltip (ms)
            wraplength: Độ rộng tối đa trước khi xuống dòng
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wraplength = wraplength
        self.tooltip_window = None
        self.after_id = None
        
        # Bind events
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<ButtonPress>", self._on_leave)
    
    def _on_enter(self, event):
        """Bắt đầu timer khi chuột vào widget."""
        self._cancel()
        self.after_id = self.widget.after(self.delay, self._show_tooltip)
    
    def _on_leave(self, event):
        """Ẩn tooltip khi chuột rời đi."""
        self._cancel()
        self._hide_tooltip()
    
    def _cancel(self):
        """Hủy timer nếu có."""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
    
    def _show_tooltip(self):
        """Hiển thị tooltip."""
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Giao diện tooltip
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#ffffcc",
            relief="solid",
            borderwidth=1,
            wraplength=self.wraplength,
            justify="left",
            font=("Arial", 9),
            padx=5,
            pady=3
        )
        label.pack()
    
    def _hide_tooltip(self):
        """Ẩn và xóa tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class DragDropListbox(tk.Listbox):
    """
    Listbox hỗ trợ drag-drop để sắp xếp lại items.
    
    Sử dụng:
        lb = DragDropListbox(parent)
        lb.insert(tk.END, "Item 1")
        lb.insert(tk.END, "Item 2")
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.drag_data = {"index": None}
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_drop)
    
    def _on_click(self, event):
        """Bắt đầu drag."""
        index = self.nearest(event.y)
        if index >= 0:
            self.drag_data["index"] = index
            self.selection_clear(0, tk.END)
            self.selection_set(index)
    
    def _on_drag(self, event):
        """Trong quá trình drag."""
        if self.drag_data["index"] is None:
            return
        
        new_index = self.nearest(event.y)
        if new_index < 0:
            return
        
        if new_index != self.drag_data["index"]:
            # Swap items
            item = self.get(self.drag_data["index"])
            self.delete(self.drag_data["index"])
            self.insert(new_index, item)
            self.drag_data["index"] = new_index
            self.selection_clear(0, tk.END)
            self.selection_set(new_index)
    
    def _on_drop(self, event):
        """Kết thúc drag."""
        self.drag_data["index"] = None


class StatusBar(tk.Frame):
    """
    Thanh trạng thái đơn giản.
    
    Sử dụng:
        status = StatusBar(parent)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        status.set("Đang xử lý...")
    """
    
    def __init__(self, master):
        super().__init__(master, borderwidth=1, relief="sunken")
        
        self.label = tk.Label(self, anchor="w", padx=5)
        self.label.pack(fill=tk.X)
    
    def set(self, text):
        """Cập nhật nội dung status bar."""
        self.label.config(text=text)
        self.update_idletasks()
    
    def clear(self):
        """Xóa nội dung."""
        self.label.config(text="")


class ProgressDialog(tk.Toplevel):
    """
    Dialog hiển thị tiến trình xử lý.
    
    Sử dụng:
        dialog = ProgressDialog(parent, "Đang xử lý", maximum=100)
        dialog.update_progress(50, "Đang xử lý item 5/10...")
        dialog.close()
    """
    
    def __init__(self, parent, title="Đang xử lý...", maximum=100):
        super().__init__(parent)
        
        self.title(title)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        
        w = 400
        h = 100
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.resizable(False, False)
        
        # UI
        self.label = tk.Label(self, text="Đang khởi tạo...")
        self.label.pack(pady=10)
        
        self.progress = ttk.Progressbar(self, length=350, mode='determinate', maximum=maximum)
        self.progress.pack(pady=5, padx=20)
        
        self.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable close button
    
    def update_progress(self, value, text=None):
        """Cập nhật tiến trình."""
        self.progress['value'] = value
        if text:
            self.label.config(text=text)
        self.update_idletasks()
    
    def set_indeterminate(self, text=None):
        """Chuyển sang chế độ indeterminate."""
        self.progress.config(mode='indeterminate')
        self.progress.start(10)
        if text:
            self.label.config(text=text)
        self.update_idletasks()
    
    def close(self):
        """Đóng dialog."""
        self.progress.stop()
        self.grab_release()
        self.destroy()


class ScrollableFrame(ttk.Frame):
    """
    Frame có thể scroll.
    
    Sử dụng:
        sf = ScrollableFrame(parent)
        sf.pack(fill=tk.BOTH, expand=True)
        # Thêm widgets vào sf.scrollable_frame
    """
    
    def __init__(self, container, **kwargs):
        super().__init__(container, **kwargs)
        
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mousewheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))


class FilePairListbox(tk.Frame):
    """
    Widget hiển thị cặp file (new/old) với khả năng kéo thả để sắp xếp.
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Headers
        header_frame = tk.Frame(self)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="File Mới", font=("Arial", 10, "bold"), width=40, anchor="w").pack(side=tk.LEFT)
        tk.Label(header_frame, text="File Cũ", font=("Arial", 10, "bold"), width=40, anchor="w").pack(side=tk.LEFT)
        
        # Listboxes
        list_frame = tk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.new_listbox = DragDropListbox(list_frame, width=40, height=10, selectmode=tk.SINGLE)
        self.old_listbox = DragDropListbox(list_frame, width=40, height=10, selectmode=tk.SINGLE)
        
        scrollbar = tk.Scrollbar(list_frame)
        
        self.new_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.old_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sync scroll
        scrollbar.config(command=self._sync_scroll)
        self.new_listbox.config(yscrollcommand=lambda *args: self._scroll_both(*args))
        self.old_listbox.config(yscrollcommand=lambda *args: self._scroll_both(*args))
    
    def _sync_scroll(self, *args):
        """Đồng bộ scroll cả hai listbox."""
        self.new_listbox.yview(*args)
        self.old_listbox.yview(*args)
    
    def _scroll_both(self, first, last):
        """Callback khi scroll một listbox."""
        self.new_listbox.yview_moveto(first)
        self.old_listbox.yview_moveto(first)
    
    def add_pair(self, new_file, old_file):
        """Thêm một cặp file."""
        self.new_listbox.insert(tk.END, new_file)
        self.old_listbox.insert(tk.END, old_file)
    
    def clear(self):
        """Xóa toàn bộ danh sách."""
        self.new_listbox.delete(0, tk.END)
        self.old_listbox.delete(0, tk.END)
    
    def get_pairs(self):
        """Lấy danh sách các cặp file."""
        new_files = list(self.new_listbox.get(0, tk.END))
        old_files = list(self.old_listbox.get(0, tk.END))
        return list(zip(new_files, old_files))
