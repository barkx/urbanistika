import streamlit as st
from core import compute, compute_units
from ui_dashboard import render_dashboard


def render_tab(inputs: dict):
    st.subheader("Stanovanja")

    building_footprint = (
        float(inputs["stevilo_lamel"]) * float(inputs["dolzina_lamele_m"]) * float(inputs["sirina_lamele_m"])
    )
    units_auto = compute_units(inputs, building_footprint)["units_auto"]

    st.markdown("#### Končno število stanovanj")
    selected_units = int(inputs.get("st_stanovanj", units_auto) or units_auto)
    inputs["st_stanovanj"] = st.number_input(
        "Število stanovanj",
        min_value=1,
        step=1,
        value=selected_units,
        help=f"Avtomatski izračun predlaga {units_auto} stanovanj na podlagi vnesenih parametrov."
    )

    inputs["units_mode"] = st.radio(
        "Način določanja št. stanovanj",
        ["AUTO", "ROČNO"],
        index=0 if inputs["units_mode"] == "AUTO" else 1
    )

    if inputs["units_mode"] == "ROČNO":
        st.caption("V načinu ROČNO se tipologije ne uporabljajo za izračun št. stanovanj.")
    else:
        st.caption(
            "V načinu AUTO se št. stanovanj izračuna iz NFA (BTP_nadz × neto/bruto) / povp. velikost stanovanja, "
            "končni rezultat pa lahko po potrebi prilagodite zgoraj."
        )
        st.markdown("#### Tipologije (delež + povprečna velikost)")
        for i, t in enumerate(inputs["typologies"]):
            colA, colB, colC = st.columns([2, 1, 1])
            with colA:
                inputs["typologies"][i]["name"] = st.text_input(
                    f"Ime tipologije {i+1}",
                    value=t["name"],
                    key=f"t_name_{i}"
                )
            with colB:
                inputs["typologies"][i]["share_pct"] = st.number_input(
                    f"Delež % ({i+1})",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(t["share_pct"]),
                    step=1.0,
                    key=f"t_share_{i}"
                )
            with colC:
                inputs["typologies"][i]["avg_m2"] = st.number_input(
                    f"Povp. m² ({i+1})",
                    min_value=10.0,
                    max_value=200.0,
                    value=float(t["avg_m2"]),
                    step=1.0,
                    key=f"t_m2_{i}"
                )

    r = compute(inputs)
    render_dashboard(r, net_to_gross=inputs["net_to_gross"])
    return inputs
