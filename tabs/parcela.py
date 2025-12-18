import streamlit as st
from core import compute
from ui_dashboard import render_dashboard

def render_tab(inputs: dict):
    st.subheader("Parcela")
    inputs["parcela_m2"] = st.number_input(
        "Velikost parcele (m²)",
        min_value=100,
        step=100,
        value=int(inputs["parcela_m2"])
    )
    st.caption("Sprememba parcele vpliva na dopustni odtis (FZ) in na delež raščenega terena (FZP).")
    r = compute(inputs)
    render_dashboard(r, net_to_gross=inputs["net_to_gross"])
    return inputs
