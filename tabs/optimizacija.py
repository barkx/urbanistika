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
    option_details = {}
    if status.startswith("NESKLADNO (FI)"):
        proposals = [
            ("Zmanjšaj št. nadzemnih etaž (−1)", "FI_1_reduce_floors"),
            ("Zmanjšaj število lamel (−1)", "FI_2_reduce_lamels"),
            ("Povečaj FI (OPN parameter) (+0,05)", "FI_3_increase_FI_limit"),
        ]
        option_details = {
            "FI_1_reduce_floors": (
                "**Kaj naredi:** zniža število nadzemnih etaž za 1 (P+N → P+(N−1)).\n"
                "\n"
                "**Vpliv:** neposredno zmanjša nadzemni BTP, zato najhitreje izboljša skladnost po FI.\n"
                "\n"
                "**Kompromis:** manj prodajne površine in praviloma manj stanovanj ali manjši program."
            ),
            "FI_2_reduce_lamels": (
                "**Kaj naredi:** zmanjša število lamel za 1.\n"
                "\n"
                "**Vpliv:** zmanjša odtis in predvsem skupni BTP (torej tudi FI).\n"
                "\n"
                "**Kompromis:** manj enot, lahko pa izboljša tudi FZ/FZP, če je projekt na meji več kriterijev."
            ),
            "FI_3_increase_FI_limit": (
                "**Kaj naredi:** simulira spremembo dopustnega FI (npr. sprememba OPN/PPN parametra) za +0,05.\n"
                "\n"
                "**Vpliv:** projekt lahko postane skladen brez zmanjšanja programa.\n"
                "\n"
                "**Kompromis:** to ni tehnična optimizacija, ampak **regulativni scenarij** – izvedljivost je odvisna od prostorskega akta."
            ),
        }
        st.info("Projekt je neskladen po **FI** (nadzemni BTP presega dopustno izrabo).")
    elif status.startswith("NESKLADNO (FZ)"):
        proposals = [
            ("Povečaj parcelo (da odtis ustreza FZ)", "FZ_1_increase_parcel"),
            ("Zmanjšaj število lamel (−1)", "FZ_2_reduce_lamels"),
            ("Zmanjšaj širino lamel (proporcionalno)", "FZ_3_reduce_width"),
        ]
        option_details = {
            "FZ_1_increase_parcel": (
                "**Kaj naredi:** poveča velikost parcele na minimum, ki bi ob istem odtisu stavb izpolnil FZ limit.\n"
                "\n"
                "**Vpliv:** rešuje FZ brez spremembe gabaritov stavb.\n"
                "\n"
                "**Kompromis:** realno pomeni združitev/odkup sosednjih zemljišč ali spremembo parcelacije."
            ),
            "FZ_2_reduce_lamels": (
                "**Kaj naredi:** zmanjša število lamel za 1.\n"
                "\n"
                "**Vpliv:** zmanjša odtis stavb in s tem izboljša skladnost po FZ; pogosto pomaga tudi FZP.\n"
                "\n"
                "**Kompromis:** manj stanovanj/BT P; lahko vpliva na faznost ali koncept naselja."
            ),
            "FZ_3_reduce_width": (
                "**Kaj naredi:** proporcionalno zmanjša širino lamel, da odtis pade na dopustno vrednost.\n"
                "\n"
                "**Vpliv:** zniža FZ (odtis) pri ohranjeni dolžini lamel; lahko ohrani št. lamel.\n"
                "\n"
                "**Kompromis:** ožji tlorisi lahko poslabšajo funkcionalnost stanovanj ali jedra (stopnišča/dvigala)."
            ),
        }
        st.info("Projekt je neskladen po **FZ** (odtis stavb > dopustno).")
    else:
        proposals = [
            ("Preklopi scenarij na K-2 (vertikalizacija parkiranja)", "FZP_1_switch_to_K2"),
            ("Zmanjšaj PM/stanovanje (−0,1)", "FZP_2_reduce_pm_per_unit"),
            ("Povečaj izkoristek garaže (+0,05)", "FZP_3_increase_garage_eff"),
        ]
        option_details = {
            "FZP_1_switch_to_K2": (
                "**Kaj naredi:** preklopi parkiranje na dve kletni etaži (K-2).\n"
                "\n"
                "**Vpliv:** več PM se preseli v klet, zato se zmanjša parkiranje na terenu in se praviloma poveča FZP (več raščenih površin).\n"
                "\n"
                "**Kompromis:** več podzemnega BTP, višji stroški kleti in potencialno več zahtev ITS (prezračevanje, požarna varnost)."
            ),
            "FZP_2_reduce_pm_per_unit": (
                "**Kaj naredi:** zniža normo PM/stanovanje za 0,1.\n"
                "\n"
                "**Vpliv:** manj potrebnih PM → manj površin za parkiranje/manipulacijo na terenu → boljši FZP.\n"
                "\n"
                "**Kompromis:** preveriti je treba skladnost z občinskimi standardi in dejanskimi potrebami uporabnikov."
            ),
            "FZP_3_increase_garage_eff": (
                "**Kaj naredi:** poveča izkoristek garaže (več PM na isto bruto površino).\n"
                "\n"
                "**Vpliv:** manjka manj PM na terenu, ker jih več spravimo v klet; izboljša FZP brez spremembe FI/FZ.\n"
                "\n"
                "**Kompromis:** višji izkoristek običajno zahteva bolj optimizirano geometrijo (rampi, radiji, stebri), zato je treba preveriti projektantsko izvedljivost."
            ),
        }
        st.info("Projekt je neskladen po **FZP** (premalo raščenega terena).")

    labels = [p[0] for p in proposals]
    keys = [p[1] for p in proposals]

    choice = st.radio("Izberi optimizacijski ukrep", labels, index=0)

    # Natančnejši opis izbrane možnosti
    chosen_key = keys[labels.index(choice)]
    if chosen_key in option_details:
        st.markdown("#### Opis izbrane optimizacije")
        st.markdown(option_details[chosen_key])

    if st.button("Uporabi izbrano optimizacijo"):
        option_key = chosen_key
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
