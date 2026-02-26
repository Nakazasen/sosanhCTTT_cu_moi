"""
Modern UI Style Configuration
Thiết kế hiện đại, chuyên nghiệp và tối giản
"""
import tkinter as tk
from tkinter import ttk

# ============== COLOR PALETTE ==============
class Colors:
    """Bảng màu hiện đại"""
    # Primary Colors
    PRIMARY = "#2563EB"           # Blue 600
    PRIMARY_DARK = "#1D4ED8"      # Blue 700
    PRIMARY_LIGHT = "#3B82F6"     # Blue 500
    
    # Secondary Colors  
    SECONDARY = "#64748B"         # Slate 500
    SECONDARY_DARK = "#475569"    # Slate 600
    SECONDARY_LIGHT = "#94A3B8"   # Slate 400
    
    # Background Colors
    BG_MAIN = "#F8FAFC"           # Slate 50
    BG_CARD = "#FFFFFF"           # White
    BG_DARK = "#1E293B"           # Slate 800
    
    # Surface Colors
    SURFACE = "#F1F5F9"           # Slate 100
    SURFACE_HOVER = "#E2E8F0"     # Slate 200
    BORDER = "#CBD5E1"            # Slate 300
    BORDER_LIGHT = "#E2E8F0"      # Slate 200
    
    # Text Colors
    TEXT_PRIMARY = "#1E293B"      # Slate 800
    TEXT_SECONDARY = "#475569"    # Slate 600
    TEXT_MUTED = "#94A3B8"        # Slate 400
    TEXT_INVERSE = "#FFFFFF"      # White
    
    # Accent Colors
    SUCCESS = "#10B981"           # Emerald 500
    WARNING = "#F59E0B"           # Amber 500
    ERROR = "#EF4444"             # Red 500
    INFO = "#3B82F6"              # Blue 500
    
    # Special
    ACCENT = "#6366F1"            # Indigo 500
    GRADIENT_START = "#3B82F6"    # Blue 500
    GRADIENT_END = "#6366F1"      # Indigo 500

# ============== TYPOGRAPHY ==============
class Fonts:
    """Font configuration"""
    FAMILY = "Segoe UI"
    FAMILY_MONO = "Consolas"
    
    # Sizes
    SIZE_XS = 10
    SIZE_SM = 11
    SIZE_BASE = 12
    SIZE_LG = 14
    SIZE_XL = 16
    SIZE_2XL = 20
    SIZE_3XL = 24
    
    # Weights
    NORMAL = "normal"
    BOLD = "bold"
    
    @staticmethod
    def get(size="base", weight="normal"):
        sizes = {
            "xs": Fonts.SIZE_XS, "sm": Fonts.SIZE_SM, "base": Fonts.SIZE_BASE,
            "lg": Fonts.SIZE_LG, "xl": Fonts.SIZE_XL, "2xl": Fonts.SIZE_2XL, "3xl": Fonts.SIZE_3XL
        }
        return (Fonts.FAMILY, sizes.get(size, Fonts.SIZE_BASE), weight)

# ============== SPACING ==============
class Spacing:
    """Spacing và padding values"""
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32

# ============== SHADOWS ==============
class Shadows:
    """Shadow configurations (for supported widgets)"""
    SM = {"borderwidth": 1, "relief": "solid"}
    MD = {"borderwidth": 2, "relief": "ridge"}
    LG = {"borderwidth": 3, "relief": "groove"}

