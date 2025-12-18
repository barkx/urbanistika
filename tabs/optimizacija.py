import math
import streamlit as st
from core import compute
from ui_dashboard import render_dashboard, area_fmt, pct_fmt

def _apply_option(inputs: dict, option_key: str) -> dict:
    r = compute(inputs)

    P = float(inputs["parcela_m2"])
    FZ = float(inputs["fz"])
    building_fp = float(r["building_footprint"])
    btp_above = float(r["btp_above"])
    FI_limit = float(inputs["fi"])

    if option_key == "FI_1_reduce_floors":
        if int(inputs["st_etas_nadz"]) > 1:
            inputs["st_etas_nadz"] = int(inputs["st_etas_nadz"]) - 1

    elif option_key == "FI_2_reduce_lamels":
        if int(inputs["stevilo_lamel"]) > 1:
            inputs["stevilo_lamel"] = int(inputs["stevilo_lamel"]) - 1

    elif option_key == "FI_3_increase_FI_limit":
        # policy lever (OPN) – user-driven
        inputs["fi"] = round(float(inputs["fi"]) + 0.05, 2)

    elif option_key == "FZ_1_increase_parcel":
        needed_P = math.ceil(building_fp / max(FZ, 1e-6))
        inputs["parcela_m2"] = int(max(P, needed_P))

    elif option_key == "FZ_2_reduce_lamels":
        if int(inputs["stevilo_lamel"]) > 1:
            inputs["stevilo_lamel"] = int(inputs["stevilo_lamel"]) - 1

    elif option_key == "FZ_3_reduce_width":
        allowed_fp = float(r["fz_max_footprint"])
        if building_fp > 0:
            ratio = allowed_fp / building_fp
            new_w = max(5, int(round(float(inputs["sirina_lamele_m"]) * ratio)))
            inputs["sirina_lamele_m"] = new_w

    elif option_key == "FZP_1_switch_to_K2":
        inputs["scenario"] = "K-2"

    elif option_key == "FZP_2_reduce_pm_per_unit":
        inputs["pm_na_stanovanje"] = max(0.5, round(float(inputs["pm_na_stanovanje"]) - 0.1, 2))

    elif option_key == "FZP_3_increase_garage_eff":
        if inputs["scenario"] in ("K-1", "K-1 + teren"):
            inputs["garage_eff_k1"] = min(0.95, round(float(inputs["garage_eff_k1"]) + 0.05, 2))
        else:
            inputs["garage_eff_k2"] = min(0.95, round(float(inputs["garage_eff_k2"]) + 0.05, 2))

    return inputs

def render_tab(inputs: dict):
    st.subheader("Optimizacija")

    r = compute(inputs)
    render_dashboard(r, net_to_gross=inputs["net_to_gross"])

    status = r.get("status", "")
    is_noncompliant = status.startswith("NESKLADNO")

    if not is_noncompliant:
        st.success("Status je skladen. Optimizacija trenutno ni potrebna.")
        return inputs

    proposals = []
    if status.startswith("NESKLADNO (FI)"):
        proposals = [
            ("Zmanjšaj št. nadzemnih etaž (−1)", "FI_1_reduce_floors"),
            ("Zmanjšaj število lamel (−1)", "FI_2_reduce_lamels"),
            ("Povečaj FI (OPN parameter) (+0,05)", "FI_3_increase_FI_limit"),
        ]
        st.info("Projekt je neskladen po **FI** (nadzemni BTP presega dopustno izrabo).")
    elif status.startswith("NESKLADNO (FZ)"):
        proposals = [
            ("Povečaj parcelo (da odtis ustreza FZ)", "FZ_1_increase_parcel"),
            ("Zmanjšaj število lamel (−1)", "FZ_2_reduce_lamels"),
            ("Zmanjšaj širino lamel (proporcionalno)", "FZ_3_reduce_width"),
        ]
        st.info("Projekt je neskladen po **FZ** (odtis stavb > dopustno).")
    else:
        proposals = [
            ("Preklopi scenarij na K-2 (vertikalizacija parkiranja)", "FZP_1_switch_to_K2"),
            ("Zmanjšaj PM/stanovanje (−0,1)", "FZP_2_reduce_pm_per_unit"),
            ("Povečaj izkoristek garaže (+0,05)", "FZP_3_increase_garage_eff"),
        ]
        st.info("Projekt je neskladen po **FZP** (premalo raščenega terena).")

    labels = [p[0] for p in proposals]
    keys = [p[1] for p in proposals]

    choice = st.radio("Izberi optimizacijski ukrep", labels, index=0)

    if st.button("Uporabi izbrano optimizacijo"):
        option_key = keys[labels.index(choice)]
        inputs = _apply_option(inputs, option_key)
        st.success("Optimizacija uporabljena. Vrednosti so posodobljene.")
        st.rerun()

    # Konkretna razlaga odstopanja
    if status.startswith("NESKLADNO (FI)"):
        reserve = float(r.get("fi_reserve_btp", 0.0))
        st.error(f"FI presežek: {area_fmt(abs(reserve))} BTP nad dopustnim.")
    elif status.startswith("NESKLADNO (FZ)"):
        reserve = r["fz_max_footprint"] - r["building_footprint"]
        st.error(f"FZ presežek: {area_fmt(abs(reserve))} nad dopustnim.")
    else:
        fzp = r["fzp"] * 100
        fzp_min = r["FZP_min"] * 100
        st.error(f"FZP prenizek: {pct_fmt(fzp)} (min: {pct_fmt(fzp_min)}).")

    return inputs
