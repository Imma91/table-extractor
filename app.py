import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import os
import tempfile
import zipfile
from extractor import extract_all_tables

st.set_page_config(
    page_title="Table Extractor",
    page_icon="📊",
    layout="centered"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, .stTextInput, label,
    .stButton > button, [data-testid="stFileUploader"],
    [data-testid="metric-container"] {
        font-family: 'Inter', sans-serif !important;
    }
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2.5rem;
        max-width: 820px;
    }

    /* Input */
    .stTextInput > div > div > input {
        background-color: #0A1628 !important;
        border: 1px solid #1E3A5F !important;
        border-radius: 8px !important;
        color: #F1F5F9 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    }
    .stTextInput label, .stFileUploader label {
        font-size: 0.78rem !important; font-weight: 600 !important;
        color: #94A3B8 !important; letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #0A1628 !important;
        border: 1px dashed #1E3A5F !important;
        border-radius: 10px !important;
        padding: 0.4rem 0.8rem !important;
    }

    /* Bottone principale */
    .stButton > button {
        background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
        color: #F8FAFC !important; border: none !important;
        border-radius: 9px !important; padding: 0.65rem 1.4rem !important;
        font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
        font-size: 0.9rem !important;
        box-shadow: 0 2px 8px rgba(37,99,235,0.35) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1D4ED8, #1E40AF) !important;
        transform: translateY(-1px) !important;
    }

    /* Bottoni download */
    [data-testid="stDownloadButton"] > button {
        background: #0C1829 !important; color: #3B82F6 !important;
        border: 1px solid #2563EB !important; border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important; font-weight: 500 !important;
        font-size: 0.85rem !important; transition: all 0.2s ease !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: #1E3A5F !important; color: #93C5FD !important;
    }

    /* Metriche */
    [data-testid="metric-container"] {
        background: #0C1829 !important; border: 1px solid #1E3A5F !important;
        border-radius: 10px !important; padding: 0.9rem 1.1rem !important;
    }
    [data-testid="metric-container"] label {
        font-size: 0.7rem !important; font-weight: 600 !important;
        color: #64748B !important; text-transform: uppercase !important;
        letter-spacing: 0.07em !important;
    }
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 1.1rem !important; font-weight: 700 !important;
        color: #E2E8F0 !important;
    }

    h3 {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important; font-weight: 600 !important;
        color: #94A3B8 !important; letter-spacing: 0.07em !important;
        text-transform: uppercase !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 10px !important; overflow: hidden !important;
        border: 1px solid #1E3A5F !important;
    }

    [data-testid="stAlert"] {
        border-radius: 9px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
    }

    /* Progress bar */
    [data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #2563EB, #3B82F6) !important;
        border-radius: 4px !important;
    }

    hr { border-color: #1E3A5F !important; margin: 1.2rem 0 !important; }

    /* Table header block */
    .table-header {
        display: flex; align-items: center; gap: 10px;
        padding: 8px 14px; border-radius: 9px 9px 0 0;
        background: #0C1829; border: 1px solid #1E3A5F;
        border-bottom: none; margin-top: 14px;
    }
    .table-title {
        font-size: 0.88rem; font-weight: 600; color: #E2E8F0; flex: 1;
    }
    .table-notes {
        font-size: 0.78rem; color: #64748B; font-style: italic;
    }
    .table-index {
        font-size: 0.7rem; font-weight: 700; color: #3B82F6;
        background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.3);
        border-radius: 4px; padding: 1px 7px; text-transform: uppercase;
    }

    /* Page header */
    .page-header {
        display: flex; align-items: center; gap: 10px;
        padding: 6px 0; margin: 18px 0 6px 0;
        border-bottom: 1px solid #1E3A5F;
    }
    .page-label {
        font-size: 0.75rem; font-weight: 700; color: #64748B;
        letter-spacing: 0.06em; text-transform: uppercase;
    }
    .tables-count {
        font-size: 0.75rem; color: #3B82F6; font-weight: 500;
    }

    header[data-testid="stHeader"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# ─── Session state ────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None

# ─── Header ───────────────────────────────────────────────────────────────────
components.html("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <div style="font-family:'Inter',sans-serif; padding:4px 0 8px 0; background:transparent;">
        <div style="
            display:inline-block; background:rgba(59,130,246,0.12);
            border:1px solid rgba(59,130,246,0.38); border-radius:20px;
            padding:3px 12px; font-size:0.7rem; font-weight:600;
            color:#93C5FD; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:10px;
        ">Gemini 2.5 Flash Vision</div>
        <div style="
            font-size:2rem; font-weight:700; color:#F1F5F9;
            letter-spacing:-0.6px; line-height:1.2; margin-bottom:8px;
        ">Table Extractor</div>
        <div style="font-size:0.93rem; color:#64748B; font-weight:400; line-height:1.5;">
            Upload a scanned PDF or image — all tables are detected and extracted
            automatically, then exported to Excel and CSV.
        </div>
    </div>
""", height=135, scrolling=False)

st.divider()

# ─── Input ────────────────────────────────────────────────────────────────────
api_key = st.text_input(
    "GEMINI API KEY",
    type="password",
    placeholder="Paste your Gemini API key here"
)

uploaded_file = st.file_uploader(
    "PDF OR IMAGE (JPG, PNG, TIFF)",
    type=["pdf", "jpg", "jpeg", "png", "tiff", "bmp"]
)

st.divider()

# ─── Helpers ──────────────────────────────────────────────────────────────────

def table_to_df(table: dict) -> pd.DataFrame:
    headers = table.get("headers", [])
    rows    = table.get("rows", [])
    if not headers and not rows:
        return pd.DataFrame()
    if headers:
        df = pd.DataFrame(rows, columns=headers)
    else:
        df = pd.DataFrame(rows)
    return df


def build_excel(results: list) -> bytes:
    """Un foglio Excel per ogni tabella trovata."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        sheet_num = 1
        for page_data in results:
            for table in page_data["tables"]:
                df = table_to_df(table)
                if df.empty:
                    continue
                title = table.get("title") or f"Table_{sheet_num}"
                # Nome foglio max 31 caratteri (limite Excel)
                sheet_name = f"p{page_data['page']}_{title}"[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                sheet_num += 1
    return buf.getvalue()


def build_zip_csv(results: list) -> bytes:
    """Un CSV per ogni tabella, in un archivio ZIP."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        n = 1
        for page_data in results:
            for table in page_data["tables"]:
                df = table_to_df(table)
                if df.empty:
                    continue
                title = (table.get("title") or f"table{n}").replace(" ", "_")
                filename = f"p{page_data['page']}_{title}.csv"
                zf.writestr(filename, df.to_csv(index=False, encoding="utf-8-sig"))
                n += 1
    return buf.getvalue()


def count_total_tables(results: list) -> int:
    return sum(p["total_tables"] for p in results)


# ─── Logica principale ────────────────────────────────────────────────────────
if uploaded_file and api_key:

    if st.button("Extract Tables", use_container_width=True):
        st.session_state.results = None

        # Determina estensione
        filename = uploaded_file.name
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "pdf"

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            progress_bar = st.progress(0.0)
            status_text  = st.empty()

            def on_progress(current, total):
                if total > 0:
                    progress_bar.progress(current / total)
                    if current < total:
                        status_text.markdown(
                            f"<span style='font-size:0.85rem;color:#64748B;'>"
                            f"Analyzing page {current + 1} of {total}…</span>",
                            unsafe_allow_html=True
                        )
                    else:
                        status_text.empty()

            results = extract_all_tables(tmp_path, api_key,
                                         progress_callback=on_progress)
            progress_bar.empty()
            st.session_state.results = results

        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

# ─── Risultati ────────────────────────────────────────────────────────────────
if st.session_state.results:
    results = st.session_state.results

    total_tables = count_total_tables(results)
    total_pages  = len(results)
    pages_with_tables = sum(1 for p in results if p["total_tables"] > 0)

    # ── Errore globale ────────────────────────────────────────────────────
    if total_tables == 0:
        st.warning("No tables found in this document. "
                   "Make sure the document contains structured table data.")
    else:
        st.success(f"Extraction complete — {total_tables} table(s) found.")

        # ── Sommario ──────────────────────────────────────────────────────
        st.divider()
        st.subheader("Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Pages analyzed", total_pages)
        c2.metric("Tables found", total_tables)
        c3.metric("Pages with tables", pages_with_tables)

        # ── Tabelle per pagina ────────────────────────────────────────────
        st.divider()
        st.subheader("Extracted Tables")

        for page_data in results:
            if page_data["total_tables"] == 0:
                continue

            n = page_data["total_tables"]
            st.markdown(
                f'<div class="page-header">'
                f'<span class="page-label">Page {page_data["page"]}</span>'
                f'<span class="tables-count">{n} table{"s" if n > 1 else ""} found</span>'
                f'</div>',
                unsafe_allow_html=True
            )

            for table in page_data["tables"]:
                df = table_to_df(table)
                if df.empty:
                    continue

                title = table.get("title") or f"Table {table['table_index']}"
                notes = table.get("notes", "")

                # Header card della tabella
                st.markdown(
                    f'<div class="table-header">'
                    f'<span class="table-index">T{table["table_index"]}</span>'
                    f'<span class="table-title">{title}</span>'
                    f'<span class="table-notes">{notes}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Dataframe + download CSV
                col_df, col_btn = st.columns([4, 1])
                with col_df:
                    st.dataframe(df, use_container_width=True)
                with col_btn:
                    csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
                    safe_title = (table.get("title") or f"table{table['table_index']}").replace(" ", "_")
                    st.download_button(
                        label="CSV",
                        data=csv_bytes,
                        file_name=f"p{page_data['page']}_{safe_title}.csv",
                        mime="text/csv",
                        key=f"csv_p{page_data['page']}_t{table['table_index']}",
                        use_container_width=True
                    )

            if page_data.get("error"):
                st.warning(f"Page {page_data['page']}: {page_data['error']}")

        # ── Export globale ────────────────────────────────────────────────
        st.divider()
        st.subheader("Export All")

        col_xl, col_zip = st.columns(2)

        with col_xl:
            excel_bytes = build_excel(results)
            st.download_button(
                label=f"Download Excel ({total_tables} sheets)",
                data=excel_bytes,
                file_name="extracted_tables.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col_zip:
            zip_bytes = build_zip_csv(results)
            st.download_button(
                label=f"Download all CSV (ZIP)",
                data=zip_bytes,
                file_name="extracted_tables_csv.zip",
                mime="application/zip",
                use_container_width=True
            )

else:
    if not api_key:
        st.caption("Insert your Gemini API key to get started.")
    elif not uploaded_file:
        st.caption("Upload a PDF or image to continue.")