# ============== STYLE CONFIGURATOR ==============
def configure_styles(root):
    """
    Áp dụng ttk styling hiện đại cho toàn bộ ứng dụng.
    Call function này ngay sau khi tạo root window.
    """
    style = ttk.Style(root)
    
    # Theme base
    try:
        style.theme_use("clam")
    except:
        pass
    
    # ============== BUTTON STYLES ==============
    # Primary Button (Blue)
    style.configure(
        "Primary.TButton",
        font=Fonts.get("base", "bold"),
        padding=(Spacing.LG, Spacing.SM),
        background=Colors.PRIMARY,
        foreground=Colors.TEXT_INVERSE,
        borderwidth=0,
        focuscolor="none"
    )
    style.map("Primary.TButton",
        background=[("active", Colors.PRIMARY_DARK), ("pressed", Colors.PRIMARY_DARK)],
        foreground=[("active", Colors.TEXT_INVERSE)]
    )
    
    # Secondary Button (Gray)
    style.configure(
        "Secondary.TButton",
        font=Fonts.get("base"),
        padding=(Spacing.MD, Spacing.SM),
        background=Colors.SURFACE,
        foreground=Colors.TEXT_PRIMARY,
        borderwidth=1,
        bordercolor=Colors.BORDER
    )
    style.map("Secondary.TButton",
        background=[("active", Colors.SURFACE_HOVER)]
    )
    
    # Success Button (Green)
    style.configure(
        "Success.TButton",
        font=Fonts.get("base", "bold"),
        padding=(Spacing.LG, Spacing.SM),
        background=Colors.SUCCESS,
        foreground=Colors.TEXT_INVERSE,
        borderwidth=0
    )
    
    # Warning Button (Orange/Yellow)
    style.configure(
        "Warning.TButton",
        font=Fonts.get("base", "bold"),
        padding=(Spacing.LG, Spacing.SM),
        background=Colors.WARNING,
        foreground=Colors.TEXT_PRIMARY,
        borderwidth=0
    )
    
    # ============== LABEL STYLES ==============
    style.configure(
        "TLabel",
        font=Fonts.get("base"),
        background=Colors.BG_MAIN,
        foreground=Colors.TEXT_PRIMARY
    )
    
    style.configure(
        "Header.TLabel",
        font=Fonts.get("2xl", "bold"),
        background=Colors.BG_MAIN,
        foreground=Colors.PRIMARY
    )
    
    style.configure(
        "Subheader.TLabel",
        font=Fonts.get("lg", "bold"),
        background=Colors.BG_MAIN,
        foreground=Colors.TEXT_PRIMARY
    )
    
    style.configure(
        "Muted.TLabel",
        font=Fonts.get("sm"),
        background=Colors.BG_MAIN,
        foreground=Colors.TEXT_MUTED
    )
    
    style.configure(
        "Card.TLabel",
        font=Fonts.get("base"),
        background=Colors.BG_CARD,
        foreground=Colors.TEXT_PRIMARY
    )
    
    # ============== ENTRY STYLES ==============
    style.configure(
        "TEntry",
        font=Fonts.get("base"),
        padding=(Spacing.SM, Spacing.SM),
        fieldbackground=Colors.BG_CARD,
        borderwidth=1,
        bordercolor=Colors.BORDER,
        focuscolor=Colors.PRIMARY
    )
    
    style.configure(
        "Modern.TEntry",
        font=Fonts.get("base"),
        padding=(Spacing.MD, Spacing.SM),
        fieldbackground=Colors.BG_CARD,
        borderwidth=2,
        bordercolor=Colors.BORDER_LIGHT
    )
    
    # ============== FRAME STYLES ==============
    style.configure(
        "TFrame",
        background=Colors.BG_MAIN
    )
    
    style.configure(
        "Card.TFrame",
        background=Colors.BG_CARD,
        borderwidth=1,
        relief="solid",
        bordercolor=Colors.BORDER_LIGHT
    )
    
    style.configure(
        "Surface.TFrame",
        background=Colors.SURFACE
    )
    
    # ============== LABELFRAME STYLES ==============
    style.configure(
        "TLabelframe",
        background=Colors.BG_CARD,
        borderwidth=1,
        relief="solid"
    )
    style.configure(
        "TLabelframe.Label",
        font=Fonts.get("base", "bold"),
        background=Colors.BG_CARD,
        foreground=Colors.PRIMARY
    )
    
    style.configure(
        "Card.TLabelframe",
        background=Colors.BG_CARD,
        borderwidth=2,
        relief="groove"
    )
    style.configure(
        "Card.TLabelframe.Label",
        font=Fonts.get("lg", "bold"),
        background=Colors.BG_CARD,
        foreground=Colors.PRIMARY
    )
    
    # ============== COMBOBOX STYLES ==============
    style.configure(
        "TCombobox",
        font=Fonts.get("base"),
        padding=(Spacing.SM, Spacing.SM),
        fieldbackground=Colors.BG_CARD,
        background=Colors.BG_CARD
    )
    style.map("TCombobox",
        fieldbackground=[("readonly", Colors.BG_CARD)],
        selectbackground=[("readonly", Colors.PRIMARY)]
    )
    
    # ============== CHECKBOX & RADIOBUTTON ==============
    style.configure(
        "TCheckbutton",
        font=Fonts.get("base"),
        background=Colors.BG_MAIN,
        foreground=Colors.TEXT_PRIMARY
    )
    style.map("TCheckbutton",
        background=[("active", Colors.BG_MAIN)]
    )
    
    style.configure(
        "Card.TCheckbutton",
        font=Fonts.get("base"),
        background=Colors.BG_CARD,
        foreground=Colors.TEXT_PRIMARY
    )
    
    style.configure(
        "TRadiobutton",
        font=Fonts.get("base"),
        background=Colors.BG_MAIN,
        foreground=Colors.TEXT_PRIMARY
    )
    
    # ============== PROGRESSBAR ==============
    style.configure(
        "TProgressbar",
        background=Colors.PRIMARY,
        troughcolor=Colors.SURFACE,
        borderwidth=0,
        thickness=8
    )
    
    style.configure(
        "Success.TProgressbar",
        background=Colors.SUCCESS,
        troughcolor=Colors.SURFACE
    )
    
    # ============== SCALE/SLIDER ==============
    style.configure(
        "TScale",
        background=Colors.BG_MAIN,
        troughcolor=Colors.SURFACE,
        sliderthickness=16
    )
    
    # ============== NOTEBOOK/TABS ==============
    style.configure(
        "TNotebook",
        background=Colors.BG_MAIN,
        borderwidth=0
    )
    style.configure(
        "TNotebook.Tab",
        font=Fonts.get("base"),
        padding=(Spacing.LG, Spacing.SM),
        background=Colors.SURFACE,
        foreground=Colors.TEXT_SECONDARY
    )
    style.map("TNotebook.Tab",
        background=[("selected", Colors.BG_CARD)],
        foreground=[("selected", Colors.PRIMARY)]
    )
    
    # ============== SCROLLBAR ==============
    style.configure(
        "TScrollbar",
        background=Colors.SURFACE,
        troughcolor=Colors.BG_MAIN,
        borderwidth=0,
        arrowsize=12
    )
    style.map("TScrollbar",
        background=[("active", Colors.SECONDARY_LIGHT)]
    )
    
    # ============== SEPARATOR ==============
    style.configure(
        "TSeparator",
        background=Colors.BORDER_LIGHT
    )
    
    return style


