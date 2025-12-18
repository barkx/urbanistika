import streamlit as st
from core import compute
from ui_dashboard import render_dashboard

def render_tab(inputs: dict):
    st.subheader("Informacije o projektu")

    c1, c2 = st.columns(2)
    with c1:
        inputs["project_name"] = st.text_input("Ime projekta", value=str(inputs.get("project_name", "")))
        inputs["project_code"] = st.text_input("Šifra projekta", value=str(inputs.get("project_code", "")))
    with c2:
        inputs["cadastral_municipality"] = st.text_input("Katastrska občina", value=str(inputs.get("cadastral_municipality", "")))
        inputs["parcel_no"] = st.text_input("Parcelna številka", value=str(inputs.get("parcel_no", "")))

    st.caption("Ti podatki se uporabijo v PDF izpisu.")
    r = compute(inputs)
    render_dashboard(r, net_to_gross=inputs["net_to_gross"])
    return inputs
