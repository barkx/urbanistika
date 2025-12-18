import streamlit as st
from core import compute
from ui_dashboard import render_dashboard, eur_fmt, eur_m2_fmt, area_fmt

def render_tab(inputs: dict):
    st.subheader("Ekonomika")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        inputs["land_price_eur_m2"] = st.number_input("Cena zemljišča (€/m² parcele)", 0.0, step=10.0, value=float(inputs["land_price_eur_m2"]))
    with c2:
        inputs["cost_above_eur_m2"] = st.number_input("Gradnja nad terenom (€/m² BTP)", 0.0, step=10.0, value=float(inputs["cost_above_eur_m2"]))
    with c3:
        inputs["cost_below_eur_m2"] = st.number_input("Gradnja pod terenom (€/m² BTP)", 0.0, step=10.0, value=float(inputs["cost_below_eur_m2"]))
    with c4:
        inputs["soft_cost_pct"] = st.number_input("Soft costs (%)", 0.0, 50.0, step=0.5, value=float(inputs["soft_cost_pct"]))

    inputs["sales_price_eur_m2"] = st.number_input("Prodajna cena (€/m² NFA)", 0.0, step=50.0, value=float(inputs["sales_price_eur_m2"]))

    r = compute(inputs)
    render_dashboard(r, net_to_gross=inputs["net_to_gross"])

    econ = r["econ"]
    st.markdown("#### Razčlenitev investicije")
    a, b, c, d = st.columns(4)
    a.metric("Zemljišče", eur_fmt(econ["land_cost"]))
    b.metric("Hard cost", eur_fmt(econ["hard_cost"]))
    c.metric("Soft cost", eur_fmt(econ["soft_cost"]))
    d.metric("Skupaj", eur_fmt(econ["total_invest"]))

    st.markdown("#### Površine in kazalniki")
    e, f, g, h = st.columns(4)
    e.metric("Nadzemni BTP", area_fmt(r["btp_above"]))
    f.metric("Podzemni BTP", area_fmt(econ["btp_below"]))
    g.metric("Cost / m² (NFA)", eur_m2_fmt(econ["cost_per_m2_nfa"]))
    h.metric("Prodajna cena / m²", eur_m2_fmt(econ["sales_price_m2"]))

    st.markdown("#### Prihodki in margin (ocena)")
    i, j, k = st.columns(3)
    i.metric("Prihodki", eur_fmt(econ["revenue"]))
    j.metric("Margin", eur_fmt(econ["margin_abs"]))
    k.metric("Margin %", f"{econ['margin_pct']*100:.1f} %")

    return inputs
