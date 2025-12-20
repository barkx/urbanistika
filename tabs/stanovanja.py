import math

import streamlit as st
from core import compute
from ui_dashboard import render_dashboard


def _preview_units_by_typology(total_units: int, typologies: list[dict]) -> list[int]:
    total_share = sum(max(0.0, float(t.get("share_pct", 0.0))) for t in typologies)

    if total_units <= 0 or total_share <= 0:
        return [0 for _ in typologies]

    base_units: list[int] = []
    fractions: list[tuple[int, float]] = []

    for idx, t in enumerate(typologies):
        share = max(0.0, float(t.get("share_pct", 0.0))) / total_share
        raw_units = total_units * share
        floor_units = int(math.floor(raw_units))

        base_units.append(floor_units)
        fractions.append((idx, raw_units - floor_units))

    remaining = max(0, int(total_units - sum(base_units)))
    fractions.sort(key=lambda x: x[1], reverse=True)

    for i in range(remaining):
        base_units[fractions[i % len(fractions)][0]] += 1

    return base_units


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

    st.markdown("#### Predogled števila stanovanj po tipologijah")
    typology_units = _preview_units_by_typology(r["units"], inputs.get("typologies", []))

    if inputs.get("typologies"):
        table_rows = []
        for t, units in zip(inputs["typologies"], typology_units):
            table_rows.append(
                {
                    "Tipologija": t.get("name", ""),
                    "Delež %": f"{float(t.get('share_pct', 0.0)):.1f} %",
                    "Povp. m²": f"{float(t.get('avg_m2', 0.0)):.1f}",
                    "Št. stanovanj": units,
                }
            )

        st.table(table_rows)

        if inputs["units_mode"] == "ROČNO":
            st.caption("Predogled tipologij je informativen – ročno nastavljeno število stanovanj se razdeli po deležih.")
    else:
        st.info("Dodaj tipologije za prikaz predogleda števila stanovanj.")
    return inputs
