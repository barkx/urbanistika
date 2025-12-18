import streamlit as st
from core import compute
from ui_dashboard import render_dashboard

def render_tab(inputs: dict):
    st.subheader("Klet / parkiranje")

    inputs["scenario"] = st.radio(
        "Izberi scenarij",
        ["K-1", "K-1 + teren", "K-2"],
        index=["K-1", "K-1 + teren", "K-2"].index(inputs["scenario"])
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("Stanovanja:")
        st.caption("AUTO nastaviš v zavihku Stanovanja.")
        if inputs["units_mode"] == "ROČNO":
            inputs["st_stanovanj"] = st.number_input("Št. stanovanj (ROČNO)", min_value=1, step=1, value=int(inputs["st_stanovanj"]))
    with c2:
        inputs["pm_na_stanovanje"] = st.number_input("PM na stanovanje", min_value=0.5, step=0.1, value=float(inputs["pm_na_stanovanje"]))
    with c3:
        inputs["visitor_share"] = st.slider("Delež obiskovalcev v skupnih PM", 0.0, 0.6, float(inputs["visitor_share"]), 0.01)

    st.markdown("#### Realistične nastavitve garaže")
    c4, c5, c6 = st.columns(3)
    with c4:
        inputs["garage_eff_k1"] = st.number_input("Izkoristek garaže K-1 (0–1)", 0.40, 0.95, float(inputs["garage_eff_k1"]), 0.01)
    with c5:
        inputs["garage_eff_k2"] = st.number_input("Izkoristek garaže K-2 (0–1)", 0.40, 0.95, float(inputs["garage_eff_k2"]), 0.01)
    with c6:
        inputs["ramp_footprint_m2"] = st.number_input("Dodatek (rampa/tehnika) odtis (m²)", 0.0, 800.0, float(inputs["ramp_footprint_m2"]), 10.0)

    c7, c8, c9 = st.columns(3)
    with c7:
        inputs["area_per_pm_garage_m2"] = st.number_input("m² na PM v kleti (bruto)", 18.0, 40.0, float(inputs["area_per_pm_garage_m2"]), 1.0)
    with c8:
        inputs["area_per_pm_surface_m2"] = st.number_input("m² na PM na terenu", 15.0, 40.0, float(inputs["area_per_pm_surface_m2"]), 1.0)
    with c9:
        inputs["surface_mult"] = st.number_input("Faktor manipulacije terena (1.0–1.5)", 1.0, 1.5, float(inputs["surface_mult"]), 0.05)

    r = compute(inputs)
    render_dashboard(r, net_to_gross=inputs["net_to_gross"])
    return inputs
