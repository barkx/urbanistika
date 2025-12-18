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
    net_to_gross = float(inputs.get("net_to_gross", 0) or 0)

    # Program
    units = int(r.get("units", 0) or 0)
    units_mode = _safe(r.get("units_mode") or inputs.get("units_mode") or "")

    # Areas
    btp_above = float(r.get("btp_above", 0) or 0)
    btp_below = float(r.get("btp_below", 0) or 0)
    net_area = float(r.get("net_area", 0) or 0)

    # Parking
    pm_total = int(r.get("pm_total", 0) or 0)
    pm_basement = int(r.get("pm_in_basement", 0) or 0)
    pm_surface = int(r.get("pm_on_surface", 0) or 0)
    pm_per_unit = float(inputs.get("pm_na_stanovanje", 0) or 0)
    visitor_share = float(inputs.get("visitor_share", 0) or 0)

    # Typologies (structure)
    typ = inputs.get("typologies", []) or []

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

    def klet_fmt(s: str) -> str:
        s = (s or "").strip()
        if s == "K-1":
            return "1 kletna etaža (garaža)"
        if s == "K-1 + teren":
            return "1 kletna etaža + del parkiranja na terenu"
        if s == "K-2":
            return "2 kletni etaži (garaža)"
        return s or "—"

    def typology_lines() -> str:
        if not typ:
            return "—"
        parts = []
        for t in typ:
            try:
                name = _safe(t.get("name", ""))
                share = float(t.get("share_pct", 0) or 0)
                avg = float(t.get("avg_m2", 0) or 0)
                parts.append(f"{name}: {share:.0f} % (≈ {avg:.0f} m²)")
            except Exception:
                continue
        return "<br/>".join(parts) if parts else "—"

    # --- Template helpers -------------------------------------------------
    def etaznost() -> str:
        # floors = total above-ground floors (incl. P)
        return f"P + {max(floors - 1, 0)}"

    def klet_levels_text() -> str:
        s = (scenario or "").strip()
        if s == "K-2":
            return "z dvema kletnima etažama (K-2, K-1)"
        if s == "K-1":
            return "z eno kletno etažo (K-1)"
        if s == "K-1 + teren":
            return "z eno kletno etažo (K-1) in delnim parkiranjem na terenu"
        return "(kletni scenarij po izbiri)"

    def typology_block_html() -> str:
        if not typ:
            return "—"
        lines = []
        for t in typ:
            try:
                name = _safe(t.get("name", ""))
                share = float(t.get("share_pct", 0) or 0)
                avg = float(t.get("avg_m2", 0) or 0)
                approx_n = int(round(units * share / 100.0)) if units else 0
                lines.append(
                    f"{name}:<br/>"
                    f"{share:.0f} % (≈ {approx_n} enot), povp. velikost ≈ {avg:.0f} m²"
                )
            except Exception:
                continue
        return "<br/><br/>".join(lines) if lines else "—"

    # --- Section 1 --------------------------------------------------------
    p1 = (
        "<b>1. Osnovna zasnova in tipologija objektov</b><br/><br/>"
        f"Projekt obravnava izgradnjo stanovanjske soseske s skupno <b>{units}</b> stanovanji, "
        f"umeščene v večstanovanjske objekte etažnosti <b>{etaznost()}</b> {klet_levels_text()}. "
        f"Objekti so zasnovani kot kompaktna urbana struktura (lamelna zasnova: <b>{n_lamel}</b> lamel), "
        "z racionalnim tlorisnim razporedom, ki omogoča optimalno izrabo prostora ob hkratnem zagotavljanju "
        "visokega deleža zelenih površin.<br/><br/>"
        "Nadzemni del objektov je namenjen izključno bivanju, podzemni del pa parkiranju, tehničnim prostorom "
        "in prometnim povezavam."
    )

    # --- Section 2 --------------------------------------------------------
    fi_val = float(r.get("FI", 0) or 0)
    fi_lim = float(inputs.get("fi", 0) or 0)
    fz_val = float(r.get("building_footprint", 0) or 0)
    fz_lim = float(r.get("fz_max_footprint", 0) or 0)
    fzp_val_pct = float(r.get("fzp", 0) or 0) * 100.0
    fzp_min_pct = float(inputs.get("fzp_min_pct", 0) or 0)

    p2 = (
        "<b>2. Urbanistični kazalniki in skladnost</b><br/><br/>"
        "Projekt izpolnjuje vse ključne urbanistične pogoje in omejitve:<br/><br/>"
        "<b>Faktor izrabe (FI):</b><br/>"
        f"Dosežen {fi_val:.2f} / dovoljen {fi_lim:.2f} → <b>{'skladno' if bool(r.get('fi_ok')) else 'neskladno'}</b><br/><br/>"
        "<b>Faktor zazidanosti (FZ):</b><br/>"
        f"Odtis stavb {area_fmt(fz_val)} / dovoljeno {area_fmt(fz_lim)} → <b>{'skladno' if bool(r.get('fz_ok')) else 'neskladno'}</b><br/><br/>"
        "<b>Faktor zelenih površin (FZP):</b><br/>"
        f"Dosežen {pct_fmt(fzp_val_pct)} / minimalno zahtevano {pct_fmt(fzp_min_pct)} → <b>{'skladno' if bool(r.get('fzp_ok')) else 'neskladno'}</b><br/><br/>"
        "Zasnova tako omogoča visoko stopnjo zazelenitve in ugodno bivalno mikroklimo ob skoraj maksimalni "
        "dovoljeni izrabi zemljišča."
    )

    # --- Section 3 --------------------------------------------------------
    p3 = (
        "<b>3. Program in struktura stanovanj</b><br/><br/>"
        f"<b>Skupno število stanovanj:</b> {units}<br/><br/>"
        f"<b>Neto/bruto faktor:</b> {net_to_gross:.2f}<br/><br/>"
        "<b>Struktura stanovanj (ocena):</b><br/><br/>"
        f"{typology_block_html()}<br/><br/>"
        "Struktura stanovanj je uravnotežena in prilagojena trgu, s poudarkom na manjših in srednje velikih "
        "stanovanjih, ki praviloma predstavljajo večinski delež povpraševanja.<br/><br/>"
        "<b>Skupna bruto tlorisna površina (BTP):</b><br/><br/>"
        f"nadzemno: {area_fmt(btp_above)}<br/>"
        "podzemno: 0 m² (stanovanjski program)"
    )

    # --- Section 4 --------------------------------------------------------
    p4 = (
        "<b>4. Klet, parkiranje in prometna ureditev</b><br/><br/>"
        "<b>Tip kleti:</b><br/><br/>"
        f"{klet_fmt(_safe(scenario))}<br/><br/>"
        "<b>Izkoristek garaže:</b><br/><br/>"
        f"K-1: {float(inputs.get('garage_eff_k1', 0) or 0):.2f}<br/>"
        f"K-2: {float(inputs.get('garage_eff_k2', 0) or 0):.2f}<br/><br/>"
        f"Površina za rampe, tehnične prostore in komunikacije: ≈ {area_fmt(float(inputs.get('ramp_footprint_m2', 0) or 0))}<br/><br/>"
        "<b>Parkiranje:</b><br/><br/>"
        f"Skupno parkirnih mest (PM): {pm_total}<br/>"
        f"v kleti: {pm_basement} PM<br/>"
        f"na terenu: {pm_surface} PM<br/><br/>"
        f"Parkirna norma: {pm_per_unit:.2f} PM / stanovanje<br/>"
        f"vključuje cca {visitor_share:.0%} PM za obiskovalce<br/><br/>"
        "Prometne in manipulacijske površine so dimenzionirane skladno s predpisi ter omogočajo nemoten dostop "
        "intervencijskim, dostavnim in servisnim vozilom."
    )

    # --- Section 5 --------------------------------------------------------
    growing_area = float(r.get("growing_area", 0) or 0)
    p5 = (
        "<b>5. Zunanja ureditev in raščen teren</b><br/><br/>"
        f"Raščen teren: cca {area_fmt(growing_area)}, kar predstavlja {pct_fmt(fzp_val_pct)} celotne površine območja.<br/><br/>"
        "Zunanje površine vključujejo zelene površine, pešpoti in skupne odprte prostore. "
        "Prednost je minimalno površinsko parkiranje, kar izboljšuje kakovost bivanja in vizualno podobo soseske."
    )

    # --- Section 6 --------------------------------------------------------
    p6 = (
        "<b>6. Komunalna opremljenost in ITS</b><br/><br/>"
        "Objekti bodo priključeni na obstoječo oziroma predvideno komunalno infrastrukturo:<br/><br/>"
        "• vodovod<br/>"
        "• fekalna in meteorna kanalizacija<br/>"
        "• elektroenergetsko omrežje<br/>"
        "• telekomunikacijsko omrežje<br/><br/>"
        "ITS (infrastrukturno-tehnične storitve) vključujejo tudi organizacijo intervencijskih poti, dostopov ter "
        "logično razporeditev funkcionalnih površin v sklopu parcelacije in zunanje ureditve."
    )

    # --- Section 7 --------------------------------------------------------
    p7 = (
        "<b>7. Ekonomski povzetek (ocena)</b><br/><br/>"
        f"Skupna investicijska vrednost: {eur_fmt(invest)}<br/><br/>"
        f"Ocenjeni prihodki od prodaje: {eur_fmt(revenue)}<br/><br/>"
        f"Razlika (rezultat projekta): {eur_fmt(margin)}"
    )

    # --- Section 8 --------------------------------------------------------
    p8 = (
        "<b>8. Zaključna ocena</b><br/><br/>"
        f"Projekt je z vidika urbanističnih kazalnikov, prostorske izrabe in bivalne kakovosti ocenjen kot <b>{_safe(r.get('status'))}</b>. "
        "V primeru negativnega rezultata je smiselno razmisliti o:<br/><br/>"
        "• optimizaciji investicijskih stroškov,<br/>"
        "• prilagoditvi strukture stanovanj,<br/>"
        "• izboljšanju prodajnih cen oziroma faznosti izvedbe."
    )

    # Optional title line (project name/code) if present
    prefix = ""
    if proj or code:
        prefix = f"<b>{_safe(proj)}</b> {('(' + _safe(code) + ')') if code else ''}".strip()
        prefix = prefix.replace("  ", " ")

    paragraphs = [p1, p2, p3, p4, p5, p6, p7, p8]
    if prefix:
        paragraphs.insert(0, prefix)
    return paragraphs


