import streamlit as st
from core import compute
from ui_dashboard import render_dashboard


def render_tab(inputs: dict):
    st.subheader("Stanovanja")
    inputs["units_mode"] = st.radio(
        "Način določanja št. stanovanj",
        ["AUTO", "ROČNO"],
        index=0 if inputs["units_mode"] == "AUTO" else 1
    )

    if inputs["units_mode"] == "ROČNO":
        inputs["st_stanovanj"] = st.number_input(
            "Število stanovanj (ročno)",
            min_value=1,
            step=1,
            value=int(inputs["st_stanovanj"])
        )
        st.caption("V načinu ROČNO se tipologije ne uporabljajo za izračun št. stanovanj.")
    else:
        st.caption("V načinu AUTO se št. stanovanj izračuna iz NFA (BTP_nadz × neto/bruto) / povp. velikost stanovanja.")
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

    st.markdown("#### Končno število stanovanj")
    st.metric("Št. stanovanj", int(r["units"]))
    return inputs
