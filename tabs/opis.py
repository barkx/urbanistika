import streamlit as st
from core import compute
from ui_dashboard import render_dashboard, area_fmt, pct_fmt, eur_fmt

def _yesno(ok: bool) -> str:
    return "SKLADNO" if ok else "NESKLADNO"

def render_tab(inputs: dict, embedded: bool = False):
    """Render the project description.

    When embedded=True, the caller is responsible for rendering the surrounding header.
    """
    if not embedded:
        st.subheader("Opis projekta")

    r = compute(inputs)
    render_dashboard(r, net_to_gross=inputs["net_to_gross"])

    # Extract data
    proj = inputs.get("project_name", "")
    code = inputs.get("project_code", "")
    ko = inputs.get("cadastral_municipality", "")
    parc_no = inputs.get("parcel_no", "")

    P = r["P"]
    n_lamel = int(inputs["stevilo_lamel"])
    floors = int(inputs["st_etas_nadz"])
    scenario = inputs["scenario"]

    econ = r["econ"]
    margin = econ.get("margin_abs", 0.0)
    revenue = econ.get("revenue", 0.0)
    invest = econ.get("total_invest", 0.0)

    text = f"""**Investitor** želi na parceli **{parc_no}** v katastrski občini **{ko}** na zemljišču velikosti **{area_fmt(P)}** izvesti **{n_lamel}** večstanovanjske stavbe v obliki **lamel** (P+{floors-1}), ki jih podpira izbrani scenarij parkiranja **{scenario}**.

**Ključni urbanistični faktorji in skladnost**
- Faktor izrabe (FI): dosežen **{r['FI']:.2f}** / limit **{inputs['fi']:.2f}** → **{_yesno(r['fi_ok'])}**
- Faktor zazidanosti (FZ): odtis stavb **{area_fmt(r['building_footprint'])}** / dopustno **{area_fmt(r['fz_max_footprint'])}** → **{_yesno(r['fz_ok'])}**
- Faktor zelenih površin (FZP): dosežen **{pct_fmt(r['fzp']*100)}** / min **{pct_fmt(r['FZP_min']*100)}** → **{_yesno(r['fzp_ok'])}**

**Program in parkiranje (ocena)**
- Program: **{r['units']} stanovanj** (način: {r['units_mode']})
- Parkiranje: **{r['pm_total']} PM** (klet: {r['pm_in_basement']}, teren: {r['pm_on_surface']})
- Raščen teren (ocena): **{area_fmt(r['growing_area'])}** ({pct_fmt(r['fzp']*100)})

**Ekonomski povzetek (ocena)**
- Skupna investicija: **{eur_fmt(invest)}**
- Prihodki: **{eur_fmt(revenue)}**
- Ostane (margin): **{eur_fmt(margin)}**

**Zaključek**
Projekt je trenutno ocenjen kot: **{r['status']}**."""

    st.markdown(text)

    st.download_button(
        "⬇️ Prenesi opis (TXT)",
        data=text,
        file_name=(code or "opis_projekta") + ".txt",
        mime="text/plain"
    )

    return inputs
