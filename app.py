import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import os
import sys

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class CustomerTableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Table Generator")
        self.root.geometry("1000x700")
        self.root.minsize(800, 550)

        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Header.TLabel", font=("Helvetica", 13, "bold"), foreground="#2c3e50")
        style.configure("Action.TButton", font=("Helvetica", 10), padding=6)
        style.configure("Primary.TButton", font=("Helvetica", 10, "bold"), padding=6)

    def _build_ui(self):
        # Top toolbar
        toolbar = ttk.Frame(self.root, padding=8)
        toolbar.pack(fill="x", side="top")

        ttk.Label(toolbar, text="Customer Table Generator", style="Header.TLabel").pack(side="left")
        ttk.Button(toolbar, text="Export PDF", style="Primary.TButton", command=self._export_pdf).pack(side="right", padx=4)
        ttk.Button(toolbar, text="Preview", style="Action.TButton", command=self._preview).pack(side="right", padx=4)

        ttk.Separator(self.root, orient="horizontal").pack(fill="x")

        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        # Left panel: document settings
        left = ttk.LabelFrame(main, text="Document Settings", padding=10)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.pack_propagate(False)
        left.configure(width=260)

        ttk.Label(left, text="Headline:").pack(anchor="w")
        self.headline_var = tk.StringVar(value="Customer Invoice")
        ttk.Entry(left, textvariable=self.headline_var, width=28).pack(fill="x", pady=(0, 8))

        ttk.Label(left, text="Subtitle:").pack(anchor="w")
        self.subtitle_var = tk.StringVar(value="")
        ttk.Entry(left, textvariable=self.subtitle_var, width=28).pack(fill="x", pady=(0, 8))

        ttk.Label(left, text="Footer note:").pack(anchor="w")
        self.footer_var = tk.StringVar(value="Thank you for your business!")
        ttk.Entry(left, textvariable=self.footer_var, width=28).pack(fill="x", pady=(0, 12))

        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=6)
        ttk.Label(left, text="Columns", style="Header.TLabel").pack(anchor="w")

        col_frame = ttk.Frame(left)
        col_frame.pack(fill="x", pady=4)
        self.col_entry = ttk.Entry(col_frame, width=16)
        self.col_entry.insert(0, "Column name")
        self.col_entry.pack(side="left", padx=(0, 4))
        ttk.Button(col_frame, text="Add", command=self._add_column).pack(side="left")

        self.col_listbox = tk.Listbox(left, height=6, selectmode="single", font=("Helvetica", 10))
        self.col_listbox.pack(fill="x", pady=4)

        btn_row = ttk.Frame(left)
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Remove", command=self._remove_column).pack(side="left", padx=(0, 4))
        ttk.Button(btn_row, text="Up", command=lambda: self._move_col(-1)).pack(side="left", padx=(0, 4))
        ttk.Button(btn_row, text="Down", command=lambda: self._move_col(1)).pack(side="left")

        # Default columns
        for col in ["Item", "Description", "Qty", "Unit Price", "Total"]:
            self.col_listbox.insert("end", col)

        # Right panel: table data
        right = ttk.LabelFrame(main, text="Table Data", padding=10)
        right.pack(side="left", fill="both", expand=True)

        tree_frame = ttk.Frame(right)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self._on_double_click)

        row_btns = ttk.Frame(right)
        row_btns.pack(fill="x", pady=(8, 0))
        ttk.Button(row_btns, text="Add Row", command=self._add_row).pack(side="left", padx=(0, 4))
        ttk.Button(row_btns, text="Delete Row", command=self._delete_row).pack(side="left", padx=(0, 4))
        ttk.Button(row_btns, text="Clear All", command=self._clear_rows).pack(side="left")

        self._refresh_columns()

    # ── Column management ──────────────────────────────────────────────────

    def _get_columns(self):
        return list(self.col_listbox.get(0, "end"))

    def _add_column(self):
        name = self.col_entry.get().strip()
        if name:
            self.col_listbox.insert("end", name)
            self.col_entry.delete(0, "end")
            self._refresh_columns()

    def _remove_column(self):
        sel = self.col_listbox.curselection()
        if sel:
            self.col_listbox.delete(sel[0])
            self._refresh_columns()

    def _move_col(self, direction):
        sel = self.col_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        new_idx = idx + direction
        cols = self._get_columns()
        if 0 <= new_idx < len(cols):
            cols[idx], cols[new_idx] = cols[new_idx], cols[idx]
            self.col_listbox.delete(0, "end")
            for c in cols:
                self.col_listbox.insert("end", c)
            self.col_listbox.select_set(new_idx)
            self._refresh_columns()

    def _refresh_columns(self):
        cols = self._get_columns()
        # Save existing data
        existing = []
        old_cols = list(self.tree["columns"]) if self.tree["columns"] else []
        for iid in self.tree.get_children():
            vals = self.tree.item(iid, "values")
            row = {old_cols[i]: v for i, v in enumerate(vals)}
            existing.append(row)

        self.tree["columns"] = cols
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=max(80, 140 // max(1, len(cols)) * 2), anchor="center")

        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for row in existing:
            vals = tuple(row.get(c, "") for c in cols)
            self.tree.insert("", "end", values=vals)

    # ── Row management ─────────────────────────────────────────────────────

    def _add_row(self):
        cols = self._get_columns()
        if not cols:
            messagebox.showwarning("No Columns", "Add at least one column first.")
            return
        RowDialog(self.root, cols, on_save=lambda vals: self.tree.insert("", "end", values=vals))

    def _delete_row(self):
        sel = self.tree.selection()
        if sel:
            self.tree.delete(sel[0])

    def _clear_rows(self):
        if messagebox.askyesno("Clear", "Remove all rows?"):
            for iid in self.tree.get_children():
                self.tree.delete(iid)

    def _on_double_click(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        cols = self._get_columns()
        current_vals = list(self.tree.item(iid, "values"))

        def save(vals):
            self.tree.item(iid, values=vals)

        RowDialog(self.root, cols, initial=current_vals, on_save=save)

    # ── Preview ────────────────────────────────────────────────────────────

    def _preview(self):
        cols = self._get_columns()
        rows = [list(self.tree.item(iid, "values")) for iid in self.tree.get_children()]
        PreviewWindow(self.root, self.headline_var.get(), self.subtitle_var.get(),
                      self.footer_var.get(), cols, rows)

    # ── PDF export ─────────────────────────────────────────────────────────

    def _export_pdf(self):
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Missing library",
                                 "reportlab is not installed.\nRun: pip install reportlab")
            return
        cols = self._get_columns()
        if not cols:
            messagebox.showwarning("No columns", "Add at least one column.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF",
            initialfile=f"{self.headline_var.get() or 'document'}.pdf"
        )
        if not path:
            return

        rows = [list(self.tree.item(iid, "values")) for iid in self.tree.get_children()]
        try:
            _generate_pdf(path, self.headline_var.get(), self.subtitle_var.get(),
                          self.footer_var.get(), cols, rows)
            messagebox.showinfo("Saved", f"PDF saved to:\n{path}")
            _open_file(path)
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ── Row edit dialog ────────────────────────────────────────────────────────────

class RowDialog(tk.Toplevel):
    def __init__(self, parent, cols, initial=None, on_save=None):
        super().__init__(parent)
        self.title("Edit Row")
        self.grab_set()
        self.resizable(False, False)
        self.on_save = on_save

        self.entries = []
        for i, col in enumerate(cols):
            ttk.Label(self, text=col + ":").grid(row=i, column=0, sticky="w", padx=10, pady=4)
            e = ttk.Entry(self, width=30)
            if initial and i < len(initial):
                e.insert(0, initial[i])
            e.grid(row=i, column=1, padx=10, pady=4)
            self.entries.append(e)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=len(cols), column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=4)

        self.entries[0].focus_set() if self.entries else None
        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())

    def _save(self):
        vals = tuple(e.get() for e in self.entries)
        if self.on_save:
            self.on_save(vals)
        self.destroy()


