"""Generate the MURL Excel Dashboard — Pro version.

Reads input/requests.csv (16 columns matching DATA_HEADERS exactly) and builds
murl_dashboard_pro.xlsx with KPI cards, filter panel, mini-pivots, and a
FILTER-spill results table.

Run:
    python build_dashboard_pro.py             # reads ./input/requests.csv
    python build_dashboard_pro.py --csv X.csv # custom CSV path
    python build_dashboard_pro.py --empty     # empty template, no CSV needed

Output: ./murl_dashboard_pro.xlsx
"""

import argparse
import csv
from pathlib import Path

import xlsxwriter

SCRIPT_DIR = Path(__file__).parent
OUTPUT_PATH = SCRIPT_DIR / "murl_dashboard.xlsx"
DEFAULT_CSV_PATH = SCRIPT_DIR / "input" / "requests.csv"

# Corporate palette
RED = "#E60000"
BLACK = "#000000"
WHITE = "#FFFFFF"
PAGE_BG = "#F7F7F5"
PASTEL_I = "#ECEBE4"
GRAY_I = "#CCCABC"
GRAY_IV = "#7A7870"
GRAY_VI = "#404040"
RAG_GREEN = "#6F7A1A"
RAG_AMBER = "#E4A911"
LAKE = "#0C7EC6"

DATA_HEADERS = [
    "Labels", "Reference", "MURL", "Service project", "Status",
    "Requester", "Type", "Region(s)", "Line manager", "MURL name",
    "Activation", "Properties", "GOTO/MURL Owner 1", "GOTO/MURL Owner 2",
    "Business Division requested for", "Target URL",
]
COL_WIDTHS = [14, 14, 50, 14, 22, 22, 22, 14, 22, 24, 14, 24, 22, 22, 30, 60]
LAST_COL = len(DATA_HEADERS) - 1  # 0-indexed
LAST_COL_LETTER = chr(ord("A") + LAST_COL)

# Maps the dashboard column name → original Tableau CSV column name.
# Anything not in this map uses the same name in CSV and dashboard.
CSV_RENAME = {
    "MURL": "Summary",
    "Target URL": "Target Default",
}
CSV_HEADERS = [CSV_RENAME.get(h, h) for h in DATA_HEADERS]


