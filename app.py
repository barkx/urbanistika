import streamlit as st
from pathlib import Path
from tabs import informacije, parcela, faktorji, tipologije, stavbe, stanovanja, klet, ekonomika, optimizacija, izpis

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(page_title="URBANISTIKA", layout="wide")

# =================================================
# HEADER (LOGO + NASLOV – PORAVNANO BLIŽJE)
# =================================================
logo_path = Path("assets/logo.png")

col_logo, col_title = st.columns([1, 20], vertical_alignment="center")

with col_logo:
    if logo_path.exists():
        st.image(str(logo_path), width=90)

with col_title:
    st.markdown(
        """
        <div style="line-height:1.05; margin-left:-10px;">
            <div style="font-size:3.0em; font-weight:700; letter-spacing:0.04em;">
                URBANISTIKA
            </div>
            <div style="font-size:1.15em; color:#555; margin-top:2px;">
                Urbanistično-ekonomski kalkulator
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# =================================================
# SESSION STATE
# =================================================
if "inputs" not in st.session_state:
    st.session_state.inputs = {
        "parcela_m2": 5000,
        "fi": 1.35,
        "fz": 0.35,
        "fzp_min_pct": 20,
        "stevilo_lamel": 3,
        "dolzina_lamele_m": 40,
        "sirina_lamele_m": 14,
        "st_etas_nadz": 4,
        "net_to_gross": 0.82,
        "units_mode": "RAČUNSKO",
        "st_stanovanj": 76,
        "default_avg_unit_m2": 60.0,
        "typologies": [
            {"name": "1-sobno", "share_pct": 20.0, "avg_m2": 35.0},
            {"name": "2-sobno", "share_pct": 45.0, "avg_m2": 55.0},
            {"name": "3-sobno", "share_pct": 30.0, "avg_m2": 75.0},
            {"name": "4-sobno", "share_pct": 5.0, "avg_m2": 95.0},
        ],
        "pm_na_stanovanje": 1.5,
        "visitor_share": 0.33,
        "area_per_pm_garage_m2": 25.0,
        "area_per_pm_surface_m2": 25.0,
        "garage_eff_k1": 0.70,
        "garage_eff_k2": 0.85,
        "ramp_footprint_m2": 200.0,
        "surface_mult": 1.00,
        "scenario": "K-2",
        "land_price_eur_m2": 450.0,
        "cost_above_eur_m2": 1400.0,
        "cost_below_eur_m2": 1100.0,
        "soft_cost_pct": 12.0,
        "sales_price_eur_m2": 3200.0,
        "project_name": "",
        "project_code": "",
        "parcel_no": "",
        "cadastral_municipality": "",
    }

inputs = st.session_state.inputs

# =================================================
# TABS
# =================================================
tab_objs = st.tabs([
    "Informacije",
    "Parcela",
    "Faktorji",
    "Tipologije",
    "Stavbe",
    "Stanovanja",
    "Klet",
    "Ekonomika",
    "Optimizacija",
    "Izpis",
])

with tab_objs[0]:
    inputs = informacije.render_tab(inputs)
with tab_objs[1]:
    inputs = parcela.render_tab(inputs)
with tab_objs[2]:
    inputs = faktorji.render_tab(inputs)
with tab_objs[3]:
    inputs = tipologije.render_tab(inputs)
with tab_objs[4]:
    inputs = stavbe.render_tab(inputs)
with tab_objs[5]:
    inputs = stanovanja.render_tab(inputs)
with tab_objs[6]:
    inputs = klet.render_tab(inputs)
with tab_objs[7]:
    inputs = ekonomika.render_tab(inputs)
with tab_objs[8]:
    inputs = optimizacija.render_tab(inputs)
with tab_objs[9]:
    inputs = izpis.render_tab(inputs)

st.session_state.inputs = inputs

# =================================================
# FOOTER
# =================================================
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #ffffff;
        border-top: 1px solid #e0e0e0;
        padding: 8px 0;
        font-size: 0.8em;
        color: #555;
        z-index: 100;
        text-align: center;
        line-height: 1.5;
    }
    </style>

    <div class="footer">
        <div>
            <strong>Urbanistično-ekonomski kalkulator</strong> · Raziskovalni program ·
            Marcel Žnidarič, d.i.a. (UN) · LUZ, d.d.
        </div>
        <div style="font-style: italic;">
            Interno razvojno orodje · Verzija v1.1.0 · 2025
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
