import streamlit as st
from core import compute
from ui_dashboard import render_dashboard

def render_tab(inputs: dict):
    st.subheader("Stavbe")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        inputs["stevilo_lamel"] = st.number_input("Število lamel", min_value=1, step=1, value=int(inputs["stevilo_lamel"]))
    with c2:
        inputs["dolzina_lamele_m"] = st.number_input("Dolžina lamele (m)", min_value=5, step=1, value=int(inputs["dolzina_lamele_m"]))
    with c3:
        inputs["sirina_lamele_m"] = st.number_input("Širina lamele (m)", min_value=5, step=1, value=int(inputs["sirina_lamele_m"]))
    with c4:
        inputs["st_etas_nadz"] = st.number_input("Št. nadzemnih etaž (P+3=4)", min_value=1, step=1, value=int(inputs["st_etas_nadz"]))
    with c5:
        inputs["net_to_gross"] = st.number_input("Neto/Bruto (NFA/BTP)", min_value=0.50, max_value=0.95, step=0.01, value=float(inputs["net_to_gross"]))

    st.caption("Dimenzije, etaže in neto/bruto vplivajo na NFA in avtomatsko število stanovanj (če je AUTO).")
    r = compute(inputs)
    render_dashboard(r, net_to_gross=inputs["net_to_gross"])
    return inputs
