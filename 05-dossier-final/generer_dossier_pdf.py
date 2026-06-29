#!/usr/bin/env python3
"""
generer_dossier_pdf.py — Génère dossier-facom.pdf depuis dossier-facom.md

Utilise fpdf2 pour une mise en page propre et professionnelle.
Exécuter depuis la racine du projet ou depuis 05-dossier-final/.

    python 05-dossier-final/generer_dossier_pdf.py
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent

# On ajoute le venv du POC au path pour fpdf2
sys.path.insert(0, str(ROOT / "04-poc" / ".venv" / "lib" /
                        "python3.13" / "site-packages"))

from fpdf import FPDF, XPos, YPos

# ── Palette ──────────────────────────────────────────────────────────────────
BLEU   = (44,  62,  80)
VERT   = (46, 204, 113)
GRIS   = (236, 240, 241)
NOIR   = (33,  33,  33)
GRIS_T = (127, 140, 141)

GITHUB = "https://github.com/rsladky/Concours-Natio-IA-Data"
TITRE  = "Dossier de proposition - Seconde vie du FACOM SCANDIAG(r) (DX.TSCANPB)"

# ── Nettoyage Unicode → Latin-1 ──────────────────────────────────────────────

_REMPLACEMENTS = str.maketrans({
    "—": "-",   # em dash —
    "–": "-",   # en dash –
    "→": "->",  # →
    "←": "<-",  # ←
    "≤": "<=",  # ≤
    "≥": ">=",  # ≥
    "✅": "[OK]",
    "⚠": "[!]",
    "️": "",    # variation selector
    "❌": "[X]",
    "⭐": "*",
    "®": "(r)",
    "×": "x",
    "•": "-",   # bullet •
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "«": '"',
    "»": '"',
    "…": "...",
    " ": " ",   # espace insécable
})

def clean(s: str) -> str:
    """Remplace les caractères hors Latin-1 par des équivalents ASCII."""
    s = s.translate(_REMPLACEMENTS)
    return s.encode("latin-1", errors="replace").decode("latin-1")


# ── Helpers ───────────────────────────────────────────────────────────────────

def couleur(pdf: FPDF, rgb: tuple, fill=False, draw=False, text=False) -> None:
    if fill: pdf.set_fill_color(*rgb)
    if draw: pdf.set_draw_color(*rgb)
    if text: pdf.set_text_color(*rgb)


class Dossier(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        couleur(self, GRIS_T, text=True)
        self.cell(0, 8, clean("ProfilScan - Réemploi RSE FACOM SCANDIAG(r) (DX.TSCANPB) - Concours Ynov 2026"),
                  align="C")
        self.ln(2)
        couleur(self, BLEU, draw=True)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)
        couleur(self, NOIR, text=True)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        couleur(self, GRIS_T, text=True)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")
        couleur(self, NOIR, text=True)

    # ── Titres ──────────────────────────────────────────────────────────────

    def h1(self, txt: str) -> None:
        self.ln(4)
        couleur(self, BLEU, fill=True)
        self.set_font("Helvetica", "B", 14)
        couleur(self, (255, 255, 255), text=True)
        self.cell(0, 10, clean(txt), fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        couleur(self, NOIR, text=True)
        self.ln(3)

    def h2(self, txt: str) -> None:
        self.ln(3)
        couleur(self, VERT, draw=True)
        self.set_line_width(0.8)
        self.set_font("Helvetica", "B", 11)
        couleur(self, BLEU, text=True)
        self.cell(0, 7, clean(txt), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.line(self.l_margin, self.get_y(),
                  self.l_margin + 190, self.get_y())
        couleur(self, NOIR, text=True)
        self.set_line_width(0.2)
        self.ln(2)

    def h3(self, txt: str) -> None:
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        couleur(self, BLEU, text=True)
        self.multi_cell(0, 6, clean(txt), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        couleur(self, NOIR, text=True)
        self.ln(1)

    # ── Corps de texte ──────────────────────────────────────────────────────

    def _md_strip(self, txt: str) -> str:
        txt = re.sub(r'\*\*(.+?)\*\*', r'\1', txt)
        txt = re.sub(r'\*(.+?)\*', r'\1', txt)
        txt = re.sub(r'`(.+?)`', r'\1', txt)
        txt = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', txt)
        return clean(txt)

    def para(self, txt: str, indent: int = 0) -> None:
        self.set_font("Helvetica", "", 9.5)
        txt = self._md_strip(txt)
        if indent:
            self.set_x(self.l_margin + indent)
        self.multi_cell(0, 5.5, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def bullet(self, txt: str, level: int = 0) -> None:
        indent = 5 + level * 6
        self.set_font("Helvetica", "", 9.5)
        txt = self._md_strip(txt)
        self.set_x(self.l_margin + indent)
        marker = "-" if level == 0 else " "
        self.multi_cell(0, 5.5, f"{marker}  {txt}",
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def code_block(self, lines: list[str]) -> None:
        self.ln(1)
        couleur(self, (245, 245, 245), fill=True)
        couleur(self, (200, 200, 200), draw=True)
        self.set_line_width(0.2)
        x0 = self.l_margin
        y0 = self.get_y()
        self.set_font("Courier", "", 8)
        for line in lines:
            self.set_x(x0 + 3)
            self.multi_cell(180, 4.5, clean(line), fill=True,
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.rect(x0, y0, 190, self.get_y() - y0)
        self.ln(2)
        couleur(self, NOIR, text=True)

    # ── Tableau générique ────────────────────────────────────────────────────

    def tableau(self, headers: list[str], rows: list[list[str]],
                col_widths: list[float] | None = None) -> None:
        if col_widths is None:
            w = 190 / len(headers)
            col_widths = [w] * len(headers)

        self.set_font("Helvetica", "B", 8.5)
        couleur(self, BLEU, fill=True, draw=True)
        couleur(self, (255, 255, 255), text=True)
        self.set_line_width(0.2)
        for h, w in zip(headers, col_widths):
            self.cell(w, 7, clean(h), border=1, fill=True, align="C")
        self.ln()

        self.set_font("Helvetica", "", 8.5)
        couleur(self, NOIR, text=True)
        for i, row in enumerate(rows):
            if i % 2 == 0:
                couleur(self, (255, 255, 255), fill=True)
            else:
                couleur(self, GRIS, fill=True)
            for cell, w in zip(row, col_widths):
                cell = re.sub(r'\*\*(.+?)\*\*', r'\1', cell)
                cell = re.sub(r'`(.+?)`', r'\1', cell)
                self.cell(w, 6, clean(cell.strip()), border=1, fill=True)
            self.ln()

        couleur(self, NOIR, fill=True, draw=True, text=True)
        self.ln(3)


# ── Page de couverture ────────────────────────────────────────────────────────

def page_couverture(pdf: Dossier) -> None:
    pdf.add_page()
    # Fond bleu haut
    couleur(pdf, BLEU, fill=True)
    pdf.rect(0, 0, 210, 100, "F")
    # Accent vert
    couleur(pdf, VERT, fill=True)
    pdf.rect(0, 100, 210, 3, "F")

    pdf.set_y(22)
    pdf.set_font("Helvetica", "B", 22)
    couleur(pdf, (255, 255, 255), text=True)
    pdf.cell(0, 12, "Dossier de proposition", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "B", 16)
    couleur(pdf, VERT, text=True)
    pdf.cell(0, 10, "Seconde vie du FACOM SCANDIAG(r) (DX.TSCANPB)", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 11)
    couleur(pdf, (189, 195, 199), text=True)
    pdf.cell(0, 8, "Remis a la Direction RSE de FACOM - Groupe Stanley Black & Decker",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "I", 10)
    couleur(pdf, (189, 195, 199), text=True)
    pdf.cell(0, 7, "Concours National Informatique Ynov - 29/06/2026",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Bloc infos
    pdf.set_y(112)
    couleur(pdf, NOIR, text=True)

    equipe = [
        ("CONTI Jérémy",    "B3 IA DATA", "Aix-en-Provence"),
        ("SLADKY Robin",               "B3 IA DATA", "Aix-en-Provence"),
        ("MIRALLES Baptiste",          "B3 IA DATA", "Aix-en-Provence"),
        ("AHOLOU Sophie",              "B3 IA DATA", "Aix-en-Provence"),
        ("MERY Téo",              "B3 IA DATA", "Aix-en-Provence"),
        ("LE COZ Tara",                "B3 IA DATA", "Aix-en-Provence"),
    ]
    pdf.h2("Equipe")
    pdf.tableau(["Nom", "Classe", "Campus Ynov"], equipe, [80, 55, 55])

    # Métriques clés
    pdf.h2("Concept retenu : ProfilScan")
    metrics = [
        ["Concept", "Profilomètre laser open-source — pipeline Data/IA"],
        ["Taux de réemploi", "95% des composants du SCANDIAG conservés"],
        ["Calibration réelle", "Pièce 20c (2.14 mm) — erreur mesurée : 6%"],
        ["Détection", "4032/4032 colonnes — canal laser vert 520 nm"],
        ["Code source", GITHUB],
    ]
    pdf.tableau(["Indicateur", "Valeur"], metrics, [60, 130])


# ── Parseur markdown simplifié ────────────────────────────────────────────────

def render_md_section(pdf: Dossier, md_text: str) -> None:
    """Rend un bloc de texte markdown dans le PDF."""
    lines = md_text.split("\n")
    in_code = False
    code_buf: list[str] = []
    in_table = False
    table_headers: list[str] = []
    table_rows: list[list[str]] = []

    def flush_table():
        nonlocal in_table, table_headers, table_rows
        if table_headers:
            # Largeurs auto
            n = len(table_headers)
            w = 190 / n
            pdf.tableau(table_headers, table_rows, [w] * n)
        in_table = False
        table_headers = []
        table_rows = []

    for line in lines:
        # Blocs de code
        if line.strip().startswith("```"):
            if in_code:
                pdf.code_block(code_buf)
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue

        # Tables markdown
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.match(r"^[-:]+$", c) for c in cells if c):
                continue  # ligne séparatrice
            if in_table:
                if table_headers:
                    table_rows.append(cells)
            else:
                in_table = True
                table_headers = cells
            continue
        else:
            if in_table:
                flush_table()

        # Titres
        if line.startswith("#### "):
            pdf.h3(line[5:].strip())
        elif line.startswith("### "):
            pdf.h3(line[4:].strip())
        elif line.startswith("## "):
            pdf.h2(line[3:].strip())
        elif line.startswith("# "):
            pdf.h1(line[2:].strip())
        # Listes
        elif re.match(r"^[\-\*]\s", line):
            pdf.bullet(line[2:].strip(), level=0)
        elif re.match(r"^\s{2,4}[\-\*]\s", line):
            pdf.bullet(line.lstrip()[2:].strip(), level=1)
        elif re.match(r"^\d+\.\s", line):
            m = re.match(r"^(\d+)\.\s(.*)", line)
            if m:
                pdf.bullet(f"{m.group(1)}.  {m.group(2)}", level=0)
        # Séparateur
        elif line.strip() == "---":
            pdf.ln(2)
            couleur(pdf, GRIS, draw=True)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 190, pdf.get_y())
            couleur(pdf, NOIR, draw=True)
            pdf.ln(3)
        # Ligne vide
        elif line.strip() == "":
            if not in_table:
                pdf.ln(1.5)
        # Paragraphe
        else:
            stripped = line.strip()
            stripped = re.sub(r'^>\s?', '', stripped)  # blockquote
            if stripped:
                pdf.para(stripped)

    if in_table:
        flush_table()
    if in_code and code_buf:
        pdf.code_block(code_buf)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    md_path = HERE / "dossier-facom.md"
    out_path = HERE / "dossier-facom.pdf"

    print(f"Lecture : {md_path}")
    content = md_path.read_text(encoding="utf-8")

    # Supprimer le H1 principal (remplacé par la couverture)
    content = re.sub(r'^#\s+.+\n###.+\n\n---\n\n', '', content)

    # Découper en sections H2
    sections = re.split(r'(?=^## )', content, flags=re.MULTILINE)

    pdf = Dossier(orientation="P", unit="mm", format="A4")
    pdf.set_margins(10, 15, 10)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_title("Dossier ProfilScan — Réemploi RSE FACOM SCANDIAG®")
    pdf.set_author("Equipe B3 IA DATA — Ynov Aix-en-Provence")

    page_couverture(pdf)

    for i, section in enumerate(sections):
        if not section.strip():
            continue
        # Nouvelles pages pour les grandes sections
        if section.startswith("## "):
            pdf.add_page()
        render_md_section(pdf, section)

    # Page finale : rapport POC images
    poc_plat = ROOT / "04-poc" / "output" / "rapport_ref_plat.png"
    poc_piece = ROOT / "04-poc" / "output" / "rapport_piece_20c.png"
    for titre_img, chemin_img in [
        ("Annexe A — Rapport mesure : surface plate", poc_plat),
        ("Annexe B — Rapport mesure : piece de 20 centimes", poc_piece),
    ]:
        if chemin_img.exists():
            pdf.add_page()
            pdf.h1(titre_img)
            pdf.image(str(chemin_img), x=10, w=190)

    pdf.output(str(out_path))
    size_kb = out_path.stat().st_size // 1024
    print(f"PDF genere : {out_path}  ({size_kb} Ko, {pdf.page_no()} pages)")


if __name__ == "__main__":
    main()