def create_card_frame(parent, title=None, padding=Spacing.LG):
    """
    Tạo một Card Frame với viền bo góc và shadow (simulated).
    
    Args:
        parent: Widget cha
        title: Tiêu đề của card (optional)
        padding: Padding bên trong
        
    Returns:
        Frame object để add widgets vào
    """
    if title:
        frame = ttk.LabelFrame(
            parent, 
            text=f"  {title}  ",
            style="Card.TLabelframe",
            padding=padding
        )
    else:
        frame = ttk.Frame(parent, style="Card.TFrame", padding=padding)
    
    return frame


def create_section_header(parent, text, icon=None):
    """
    Tạo section header với style thống nhất.
    """
    header_frame = ttk.Frame(parent, style="TFrame")
    
    if icon:
        icon_label = ttk.Label(header_frame, text=icon, style="Header.TLabel")
        icon_label.pack(side="left", padx=(0, Spacing.SM))
    
    label = ttk.Label(header_frame, text=text, style="Subheader.TLabel")
    label.pack(side="left")
    
    return header_frame


def create_modern_button(parent, text, command, style_name="Primary.TButton", width=None):
    """
    Tạo button với style hiện đại.
    """
    btn = ttk.Button(
        parent,
        text=text,
        command=command,
        style=style_name
    )
    if width:
        btn.configure(width=width)
    return btn


def create_status_bar(parent):
    """
    Tạo status bar phía dưới với gradient effect (simulated).
    """
    status_frame = ttk.Frame(parent, style="Surface.TFrame")
    status_frame.pack(side="bottom", fill="x")
    
    status_label = ttk.Label(
        status_frame,
        text="Ready",
        style="Muted.TLabel"
    )
    status_label.pack(side="left", padx=Spacing.LG, pady=Spacing.SM)
    
    return status_frame, status_label


# ============== HELPER FUNCTIONS ==============
def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def darken_color(hex_color, factor=0.8):
    """Darken a hex color by factor"""
    rgb = hex_to_rgb(hex_color)
    darkened = tuple(int(c * factor) for c in rgb)
    return rgb_to_hex(darkened)

def lighten_color(hex_color, factor=1.2):
    """Lighten a hex color by factor"""
    rgb = hex_to_rgb(hex_color)
    lightened = tuple(min(255, int(c * factor)) for c in rgb)
    return rgb_to_hex(lightened)