# ── Preview window ─────────────────────────────────────────────────────────────

class PreviewWindow(tk.Toplevel):
    def __init__(self, parent, headline, subtitle, footer, cols, rows):
        super().__init__(parent)
        self.title("Preview")
        self.geometry("700x500")

        text = tk.Text(self, font=("Courier", 10), bg="#fafafa", relief="flat", padx=10, pady=10)
        sb = ttk.Scrollbar(self, command=text.yview)
        text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        text.pack(fill="both", expand=True)

        lines = []
        if headline:
            lines.append(headline.center(72))
            lines.append("=" * 72)
        if subtitle:
            lines.append(subtitle.center(72))
            lines.append("")

        if cols:
            col_w = max(12, 70 // len(cols))
            header = " | ".join(c[:col_w].ljust(col_w) for c in cols)
            lines.append(header)
            lines.append("-" * len(header))
            for row in rows:
                line = " | ".join((str(v)[:col_w]).ljust(col_w) for v in (list(row) + [""] * len(cols))[:len(cols)])
                lines.append(line)

        lines.append("")
        if footer:
            lines.append("-" * 72)
            lines.append(footer.center(72))

        text.insert("1.0", "\n".join(lines))
        text.config(state="disabled")


# ── PDF generation ─────────────────────────────────────────────────────────────

def _generate_pdf(path, headline, subtitle, footer, cols, rows):
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("title", parent=styles["Title"],
                                 fontSize=20, spaceAfter=4,
                                 textColor=colors.HexColor("#2c3e50"))
    sub_style = ParagraphStyle("sub", parent=styles["Normal"],
                               fontSize=11, spaceAfter=12,
                               textColor=colors.HexColor("#7f8c8d"), alignment=TA_CENTER)
    footer_style = ParagraphStyle("footer", parent=styles["Normal"],
                                  fontSize=9, alignment=TA_CENTER,
                                  textColor=colors.HexColor("#95a5a6"))

    if headline:
        story.append(Paragraph(headline, title_style))
    if subtitle:
        story.append(Paragraph(subtitle, sub_style))
    story.append(Spacer(1, 6*mm))

    table_data = [cols] + [list(r) for r in rows]
    usable_w = A4[0] - 40*mm
    col_w = usable_w / max(1, len(cols))

    t = Table(table_data, colWidths=[col_w] * len(cols), repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 10),
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#ecf0f1")]),
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",   (0, 1), (-1, -1), 9),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

    if footer:
        story.append(Spacer(1, 10*mm))
        story.append(Paragraph(footer, footer_style))

    doc.build(story)


def _open_file(path):
    import subprocess
    if sys.platform == "darwin":
        subprocess.Popen(["open", path])
    elif sys.platform == "win32":
        os.startfile(path)
    else:
        subprocess.Popen(["xdg-open", path])


if __name__ == "__main__":
    root = tk.Tk()
    app = CustomerTableApp(root)
    root.mainloop()
