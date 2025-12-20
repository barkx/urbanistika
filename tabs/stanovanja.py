import streamlit as st
from core import compute, compute_units
from ui_dashboard import render_dashboard


def render_tab(inputs: dict):
    st.subheader("Stanovanja")

    building_footprint = (
        float(inputs["stevilo_lamel"]) * float(inputs["dolzina_lamele_m"]) * float(inputs["sirina_lamele_m"])
    )
    units_auto = compute_units(inputs, building_footprint)["units_auto"]

    st.markdown("#### Način določanja št. stanovanj")
    inputs["units_mode"] = st.radio(
        "Način določanja št. stanovanj",
        ["RAČUNSKO", "AVTO"],
        index=0 if inputs.get("units_mode") == "RAČUNSKO" else 1,
        help="V načinu RAČUNSKO se število stanovanj preračuna iz znanih podatkov. V načinu AVTO lahko rezultat "
        "ročno prilagodiš in spreminjaš deleže tipologij."
    )

    st.markdown("#### Končno število stanovanj")
    if inputs["units_mode"] == "RAČUNSKO":
        inputs["st_stanovanj"] = units_auto
        st.number_input(
            "Število stanovanj (računsko)",
            min_value=1,
            step=1,
            value=units_auto,
            disabled=True,
            help="Računski izračun zaklene število stanovanj na podlagi povprečne velikosti in razporeditve tipologij."
        )
        st.caption(
            f"Izračun temelji na povprečni velikosti {compute_units(inputs, building_footprint)['avg_unit_m2']:.1f} m² "
            "in trenutni razporeditvi tipologij."
        )

        st.markdown("#### Tipologije (informativno)")
        summary = []
        for t in inputs["typologies"]:
            share = float(t["share_pct"])
            approx_units = int(round(units_auto * share / 100.0)) if units_auto else 0
            summary.append({
                "Tipologija": t["name"],
                "Delež %": f"{share:.0f}",
                "Povp. m²": f"{float(t['avg_m2']):.0f}",
                "≈ št. enot": approx_units,
            })
        st.dataframe(summary, use_container_width=True, hide_index=True)
    else:
        selected_units = int(inputs.get("st_stanovanj", units_auto) or units_auto)
        inputs["st_stanovanj"] = st.number_input(
            "Število stanovanj (ročno nastavljivo)",
            min_value=1,
            step=1,
            value=selected_units,
            help=f"Računski predlog je {units_auto} stanovanj; vrednost lahko po potrebi prilagodiš."
        )
        st.caption(
            "V načinu AVTO lahko spremeniš predlagano število stanovanj in deleže posameznih tipologij."
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
