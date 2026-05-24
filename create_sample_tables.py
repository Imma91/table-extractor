"""
Genera sample_docs/sample_tables.pdf — 2 pagine con tabelle multiple:
  Pagina 1: Inventario magazzino + Riepilogo giacenze
  Pagina 2: Listino prezzi 2024
Esegui: python create_sample_tables.py
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, PageBreak
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

NAVY  = colors.HexColor("#0D1B2A")
BLUE  = colors.HexColor("#1A56DB")
LBLUE = colors.HexColor("#EBF3FF")
GRAY  = colors.HexColor("#D1D5DB")
GTXT  = colors.HexColor("#6B7280")
GREEN = colors.HexColor("#D1FAE5")
RED   = colors.HexColor("#FEE2E2")
WHITE = colors.white

def s(name, **kw):
    d = dict(fontName="Helvetica", fontSize=9, leading=12, textColor=NAVY)
    d.update(kw)
    return ParagraphStyle(name, **d)

def header_bar(c, doc, title):
    w, h = A4
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, h - 18*mm, w, 18*mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(WHITE)
    c.drawString(15*mm, h - 12*mm, title)
    c.setFont("Helvetica", 7)
    c.setFillColor(GTXT)
    c.drawCentredString(w/2, 8*mm, "Documento fittizio — generato a fini dimostrativi")
    c.restoreState()


def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=24*mm, bottomMargin=16*mm
    )

    SH = s("sh", fontName="Helvetica-Bold", fontSize=11, textColor=NAVY, spaceAfter=4)
    SB = s("sb", fontSize=8.5)
    SW = s("sw", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE)
    SL = s("sl", fontName="Helvetica-Bold", fontSize=7, textColor=GTXT)
    SR = s("sr", fontSize=8.5, alignment=TA_RIGHT)

    story = []

    # ══════════════════════════════════════════════════════════════
    # PAGINA 1 — Inventario + Riepilogo
    # ══════════════════════════════════════════════════════════════

    story.append(Paragraph("INVENTARIO MAGAZZINO — Situazione al 30/11/2024", SH))
    story.append(Spacer(1, 2*mm))

    inv_data = [
        [Paragraph(h, SW) for h in
         ["CODICE ART.", "DESCRIZIONE", "U.M.", "Q.TÀ DISP.", "Q.TÀ MIN.", "UBICAZIONE", "STATO"]],
        ["ART-001", "Vite M6x20 zincata (conf. 100 pz)",     "CF", "85",  "20", "A-01-03", "OK"],
        ["ART-002", "Dado M6 inox (conf. 50 pz)",             "CF", "12",  "15", "A-01-04", "BASSO"],
        ["ART-003", "Rondella piana M8 (conf. 200 pz)",       "CF", "43",  "10", "A-02-01", "OK"],
        ["ART-004", "Bullone M10x50 acciaio 8.8",             "PZ", "320", "50", "A-02-05", "OK"],
        ["ART-005", "Cavo elettrico 3x1.5mm² (rotolo 100m)",  "RT", "4",   "5",  "B-01-01", "BASSO"],
        ["ART-006", "Guaina termorestringente Ø6mm (5m)",     "PZ", "156", "30", "B-01-03", "OK"],
        ["ART-007", "Morsetto a pressione 2.5mm²",            "PZ", "890", "100","B-02-01", "OK"],
        ["ART-008", "Interruttore magnetotermico 16A 1P",     "PZ", "28",  "10", "C-01-02", "OK"],
        ["ART-009", "Presa Schuko 16A da incasso",            "PZ", "67",  "20", "C-01-05", "OK"],
        ["ART-010", "Scatola di derivazione 80x80mm",         "PZ", "5",   "10", "C-02-01", "BASSO"],
    ]

    inv_table = Table(inv_data, colWidths=[22*mm, 62*mm, 12*mm, 18*mm, 18*mm, 20*mm, 18*mm])

    row_styles = [
        ("BACKGROUND", (0,0), (-1,0), BLUE),
        ("BOX", (0,0), (-1,-1), 0.4, GRAY),
        ("INNERGRID", (0,0), (-1,-1), 0.3, GRAY),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("FONTSIZE", (0,1), (-1,-1), 8),
    ]
    # Righe BASSO in rosso chiaro
    for i, row in enumerate(inv_data[1:], 1):
        if row[-1] == "BASSO":
            row_styles.append(("BACKGROUND", (0,i), (-1,i), RED))
        elif i % 2 == 0:
            row_styles.append(("BACKGROUND", (0,i), (-1,i), LBLUE))

    inv_table.setStyle(TableStyle(row_styles))
    story.append(inv_table)
    story.append(Spacer(1, 6*mm))

    # Seconda tabella — Riepilogo per categoria
    story.append(Paragraph("RIEPILOGO GIACENZE PER CATEGORIA", SH))
    story.append(Spacer(1, 2*mm))

    riepilogo_data = [
        [Paragraph(h, SW) for h in ["CATEGORIA", "N° ARTICOLI", "ARTICOLI OK", "ARTICOLI BASSI", "% COPERTURA"]],
        ["Viteria / Bulloneria",  "4", "3", "1", "75.0%"],
        ["Cablaggio elettrico",   "3", "2", "1", "66.7%"],
        ["Componentistica elec.", "3", "2", "1", "66.7%"],
        [Paragraph("TOTALE", s("t", fontName="Helvetica-Bold", fontSize=8.5)),
         "10", "7",
         Paragraph("3", s("red", fontSize=8.5, textColor=colors.HexColor("#DC2626"))),
         "70.0%"],
    ]
    rip_table = Table(riepilogo_data, colWidths=[55*mm, 30*mm, 28*mm, 32*mm, 35*mm])
    rip_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BLUE),
        ("BACKGROUND", (0,1), (-1,2), WHITE),
        ("BACKGROUND", (0,3), (-1,3), LBLUE),
        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#F0F9FF")),
        ("BOX", (0,0), (-1,-1), 0.4, GRAY),
        ("INNERGRID", (0,0), (-1,-1), 0.3, GRAY),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("ALIGN", (1,0), (-1,-1), "CENTER"),
    ]))
    story.append(rip_table)

    # ══════════════════════════════════════════════════════════════
    # PAGINA 2 — Listino prezzi
    # ══════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("LISTINO PREZZI — Validità 01/01/2024 – 31/12/2024", SH))
    story.append(Spacer(1, 2*mm))

    listino_data = [
        [Paragraph(h, SW) for h in
         ["COD.", "DESCRIZIONE PRODOTTO", "U.M.", "PREZZO 2023", "PREZZO 2024", "VAR. %", "IVA"]],
        ["P-101", "Cavo FG16OR16 3x1.5mm²",          "MT",   "€ 2,10",  "€ 2,25",  "+7.1%",  "22%"],
        ["P-102", "Cavo FG16OR16 3x2.5mm²",          "MT",   "€ 3,40",  "€ 3,60",  "+5.9%",  "22%"],
        ["P-103", "Cavo FG16OR16 3x4mm²",            "MT",   "€ 5,20",  "€ 5,50",  "+5.8%",  "22%"],
        ["P-104", "Cavo FG16OR16 5x2.5mm²",          "MT",   "€ 5,80",  "€ 6,10",  "+5.2%",  "22%"],
        ["P-201", "Interruttore magn. 10A 1P curva C","PZ",  "€ 8,50",  "€ 9,00",  "+5.9%",  "22%"],
        ["P-202", "Interruttore magn. 16A 1P curva C","PZ",  "€ 8,50",  "€ 9,00",  "+5.9%",  "22%"],
        ["P-203", "Interruttore magn. 20A 2P curva C","PZ",  "€ 16,00", "€ 17,50", "+9.4%",  "22%"],
        ["P-204", "Interruttore diff. 25A 2P 30mA",   "PZ",  "€ 28,00", "€ 30,00", "+7.1%",  "22%"],
        ["P-301", "Quadro da incasso 12 moduli",      "PZ",  "€ 14,00", "€ 14,00", "0.0%",   "22%"],
        ["P-302", "Quadro da incasso 24 moduli",      "PZ",  "€ 22,00", "€ 22,50", "+2.3%",  "22%"],
        ["P-303", "Quadro da incasso 36 moduli",      "PZ",  "€ 32,00", "€ 33,00", "+3.1%",  "22%"],
        ["P-401", "Presa Schuko 16A bianca",          "PZ",  "€ 3,20",  "€ 3,20",  "0.0%",   "22%"],
        ["P-402", "Interruttore unipolare 10A",       "PZ",  "€ 2,80",  "€ 2,90",  "+3.6%",  "22%"],
        ["P-403", "Deviatore 10A",                    "PZ",  "€ 3,50",  "€ 3,60",  "+2.9%",  "22%"],
    ]

    listino_table = Table(
        listino_data,
        colWidths=[16*mm, 66*mm, 13*mm, 22*mm, 22*mm, 16*mm, 15*mm]
    )

    lt_styles = [
        ("BACKGROUND", (0,0), (-1,0), BLUE),
        ("BOX", (0,0), (-1,-1), 0.4, GRAY),
        ("INNERGRID", (0,0), (-1,-1), 0.3, GRAY),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("FONTSIZE", (0,1), (-1,-1), 8),
        ("ALIGN", (2,0), (-1,-1), "CENTER"),
    ]
    for i in range(1, len(listino_data)):
        if i % 2 == 0:
            lt_styles.append(("BACKGROUND", (0,i), (-1,i), LBLUE))
        # VAR% 0.0 in verde, aumenti in normale
        var = listino_data[i][5]
        if var == "0.0%":
            lt_styles.append(("TEXTCOLOR", (5,i), (5,i), colors.HexColor("#059669")))

    listino_table.setStyle(TableStyle(lt_styles))
    story.append(listino_table)
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "Prezzi IVA esclusa. Validi per ordini ≥ 100€ imponibile. "
        "Per quantitativi ≥ 500€ applicare sconto 5%. Condizioni soggette a variazione.",
        s("note", fontSize=7.5, textColor=GTXT)
    ))

    def on_page(c, d):
        from reportlab.lib.pagesizes import A4 as _A4
        w, h = _A4
        c.saveState()
        c.setFillColor(NAVY)
        c.rect(0, h - 18*mm, w, 18*mm, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(WHITE)
        titles = {1: "INVENTARIO MAGAZZINO", 2: "LISTINO PREZZI 2024"}
        c.drawString(15*mm, h - 12*mm, titles.get(d.page, "DOCUMENTO"))
        c.setFont("Helvetica", 7)
        c.setFillColor(GTXT)
        c.drawCentredString(w/2, 8*mm, "Documento fittizio — generato a fini dimostrativi")
        c.restoreState()

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"Creato: {output_path}")
    print("Pagina 1: Inventario (10 righe) + Riepilogo categorie (4 righe)")
    print("Pagina 2: Listino prezzi (14 righe, 7 colonne)")


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "sample_docs")
    os.makedirs(out_dir, exist_ok=True)
    build_pdf(os.path.join(out_dir, "sample_tables.pdf"))
    print("\n(Tutti i dati sono completamente fittizi)")
