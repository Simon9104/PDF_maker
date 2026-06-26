import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os, sys
from datetime import date

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                    Paragraph, Spacer, HRFlowable)
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

C_ACCENT   = colors.HexColor("#1a5fa8")
C_DARK     = colors.HexColor("#1c2b3a")
C_LIGHT_BG = colors.HexColor("#f0f4f8")
C_TOTAL_BG = colors.HexColor("#1a5fa8")
C_BORDER   = colors.HexColor("#c8d6e5")


class CustomerTableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice / Document Generator")
        self.root.geometry("1100x780")
        self.root.minsize(900, 600)
        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except Exception:
            pass
        s.configure("H.TLabel",  font=("Helvetica", 12, "bold"), foreground="#1a5fa8")
        s.configure("Sec.TLabel", font=("Helvetica", 10, "bold"), foreground="#1c2b3a")
        s.configure("Primary.TButton", font=("Helvetica", 10, "bold"), padding=7)
        s.configure("Action.TButton",  font=("Helvetica", 10), padding=6)

    def _build_ui(self):
        bar = ttk.Frame(self.root, padding=(10, 6))
        bar.pack(fill="x")
        ttk.Label(bar, text="Invoice / Document Generator", style="H.TLabel").pack(side="left")
        ttk.Button(bar, text="Export PDF", style="Primary.TButton",
                   command=self._export_pdf).pack(side="right", padx=4)
        ttk.Button(bar, text="Preview", style="Action.TButton",
                   command=self._preview).pack(side="right", padx=4)
        ttk.Separator(self.root).pack(fill="x")

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        self._tab_supplier(nb)
        self._tab_customer(nb)
        self._tab_meta(nb)
        self._tab_items(nb)
        self._tab_totals(nb)

    def _field(self, parent, label, var, row, col=0, width=30, colspan=1):
        ttk.Label(parent, text=label).grid(row=row, column=col*2,
                                            sticky="w", padx=6, pady=3)
        e = ttk.Entry(parent, textvariable=var, width=width)
        e.grid(row=row, column=col*2+1, sticky="ew", padx=6, pady=3,
               columnspan=colspan)
        return e

    def _tab_supplier(self, nb):
        f = ttk.Frame(nb, padding=16)
        nb.add(f, text="  Supplier  ")
        f.columnconfigure(1, weight=1)
        f.columnconfigure(3, weight=1)

        ttk.Label(f, text="Supplier / Your Company", style="Sec.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        self.sup_name    = tk.StringVar(value="Your Company s.r.o.")
        self.sup_street  = tk.StringVar(value="Main Street 1")
        self.sup_city    = tk.StringVar(value="10000 City")
        self.sup_country = tk.StringVar(value="")
        self.sup_ico     = tk.StringVar()
        self.sup_dic     = tk.StringVar()
        self.sup_icdph   = tk.StringVar()
        self.sup_iban    = tk.StringVar()
        self.sup_swift   = tk.StringVar()
        self.sup_bank    = tk.StringVar()
        self.sup_phone   = tk.StringVar()
        self.sup_email   = tk.StringVar()
        self.sup_web     = tk.StringVar()

        self._field(f, "Company name",    self.sup_name,    1)
        self._field(f, "Street",          self.sup_street,  2)
        self._field(f, "City / ZIP",      self.sup_city,    3)
        self._field(f, "Country",         self.sup_country, 4)
        ttk.Separator(f, orient="horizontal").grid(row=5, column=0, columnspan=4, sticky="ew", pady=8)
        self._field(f, "ID / ICO",        self.sup_ico,     6)
        self._field(f, "Tax ID / DIC",    self.sup_dic,     7)
        self._field(f, "VAT ID / IC DPH", self.sup_icdph,   8)
        ttk.Separator(f, orient="horizontal").grid(row=9, column=0, columnspan=4, sticky="ew", pady=8)
        self._field(f, "IBAN",            self.sup_iban,   10, width=40)
        self._field(f, "SWIFT / BIC",     self.sup_swift,  11)
        self._field(f, "Bank",            self.sup_bank,   12)
        ttk.Separator(f, orient="horizontal").grid(row=13, column=0, columnspan=4, sticky="ew", pady=8)
        self._field(f, "Phone",           self.sup_phone,  14)
        self._field(f, "E-mail",          self.sup_email,  15)
        self._field(f, "Website",         self.sup_web,    16)

    def _tab_customer(self, nb):
        f = ttk.Frame(nb, padding=16)
        nb.add(f, text="  Customer  ")
        f.columnconfigure(1, weight=1)

        ttk.Label(f, text="Customer / Recipient", style="Sec.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        self.cus_name    = tk.StringVar(value="Customer Company Ltd.")
        self.cus_street  = tk.StringVar()
        self.cus_city    = tk.StringVar()
        self.cus_country = tk.StringVar()
        self.cus_ico     = tk.StringVar()
        self.cus_dic     = tk.StringVar()

        self._field(f, "Company / Name", self.cus_name,    1)
        self._field(f, "Street",         self.cus_street,  2)
        self._field(f, "City / ZIP",     self.cus_city,    3)
        self._field(f, "Country",        self.cus_country, 4)
        ttk.Separator(f, orient="horizontal").grid(row=5, column=0, columnspan=2, sticky="ew", pady=8)
        self._field(f, "ID / ICO",       self.cus_ico,     6)
        self._field(f, "Tax ID / DIC",   self.cus_dic,     7)

    def _tab_meta(self, nb):
        f = ttk.Frame(nb, padding=16)
        nb.add(f, text="  Document  ")
        f.columnconfigure(1, weight=1)

        ttk.Label(f, text="Document Details", style="Sec.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        today = date.today().strftime("%d.%m.%Y")
        self.doc_title    = tk.StringVar(value="INVOICE")
        self.doc_number   = tk.StringVar(value="2024001")
        self.doc_issue    = tk.StringVar(value=today)
        self.doc_due      = tk.StringVar(value="")
        self.doc_var_sym  = tk.StringVar(value="2024001")
        self.doc_payment  = tk.StringVar(value="Bank transfer")
        self.doc_currency = tk.StringVar(value="€")

        self._field(f, "Document title",  self.doc_title,    1)
        self._field(f, "Document number", self.doc_number,   2)
        self._field(f, "Issue date",      self.doc_issue,    3)
        self._field(f, "Due date",        self.doc_due,      4)
        self._field(f, "Variable symbol", self.doc_var_sym,  5)
        self._field(f, "Payment method",  self.doc_payment,  6)
        self._field(f, "Currency symbol", self.doc_currency, 7)
        ttk.Separator(f, orient="horizontal").grid(row=8, column=0, columnspan=2, sticky="ew", pady=8)
        ttk.Label(f, text="Note / Description:").grid(row=9, column=0, sticky="nw", padx=6)
        self.note_text = tk.Text(f, height=4, width=50, font=("Helvetica", 10))
        self.note_text.grid(row=9, column=1, sticky="ew", padx=6, pady=3)

    def _tab_items(self, nb):
        f = ttk.Frame(nb, padding=16)
        nb.add(f, text="  Items  ")

        ttk.Label(f, text="Line Items", style="Sec.TLabel").pack(anchor="w", pady=(0, 8))

        col_frame = ttk.Frame(f)
        col_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(col_frame, text="Add column:").pack(side="left")
        self.col_entry = ttk.Entry(col_frame, width=18)
        self.col_entry.pack(side="left", padx=4)
        ttk.Button(col_frame, text="Add", command=self._add_column).pack(side="left")
        ttk.Button(col_frame, text="Remove selected",
                   command=self._remove_column).pack(side="left", padx=8)
        self.col_listbox = tk.Listbox(f, height=3, selectmode="single", font=("Helvetica", 9))
        self.col_listbox.pack(fill="x")

        ttk.Separator(f).pack(fill="x", pady=8)

        tree_frame = ttk.Frame(f)
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

        btns = ttk.Frame(f)
        btns.pack(fill="x", pady=(8, 0))
        ttk.Button(btns, text="Add Row",    command=self._add_row).pack(side="left", padx=(0, 4))
        ttk.Button(btns, text="Delete Row", command=self._delete_row).pack(side="left", padx=(0, 4))
        ttk.Button(btns, text="Clear All",  command=self._clear_rows).pack(side="left")

        for c in ["Description", "Qty", "Unit Price", "Total"]:
            self.col_listbox.insert("end", c)
        self._refresh_columns()

    def _tab_totals(self, nb):
        f = ttk.Frame(nb, padding=16)
        nb.add(f, text="  Totals / Tax  ")
        f.columnconfigure(1, weight=1)

        ttk.Label(f, text="Summary & Tax Settings", style="Sec.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        self.tax_label      = tk.StringVar(value="VAT")
        self.tax_rate       = tk.StringVar(value="10")
        self.tax_enabled    = tk.BooleanVar(value=True)
        self.subtotal_label = tk.StringVar(value="Subtotal")
        self.total_label    = tk.StringVar(value="Total incl. tax")
        self.due_label      = tk.StringVar(value="Amount Due")

        ttk.Checkbutton(f, text="Show tax row", variable=self.tax_enabled).grid(
            row=1, column=0, columnspan=2, sticky="w", padx=6, pady=3)
        self._field(f, "Tax label (e.g. VAT)", self.tax_label,      2)
        self._field(f, "Tax rate %",           self.tax_rate,       3, width=10)
        ttk.Separator(f, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=8)
        self._field(f, "Subtotal label",       self.subtotal_label, 5)
        self._field(f, "Total label",          self.total_label,    6)
        self._field(f, "Amount Due label",     self.due_label,      7)

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

    def _refresh_columns(self):
        cols = self._get_columns()
        old_cols = list(self.tree["columns"]) if self.tree["columns"] else []
        existing = []
        for iid in self.tree.get_children():
            vals = self.tree.item(iid, "values")
            existing.append({old_cols[i]: v for i, v in enumerate(vals)})
        self.tree["columns"] = cols
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=max(80, 500 // max(1, len(cols))), anchor="center")
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for row in existing:
            self.tree.insert("", "end", values=tuple(row.get(c, "") for c in cols))

    def _add_row(self):
        cols = self._get_columns()
        if not cols:
            messagebox.showwarning("No Columns", "Add at least one column first.")
            return
        RowDialog(self.root, cols,
                  on_save=lambda vals: self.tree.insert("", "end", values=vals))

    def _delete_row(self):
        sel = self.tree.selection()
        if sel:
            self.tree.delete(sel[0])

    def _clear_rows(self):
        if messagebox.askyesno("Clear", "Remove all rows?"):
            for iid in self.tree.get_children():
                self.tree.delete(iid)

    def _on_double_click(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        cols = self._get_columns()
        current = list(self.tree.item(iid, "values"))
        RowDialog(self.root, cols, initial=current,
                  on_save=lambda vals: self.tree.item(iid, values=vals))

    def _get_rows(self):
        return [list(self.tree.item(iid, "values")) for iid in self.tree.get_children()]

    def _get_note(self):
        try:
            return self.note_text.get("1.0", "end").strip()
        except Exception:
            return ""

    def _preview(self):
        PreviewWindow(self.root, self._collect())

    def _collect(self):
        return {
            "sup_name":    self.sup_name.get(),
            "sup_street":  self.sup_street.get(),
            "sup_city":    self.sup_city.get(),
            "sup_country": self.sup_country.get(),
            "sup_ico":     self.sup_ico.get(),
            "sup_dic":     self.sup_dic.get(),
            "sup_icdph":   self.sup_icdph.get(),
            "sup_iban":    self.sup_iban.get(),
            "sup_swift":   self.sup_swift.get(),
            "sup_bank":    self.sup_bank.get(),
            "sup_phone":   self.sup_phone.get(),
            "sup_email":   self.sup_email.get(),
            "sup_web":     self.sup_web.get(),
            "cus_name":    self.cus_name.get(),
            "cus_street":  self.cus_street.get(),
            "cus_city":    self.cus_city.get(),
            "cus_country": self.cus_country.get(),
            "cus_ico":     self.cus_ico.get(),
            "cus_dic":     self.cus_dic.get(),
            "doc_title":   self.doc_title.get(),
            "doc_number":  self.doc_number.get(),
            "doc_issue":   self.doc_issue.get(),
            "doc_due":     self.doc_due.get(),
            "doc_var_sym": self.doc_var_sym.get(),
            "doc_payment": self.doc_payment.get(),
            "doc_currency":self.doc_currency.get(),
            "note":        self._get_note(),
            "columns":     self._get_columns(),
            "rows":        self._get_rows(),
            "tax_enabled": self.tax_enabled.get(),
            "tax_label":   self.tax_label.get(),
            "tax_rate":    self.tax_rate.get(),
            "subtotal_label": self.subtotal_label.get(),
            "total_label":    self.total_label.get(),
            "due_label":      self.due_label.get(),
        }

    def _export_pdf(self):
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Missing library",
                                 "reportlab not installed.\nRun: pip install reportlab")
            return
        d = self._collect()
        fname = f"{d['doc_title']} {d['doc_number']}".strip() or "document"
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"{fname}.pdf")
        if not path:
            return
        try:
            generate_pdf(path, d)
            messagebox.showinfo("Saved", f"PDF saved:\n{path}")
            _open_file(path)
        except Exception as e:
            messagebox.showerror("Error", str(e))


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
            e = ttk.Entry(self, width=32)
            if initial and i < len(initial):
                e.insert(0, initial[i])
            e.grid(row=i, column=1, padx=10, pady=4)
            self.entries.append(e)
        bf = ttk.Frame(self)
        bf.grid(row=len(cols), column=0, columnspan=2, pady=10)
        ttk.Button(bf, text="Save",   command=self._save).pack(side="left", padx=4)
        ttk.Button(bf, text="Cancel", command=self.destroy).pack(side="left", padx=4)
        if self.entries:
            self.entries[0].focus_set()
        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())

    def _save(self):
        if self.on_save:
            self.on_save(tuple(e.get() for e in self.entries))
        self.destroy()


class PreviewWindow(tk.Toplevel):
    def __init__(self, parent, d):
        super().__init__(parent)
        self.title("Preview")
        self.geometry("720x560")
        txt = tk.Text(self, font=("Courier", 9), bg="#fafafa", padx=12, pady=10)
        sb  = ttk.Scrollbar(self, command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        txt.pack(fill="both", expand=True)

        W = 78
        lines = []
        lines.append(f"{d['doc_title']} No. {d['doc_number']}".center(W))
        lines.append("=" * W)
        lines.append("")

        sup = [d["sup_name"], d["sup_street"], d["sup_city"]]
        if d["sup_ico"]:   sup.append(f"ID: {d['sup_ico']}")
        if d["sup_dic"]:   sup.append(f"Tax: {d['sup_dic']}")
        if d["sup_icdph"]: sup.append(f"VAT: {d['sup_icdph']}")
        cus = [d["cus_name"], d["cus_street"], d["cus_city"]]
        if d["cus_ico"]:   cus.append(f"ID: {d['cus_ico']}")

        col_w = W // 2 - 2
        lines.append("SUPPLIER".ljust(col_w) + "  CUSTOMER")
        for i in range(max(len(sup), len(cus))):
            l = sup[i] if i < len(sup) else ""
            r = cus[i] if i < len(cus) else ""
            lines.append(l[:col_w].ljust(col_w) + "  " + r[:col_w])
        lines.append("-" * W)

        for k, v in [("Issue date", d["doc_issue"]), ("Due date", d["doc_due"]),
                     ("Var. symbol", d["doc_var_sym"]), ("Payment", d["doc_payment"]),
                     ("IBAN", d["sup_iban"]), ("SWIFT", d["sup_swift"])]:
            if v:
                lines.append(f"{k+':':<18} {v}")
        lines.append("-" * W)

        if d["note"]:
            lines.append(d["note"])
            lines.append("")

        cols = d["columns"]
        if cols:
            cw = max(10, (W - 2) // len(cols))
            lines.append(" | ".join(c[:cw].ljust(cw) for c in cols))
            lines.append("-" * W)
            for row in d["rows"]:
                lines.append(" | ".join(str(v)[:cw].ljust(cw)
                              for v in (list(row) + [""] * len(cols))[:len(cols)]))
        lines.append("=" * W)

        cur = d["doc_currency"]
        try:
            subtotal = sum(float(str(r[-1]).replace(",", ".").replace(cur, "").strip())
                           for r in d["rows"] if r)
        except Exception:
            subtotal = 0.0
        lines.append(f"{d['subtotal_label']:>40}  {cur} {subtotal:,.2f}")
        if d["tax_enabled"]:
            try:
                rate = float(d["tax_rate"])
            except Exception:
                rate = 0
            tax = subtotal * rate / 100
            lines.append(f"{d['tax_label']} ({d['tax_rate']}%):".rjust(40) + f"  {cur} {tax:,.2f}")
            total = subtotal + tax
        else:
            total = subtotal
        lines.append(f"{d['total_label']:>40}  {cur} {total:,.2f}")
        lines.append(f">>> {d['due_label']:>36}  {cur} {total:,.2f} <<<")
        lines.append("-" * W)
        footer = " | ".join(x for x in [d["sup_phone"], d["sup_email"], d["sup_web"]] if x)
        if footer:
            lines.append(footer.center(W))

        txt.insert("1.0", "\n".join(lines))
        txt.config(state="disabled")


def generate_pdf(path, d):
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    story  = []
    W = A4[0] - 36*mm
    cur = d["doc_currency"]

    def ps(name, **kw):
        base = kw.pop("parent", "Normal")
        return ParagraphStyle(name, parent=styles[base], **kw)

    sTitle  = ps("DocTitle", fontSize=26, textColor=C_ACCENT,
                  fontName="Helvetica-Bold", alignment=TA_RIGHT, spaceAfter=0)
    sSupLbl = ps("SupLbl",  fontSize=7,  textColor=C_ACCENT,
                  fontName="Helvetica-Bold", spaceBefore=0, spaceAfter=1)
    sSupVal = ps("SupVal",  fontSize=9,  textColor=C_DARK, fontName="Helvetica-Bold")
    sSmall  = ps("Small",   fontSize=8,  textColor=C_DARK)
    sMeta   = ps("Meta",    fontSize=8.5, textColor=C_DARK, fontName="Helvetica-Bold")
    sMetaV  = ps("MetaV",   fontSize=8.5, textColor=C_DARK)
    sNote   = ps("Note",    fontSize=9,  textColor=C_DARK, spaceBefore=4, spaceAfter=4)
    sFooter = ps("Footer",  fontSize=7.5, textColor=colors.HexColor("#8899aa"),
                  alignment=TA_CENTER)
    sTotLbl = ps("TotLbl",  fontSize=9,  textColor=C_DARK,
                  fontName="Helvetica-Bold", alignment=TA_RIGHT)
    sTotVal = ps("TotVal",  fontSize=9,  textColor=C_DARK, alignment=TA_RIGHT)
    sDueLbl = ps("DueLbl",  fontSize=11, textColor=colors.white,
                  fontName="Helvetica-Bold", alignment=TA_RIGHT)
    sDueVal = ps("DueVal",  fontSize=11, textColor=colors.white,
                  fontName="Helvetica-Bold", alignment=TA_RIGHT)

    story.append(Table(
        [[Paragraph(d["doc_title"], sTitle)]],
        colWidths=[W],
        style=TableStyle([("ALIGN", (0,0), (-1,-1), "RIGHT"),
                          ("BOTTOMPADDING", (0,0), (-1,-1), 2)])
    ))
    story.append(Paragraph(
        f"<font size=9 color='#8899aa'>No. {d['doc_number']}</font>",
        ps("DocNum", alignment=TA_RIGHT, spaceAfter=6)))
    story.append(HRFlowable(width="100%", thickness=2, color=C_ACCENT, spaceAfter=6))

    def sup_lines():
        items = [Paragraph("SUPPLIER", sSupLbl), Paragraph(d["sup_name"], sSupVal)]
        for v in [d["sup_street"], d["sup_city"], d["sup_country"]]:
            if v: items.append(Paragraph(v, sSmall))
        for lbl, val in [("ID", d["sup_ico"]), ("Tax ID", d["sup_dic"]),
                          ("VAT ID", d["sup_icdph"])]:
            if val: items.append(Paragraph(f"{lbl}: {val}", sSmall))
        return items

    def cus_lines():
        items = [Paragraph("CUSTOMER", sSupLbl), Paragraph(d["cus_name"], sSupVal)]
        for v in [d["cus_street"], d["cus_city"], d["cus_country"]]:
            if v: items.append(Paragraph(v, sSmall))
        for lbl, val in [("ID", d["cus_ico"]), ("Tax ID", d["cus_dic"])]:
            if val: items.append(Paragraph(f"{lbl}: {val}", sSmall))
        return items

    story.append(Table(
        [[sup_lines(), cus_lines()]],
        colWidths=[W*0.45, W*0.55],
        style=TableStyle([
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ("BOX",          (0,0), (0,0),   0.5, C_BORDER),
            ("BOX",          (1,0), (1,0),   0.5, C_BORDER),
            ("BACKGROUND",   (0,0), (-1,-1), colors.white),
            ("LEFTPADDING",  (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING",   (0,0), (-1,-1), 8),
            ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ])
    ))
    story.append(Spacer(1, 5*mm))

    meta_pairs = [
        ("Issue date",      d["doc_issue"]),
        ("Variable symbol", d["doc_var_sym"]),
        ("Due date",        d["doc_due"]),
        ("Payment method",  d["doc_payment"]),
        ("IBAN",            d["sup_iban"]),
        ("SWIFT / BIC",     d["sup_swift"]),
        ("Bank",            d["sup_bank"]),
        ("", ""),
    ]
    meta_data = []
    for i in range(0, len(meta_pairs), 2):
        row = []
        for k, v in meta_pairs[i:i+2]:
            row += ([Paragraph(k, sMeta), Paragraph(v or "", sMetaV)] if k
                    else [Paragraph("", sSmall), Paragraph("", sSmall)])
        while len(row) < 4:
            row += [Paragraph("", sSmall), Paragraph("", sSmall)]
        meta_data.append(row)

    story.append(Table(meta_data,
                       colWidths=[W*0.18, W*0.32, W*0.18, W*0.32],
                       style=TableStyle([
                           ("ROWBACKGROUNDS", (0,0), (-1,-1), [C_LIGHT_BG, colors.white]),
                           ("GRID",          (0,0), (-1,-1), 0.3, C_BORDER),
                           ("LEFTPADDING",   (0,0), (-1,-1), 6),
                           ("RIGHTPADDING",  (0,0), (-1,-1), 6),
                           ("TOPPADDING",    (0,0), (-1,-1), 4),
                           ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                       ])))
    story.append(Spacer(1, 5*mm))

    if d["note"]:
        story.append(Paragraph(d["note"], sNote))
        story.append(Spacer(1, 3*mm))

    cols = d["columns"]
    if cols:
        cw = W / len(cols)
        ih = ps("IH", fontSize=9, textColor=colors.white,
                fontName="Helvetica-Bold", alignment=TA_CENTER)
        iv = ps("IV", fontSize=9, textColor=C_DARK, alignment=TA_CENTER)
        items_data = [[Paragraph(c, ih) for c in cols]]
        for row in d["rows"]:
            padded = (list(row) + [""] * len(cols))[:len(cols)]
            items_data.append([Paragraph(str(v), iv) for v in padded])
        story.append(Table(items_data, colWidths=[cw]*len(cols), repeatRows=1,
                           style=TableStyle([
                               ("BACKGROUND",    (0,0), (-1,0),  C_ACCENT),
                               ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, C_LIGHT_BG]),
                               ("GRID",          (0,0), (-1,-1), 0.4, C_BORDER),
                               ("TOPPADDING",    (0,0), (-1,-1), 5),
                               ("BOTTOMPADDING", (0,0), (-1,-1), 5),
                               ("LEFTPADDING",   (0,0), (-1,-1), 6),
                               ("RIGHTPADDING",  (0,0), (-1,-1), 6),
                           ])))
        story.append(Spacer(1, 4*mm))

    try:
        subtotal = sum(float(str(r[-1]).replace(",", ".").replace(cur, "").strip())
                       for r in d["rows"] if r)
    except Exception:
        subtotal = 0.0

    tot_rows = [[Paragraph(d["subtotal_label"], sTotLbl),
                 Paragraph(f"{cur} {subtotal:,.2f}", sTotVal)]]
    if d["tax_enabled"]:
        try:
            rate = float(d["tax_rate"])
        except Exception:
            rate = 0
        tax   = subtotal * rate / 100
        total = subtotal + tax
        tot_rows.append([Paragraph(f"{d['tax_label']} ({d['tax_rate']}%)", sTotLbl),
                         Paragraph(f"{cur} {tax:,.2f}", sTotVal)])
    else:
        total = subtotal

    tot_rows.append([Paragraph(d["total_label"], sTotLbl),
                     Paragraph(f"{cur} {total:,.2f}", sTotVal)])
    tot_rows.append([Paragraph(d["due_label"], sDueLbl),
                     Paragraph(f"{cur} {total:,.2f}", sDueVal)])

    tot_table = Table(tot_rows, colWidths=[W*0.65, W*0.35],
                      style=TableStyle([
                          ("ALIGN",        (0,0), (-1,-1),  "RIGHT"),
                          ("GRID",         (0,0), (-1,-2),  0.3, C_BORDER),
                          ("LINEBELOW",    (0,-2),(1,-2),    0.8, C_ACCENT),
                          ("BACKGROUND",   (0,-1),(1,-1),   C_ACCENT),
                          ("TOPPADDING",   (0,0), (-1,-1),  4),
                          ("BOTTOMPADDING",(0,0), (-1,-1),  4),
                          ("LEFTPADDING",  (0,0), (-1,-1),  8),
                          ("RIGHTPADDING", (0,0), (-1,-1),  8),
                      ]))
    story.append(Table([[tot_table]], colWidths=[W],
                       style=TableStyle([("ALIGN", (0,0), (-1,-1), "RIGHT")])))

    footer_parts = [x for x in [d["sup_phone"], d["sup_email"], d["sup_web"]] if x]
    if footer_parts:
        story.append(Spacer(1, 8*mm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER, spaceAfter=4))
        story.append(Paragraph(" | ".join(footer_parts), sFooter))

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
    CustomerTableApp(root)
    root.mainloop()