def main():
    parser = argparse.ArgumentParser(description="Build MURL Excel Dashboard (Pro)")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV_PATH,
                        help=f"Path to input CSV (default: {DEFAULT_CSV_PATH})")
    parser.add_argument("--empty", action="store_true",
                        help="Generate empty template (no CSV required)")
    args = parser.parse_args()

    if args.empty:
        data_rows = []
    else:
        if not args.csv.exists():
            raise SystemExit(
                f"CSV not found: {args.csv}\n"
                f"Place the Tableau CSV export at this path or pass --csv <path>."
            )
        data_rows = read_csv_rows(args.csv)
        print(f"Loaded {len(data_rows)} rows from {args.csv}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb = xlsxwriter.Workbook(str(OUTPUT_PATH))

    fmts = build_formats(wb)
    ws_dash = wb.add_worksheet("Dashboard")
    ws_data = wb.add_worksheet("Data")
    ws_lists = wb.add_worksheet("Lists")
    ws_help = wb.add_worksheet("Anleitung")

    build_data_sheet(ws_data, data_rows, fmts)
    list_ranges = build_lists_sheet(ws_lists, wb, data_rows)
    build_dashboard_sheet(ws_dash, wb, fmts, list_ranges)
    build_help_sheet(ws_help, fmts)

    ws_lists.hide()
    ws_dash.hide_gridlines(2)
    ws_data.hide_gridlines(2)
    ws_help.hide_gridlines(2)
    ws_dash.activate()

    wb.close()
    print(f"Generated: {OUTPUT_PATH}")


def read_csv_rows(csv_path):
    """Read requests.csv and map each row to the 16 DATA_HEADERS.

    Expects header row with column names matching DATA_HEADERS exactly
    (case-sensitive — note 'MURL name' is lowercase 'n').
    """
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        missing = [h for h in CSV_HEADERS if h not in fieldnames]
        if missing:
            raise SystemExit(
                f"CSV header is missing required columns: {missing}\n"
                f"CSV has: {fieldnames}\n"
                f"Expected ({len(CSV_HEADERS)}): {CSV_HEADERS}"
            )
        rows = []
        for raw in reader:
            rows.append({
                h: (raw.get(CSV_RENAME.get(h, h)) or "").strip()
                for h in DATA_HEADERS
            })
    return rows


def build_formats(wb):
    """All cell formats used across the workbook."""
    return {
        "title": wb.add_format({
            "font_name": "Calibri", "font_size": 24, "bold": True,
            "font_color": BLACK, "align": "left", "valign": "vcenter",
            "indent": 1, "bottom": 2, "bottom_color": RED,
        }),
        "subtitle": wb.add_format({
            "font_name": "Calibri", "font_size": 11, "font_color": GRAY_IV,
            "align": "left", "valign": "vcenter", "indent": 1,
        }),
        "title_border": wb.add_format({
            "bottom": 2, "bottom_color": RED,
        }),
        "section": wb.add_format({
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": GRAY_VI, "align": "left", "valign": "vcenter",
        }),
        "kpi_label": wb.add_format({
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": GRAY_IV, "align": "left", "valign": "vcenter",
            "indent": 2, "bg_color": PAGE_BG,
            "left": 1, "left_color": GRAY_I,
            "right": 1, "right_color": GRAY_I,
        }),
        "kpi_value": wb.add_format({
            "font_name": "Calibri", "font_size": 22, "font_color": BLACK,
            "align": "left", "valign": "vcenter", "indent": 2,
            "bg_color": PAGE_BG,
            "left": 1, "left_color": GRAY_I,
            "right": 1, "right_color": GRAY_I,
            "bottom": 1, "bottom_color": GRAY_I,
        }),
        "filter_label": wb.add_format({
            "font_name": "Calibri", "font_size": 10, "font_color": GRAY_IV,
            "align": "left", "valign": "vcenter", "indent": 1,
        }),
        "filter_input": wb.add_format({
            "font_name": "Calibri", "font_size": 11, "font_color": BLACK,
            "align": "left", "valign": "vcenter", "indent": 1,
            "bg_color": PASTEL_I,
            "left": 1, "left_color": GRAY_IV,
            "right": 1, "right_color": GRAY_IV,
            "top": 1, "top_color": GRAY_IV,
            "bottom": 1, "bottom_color": GRAY_IV,
        }),
        "table_header": wb.add_format({
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": WHITE, "bg_color": GRAY_VI,
            "align": "left", "valign": "vcenter", "indent": 1,
            "bottom": 2, "bottom_color": RED,
        }),
        "pivot_title": wb.add_format({
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": WHITE, "bg_color": GRAY_VI,
            "align": "left", "valign": "vcenter", "indent": 1,
        }),
        "pivot_subheader": wb.add_format({
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": GRAY_IV, "bg_color": PASTEL_I,
            "align": "left", "valign": "vcenter", "indent": 1,
            "bottom": 1, "bottom_color": GRAY_I,
        }),
        "pivot_subheader_num": wb.add_format({
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": GRAY_IV, "bg_color": PASTEL_I,
            "align": "right", "valign": "vcenter", "indent": 1,
            "bottom": 1, "bottom_color": GRAY_I,
        }),
        "pivot_value": wb.add_format({
            "font_name": "Calibri", "font_size": 11, "font_color": GRAY_VI,
            "align": "left", "valign": "vcenter", "indent": 1,
        }),
        "pivot_count": wb.add_format({
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": BLACK, "align": "right", "valign": "vcenter", "indent": 1,
        }),
        "hit_counter": wb.add_format({
            "font_name": "Calibri", "font_size": 12, "bold": True,
            "font_color": GRAY_VI, "align": "right", "valign": "vcenter", "indent": 1,
        }),
        "filter_active": wb.add_format({
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": RED, "align": "left", "valign": "vcenter", "indent": 1,
        }),
        "help_h1": wb.add_format({
            "font_name": "Calibri", "font_size": 18, "bold": True,
            "font_color": BLACK, "align": "left", "valign": "vcenter",
            "bottom": 2, "bottom_color": RED,
        }),
        "help_h2": wb.add_format({
            "font_name": "Calibri", "font_size": 13, "bold": True,
            "font_color": BLACK, "align": "left", "valign": "vcenter",
        }),
        "help_body": wb.add_format({
            "font_name": "Calibri", "font_size": 11,
            "font_color": GRAY_VI, "align": "left", "valign": "vcenter",
        }),
        "help_body_bold": wb.add_format({
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": GRAY_VI, "align": "left", "valign": "vcenter",
        }),
    }


def kpi_accent_format(wb, accent):
    """KPI label format with custom top-accent border colour."""
    return wb.add_format({
        "font_name": "Calibri", "font_size": 10, "bold": True,
        "font_color": GRAY_IV, "align": "left", "valign": "vcenter",
        "indent": 2, "bg_color": PAGE_BG,
        "top": 5, "top_color": accent,
        "left": 1, "left_color": GRAY_I,
        "right": 1, "right_color": GRAY_I,
    })


def build_data_sheet(ws, rows, fmts):
    for i, w in enumerate(COL_WIDTHS):
        ws.set_column(i, i, w)
    ws.set_row(0, 28)

    # Write data rows first (skip empty values to avoid malformed cells)
    for r, row in enumerate(rows):
        for c, header in enumerate(DATA_HEADERS):
            val = row.get(header)
            if val:
                ws.write(r + 1, c, val)

    last_data_row = max(len(rows), 1)  # 0-indexed last row of table
    ws.add_table(0, 0, last_data_row, LAST_COL, {
        "name": "tblData",
        "style": "Table Style Light 1",
        "columns": [{"header": h} for h in DATA_HEADERS],
    })

    ws.freeze_panes(1, 0)


def build_lists_sheet(ws, wb, rows):
    """Static unique-value lists per dropdown column, computed at build time.

    Excel for Mac does not reliably resolve spilled-range references
    (=Lists!$A$1#) inside Data Validation sources. Pre-computed static lists
    sidestep that. Trade-off: lists are stale when source data changes — re-run
    the build script after a data refresh to regenerate.

    Returns a dict mapping the defined-name to the literal sheet range, used by
    Data Validation sources.
    """
    list_specs = [
        # (col_index, source_column_name, defined_name)
        (0, "Status", "lstStatus"),
        (2, "Requester", "lstRequester"),
        (4, "Region(s)", "lstRegion"),
        (6, "Business Division requested for", "lstDivision"),
        (8, "Activation", "lstActivation"),
    ]
    list_ranges = {}
    for col, src, name in list_specs:
        col_letter = chr(ord("A") + col)
        values = sorted({r[src] for r in rows if r.get(src)}) if rows else []
        if not values:
            values = [""]
        for i, v in enumerate(values):
            ws.write(i, col, v)
        last_row = len(values)
        sheet_range = f"Lists!${col_letter}$1:${col_letter}${last_row}"
        wb.define_name(name, f"={sheet_range}")
        list_ranges[name] = sheet_range

    return list_ranges


def build_dashboard_sheet(ws, wb, fmts, list_ranges):
    """Layout (0-indexed rows):
        0      Title
        1      Subtitle
        3-4    KPI cards (5 cards × 3 cols)
        6      "FILTER" section header
        7-8    Text filters: 4 filters × 3 cols (Labels, MURL, Target, Owners)
        9-10   Dropdown filters: 5 dropdowns × 3 cols
        12     "AGGREGATION" section header
        13     Mini-pivot panel titles (4 panels × 4 cols)
        14     Mini-pivot sub-headers (Wert | Anzahl)
        15-19  Mini-pivot data (TOP 5 per panel, spilled)
        21     "ERGEBNISSE" header + Top-N dropdown + filter indicator + hit counter
        22     Results table header
        23     FILTER spill (used as rngFilter)
    """
    last_col = LAST_COL

    for i, w in enumerate(COL_WIDTHS):
        ws.set_column(i, i, w)

    # --- Title & subtitle ---
    ws.set_row(0, 40)
    ws.merge_range(0, 0, 0, last_col, "MURL Dashboard", fmts["title"])
    ws.set_row(1, 22)
    ws.merge_range(1, 0, 1, last_col,
                   "Filter unten setzen — Dropdowns oder freier Text, Contains-Suche überall. "
                   "Aggregation und KPIs reagieren live.",
                   fmts["subtitle"])

    # --- KPI cards (rows 3 + 4) ---
    ws.set_row(3, 22)
    ws.set_row(4, 44)
    kpis = [
        ("Total", "=IFERROR(IF(COLUMNS(rngFilter)>1,ROWS(rngFilter),0),0)", RED),
        ("Active",
         '=IFERROR(SUMPRODUCT(--(INDEX(rngFilter,0,5)="Active")),0)', RAG_GREEN),
        ("Scheduled",
         '=IFERROR(SUMPRODUCT(--(INDEX(rngFilter,0,5)="Scheduled Activation")),0)', LAKE),
        ("Pending",
         '=IFERROR(SUMPRODUCT(--(INDEX(rngFilter,0,5)="Pending Change")),0)', RAG_AMBER),
        ("Deactivated",
         '=IFERROR(SUMPRODUCT(--(INDEX(rngFilter,0,5)="Deactivated")),0)', GRAY_IV),
    ]
    for i, (label, formula, accent) in enumerate(kpis):
        start_col = i * 3
        end_col = start_col + 2
        accent_fmt = kpi_accent_format(wb, accent)
        ws.merge_range(3, start_col, 3, end_col, label.upper(), accent_fmt)
        ws.merge_range(4, start_col, 4, end_col, None, fmts["kpi_value"])
        ws.write_formula(4, start_col, formula, fmts["kpi_value"])

    # --- FILTER section ---
    ws.set_row(6, 22)
    ws.write(6, 0, "FILTER", fmts["section"])

    ws.set_row(7, 18)
    ws.set_row(8, 28)
    text_filters = [
        ("Labels (Suche, z.B. ITO-12345)", 0, "f_labels"),
        ("MURL Name (Suche)",              3, "f_murl"),
        ("Target URL (Suche)",             6, "f_target"),
        ("Owners (Owner 1 oder 2)",        9, "f_owner"),
    ]
    for label, col, name in text_filters:
        ws.merge_range(7, col, 7, col + 2, label, fmts["filter_label"])
        ws.merge_range(8, col, 8, col + 2, "", fmts["filter_input"])
        col_letter = chr(ord("A") + col)
        wb.define_name(name, f"=Dashboard!${col_letter}$9")

    ws.set_row(9, 18)
    ws.set_row(10, 28)
    dropdown_filters = [
        ("Status",            0, "f_status",     "lstStatus"),
        ("Requester",         3, "f_requester",  "lstRequester"),
        ("Region",            6, "f_region",     "lstRegion"),
        ("Business Division", 9, "f_division",   "lstDivision"),
        ("Activation",       12, "f_activation", "lstActivation"),
    ]
    for label, col, name, list_name in dropdown_filters:
        ws.merge_range(9, col, 9, col + 2, label, fmts["filter_label"])
        ws.merge_range(10, col, 10, col + 2, "", fmts["filter_input"])
        col_letter = chr(ord("A") + col)
        wb.define_name(name, f"=Dashboard!${col_letter}$11")
        ws.data_validation(f"{col_letter}11", {
            "validate": "list",
            "source": f"={list_ranges[list_name]}",
            "show_error": False,
        })

    # --- AGGREGATION mini-pivots (4 panels × 4 cols each) ---
    # Each panel: title (merged 4 cols), sub-header row, spill formula
    # returning TOP 5 (value, count) sorted desc into 2 cols.
    ws.set_row(12, 22)
    ws.write(12, 0, "AGGREGATION — Top 5 im aktuellen Filter", fmts["section"])

    ws.set_row(13, 24)
    ws.set_row(14, 20)
    for r in range(15, 20):
        ws.set_row(r, 20)

    panels = [
        # (title, panel_start_col, source_col_in_rngFilter_1idx, formula_kind)
        ("Status",            0,  5,  "single"),
        ("Business Division", 4,  15, "single"),
        ("Region",            8,  8,  "single"),
        ("Top Owners",        12, 13, "owners"),  # combines Owner 1 + Owner 2
    ]
    for title, start_col, src_idx, kind in panels:
        ws.merge_range(13, start_col, 13, start_col + 3, title, fmts["pivot_title"])
        ws.merge_range(14, start_col, 14, start_col + 2, "Wert", fmts["pivot_subheader"])
        ws.write(14, start_col + 3, "Anzahl", fmts["pivot_subheader_num"])

        if kind == "owners":
            # Stack Owner 1 + Owner 2 columns, filter blanks, count uniques
            col_expr = (
                'LET(c1,INDEX(rngFilter,0,13),c2,INDEX(rngFilter,0,14),'
                'IFERROR(FILTER(VSTACK(c1,c2),VSTACK(c1,c2)<>""),""))'
            )
        else:
            col_expr = (
                f'LET(c,INDEX(rngFilter,0,{src_idx}),'
                f'IFERROR(FILTER(c,c<>""),""))'
            )

        # TOP 5: unique values, counts, sorted desc, take 5
        # IFERROR wraps every stage — rngFilter may be the "Keine Treffer" text
        pivot_formula = (
            f'=IFERROR(LET('
            f'col,{col_expr},'
            f'u,IFERROR(UNIQUE(col),""),'
            f'c,IFERROR(BYROW(u,LAMBDA(v,SUMPRODUCT(--(col=v)))),0),'
            f'TAKE(SORT(HSTACK(u,c),2,-1),5)),"")'
        )

        # Pre-format the 5 value/count cells so they look right even when spill is empty
        for r in range(15, 20):
            ws.merge_range(r, start_col, r, start_col + 2, "", fmts["pivot_value"])
            ws.write_blank(r, start_col + 3, None, fmts["pivot_count"])

        # Spill into 2 cols (value + count) starting at panel_start_col, row 15.
        # The value spills into start_col (the leftmost merged cell of the
        # value block), count into start_col+3 — we use CHOOSECOLS to split.
        value_formula = (
            f'=IFERROR(LET('
            f'col,{col_expr},'
            f'u,IFERROR(UNIQUE(col),""),'
            f'c,IFERROR(BYROW(u,LAMBDA(v,SUMPRODUCT(--(col=v)))),0),'
            f'CHOOSECOLS(TAKE(SORT(HSTACK(u,c),2,-1),5),1)),"")'
        )
        count_formula = (
            f'=IFERROR(LET('
            f'col,{col_expr},'
            f'u,IFERROR(UNIQUE(col),""),'
            f'c,IFERROR(BYROW(u,LAMBDA(v,SUMPRODUCT(--(col=v)))),0),'
            f'CHOOSECOLS(TAKE(SORT(HSTACK(u,c),2,-1),5),2)),"")'
        )
        ws.write_dynamic_array_formula(15, start_col, 15, start_col,
                                        value_formula, fmts["pivot_value"])
        ws.write_dynamic_array_formula(15, start_col + 3, 15, start_col + 3,
                                        count_formula, fmts["pivot_count"])

    # --- ERGEBNISSE header row with filter indicator + hit counter ---
    ws.set_row(21, 24)
    ws.write(21, 0, "ERGEBNISSE", fmts["section"])

    # Filter-active indicator at cols 5-7
    filter_active_formula = (
        '=IF((f_labels<>"")+(f_murl<>"")+(f_target<>"")+(f_owner<>"")+'
        '(f_status<>"")+(f_requester<>"")+(f_region<>"")+(f_division<>"")+'
        '(f_activation<>"")>0,"FILTER AKTIV","Keine Filter gesetzt")'
    )
    ws.merge_range(21, 5, 21, 7, "", fmts["filter_active"])
    ws.write_formula(21, 5, filter_active_formula, fmts["filter_active"])

    # Hit counter at cols 10-15 (right side)
    hit_counter_formula = (
        '="Zeigt " & IF(COLUMNS(rngFilter)>1,TEXT(ROWS(rngFilter),"#\'##0"),0)'
        ' & " von " & TEXT(ROWS(tblData),"#\'##0") & " Einträgen"'
    )
    ws.merge_range(21, 10, 21, 15, "", fmts["hit_counter"])
    ws.write_formula(21, 10, hit_counter_formula, fmts["hit_counter"])

    # --- Results header (row 22) ---
    ws.set_row(22, 26)
    for c, header in enumerate(DATA_HEADERS):
        ws.write(22, c, header, fmts["table_header"])

    # --- FILTER spill (row 23) ---
    # Single spill, anchored at A24. KPIs, mini-pivots and hit counter all
    # reference rngFilter so they always reflect the full filtered result set.
    filter_conditions = (
        '(tblData[Reference]<>"")*'
        '((f_labels="")+ISNUMBER(SEARCH(f_labels,tblData[Labels])))*'
        '((f_murl="")+ISNUMBER(SEARCH(f_murl,tblData[MURL name])))*'
        '((f_target="")+ISNUMBER(SEARCH(f_target,tblData[Target URL])))*'
        '((f_owner="")+ISNUMBER(SEARCH(f_owner,tblData[GOTO/MURL Owner 1]))+'
        'ISNUMBER(SEARCH(f_owner,tblData[GOTO/MURL Owner 2])))*'
        '((f_status="")+ISNUMBER(SEARCH(f_status,tblData[Status])))*'
        '((f_requester="")+ISNUMBER(SEARCH(f_requester,tblData[Requester])))*'
        '((f_region="")+ISNUMBER(SEARCH(f_region,tblData[Region(s)])))*'
        '((f_division="")+ISNUMBER(SEARCH(f_division,tblData[Business Division requested for])))*'
        '((f_activation="")+ISNUMBER(SEARCH(f_activation,tblData[Activation])))'
    )
    filter_formula = (
        f'=IFERROR(FILTER(tblData,{filter_conditions}),'
        f'"Keine Treffer — Filter zurücksetzen")'
    )
    ws.write_dynamic_array_formula(23, 0, 23, 0, filter_formula)
    wb.define_name("rngFilter", "=Dashboard!$A$24#")

    ws.freeze_panes(22, 0)



def build_help_sheet(ws, fmts):
    ws.set_column(0, 0, 130)
    ws.set_row(0, 32)

    lines = [
        ("Anleitung — MURL Dashboard (Pro)", "h1"),
        ("", "body"),
        ("1. Filter nutzen", "h2"),
        ("Alle Filter sind Contains-Search: leeres Feld = kein Filter, jeder eingegebene Text wird als Teilstring gesucht.", "body"),
        ("Dropdowns zeigen alle vorhandenen Werte — Auswahl ODER freies Tippen (z.B. 'GW' findet 'GWM' und 'GWM Americas').", "body"),
        ("Owners-Suche prüft sowohl 'GOTO/MURL Owner 1' als auch 'Owner 2'.", "body"),
        ("Filter zurücksetzen: Zelle markieren, Entf drücken.", "body"),
        ("", "body"),
        ("2. KPIs", "h2"),
        ("Die 5 Kacheln oben aktualisieren sich live — sie zählen nur die aktuell gefilterten Treffer.", "body"),
        ("", "body"),
        ("3. Refresh (neu bauen mit aktualisierten Daten)", "h2"),
        ("Tableau-CSV-Export als 'requests.csv' in den Unterordner 'input/' legen.", "body"),
        ("Im Terminal/CMD im Excel-Ordner ausführen:", "body"),
        ("   python build_dashboard_pro.py", "body_bold"),
        ("Das Skript liest input/requests.csv und überschreibt murl_dashboard.xlsx.", "body"),
        ("Voraussetzung: Python 3 + xlsxwriter (pip install xlsxwriter).", "body"),
        ("", "body"),
        ("4. Teilen via OneDrive", "h2"),
        ("Datei in OneDrive ablegen, mit Empfängern teilen — Excel for the Web supports FILTER/UNIQUE/SORT seit 2022.", "body"),
        ("Voraussetzung: Excel 365. Nicht kompatibel mit Excel 2019 oder älter.", "body"),
    ]
    style_map = {
        "h1": fmts["help_h1"],
        "h2": fmts["help_h2"],
        "body": fmts["help_body"],
        "body_bold": fmts["help_body_bold"],
    }
    for i, (text, style) in enumerate(lines):
        ws.write(i, 0, text, style_map[style])


if __name__ == "__main__":
    main()
