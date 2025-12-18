from __future__ import annotations

from io import BytesIO
from typing import Dict, Any, List
import os

def _safe(v: Any) -> str:
    return "" if v is None else str(v)


def _yesno(ok: bool) -> str:
    return "SKLADNO" if ok else "NESKLADNO"


def _build_project_description_html(inputs: Dict[str, Any], r: Dict[str, Any]) -> List[str]:
    """Return the project description as a list of HTML-ish paragraphs.

    ReportLab's Paragraph supports a small subset of HTML tags (e.g. <b>, <br/>).
    """
    proj = inputs.get("project_name", "")
    code = inputs.get("project_code", "")
    ko = inputs.get("cadastral_municipality", "")
    parc_no = inputs.get("parcel_no", "")

    P = float(r.get("P", 0) or 0)
    n_lamel = int(inputs.get("stevilo_lamel", 0) or 0)
    floors = int(inputs.get("st_etas_nadz", 0) or 0)
    scenario = inputs.get("scenario", "")

    econ = r.get("econ", {}) or {}
    margin = float(econ.get("margin_abs", 0) or 0)
    revenue = float(econ.get("revenue", 0) or 0)
    invest = float(econ.get("total_invest", 0) or 0)

    # Local formatting (kept simple and robust)
    def area_fmt(v: float) -> str:
        return f"{v:,.0f} m²".replace(",", " ")

    def pct_fmt(v: float) -> str:
        return f"{v:.1f} %"

    def eur_fmt(v: float) -> str:
        return f"{v:,.0f} €".replace(",", " ")

    p1 = (
        f"<b>Investitor</b> želi na parceli <b>{_safe(parc_no)}</b> v katastrski občini "
        f"<b>{_safe(ko)}</b> na zemljišču velikosti <b>{area_fmt(P)}</b> izvesti "
        f"<b>{n_lamel}</b> večstanovanjske stavbe v obliki <b>lamel</b> (P+{max(floors-1, 0)}), "
        f"ki jih podpira izbrani scenarij parkiranja <b>{_safe(scenario)}</b>."
    )

    p2 = (
        "<b>Ključni urbanistični faktorji in skladnost</b><br/>"
        f"• Faktor izrabe (FI): dosežen <b>{float(r.get('FI', 0)):.2f}</b> / limit <b>{float(inputs.get('fi', 0)):.2f}</b> → <b>{_yesno(bool(r.get('fi_ok')))}</b><br/>"
        f"• Faktor zazidanosti (FZ): odtis stavb <b>{area_fmt(float(r.get('building_footprint', 0) or 0))}</b> / dopustno <b>{area_fmt(float(r.get('fz_max_footprint', 0) or 0))}</b> → <b>{_yesno(bool(r.get('fz_ok')))}</b><br/>"
        f"• Faktor zelenih površin (FZP): dosežen <b>{pct_fmt(float(r.get('fzp', 0) or 0)*100)}</b> / min <b>{pct_fmt(float(r.get('FZP_min', 0) or 0)*100)}</b> → <b>{_yesno(bool(r.get('fzp_ok')))}</b>"
    )

    p3 = (
        "<b>Program in parkiranje (ocena)</b><br/>"
        f"• Program: <b>{_safe(r.get('units'))} stanovanj</b> (način: {_safe(r.get('units_mode'))})<br/>"
        f"• Parkiranje: <b>{_safe(r.get('pm_total'))} PM</b> (klet: {_safe(r.get('pm_in_basement'))}, teren: {_safe(r.get('pm_on_surface'))})<br/>"
        f"• Raščen teren (ocena): <b>{area_fmt(float(r.get('growing_area', 0) or 0))}</b> ({pct_fmt(float(r.get('fzp', 0) or 0)*100)})"
    )

    p4 = (
        "<b>Ekonomski povzetek (ocena)</b><br/>"
        f"• Skupna investicija: <b>{eur_fmt(invest)}</b><br/>"
        f"• Prihodki: <b>{eur_fmt(revenue)}</b><br/>"
        f"• Ostane (margin): <b>{eur_fmt(margin)}</b>"
    )

    p5 = f"<b>Zaključek</b><br/>Projekt je trenutno ocenjen kot: <b>{_safe(r.get('status'))}</b>."

    # Optional title line (project name/code) if present
    prefix = ""
    if proj or code:
        prefix = f"<b>{_safe(proj)}</b> {('(' + _safe(code) + ')') if code else ''}".strip()
        prefix = prefix.replace("  ", " ")

    paragraphs = [p1, p2, p3, p4, p5]
    if prefix:
        paragraphs.insert(0, prefix)
    return paragraphs

def build_pdf(inputs: Dict[str, Any], results: Dict[str, Any]) -> bytes:
    """Build a short PDF (A4) that includes ONLY the project description (Opis projekta).

    Uses an embedded DejaVuSans font to support Slovene characters (šumniki).
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    here = os.path.dirname(__file__)
    font_path = os.path.join(here, "assets", "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "title_dv",
        parent=styles["Title"],
        fontName="DejaVuSans",
        fontSize=18,
        leading=22,
        spaceAfter=10,
    )
    body_style = ParagraphStyle(
        "body_dv",
        parent=styles["BodyText"],
        fontName="DejaVuSans",
        fontSize=10.5,
        leading=14,
    )

    story: List[Any] = []

    title = inputs.get("project_name") or "Opis projekta"
    story.append(Paragraph(f"<b>{_safe(title)}</b>", title_style))

    for i, para in enumerate(_build_project_description_html(inputs, results)):
        if i == 0:
            # if the first line is a prefix (project name/code), keep it compact
            story.append(Paragraph(para, body_style))
            story.append(Spacer(1, 8))
            continue
        story.append(Paragraph(para, body_style))
        story.append(Spacer(1, 10))

    doc.build(story)
    return buf.getvalue()
