#!/usr/bin/env python3
"""
ShortlistIQ — AI Resume Shortlisting System
Premium Desktop GUI Application (Tkinter)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import shutil
import json
import math
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
#  COLOR SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class C:
    BG          = "#0b0e14"
    BG2         = "#0f1219"
    SIDEBAR     = "#0d1017"
    SIDEBAR_SEP = "#1a1f2b"
    CARD        = "#141820"
    CARD2       = "#181d27"
    CARD_HOVER  = "#1c2230"
    INPUT       = "#0d1117"
    ACCENT      = "#7c3aed"
    ACCENT_L    = "#a78bfa"
    ACCENT_D    = "#2e1065"
    TEAL        = "#06b6d4"
    TEAL_D      = "#0c2d3e"
    GREEN       = "#10b981"
    GREEN_D     = "#052e1c"
    YELLOW      = "#f59e0b"
    YELLOW_D    = "#3d2a08"
    RED         = "#ef4444"
    RED_D       = "#3b1010"
    ORANGE      = "#f97316"
    BLUE        = "#3b82f6"
    BLUE_D      = "#0c1e42"
    PINK        = "#ec4899"
    TEXT        = "#e6edf3"
    TEXT2       = "#8b949e"
    TEXT3       = "#484f58"
    BORDER      = "#21262d"
    BORDER_L    = "#30363d"
    NAV_ACTIVE  = "#151b28"
    GLOW        = "#7c3aed"

# ── Fonts ──
F_HERO      = ("Segoe UI", 28, "bold")
F_TITLE     = ("Segoe UI", 20, "bold")
F_H1        = ("Segoe UI", 16, "bold")
F_H2        = ("Segoe UI", 13, "bold")
F_H3        = ("Segoe UI", 11, "bold")
F_BODY      = ("Segoe UI", 11)
F_BODY_B    = ("Segoe UI", 11, "bold")
F_SM        = ("Segoe UI", 9)
F_SM_B      = ("Segoe UI", 9, "bold")
F_XS        = ("Segoe UI", 8)
F_METRIC    = ("Segoe UI", 32, "bold")
F_METRIC_SM = ("Segoe UI", 20, "bold")
F_NAV       = ("Segoe UI", 11)
F_NAV_B     = ("Segoe UI", 11, "bold")
F_CODE      = ("Consolas", 10)
F_LOGO      = ("Segoe UI", 15, "bold")

SIDEBAR_W = 240

# ═══════════════════════════════════════════════════════════════════════════════
#  CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════

class CircularGauge(tk.Canvas):
    """Animated circular score gauge drawn with Canvas arcs."""

    def __init__(self, parent, size=110, score=0, max_score=50, color=C.ACCENT,
                 label="", **kw):
        super().__init__(parent, width=size, height=size, bg=C.CARD,
                         highlightthickness=0, bd=0, **kw)
        self.size = size
        self.score = score
        self.max_score = max_score
        self.color = color
        self.label = label
        self._anim_pct = 0
        self._draw()

    def _draw(self):
        self.delete("all")
        s = self.size
        pad = 10
        lw = 7
        cx, cy = s // 2, s // 2
        r = (s - 2 * pad) // 2

        # Background ring
        self.create_oval(pad, pad, s - pad, s - pad, outline=C.BORDER_L, width=lw)

        # Score arc
        pct = (self.score / self.max_score) if self.max_score else 0
        pct = min(max(pct, 0), 1)
        extent = pct * 360 * self._anim_pct
        if extent > 0:
            self.create_arc(pad, pad, s - pad, s - pad, start=90,
                            extent=-extent, outline=self.color, width=lw, style="arc")

        # Center text
        self.create_text(cx, cy - 6, text=str(self.score),
                         font=F_METRIC_SM, fill=self.color)
        self.create_text(cx, cy + 16, text=self.label,
                         font=F_XS, fill=C.TEXT3)

    def animate(self, step=0):
        self._anim_pct = min(step / 20, 1.0)
        self._draw()
        if step < 20:
            self.after(25, self.animate, step + 1)


class ScoreBar(tk.Canvas):
    """Animated horizontal score bar."""

    def __init__(self, parent, score=0, max_score=10, color=C.ACCENT,
                 width=300, height=6, **kw):
        super().__init__(parent, width=width, height=height, bg=C.CARD,
                         highlightthickness=0, bd=0, **kw)
        self.score = score
        self.max_score = max_score
        self.color = color
        self.bar_w = width
        self.bar_h = height
        self._anim = 0
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, e=None):
        self.bar_w = self.winfo_width()
        self._redraw()

    def _redraw(self):
        self.delete("all")
        # Background track
        self.create_rectangle(0, 0, self.bar_w, self.bar_h,
                              fill=C.BORDER, outline="")
        # Filled bar
        pct = (self.score / self.max_score) if self.max_score else 0
        fill_w = int(self.bar_w * pct * self._anim)
        if fill_w > 0:
            self.create_rectangle(0, 0, fill_w, self.bar_h,
                                  fill=self.color, outline="")

    def animate(self, step=0):
        self._anim = min(step / 15, 1.0)
        self._redraw()
        if step < 15:
            self.after(30, self.animate, step + 1)


class PulsingDot(tk.Canvas):
    """Small pulsing status indicator dot."""

    def __init__(self, parent, color=C.GREEN, size=10, **kw):
        super().__init__(parent, width=size + 6, height=size + 6,
                         bg=parent.cget("bg"), highlightthickness=0, bd=0, **kw)
        self.color = color
        self.dot_size = size
        self._pulse_r = 0
        self._draw()

    def _draw(self):
        self.delete("all")
        cx, cy = (self.dot_size + 6) // 2, (self.dot_size + 6) // 2
        r = self.dot_size // 2
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill=self.color, outline="")

    def start_pulse(self):
        self._do_pulse(0)

    def _do_pulse(self, step):
        self.delete("all")
        cx, cy = (self.dot_size + 6) // 2, (self.dot_size + 6) // 2
        r = self.dot_size // 2
        # Outer glow
        phase = (math.sin(step * 0.15) + 1) / 2
        gr = r + int(3 * phase)
        self.create_oval(cx - gr, cy - gr, cx + gr, cy + gr,
                         fill="", outline=self.color, width=1)
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill=self.color, outline="")
        self.after(60, self._do_pulse, step + 1)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

class ShortlistIQApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ShortlistIQ — AI Resume Shortlisting System")
        self.root.geometry("1400x860")
        self.root.minsize(1150, 720)
        self.root.configure(bg=C.BG)
        try:
            self.root.iconbitmap(default="")
        except Exception:
            pass

        # State
        self.current_page = None
        self.nav_btns: dict = {}
        self.evaluation_result = None
        self.raw_response = None
        self.is_evaluating = False
        self.resume_files: list[Path] = []
        self.candidates_data: list[dict] = []
        self._toast_id = None

        self._setup_styles()
        self._build_layout()
        self._refresh_resumes()
        self.show_page("dashboard")

    # ──────────────────────────── Styles ──────────────────────────────────

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Dark.Treeview", background=C.CARD, foreground=C.TEXT,
                     fieldbackground=C.CARD, borderwidth=0, rowheight=40, font=F_BODY)
        s.configure("Dark.Treeview.Heading", background=C.BG2, foreground=C.TEXT2,
                     borderwidth=0, font=F_SM_B, padding=(10, 8))
        s.map("Dark.Treeview",
              background=[("selected", C.ACCENT_D)],
              foreground=[("selected", C.TEXT)])
        s.configure("Accent.Horizontal.TProgressbar",
                     troughcolor=C.BORDER, background=C.ACCENT, borderwidth=0)

    # ──────────────────────────── Layout ─────────────────────────────────

    def _build_layout(self):
        master = tk.Frame(self.root, bg=C.BG)
        master.pack(fill="both", expand=True)

        self._build_sidebar(master)

        right = tk.Frame(master, bg=C.BG)
        right.pack(side="left", fill="both", expand=True)

        self._build_header(right)
        tk.Frame(right, bg=C.BORDER, height=1).pack(fill="x", padx=0)

        self.page_frame = tk.Frame(right, bg=C.BG)
        self.page_frame.pack(fill="both", expand=True)

    # ──────────────────────────── Sidebar ─────────────────────────────────

    def _build_sidebar(self, parent):
        self.sidebar = tk.Frame(parent, bg=C.SIDEBAR, width=SIDEBAR_W)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo_fr = tk.Frame(self.sidebar, bg=C.SIDEBAR)
        logo_fr.pack(fill="x", padx=20, pady=(22, 0))

        # Glow dot + logo text
        top_row = tk.Frame(logo_fr, bg=C.SIDEBAR)
        top_row.pack(anchor="w")
        glow = tk.Canvas(top_row, width=12, height=12, bg=C.SIDEBAR, highlightthickness=0)
        glow.pack(side="left", padx=(0, 8), pady=4)
        glow.create_oval(1, 1, 11, 11, fill=C.ACCENT, outline=C.ACCENT_L)
        tk.Label(top_row, text="ShortlistIQ", font=F_LOGO,
                 bg=C.SIDEBAR, fg=C.TEXT).pack(side="left")

        tk.Label(logo_fr, text="AI Resume Shortlisting System", font=F_XS,
                 bg=C.SIDEBAR, fg=C.TEXT3).pack(anchor="w", padx=(20, 0), pady=(2, 0))

        tk.Frame(self.sidebar, bg=C.SIDEBAR_SEP, height=1).pack(fill="x", padx=16, pady=(18, 14))

        # Section label
        tk.Label(self.sidebar, text="  MAIN MENU", font=F_XS,
                 bg=C.SIDEBAR, fg=C.TEXT3).pack(anchor="w", padx=18, pady=(0, 6))

        nav = [
            ("dashboard", "⬡", "Dashboard"),
            ("resumes",   "◫", "Resume Manager"),
            ("jobdesc",   "≡", "Job Description"),
            ("evaluate",  "⚡","Evaluate"),
            ("results",   "◈", "Results"),
        ]
        for key, icon, label in nav:
            self._add_nav(key, icon, label)

        tk.Frame(self.sidebar, bg=C.SIDEBAR).pack(fill="both", expand=True)
        tk.Frame(self.sidebar, bg=C.SIDEBAR_SEP, height=1).pack(fill="x", padx=16, pady=(0, 8))

        tk.Label(self.sidebar, text="  SYSTEM", font=F_XS,
                 bg=C.SIDEBAR, fg=C.TEXT3).pack(anchor="w", padx=18, pady=(0, 6))
        self._add_nav("about", "ⓘ", "About")

        # Footer
        ft = tk.Frame(self.sidebar, bg=C.SIDEBAR)
        ft.pack(fill="x", padx=20, pady=(10, 16))
        tk.Label(ft, text="Groq LPU  ·  Qwen 3.8-27B", font=F_XS,
                 bg=C.SIDEBAR, fg=C.TEXT3).pack(anchor="w")
        tk.Label(ft, text="v1.0.0", font=F_XS,
                 bg=C.SIDEBAR, fg=C.TEXT3).pack(anchor="w")

    def _add_nav(self, key, icon, label):
        fr = tk.Frame(self.sidebar, bg=C.SIDEBAR, cursor="hand2")
        fr.pack(fill="x", padx=8, pady=1)

        bar = tk.Frame(fr, bg=C.SIDEBAR, width=3)
        bar.pack(side="left", fill="y")

        icon_lbl = tk.Label(fr, text=icon, font=("Segoe UI", 13),
                            bg=C.SIDEBAR, fg=C.TEXT3, width=2)
        icon_lbl.pack(side="left", padx=(10, 4), pady=9)

        text_lbl = tk.Label(fr, text=label, font=F_NAV,
                            bg=C.SIDEBAR, fg=C.TEXT2, anchor="w")
        text_lbl.pack(side="left", fill="x", expand=True, pady=9)

        self.nav_btns[key] = {"fr": fr, "bar": bar, "icon": icon_lbl, "text": text_lbl}

        for w in (fr, icon_lbl, text_lbl):
            w.bind("<Button-1>", lambda e, k=key: self.show_page(k))
            w.bind("<Enter>", lambda e, k=key: self._nav_enter(k))
            w.bind("<Leave>", lambda e, k=key: self._nav_leave(k))

    def _nav_enter(self, key):
        if self.current_page == key:
            return
        n = self.nav_btns[key]
        for w in (n["fr"], n["icon"], n["text"]):
            w.configure(bg=C.CARD)

    def _nav_leave(self, key):
        if self.current_page == key:
            return
        n = self.nav_btns[key]
        for w in (n["fr"], n["icon"], n["text"]):
            w.configure(bg=C.SIDEBAR)

    def _set_active_nav(self, key):
        for k, n in self.nav_btns.items():
            active = (k == key)
            bg = C.NAV_ACTIVE if active else C.SIDEBAR
            bar_bg = C.ACCENT if active else C.SIDEBAR
            fg = C.TEXT if active else C.TEXT2
            icon_fg = C.ACCENT_L if active else C.TEXT3
            font = F_NAV_B if active else F_NAV
            for w in (n["fr"], n["icon"], n["text"]):
                w.configure(bg=bg)
            n["bar"].configure(bg=bar_bg)
            n["text"].configure(fg=fg, font=font)
            n["icon"].configure(fg=icon_fg)

    # ──────────────────────────── Header ─────────────────────────────────

    def _build_header(self, parent):
        hdr = tk.Frame(parent, bg=C.BG, height=54)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        left = tk.Frame(hdr, bg=C.BG)
        left.pack(side="left", fill="y", padx=(28, 0))

        self.hdr_title = tk.Label(left, text="Dashboard", font=F_TITLE,
                                   bg=C.BG, fg=C.TEXT)
        self.hdr_title.pack(side="left")

        self.hdr_badge = tk.Label(left, text="", font=F_XS, bg=C.BG, fg=C.BG)
        self.hdr_badge.pack(side="left", padx=(12, 0))

        right = tk.Frame(hdr, bg=C.BG)
        right.pack(side="right", fill="y", padx=(0, 28))

        self.hdr_clock = tk.Label(right, text="", font=F_SM, bg=C.BG, fg=C.TEXT3)
        self.hdr_clock.pack(side="right")
        self._tick_clock()

        # Status dot
        self._api_dot = PulsingDot(right, color=C.GREEN if self._check_api() else C.RED, size=8)
        self._api_dot.pack(side="right", padx=(0, 8))
        api_label = "API Connected" if self._check_api() else "API Missing"
        tk.Label(right, text=api_label, font=F_XS, bg=C.BG,
                 fg=C.GREEN if self._check_api() else C.RED).pack(side="right", padx=(0, 4))

    def _tick_clock(self):
        self.hdr_clock.configure(text=datetime.now().strftime("%a, %d %b %Y  ·  %I:%M %p"))
        self.root.after(20000, self._tick_clock)

    # ──────────────────────────── Router ──────────────────────────────────

    def show_page(self, key):
        self.current_page = key
        self._set_active_nav(key)

        titles = {"dashboard": "Dashboard", "resumes": "Resume Manager",
                  "jobdesc": "Job Description", "evaluate": "Run Evaluation",
                  "results": "Evaluation Results", "about": "About"}
        self.hdr_title.configure(text=titles.get(key, ""))

        for w in self.page_frame.winfo_children():
            w.destroy()

        {"dashboard": self._pg_dashboard, "resumes": self._pg_resumes,
         "jobdesc": self._pg_jobdesc, "evaluate": self._pg_evaluate,
         "results": self._pg_results, "about": self._pg_about
        }.get(key, self._pg_dashboard)()

    # ──────────────────────────── Helpers ─────────────────────────────────

    def _scroll_frame(self, parent):
        canvas = tk.Canvas(parent, bg=C.BG, highlightthickness=0, bd=0)
        inner = tk.Frame(canvas, bg=C.BG)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        wid = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1 * int(e.delta / 120), "units"))
        return inner

    def _card(self, parent, border_color=C.BORDER):
        outer = tk.Frame(parent, bg=border_color)
        inner = tk.Frame(outer, bg=C.CARD)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        return outer, inner

    def _accent_card(self, parent, accent_color=C.ACCENT):
        """Card with a colored top accent strip."""
        outer = tk.Frame(parent, bg=C.BORDER)
        wrapper = tk.Frame(outer, bg=C.CARD)
        wrapper.pack(fill="both", expand=True, padx=1, pady=1)
        tk.Frame(wrapper, bg=accent_color, height=3).pack(fill="x")
        inner = tk.Frame(wrapper, bg=C.CARD)
        inner.pack(fill="both", expand=True)
        return outer, inner

    def _metric_card(self, parent, label, value, color=C.ACCENT_L, sub="",
                     accent=None):
        outer, inner = self._accent_card(parent, accent_color=accent or color)
        inner.configure(padx=20, pady=14)
        tk.Label(inner, text=label, font=F_SM_B, bg=C.CARD, fg=C.TEXT3).pack(anchor="w")
        tk.Label(inner, text=str(value), font=F_METRIC_SM,
                 bg=C.CARD, fg=color).pack(anchor="w", pady=(4, 0))
        if sub:
            tk.Label(inner, text=sub, font=F_XS, bg=C.CARD, fg=C.TEXT3).pack(anchor="w", pady=(2, 0))
        return outer

    def _btn(self, parent, text, cmd, bg=C.ACCENT, fg="#fff", font=None):
        lbl = tk.Label(parent, text=text, font=font or F_BODY_B,
                       bg=bg, fg=fg, padx=18, pady=9, cursor="hand2")
        lbl.bind("<Button-1>", lambda e: cmd())
        lbl.bind("<Enter>", lambda e: lbl.configure(bg=self._lighten(bg, 20)))
        lbl.bind("<Leave>", lambda e: lbl.configure(bg=bg))
        return lbl

    def _ghost_btn(self, parent, text, cmd):
        """Outlined/ghost style button."""
        fr = tk.Frame(parent, bg=C.BORDER_L)
        lbl = tk.Label(fr, text=text, font=F_BODY, bg=C.BG2, fg=C.TEXT2,
                       padx=16, pady=8, cursor="hand2")
        lbl.pack(padx=1, pady=1)
        lbl.bind("<Button-1>", lambda e: cmd())
        lbl.bind("<Enter>", lambda e: lbl.configure(bg=C.CARD, fg=C.TEXT))
        lbl.bind("<Leave>", lambda e: lbl.configure(bg=C.BG2, fg=C.TEXT2))
        return fr

    def _toast(self, msg, color=C.GREEN):
        """Show a temporary notification toast at top-right."""
        if self._toast_id:
            try:
                self.root.after_cancel(self._toast_id)
            except Exception:
                pass
        t = tk.Toplevel(self.root)
        t.overrideredirect(True)
        t.attributes("-topmost", True)
        t.configure(bg=color)
        tk.Label(t, text=f"  {msg}  ", font=F_BODY_B, bg=color, fg="#fff",
                 padx=14, pady=8).pack()
        t.update_idletasks()
        rx = self.root.winfo_rootx() + self.root.winfo_width() - t.winfo_width() - 30
        ry = self.root.winfo_rooty() + 60
        t.geometry(f"+{rx}+{ry}")
        self._toast_id = self.root.after(3000, t.destroy)

    @staticmethod
    def _lighten(hex_c, amt=20):
        r, g, b = int(hex_c[1:3], 16), int(hex_c[3:5], 16), int(hex_c[5:7], 16)
        return f"#{min(r+amt,255):02x}{min(g+amt,255):02x}{min(b+amt,255):02x}"

    def _refresh_resumes(self):
        d = Path("resumes")
        if not d.exists():
            try:
                d.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
        self.resume_files = sorted(d.glob("*.pdf")) if d.exists() else []

    def _check_api(self):
        try:
            from dotenv import load_dotenv
            load_dotenv(".env.local", override=True)
            k = os.getenv("GROQ_API_KEY", "")
            return bool(k and k != "your-groq-api-key")
        except Exception:
            return False

    def _score_color(self, s, mx=10):
        p = s / mx if mx else 0
        if p >= 0.8: return C.GREEN
        if p >= 0.6: return C.YELLOW
        if p >= 0.4: return C.ORANGE
        return C.RED

    # ═══════════════════════════════════════════════════════════════════════
    #  DASHBOARD
    # ═══════════════════════════════════════════════════════════════════════

    def _pg_dashboard(self):
        self._refresh_resumes()
        sc = self._scroll_frame(self.page_frame)
        pad = tk.Frame(sc, bg=C.BG)
        pad.pack(fill="both", expand=True, padx=28, pady=(14, 20))

        # ── Hero ──
        hero_border = tk.Frame(pad, bg=C.ACCENT)
        hero_border.pack(fill="x", pady=(0, 22))
        hero = tk.Frame(hero_border, bg=C.ACCENT_D)
        hero.pack(fill="both", expand=True, padx=2, pady=2)
        hi = tk.Frame(hero, bg=C.ACCENT_D, padx=36, pady=28)
        hi.pack(fill="x")

        tk.Label(hi, text="Welcome to ShortlistIQ", font=F_HERO,
                 bg=C.ACCENT_D, fg="#fff").pack(anchor="w")
        tk.Label(hi, text=("Intelligent, bias-free resume screening powered by Groq Cloud & LLMs.\n"
                           "Upload resumes  →  Set job requirements  →  Get AI-ranked shortlists instantly."),
                 font=F_BODY, bg=C.ACCENT_D, fg=C.ACCENT_L, justify="left",
                 wraplength=720).pack(anchor="w", pady=(8, 18))

        hb = tk.Frame(hi, bg=C.ACCENT_D)
        hb.pack(anchor="w")
        self._btn(hb, "  ⚡  Start Evaluation  ", lambda: self.show_page("evaluate")).pack(side="left", padx=(0, 10))
        self._ghost_btn(hb, "  ◫  Manage Resumes  ", lambda: self.show_page("resumes")).pack(side="left", padx=(0, 10))
        self._ghost_btn(hb, "  ≡  Edit Job Description  ", lambda: self.show_page("jobdesc")).pack(side="left")

        # ── Stats Row ──
        sr = tk.Frame(pad, bg=C.BG)
        sr.pack(fill="x", pady=(0, 22))
        sr.columnconfigure((0, 1, 2, 3), weight=1, uniform="s")

        api_ok = self._check_api()
        jd_ok = Path("job_description.md").exists()
        has_res = bool(self.candidates_data)

        self._metric_card(sr, "RESUMES LOADED", str(len(self.resume_files)),
                          C.TEAL, f"{len(self.resume_files)} PDF files", C.TEAL
                          ).grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self._metric_card(sr, "JOB DESCRIPTION", "Loaded" if jd_ok else "Missing",
                          C.GREEN if jd_ok else C.RED, "job_description.md",
                          C.GREEN if jd_ok else C.RED
                          ).grid(row=0, column=1, sticky="nsew", padx=6)
        self._metric_card(sr, "GROQ API", "Connected" if api_ok else "Not Set",
                          C.GREEN if api_ok else C.RED, "LPU Inference Engine",
                          C.GREEN if api_ok else C.RED
                          ).grid(row=0, column=2, sticky="nsew", padx=6)
        self._metric_card(sr, "LAST RUN", f"{len(self.candidates_data)} evaluated" if has_res else "—",
                          C.ACCENT_L if has_res else C.TEXT3, "Click Results to view",
                          C.ACCENT if has_res else C.BORDER
                          ).grid(row=0, column=3, sticky="nsew", padx=(6, 0))

        # ── Pipeline Visualization ──
        tk.Label(pad, text="Evaluation Pipeline", font=F_H1,
                 bg=C.BG, fg=C.TEXT).pack(anchor="w", pady=(4, 14))

        pipe_fr = tk.Frame(pad, bg=C.BG)
        pipe_fr.pack(fill="x")
        pipe_fr.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="pipe")

        steps = [
            ("01", "Upload", "Add PDF resumes\nto resumes/ folder", C.TEAL, "◫"),
            ("02", "Configure", "Set job description\n& evaluation criteria", C.ACCENT, "≡"),
            ("03", "Tokenize", "Extract text via\nPyMuPDF engine", C.BLUE, "⚙"),
            ("04", "Inference", "Groq LPU dispatches\nto Qwen 3.8-27B", C.ORANGE, "⚡"),
            ("05", "Rank", "Multi-dimensional\nscoring & shortlist", C.GREEN, "◈"),
        ]

        for i, (num, title, desc, color, icon) in enumerate(steps):
            outer, inner = self._accent_card(pipe_fr, accent_color=color)
            inner.configure(padx=14, pady=14)

            # Top row: number + icon
            top = tk.Frame(inner, bg=C.CARD)
            top.pack(fill="x")
            tk.Label(top, text=num, font=F_XS, bg=color, fg="#fff",
                     padx=6, pady=1).pack(side="left")
            tk.Label(top, text=icon, font=("Segoe UI", 16), bg=C.CARD,
                     fg=color).pack(side="right")

            tk.Label(inner, text=title, font=F_H3, bg=C.CARD, fg=C.TEXT,
                     wraplength=160).pack(anchor="w", pady=(8, 2))
            tk.Label(inner, text=desc, font=F_XS, bg=C.CARD, fg=C.TEXT3,
                     wraplength=160, justify="left").pack(anchor="w")

            px = (0, 4) if i == 0 else (4, 0) if i == 4 else (4, 4)
            outer.grid(row=0, column=i, sticky="nsew", padx=px, pady=2)

        # ── Recent Activity ──
        tk.Label(pad, text="Quick Info", font=F_H1,
                 bg=C.BG, fg=C.TEXT).pack(anchor="w", pady=(22, 10))

        info_outer, info_inner = self._card(pad)
        info_outer.pack(fill="x")
        info_inner.configure(padx=20, pady=16)

        infos = [
            ("Model", "qwen/qwen3.8-27b via Groq Cloud LPU", C.ACCENT_L),
            ("Scoring", "5 dimensions × 10 points = 50 max score", C.TEAL),
            ("Output", "Structured JSON with Pydantic v2 validation", C.GREEN),
            ("Ranking", "Timsort O(N log N) with tier recommendations", C.YELLOW),
        ]
        for label, val, color in infos:
            row = tk.Frame(info_inner, bg=C.CARD)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"  ●  {label}:", font=F_BODY_B,
                     bg=C.CARD, fg=color, width=12, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=F_BODY, bg=C.CARD, fg=C.TEXT2).pack(side="left")

    # ═══════════════════════════════════════════════════════════════════════
    #  RESUMES
    # ═══════════════════════════════════════════════════════════════════════

    def _pg_resumes(self):
        self._refresh_resumes()
        pad = tk.Frame(self.page_frame, bg=C.BG, padx=28, pady=14)
        pad.pack(fill="both", expand=True)

        # Top bar
        top = tk.Frame(pad, bg=C.BG)
        top.pack(fill="x", pady=(0, 14))

        # Left: info
        tk.Label(top, text=f"{len(self.resume_files)} resume(s) in resumes/ directory",
                 font=F_BODY, bg=C.BG, fg=C.TEXT2).pack(side="left")

        # Right: buttons
        br = tk.Frame(top, bg=C.BG)
        br.pack(side="right")
        self._btn(br, "  + Add PDFs  ", self._add_resumes).pack(side="left", padx=(0, 8))
        self._btn(br, "  ✕ Remove  ", self._remove_resume, bg=C.RED_D).pack(side="left")

        # Table
        tbl_outer, tbl_inner = self._card(pad)
        tbl_outer.pack(fill="both", expand=True)

        cols = ("icon", "filename", "size", "pages")
        self.res_tree = ttk.Treeview(tbl_inner, columns=cols, show="headings",
                                      style="Dark.Treeview", selectmode="extended")
        self.res_tree.heading("icon", text="")
        self.res_tree.heading("filename", text="Filename", anchor="w")
        self.res_tree.heading("size", text="Size")
        self.res_tree.heading("pages", text="Pages")
        self.res_tree.column("icon", width=36, anchor="center", stretch=False)
        self.res_tree.column("filename", width=460, anchor="w")
        self.res_tree.column("size", width=100, anchor="center")
        self.res_tree.column("pages", width=80, anchor="center")

        sb = ttk.Scrollbar(tbl_inner, orient="vertical", command=self.res_tree.yview)
        self.res_tree.configure(yscrollcommand=sb.set)
        self.res_tree.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        sb.pack(side="right", fill="y", pady=1, padx=(0, 1))

        self._fill_res_tree()
        self.res_tree.bind("<Double-1>", self._preview_resume)

        # Footer
        ft = tk.Frame(pad, bg=C.BG)
        ft.pack(fill="x", pady=(10, 0))
        tk.Label(ft, text="💡", font=F_SM, bg=C.BG, fg=C.YELLOW).pack(side="left")
        tk.Label(ft, text="  Double-click to preview extracted text  ·  Drag & drop PDFs into resumes/ folder",
                 font=F_SM, bg=C.BG, fg=C.TEXT3).pack(side="left")

    def _fill_res_tree(self):
        if not hasattr(self, 'res_tree'):
            return
        for c in self.res_tree.get_children():
            self.res_tree.delete(c)
        for f in self.resume_files:
            sz = f.stat().st_size / 1024
            sz_s = f"{sz:.0f} KB" if sz < 1024 else f"{sz/1024:.1f} MB"
            try:
                import pymupdf
                doc = pymupdf.open(str(f))
                pg = len(doc)
                doc.close()
            except Exception:
                pg = "—"
            self.res_tree.insert("", "end", iid=str(f),
                                  values=("📄", f.name, sz_s, pg))

    def _add_resumes(self):
        files = filedialog.askopenfilenames(title="Select Resume PDFs",
                                             filetypes=[("PDF", "*.pdf")])
        if not files:
            return
        Path("resumes").mkdir(exist_ok=True)
        n = 0
        for f in files:
            dst = Path("resumes") / Path(f).name
            if not dst.exists():
                shutil.copy2(f, dst)
                n += 1
        self._refresh_resumes()
        self._fill_res_tree()
        if n:
            self._toast(f"Added {n} resume(s) ✓")

    def _remove_resume(self):
        sel = self.res_tree.selection()
        if not sel:
            return self._toast("Select resume(s) first", C.YELLOW)
        if not messagebox.askyesno("Confirm", f"Delete {len(sel)} file(s)?"):
            return
        for s in sel:
            try: Path(s).unlink()
            except Exception: pass
        self._refresh_resumes()
        self._fill_res_tree()
        self._toast(f"Removed {len(sel)} file(s)")

    def _preview_resume(self, event):
        sel = self.res_tree.selection()
        if not sel: return
        p = Path(sel[0])
        try:
            from utils import extract_text_from_pdf
            text = extract_text_from_pdf(str(p))
        except Exception as e:
            text = f"Error: {e}"

        win = tk.Toplevel(self.root)
        win.title(f"Preview — {p.name}")
        win.geometry("750x580")
        win.configure(bg=C.BG)

        tk.Label(win, text=f"📄  {p.name}", font=F_H1, bg=C.BG, fg=C.TEXT
                 ).pack(padx=20, pady=(16, 8), anchor="w")

        txt = tk.Text(win, bg=C.CARD, fg=C.TEXT, font=F_CODE,
                      insertbackground=C.TEXT, relief="flat", bd=0,
                      wrap="word", padx=16, pady=12)
        txt.insert("1.0", text)
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # ═══════════════════════════════════════════════════════════════════════
    #  JOB DESCRIPTION
    # ═══════════════════════════════════════════════════════════════════════

    def _pg_jobdesc(self):
        pad = tk.Frame(self.page_frame, bg=C.BG, padx=28, pady=14)
        pad.pack(fill="both", expand=True)

        top = tk.Frame(pad, bg=C.BG)
        top.pack(fill="x", pady=(0, 12))
        tk.Label(top, text="Edit target role description, requirements, and qualifications.",
                 font=F_BODY, bg=C.BG, fg=C.TEXT2).pack(side="left")
        br = tk.Frame(top, bg=C.BG)
        br.pack(side="right")
        self._ghost_btn(br, "  ↑ Load File  ", self._load_jd).pack(side="left", padx=(0, 8))
        self._btn(br, "  ✓ Save  ", self._save_jd, bg=C.GREEN).pack(side="left")

        # Editor
        eo, ei = self._card(pad)
        eo.pack(fill="both", expand=True)

        self.jd_txt = tk.Text(ei, bg=C.CARD, fg=C.TEXT, font=F_BODY,
                               insertbackground=C.TEXT, relief="flat", bd=0,
                               wrap="word", padx=20, pady=16, undo=True,
                               selectbackground=C.ACCENT, selectforeground="#fff")
        self.jd_txt.pack(fill="both", expand=True, padx=1, pady=1)

        jd = Path("job_description.md")
        if jd.exists():
            self.jd_txt.insert("1.0", jd.read_text(encoding="utf-8"))
        elif hasattr(sys, "_MEIPASS") and (Path(sys._MEIPASS) / "job_description.md").exists():
            self.jd_txt.insert("1.0", (Path(sys._MEIPASS) / "job_description.md").read_text(encoding="utf-8"))

        # Footer stats
        self.jd_stats = tk.Label(pad, text="", font=F_SM, bg=C.BG, fg=C.TEXT3)
        self.jd_stats.pack(anchor="w", pady=(8, 0))
        self._jd_count()
        self.jd_txt.bind("<KeyRelease>", lambda e: self._jd_count())

    def _jd_count(self):
        if not hasattr(self, 'jd_txt'): return
        t = self.jd_txt.get("1.0", "end-1c")
        w = len(t.split())
        lines = t.count("\n") + 1
        self.jd_stats.configure(text=f"{w} words  ·  {lines} lines  ·  {len(t)} chars  ·  job_description.md")

    def _load_jd(self):
        p = filedialog.askopenfilename(filetypes=[("Text", "*.md *.txt")])
        if p:
            self.jd_txt.delete("1.0", "end")
            self.jd_txt.insert("1.0", Path(p).read_text(encoding="utf-8"))
            self._jd_count()
            self._toast("File loaded ✓")

    def _save_jd(self):
        Path("job_description.md").write_text(
            self.jd_txt.get("1.0", "end-1c"), encoding="utf-8")
        self._toast("Saved to job_description.md ✓")

    # ═══════════════════════════════════════════════════════════════════════
    #  EVALUATE
    # ═══════════════════════════════════════════════════════════════════════

    def _pg_evaluate(self):
        self._refresh_resumes()
        sc = self._scroll_frame(self.page_frame)
        pad = tk.Frame(sc, bg=C.BG, padx=28, pady=14)
        pad.pack(fill="both", expand=True)

        # ── Preflight ──
        tk.Label(pad, text="Pre-flight Checklist", font=F_H1,
                 bg=C.BG, fg=C.TEXT).pack(anchor="w", pady=(0, 12))

        api_ok = self._check_api()
        jd_ok = Path("job_description.md").exists() or (hasattr(sys, "_MEIPASS") and (Path(sys._MEIPASS) / "job_description.md").exists())
        res_ok = len(self.resume_files) > 0
        gp_ok = Path("guidance_prompt.md").exists() or (hasattr(sys, "_MEIPASS") and (Path(sys._MEIPASS) / "guidance_prompt.md").exists())

        checks = [
            (api_ok, "Groq API Key", "GROQ_API_KEY in .env.local or env", "resumes"),
            (res_ok, f"Resumes ({len(self.resume_files)} files)", "PDF files detected in resumes/", "resumes"),
            (jd_ok, "Job Description", "job_description.md present", "jobdesc"),
            (gp_ok, "Guidance Prompt", "guidance_prompt.md present", None),
        ]

        for ok, title, desc, link in checks:
            co, ci = self._card(pad, border_color=C.GREEN_D if ok else C.RED_D)
            co.pack(fill="x", pady=3)
            ci.configure(padx=16, pady=10)

            dot = PulsingDot(ci, color=C.GREEN if ok else C.RED, size=8)
            dot.pack(side="left", padx=(0, 12))

            tk.Label(ci, text=title, font=F_BODY_B, bg=C.CARD, fg=C.TEXT).pack(side="left")
            tk.Label(ci, text=f"  —  {desc}", font=F_BODY, bg=C.CARD, fg=C.TEXT2).pack(side="left")

            tag = "Ready" if ok else "Missing"
            tag_bg = C.GREEN_D if ok else C.RED_D
            tag_fg = C.GREEN if ok else C.RED
            tk.Label(ci, text=f"  {tag}  ", font=F_XS, bg=tag_bg, fg=tag_fg).pack(side="right")

        all_ok = api_ok and jd_ok and res_ok and gp_ok

        # ── Run Button ──
        run_fr = tk.Frame(pad, bg=C.BG)
        run_fr.pack(fill="x", pady=(16, 12))

        if all_ok and not self.is_evaluating:
            self._btn(run_fr, "     ⚡  Start AI Evaluation     ",
                      self._run_eval, font=F_H1).pack(anchor="w")
        elif self.is_evaluating:
            tk.Label(run_fr, text="  ⏳  Evaluation in progress…  ", font=F_H2,
                     bg=C.YELLOW_D, fg=C.YELLOW, padx=18, pady=10).pack(anchor="w")
        else:
            tk.Label(run_fr, text="  ⚠  Resolve issues above before running  ",
                     font=F_BODY_B, bg=C.RED_D, fg=C.RED, padx=18, pady=10).pack(anchor="w")

        # ── Progress + Log ──
        tk.Label(pad, text="Evaluation Log", font=F_H1,
                 bg=C.BG, fg=C.TEXT).pack(anchor="w", pady=(8, 8))

        self.eval_prog = ttk.Progressbar(pad, mode="indeterminate",
                                          style="Accent.Horizontal.TProgressbar")
        self.eval_prog.pack(fill="x", pady=(0, 8))

        lo, li = self._card(pad)
        lo.pack(fill="both", expand=True)

        self.eval_log = tk.Text(li, bg=C.CARD, fg=C.TEXT2, font=F_CODE,
                                 relief="flat", bd=0, wrap="word",
                                 padx=16, pady=12, height=14, state="disabled",
                                 insertbackground=C.TEXT)
        self.eval_log.pack(fill="both", expand=True, padx=1, pady=1)

        for tag, fg in [("info", C.TEAL), ("ok", C.GREEN), ("err", C.RED),
                        ("warn", C.YELLOW), ("dim", C.TEXT3)]:
            self.eval_log.tag_configure(tag, foreground=fg)

    def _log(self, msg, tag="info"):
        if not hasattr(self, 'eval_log'): return
        ts = datetime.now().strftime("%H:%M:%S")
        self.eval_log.configure(state="normal")
        self.eval_log.insert("end", f"[{ts}]  {msg}\n", tag)
        self.eval_log.see("end")
        self.eval_log.configure(state="disabled")

    def _run_eval(self):
        if self.is_evaluating: return
        self.is_evaluating = True
        self.show_page("evaluate")
        self.eval_prog.start(14)

        def worker():
            try:
                self._log("Initializing ShortlistIQ evaluation pipeline…")
                time.sleep(0.3)
                self._log("Validating environment & API credentials…")
                from utils import (setup_environment, load_text_file,
                                   get_resume_files, prepare_resume_inputs, call_groq_api)
                setup_environment()
                self._log("Environment validated ✓", "ok")

                self._log("Loading guidance_prompt.md & job_description.md…")
                guidance = load_text_file("guidance_prompt.md")
                jd = load_text_file("job_description.md")
                self._log("Templates loaded ✓", "ok")

                self._log("Scanning resumes/ directory…")
                pdfs = get_resume_files("resumes")
                self._log(f"Found {len(pdfs)} PDF(s):", "ok")
                for p in pdfs:
                    self._log(f"   📄  {p.name}", "dim")

                self._log("Extracting text via PyMuPDF…")
                inputs = prepare_resume_inputs(pdfs)
                self._log(f"Tokenized {len(inputs)} resumes ✓", "ok")

                self._log("Dispatching to Groq Cloud  ⚡  qwen/qwen3.8-27b", "warn")
                self._log("Waiting for LPU inference (may take 10–30s)…", "warn")

                result, raw = call_groq_api(guidance, jd, inputs)
                self._log("Inference complete ✓", "ok")

                try:
                    u = raw.usage
                    self._log(f"Tokens — prompt: {u.prompt_tokens}  "
                              f"completion: {u.completion_tokens}  total: {u.total_tokens}", "dim")
                except Exception:
                    pass

                cdata = []
                for c in result.candidates:
                    cdata.append({
                        "name": c.name, "filename": c.filename,
                        "technical_skills": c.technical_skills.score,
                        "technical_skills_r": c.technical_skills.reasoning,
                        "experience": c.experience.score,
                        "experience_r": c.experience.reasoning,
                        "industry_relevance": c.industry_relevance.score,
                        "industry_relevance_r": c.industry_relevance.reasoning,
                        "education": c.education.score,
                        "education_r": c.education.reasoning,
                        "overall_fit": c.overall_fit.score,
                        "overall_fit_r": c.overall_fit.reasoning,
                        "total_score": c.total_score,
                        "strengths": c.key_strengths,
                        "concerns": c.concerns,
                    })

                self.evaluation_result = result
                self.raw_response = raw
                self.candidates_data = cdata
                self._log(f"Processed {len(cdata)} candidate(s) ✓", "ok")
                self._log("Done! Navigate to Results page →", "ok")

                self.root.after(400, self.eval_prog.stop)
                self.is_evaluating = False
                self.root.after(600, lambda: self._toast("Evaluation complete! View Results →"))

            except Exception as e:
                self._log(f"ERROR: {e}", "err")
                self.root.after(100, self.eval_prog.stop)
                self.is_evaluating = False

        threading.Thread(target=worker, daemon=True).start()

    # ═══════════════════════════════════════════════════════════════════════
    #  RESULTS
    # ═══════════════════════════════════════════════════════════════════════

    def _pg_results(self):
        if not self.candidates_data:
            empty = tk.Frame(self.page_frame, bg=C.BG)
            empty.pack(expand=True)
            tk.Label(empty, text="◈", font=("Segoe UI", 56), bg=C.BG, fg=C.TEXT3).pack()
            tk.Label(empty, text="No Results Yet", font=F_H1, bg=C.BG, fg=C.TEXT2).pack(pady=(8, 4))
            tk.Label(empty, text="Run an evaluation first to see candidate rankings.",
                     font=F_BODY, bg=C.BG, fg=C.TEXT3).pack()
            self._btn(empty, "  ⚡ Go to Evaluate  ",
                      lambda: self.show_page("evaluate")).pack(pady=20)
            return

        sc = self._scroll_frame(self.page_frame)
        pad = tk.Frame(sc, bg=C.BG, padx=28, pady=14)
        pad.pack(fill="both", expand=True)

        cands = sorted(self.candidates_data, key=lambda x: x["total_score"], reverse=True)
        n = len(cands)
        avg = sum(c["total_score"] for c in cands) / n
        top = cands[0]
        strong = sum(1 for c in cands if c["total_score"] >= 35)

        # ── Metrics + Gauges Row ──
        mr = tk.Frame(pad, bg=C.BG)
        mr.pack(fill="x", pady=(0, 18))
        mr.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="mr")

        self._metric_card(mr, "CANDIDATES", str(n), C.TEAL, accent=C.TEAL
                          ).grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self._metric_card(mr, "AVG SCORE", f"{avg:.1f}/50",
                          self._score_color(avg, 50), accent=self._score_color(avg, 50)
                          ).grid(row=0, column=1, sticky="nsew", padx=5)
        self._metric_card(mr, "🏆 TOP", top["name"], C.GREEN,
                          f"{top['total_score']}/50", C.GREEN
                          ).grid(row=0, column=2, sticky="nsew", padx=5)
        self._metric_card(mr, "STRONG (35+)", str(strong),
                          C.GREEN if strong else C.TEXT3,
                          accent=C.GREEN if strong else C.BORDER
                          ).grid(row=0, column=3, sticky="nsew", padx=5)

        # Top candidate gauge
        go, gi = self._accent_card(mr, C.ACCENT)
        gi.configure(padx=10, pady=8)
        gauge = CircularGauge(gi, size=100, score=top["total_score"],
                              max_score=50, color=C.GREEN, label="TOP SCORE")
        gauge.pack()
        gauge.animate()
        go.grid(row=0, column=4, sticky="nsew", padx=(5, 0))

        # ── Ranking Table ──
        tk.Label(pad, text="Candidate Rankings", font=F_H1,
                 bg=C.BG, fg=C.TEXT).pack(anchor="w", pady=(4, 10))

        to, ti = self._card(pad)
        to.pack(fill="x")

        cols = ("rank", "name", "tech", "exp", "ind", "edu", "fit", "total", "rec")
        tree = ttk.Treeview(ti, columns=cols, show="headings",
                            style="Dark.Treeview", height=min(n, 10))

        hdrs = [("rank", "Rank", 55), ("name", "Candidate", 170),
                ("tech", "Technical", 80), ("exp", "Experience", 80),
                ("ind", "Industry", 80), ("edu", "Education", 80),
                ("fit", "Fit", 70), ("total", "Total", 80), ("rec", "Verdict", 110)]
        for col, text, w in hdrs:
            tree.heading(col, text=text, anchor="center" if col != "name" else "w")
            tree.column(col, width=w, anchor="center" if col != "name" else "w")

        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        for i, c in enumerate(cands, 1):
            rec = "—"
            if self.evaluation_result:
                for rc in self.evaluation_result.final_ranking:
                    if rc.name == c["name"]:
                        rec = rc.recommendation
                        break
            tree.insert("", "end", iid=str(i), values=(
                medals.get(i, f" {i}."), f"  {c['name']}",
                f"{c['technical_skills']}/10", f"{c['experience']}/10",
                f"{c['industry_relevance']}/10", f"{c['education']}/10",
                f"{c['overall_fit']}/10", f"{c['total_score']}/50", rec))

        tree.pack(fill="x", padx=1, pady=1)

        # ── AI Summary ──
        if self.evaluation_result:
            ev = self.evaluation_result
            so, si = self._accent_card(pad, C.ACCENT)
            so.pack(fill="x", pady=(16, 0))
            si.configure(padx=20, pady=14)
            tk.Label(si, text="AI Summary", font=F_H2, bg=C.CARD, fg=C.ACCENT_L).pack(anchor="w")
            for line in [f"Top Recommendation:  {ev.top_recommendation}",
                         f"Ready for Interview:  {', '.join(ev.ready_for_interview)}",
                         f"Total Evaluated:  {ev.total_candidates_evaluated}"]:
                tk.Label(si, text=line, font=F_BODY, bg=C.CARD, fg=C.TEXT2).pack(anchor="w", pady=1)
            if ev.notes:
                tk.Label(si, text=f"Notes:  {ev.notes}", font=F_BODY,
                         bg=C.CARD, fg=C.TEXT3).pack(anchor="w", pady=1)

        # ── Detail Panel (on click) ──
        self._detail_fr = tk.Frame(pad, bg=C.BG)
        self._detail_fr.pack(fill="x", pady=(18, 8))

        tree.bind("<<TreeviewSelect>>",
                  lambda e: self._show_detail(tree, cands))

    def _show_detail(self, tree, cands):
        sel = tree.selection()
        if not sel: return
        c = cands[int(sel[0]) - 1]

        for w in self._detail_fr.winfo_children():
            w.destroy()

        # Header
        hdr = tk.Frame(self._detail_fr, bg=C.BG)
        hdr.pack(fill="x", pady=(0, 12))
        tk.Label(hdr, text=f"Detailed Analysis  —  {c['name']}", font=F_H1,
                 bg=C.BG, fg=C.TEXT).pack(side="left")

        total_color = self._score_color(c["total_score"], 50)
        tk.Label(hdr, text=f"  {c['total_score']}/50  ", font=F_H2,
                 bg=total_color, fg="#fff", padx=10, pady=2).pack(side="right")

        # Two-column layout
        cols = tk.Frame(self._detail_fr, bg=C.BG)
        cols.pack(fill="x")
        cols.columnconfigure(0, weight=3)
        cols.columnconfigure(1, weight=2)

        # ── Left: Score Bars with Reasoning ──
        lo, li = self._card(cols)
        lo.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        li.configure(padx=22, pady=18)

        tk.Label(li, text="Score Breakdown", font=F_H2, bg=C.CARD, fg=C.TEXT
                 ).pack(anchor="w", pady=(0, 16))

        dims = [
            ("Technical Skills", c["technical_skills"], c.get("technical_skills_r", "")),
            ("Experience", c["experience"], c.get("experience_r", "")),
            ("Industry Relevance", c["industry_relevance"], c.get("industry_relevance_r", "")),
            ("Education", c["education"], c.get("education_r", "")),
            ("Overall Fit", c["overall_fit"], c.get("overall_fit_r", "")),
        ]

        for label, score, reason in dims:
            color = self._score_color(score)

            row_top = tk.Frame(li, bg=C.CARD)
            row_top.pack(fill="x", pady=(6, 0))
            tk.Label(row_top, text=label, font=F_BODY, bg=C.CARD, fg=C.TEXT2).pack(side="left")
            tk.Label(row_top, text=f"{score}/10", font=F_BODY_B, bg=C.CARD, fg=color).pack(side="right")

            bar = ScoreBar(li, score=score, max_score=10, color=color, height=6)
            bar.pack(fill="x", pady=(4, 0))
            bar.animate()

            if reason:
                tk.Label(li, text=reason, font=F_XS, bg=C.CARD, fg=C.TEXT3,
                         wraplength=420, justify="left", anchor="w").pack(anchor="w", pady=(3, 2))

        # ── Right Column ──
        right = tk.Frame(cols, bg=C.BG)
        right.grid(row=0, column=1, sticky="nsew")

        # Circular gauge
        go, gi = self._accent_card(right, total_color)
        go.pack(fill="x", pady=(0, 8))
        gi.configure(padx=10, pady=10)
        gauge = CircularGauge(gi, size=120, score=c["total_score"],
                              max_score=50, color=total_color, label="TOTAL")
        gauge.pack(pady=4)
        gauge.animate()

        # Recommendation
        if self.evaluation_result:
            for rc in self.evaluation_result.final_ranking:
                if rc.name == c["name"]:
                    rec_colors = {"Hire": C.GREEN, "Strong Consider": C.TEAL,
                                  "Interview": C.YELLOW, "Pass": C.RED}
                    rc_color = rec_colors.get(rc.recommendation, C.TEXT2)
                    tk.Label(gi, text=rc.recommendation, font=F_H2,
                             bg=C.CARD, fg=rc_color).pack(pady=(4, 0))
                    break

        # Strengths
        so, si = self._accent_card(right, C.GREEN)
        so.pack(fill="x", pady=(0, 8))
        si.configure(padx=16, pady=12)
        tk.Label(si, text="✦  Key Strengths", font=F_H3, bg=C.CARD, fg=C.GREEN).pack(anchor="w", pady=(0, 6))
        for s in c.get("strengths", []):
            tk.Label(si, text=f"  •  {s}", font=F_SM, bg=C.CARD, fg=C.TEXT2,
                     wraplength=280, justify="left", anchor="w").pack(anchor="w", pady=1)

        # Concerns
        co, ci = self._accent_card(right, C.YELLOW)
        co.pack(fill="x")
        ci.configure(padx=16, pady=12)
        tk.Label(ci, text="⚠  Concerns", font=F_H3, bg=C.CARD, fg=C.YELLOW).pack(anchor="w", pady=(0, 6))
        concerns = c.get("concerns", [])
        if concerns:
            for cn in concerns:
                tk.Label(ci, text=f"  •  {cn}", font=F_SM, bg=C.CARD, fg=C.TEXT2,
                         wraplength=280, justify="left", anchor="w").pack(anchor="w", pady=1)
        else:
            tk.Label(ci, text="  No significant concerns.", font=F_SM,
                     bg=C.CARD, fg=C.TEXT3).pack(anchor="w")

    # ═══════════════════════════════════════════════════════════════════════
    #  ABOUT
    # ═══════════════════════════════════════════════════════════════════════

    def _pg_about(self):
        sc = self._scroll_frame(self.page_frame)
        pad = tk.Frame(sc, bg=C.BG, padx=28, pady=14)
        pad.pack(fill="both", expand=True)

        # Project header
        po, pi = self._accent_card(pad, C.ACCENT)
        po.pack(fill="x", pady=(0, 20))
        pi.configure(padx=30, pady=24)
        tk.Label(pi, text="ShortlistIQ", font=F_HERO, bg=C.CARD, fg=C.ACCENT_L).pack(anchor="w")
        tk.Label(pi, text="Automated Resume Screening & Candidate Shortlisting System", font=F_BODY,
                 bg=C.CARD, fg=C.TEXT2).pack(anchor="w", pady=(4, 14))
        tk.Label(pi, text=("ShortlistIQ automates candidate evaluation by semantically parsing resumes "
                           "against specific job descriptions using LLMs. It produces objective scores "
                           "across 5 dimensions, detailed reasoning, and ranked shortlists — eliminating "
                           "recruiter bias and manual screening fatigue."),
                 font=F_BODY, bg=C.CARD, fg=C.TEXT, wraplength=780, justify="left").pack(anchor="w")

        # Tech stack
        tk.Label(pad, text="Technology Stack", font=F_H1,
                 bg=C.BG, fg=C.TEXT).pack(anchor="w", pady=(4, 12))

        tg = tk.Frame(pad, bg=C.BG)
        tg.pack(fill="x", pady=(0, 16))
        tg.columnconfigure((0, 1, 2), weight=1, uniform="t")

        techs = [
            ("LLM Inference", "Groq Cloud LPU\nqwen/qwen3.8-27b", C.ACCENT),
            ("PDF Processing", "PyMuPDF\nText extraction engine", C.TEAL),
            ("Data Validation", "Pydantic v2\nType-safe JSON schemas", C.GREEN),
            ("Desktop GUI", "Tkinter\nCustom dark theme", C.BLUE),
            ("Terminal UI", "Rich Library\nFormatted CLI output", C.ORANGE),
            ("Env & Deps", "python-dotenv + UV\nModern tooling", C.YELLOW),
        ]
        for i, (t, d, color) in enumerate(techs):
            o, inn = self._accent_card(tg, color)
            inn.configure(padx=16, pady=14)
            tk.Label(inn, text=t, font=F_BODY_B, bg=C.CARD, fg=C.TEXT).pack(anchor="w")
            tk.Label(inn, text=d, font=F_SM, bg=C.CARD, fg=C.TEXT2, justify="left").pack(anchor="w", pady=(4, 0))
            o.grid(row=i // 3, column=i % 3, sticky="nsew",
                   padx=(0 if i % 3 == 0 else 4, 0 if i % 3 == 2 else 4), pady=3)

        # Evaluation dimensions
        tk.Label(pad, text="Evaluation Dimensions", font=F_H1,
                 bg=C.BG, fg=C.TEXT).pack(anchor="w", pady=(8, 12))

        dims = [
            ("Technical Skills (1–10)", "Languages, frameworks, system design, AI/ML proficiency alignment.", C.TEAL),
            ("Experience (1–10)", "Hands-on engineering depth, tenure, and measurable project impact.", C.ACCENT),
            ("Industry Relevance (1–10)", "Domain expertise, enterprise scale, cloud/ML infrastructure.", C.BLUE),
            ("Education (1–10)", "Degree level, CS specialization, certifications.", C.GREEN),
            ("Overall Fit (1–10)", "Soft skills, collaborative leadership, and cultural alignment.", C.ORANGE),
        ]
        for title, desc, color in dims:
            do, di = self._card(pad)
            do.pack(fill="x", pady=2)
            di.configure(padx=16, pady=10)
            tk.Label(di, text="●", font=F_SM, bg=C.CARD, fg=color).pack(side="left", padx=(0, 10))
            tk.Label(di, text=title, font=F_BODY_B, bg=C.CARD, fg=color, width=26, anchor="w").pack(side="left")
            tk.Label(di, text=desc, font=F_BODY, bg=C.CARD, fg=C.TEXT2).pack(side="left")

        tk.Label(pad, text="Built with ♥ by Divyanshu Soni  ·  MIT License  ·  2026",
                 font=F_SM, bg=C.BG, fg=C.TEXT3).pack(pady=(24, 8))


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    root = tk.Tk()
    root.update_idletasks()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    w, h = 1400, 860
    root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    ShortlistIQApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
