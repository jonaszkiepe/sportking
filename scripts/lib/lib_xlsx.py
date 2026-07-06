"""Tiny dependency-free XLSX read + write (stdlib only).

read_sheets(path) -> {sheet_name: [ {col_letter: value}, ... ]}  (values as strings)
write_xlsx(path, sheets)  where sheets = [(name, [row, row, ...]), ...],
    each row a list of cells (str/int/float); the first row is styled as a bold,
    frozen header. Numbers are written as numbers, everything else as text.

Reading parses the zip directly, so it works even while the file is open in
Excel/LibreOffice.
"""
import re
import zipfile
import xml.etree.ElementTree as ET

_M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_NS = {"m": _M}


def _col(ref):
    return re.match(r"[A-Z]+", ref).group()


def read_sheets(path):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", _NS):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{_M}}}t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap = {r.get("Id"): r.get("Target") for r in rels}
    sheets = {}
    for s in wb.iter(f"{{{_M}}}sheet"):
        target = relmap[s.get(f"{{{_R}}}id")].lstrip("/")
        sheets[s.get("name")] = "xl/" + target if not target.startswith("xl/") else target

    def cell_val(c):
        t = c.get("t", "n")
        if t == "inlineStr":
            return "".join(x.text or "" for x in c.iter(f"{{{_M}}}t"))
        v = c.find("m:v", _NS)
        if v is None or v.text is None:
            return ""
        return shared[int(v.text)] if t == "s" else v.text

    out = {}
    for name, target in sheets.items():
        root = ET.fromstring(z.read(target))
        rows = []
        for r in root.iter(f"{{{_M}}}row"):
            rows.append({_col(c.get("r")): cell_val(c) for c in r.iter(f"{{{_M}}}c")})
        out[name] = rows
    return out


def _colname(n):
    s = ""
    while n >= 0:
        s = chr(n % 26 + 65) + s
        n = n // 26 - 1
    return s


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _sheet_xml(rows):
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
           f'<worksheet xmlns="{_M}"><sheetViews><sheetView workbookViewId="0">',
           '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>',
           '</sheetView></sheetViews><sheetData>']
    for ri, row in enumerate(rows, 1):
        out.append(f'<row r="{ri}">')
        for ci, val in enumerate(row):
            ref = f"{_colname(ci)}{ri}"
            style = ' s="1"' if ri == 1 else ""
            if isinstance(val, bool):
                val = str(val)
            if isinstance(val, (int, float)):
                out.append(f'<c r="{ref}"{style}><v>{val}</v></c>')
            else:
                out.append(f'<c r="{ref}"{style} t="inlineStr"><is>'
                           f'<t xml:space="preserve">{_esc("" if val is None else val)}</t></is></c>')
        out.append("</row>")
    out.append("</sheetData></worksheet>")
    return "".join(out)


def write_xlsx(path, sheets):
    n = len(sheets)
    ctypes = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
              '<Default Extension="xml" ContentType="application/xml"/>',
              '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
              '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>']
    for i in range(1, n + 1):
        ctypes.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
                      'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
    ctypes.append("</Types>")

    root_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                 '</Relationships>')

    sheet_tags, rel_tags = [], []
    for i, (name, _) in enumerate(sheets, 1):
        sheet_tags.append(f'<sheet name="{_esc(name)[:31]}" sheetId="{i}" r:id="rId{i}"/>')
        rel_tags.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>')
    rel_tags.append(f'<Relationship Id="rId{n + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>')

    workbook = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<workbook xmlns="{_M}" xmlns:r="{_R}"><sheets>'
                + "".join(sheet_tags) + "</sheets></workbook>")
    wb_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
               '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
               + "".join(rel_tags) + "</Relationships>")
    styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              f'<styleSheet xmlns="{_M}">'
              '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
              '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
              '<fills count="2"><fill><patternFill patternType="none"/></fill>'
              '<fill><patternFill patternType="gray125"/></fill></fills>'
              '<borders count="1"><border/></borders>'
              '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
              '<cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
              '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs>'
              '</styleSheet>')

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "".join(ctypes))
        z.writestr("_rels/.rels", root_rels)
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        z.writestr("xl/styles.xml", styles)
        for i, (_, rows) in enumerate(sheets, 1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", _sheet_xml(rows))