def build_project_description_markdown(inputs: Dict[str, Any], results: Dict[str, Any]) -> str:
    """A readable (Streamlit-friendly) markdown version of the project description."""

    html_paras = _build_project_description_html(inputs, results)
    md_parts: List[str] = []
    for para in html_paras:
        md = para.replace("<b>", "**").replace("</b>", "**")
        md = md.replace("<br/>", "\n")
        md_parts.append(md)
    return "\n\n".join(md_parts)

def build_pdf(inputs: Dict[str, Any], results: Dict[str, Any]) -> bytes:
    """Build a short PDF (A4) that includes ONLY the project description (Opis projekta).

    Uses an embedded DejaVuSans font to support Slovene characters (šumniki).
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.utils import ImageReader
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

    # Optional: project map image (uploaded in the first tab)
    map_bytes = inputs.get("map_image_bytes")
    if map_bytes:
        try:
            img_buf = BytesIO(map_bytes)
            ir = ImageReader(img_buf)
            iw, ih = ir.getSize()
            max_w = doc.width
            max_h = doc.height * 0.35  # keep the map reasonably compact
            scale = max_w / float(iw) if iw else 1.0
            w = iw * scale
            h = ih * scale
            if h > max_h and ih:
                scale = max_h / float(ih)
                w = iw * scale
                h = ih * scale
            img_buf.seek(0)
            story.append(Image(img_buf, width=w, height=h))
            story.append(Spacer(1, 12))
        except Exception:
            # If the image fails to render, just skip it.
            pass

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
