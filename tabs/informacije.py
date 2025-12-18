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

    st.markdown("### Karta (slika)")
    uploaded = st.file_uploader("Naloži sliko- karto (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if uploaded is not None:
        inputs["map_image_bytes"] = uploaded.getvalue()
        inputs["map_image_name"] = uploaded.name

    if inputs.get("map_image_bytes"):
        cimg1, cimg2 = st.columns([1, 3])
        with cimg1:
            if st.button("Odstrani karto"):
                inputs.pop("map_image_bytes", None)
                inputs.pop("map_image_name", None)
                st.rerun()
        with cimg2:
            # Keep preview compact so it comfortably fits on the page.
            st.image(
                inputs["map_image_bytes"],
                caption=inputs.get("map_image_name", "Karta"),
                width=520,
            )

    st.caption("Ti podatki se uporabijo v PDF izpisu.")
    r = compute(inputs)
    render_dashboard(r, net_to_gross=inputs["net_to_gross"])
    return inputs
