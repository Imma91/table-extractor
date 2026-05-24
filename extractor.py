"""
extractor.py — Core logic for Table Extractor from Scanned Docs.
Renders each page as an image, sends to Gemini Vision,
and returns all tables found as structured data.
"""

import fitz                          # PyMuPDF
import google.generativeai as genai
import json
import re
import io
from PIL import Image


# ─── PDF / image → pagine ─────────────────────────────────────────────────────

def pdf_to_images(pdf_path: str, zoom: float = 2.5) -> list[Image.Image]:
    """
    Renderizza ogni pagina del PDF come immagine PIL.
    Zoom 2.5x per massimizzare la leggibilità delle tabelle.
    """
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        images.append(Image.open(io.BytesIO(pix.tobytes("png"))))
    doc.close()
    return images


def load_image(image_path: str) -> list[Image.Image]:
    """Carica un'immagine singola (JPG, PNG, TIFF…) come lista di 1 elemento."""
    return [Image.open(image_path)]


# ─── Estrazione tabelle da una singola pagina ─────────────────────────────────

def extract_tables_from_image(image: Image.Image, model) -> dict:
    """
    Invia l'immagine a Gemini e restituisce tutte le tabelle trovate.

    Schema risposta:
    {
        "total_tables": N,
        "tables": [
            {
                "table_index": 1,
                "title": "string or null",
                "headers": ["col1", "col2", ...],
                "rows": [["val", ...], ...],
                "notes": "brief description"
            }
        ]
    }
    """
    prompt = """
Analyze this document image carefully.

Find ALL tables present in the image, including:
- Data tables, price lists, inventory lists
- Financial summaries, comparison tables
- Any grid-like structure with rows and columns

For each table found, extract:
1. The column headers (first row or labeled headers)
2. All data rows, preserving the original values exactly
3. A short title if visible above the table, otherwise null

Return ONLY a valid JSON object — no markdown, no backticks, no extra text.

{
    "total_tables": <integer>,
    "tables": [
        {
            "table_index": 1,
            "title": "table title or null",
            "headers": ["Column1", "Column2", "Column3"],
            "rows": [
                ["value1", "value2", "value3"],
                ["value4", "value5", "value6"]
            ],
            "notes": "brief description of this table, max 10 words"
        }
    ]
}

Important rules:
- If a cell is empty, use "" (empty string)
- Preserve numbers as strings exactly as they appear (e.g. "1.234,56" not 1234.56)
- If no tables are found: {"total_tables": 0, "tables": []}
- Do not merge separate tables into one
- Include all rows, do not truncate
"""
    response = model.generate_content([prompt, image])
    text = response.text.strip()
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)

    parsed = json.loads(text)

    # Normalizza: assicura che ogni riga abbia la stessa lunghezza degli header
    for table in parsed.get("tables", []):
        n_cols = len(table.get("headers", []))
        table["rows"] = [
            row + [""] * (n_cols - len(row)) if len(row) < n_cols
            else row[:n_cols]
            for row in table.get("rows", [])
        ]

    return parsed


# ─── Estrazione da intero documento ───────────────────────────────────────────

def extract_all_tables(file_path: str, api_key: str,
                       progress_callback=None) -> list[dict]:
    """
    Estrae tabelle da tutte le pagine di un PDF o da un'immagine.

    progress_callback(current, total) aggiorna la UI.

    Restituisce lista di:
    {
        "page": N,
        "total_tables": N,
        "tables": [...]
    }
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Carica le immagini in base al tipo di file
    ext = file_path.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        images = pdf_to_images(file_path)
    else:
        images = load_image(file_path)

    total = len(images)
    results = []

    for i, image in enumerate(images):
        if progress_callback:
            progress_callback(i, total)

        try:
            page_data = extract_tables_from_image(image, model)
        except Exception as e:
            page_data = {
                "total_tables": 0,
                "tables": [],
                "error": str(e)[:100]
            }

        results.append({
            "page": i + 1,
            "total_tables": page_data.get("total_tables", 0),
            "tables": page_data.get("tables", []),
            "error": page_data.get("error"),
        })

    if progress_callback:
        progress_callback(total, total)

    return results
