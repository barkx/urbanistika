import streamlit as st
from core import compute
from pdf_export import build_pdf, build_project_description_markdown

def render_tab(inputs: dict, embedded: bool = False):
    """Render the PDF export section.

    When embedded=True, the caller is responsible for rendering the surrounding header.
    """
    if not embedded:
        st.subheader("Izpis podatkov (PDF)")

    r = compute(inputs)

    # Preview: expanded project description (no dashboard duplication)
    st.markdown("#### Opis projekta (razširjeno)")
    st.markdown(build_project_description_markdown(inputs, r))

    st.markdown("#### Prenos poročila")
    st.caption("PDF vključuje samo opis projekta (razširjena verzija zgoraj).")

    try:
        pdf_bytes = build_pdf(inputs, r)
        filename = (inputs.get("project_code") or "URBCalc") + "_porocilo.pdf"
        st.download_button(
            label="📄 Prenesi PDF poročilo",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf"
        )
    except ImportError:
        st.error("Za izpis PDF je potreben paket 'reportlab'. Namesti ga z: pip install reportlab")
    except Exception as e:
        st.error(f"Napaka pri generiranju PDF: {e}")

    return inputs
