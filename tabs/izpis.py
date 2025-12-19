import re
from io import BytesIO
from pathlib import Path

import streamlit as st
from core import compute
from pdf_export import build_project_description_markdown


# =================================================
# REGISTER UNICODE FONTS (ŠUMNIKI + BOLD)
# =================================================
def _register_unicode_fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font_dir = Path("assets/fonts")
    regular_path = font_dir / "DejaVuSans.ttf"
    bold_path = font_dir / "DejaVuSans-Bold.ttf"

    if not regular_path.exists():
        raise FileNotFoundError(
            f"Manjka Unicode font: {regular_path}. "
            "Dodaj DejaVuSans.ttf za pravilen izpis šumnikov."
        )

    registered = set(pdfmetrics.getRegisteredFontNames())

    if "DejaVuSans" not in registered:
        pdfmetrics.registerFont(TTFont("DejaVuSans", str(regular_path)))

    if bold_path.exists() and "DejaVuSans-Bold" not in registered:
        pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(bold_path)))

    # Ključno: family map, da <b> preklopi na bold
    registered = set(pdfmetrics.getRegisteredFontNames())
    if "DejaVuSans-Bold" in registered:
        pdfmetrics.registerFontFamily(
            "DejaVuSans",
            normal="DejaVuSans",
            bold="DejaVuSans-Bold",
            italic="DejaVuSans",
            boldItalic="DejaVuSans-Bold",
        )


# =================================================
# MARKDOWN → REPORTLAB FLOWABLES
# (naslovi, bold, alineje, odstavki)
# =================================================
def _inline_format(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def _md_to_flowables(md: str):
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import Paragraph, Spacer, ListFlowable, ListItem

    styles = getSampleStyleSheet()

    # Večji fonti za poglavja (H1/H2)
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName="DejaVuSans-Bold",
        fontSize=18,
        leading=22,
        spaceAfter=10,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName="DejaVuSans-Bold",
        fontSize=14,
        leading=18,
        spaceBefore=6,
        spaceAfter=8,
    )
    p = ParagraphStyle(
        "P",
        parent=styles["BodyText"],
        fontName="DejaVuSans",
        fontSize=10.5,
        leading=14,
        spaceAfter=6,
    )

    flow = []
    bullet_items: list[str] = []
    lines = [ln.rstrip() for ln in (md or "").strip().splitlines()]

    def flush_bullets():
        nonlocal bullet_items
        if bullet_items:
            flow.append(
                ListFlowable(
                    [ListItem(Paragraph(t, p)) for t in bullet_items],
                    bulletType="bullet",
                    leftIndent=18,
                )
            )
            flow.append(Spacer(1, 4))
            bullet_items = []

    for ln in lines:
        if not ln.strip():
            flush_bullets()
            flow.append(Spacer(1, 4))
            continue

        if ln.startswith("## "):
            flush_bullets()
            flow.append(Paragraph(_inline_format(ln[3:]), h2))
            continue

        if ln.startswith("# "):
            flush_bullets()
            flow.append(Paragraph(_inline_format(ln[2:]), h1))
            continue

        if ln.startswith("- "):
            bullet_items.append(_inline_format(ln[2:]))
            continue

        # pod-alineje iz vzorca ("  - ...")
        if ln.startswith("  - "):
            bullet_items.append(_inline_format(ln[4:]))
            continue

        flush_bullets()
        flow.append(Paragraph(_inline_format(ln), p))

    flush_bullets()
    return flow


# =================================================
# BUILD PDF (OBLIKOVAN + ŠUMNIKI + BOLD)
# =================================================
def _build_pdf_rich(inputs: dict, r: dict) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate
    from reportlab.lib.units import mm

    _register_unicode_fonts()

    md = build_project_description_markdown(inputs, r)

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=(inputs.get("project_code") or "URBCalc"),
    )

    story = _md_to_flowables(md)
    doc.build(story)

    return buf.getvalue()


# =================================================
# TAB RENDER
# =================================================
def render_tab(inputs: dict, embedded: bool = False):
    if not embedded:
        st.subheader("Izpis podatkov (PDF)")

    r = compute(inputs)

    st.markdown("#### Opis projekta")
    with st.expander("Opis projekta (razširi za ogled)", expanded=False):
        st.markdown(build_project_description_markdown(inputs, r))

    st.markdown("#### Prenos poročila")
    st.caption(
        "PDF poročilo vsebuje oblikovan opis projekta (večji naslovi, odebelitve, alineje) "
        "in podpira pravilni izpis šumnikov."
    )

    try:
        pdf_bytes = _build_pdf_rich(inputs, r)
        filename = (inputs.get("project_code") or "URBCalc") + "_porocilo.pdf"

        st.download_button(
            label="Prenesi PDF poročilo",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
        )

    except FileNotFoundError as e:
        st.error(str(e))
    except ImportError:
        st.error(
            "Za izpis PDF je potreben paket 'reportlab'. "
            "Namesti ga z: pip install reportlab"
        )
    except Exception as e:
        st.error(f"Napaka pri generiranju PDF: {e}")

    return inputs
