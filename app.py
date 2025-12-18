import streamlit as st
from tabs import informacije, opis, parcela, faktorji, stavbe, stanovanja, klet, ekonomika, optimizacija, izpis

st.set_page_config(page_title="Urbanistično-ekonomska analiza", layout="wide")
st.title("Urbanistično-ekonomska analiza poslovno-stanovanjskega niza")

if "inputs" not in st.session_state:
    st.session_state.inputs = {
        "parcela_m2": 5000,
        "fi": 1.34,
        "fz": 0.35,
        "fzp_min_pct": 20,

        "stevilo_lamel": 3,
        "dolzina_lamele_m": 40,
        "sirina_lamele_m": 14,
        "st_etas_nadz": 4,
        "net_to_gross": 0.82,

        "units_mode": "AUTO",
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

        # informacije o projektu
        "project_name": "",
        "project_code": "",

        "parcel_no": "",
        "cadastral_municipality": "",

    }

inputs = st.session_state.inputs

tab_objs = st.tabs([
    "Informacije",
    "Parcela",
    "Faktorji",
    "Stavbe",
    "Stanovanja",
    "Klet",
    "Ekonomika",
    "Optimizacija",
    "Opis projekta in izpis",
])

with tab_objs[0]:
    inputs = informacije.render_tab(inputs)
with tab_objs[1]:
    inputs = parcela.render_tab(inputs)
with tab_objs[2]:
    inputs = faktorji.render_tab(inputs)
with tab_objs[3]:
    inputs = stavbe.render_tab(inputs)
with tab_objs[4]:
    inputs = stanovanja.render_tab(inputs)
with tab_objs[5]:
    inputs = klet.render_tab(inputs)
with tab_objs[6]:
    inputs = ekonomika.render_tab(inputs)
with tab_objs[7]:
    inputs = optimizacija.render_tab(inputs)
with tab_objs[8]:
    st.subheader("Opis projekta in izpis")
    inputs = opis.render_tab(inputs, embedded=True)
    st.divider()
    inputs = izpis.render_tab(inputs, embedded=True)

st.session_state.inputs = inputs
