import streamlit as st

def area_fmt(x: float) -> str:
    return f"{x:,.0f} m²".replace(",", " ")

def pct_fmt(x: float) -> str:
    return f"{x:.1f} %"

def eur_fmt(x: float) -> str:
    return f"{x:,.0f} €".replace(",", " ")

def eur_m2_fmt(x: float) -> str:
    return f"{x:,.0f} €/m²".replace(",", " ")

def render_dashboard(r: dict, show_detail: bool = True, net_to_gross: float = 0.82):
    # 8 kartic v dveh vrstah (4 + 4); Status je zadnja
    top_row = st.columns(4)
    bottom_row = st.columns(4)

    # --- FZ (odtis) semafor ---
    reserve_fz = r["fz_max_footprint"] - r["building_footprint"]
    threshold_fz = 20.0

    if reserve_fz < 0:
        top_row[0].metric(
            "Odtis stavb (FZ)",
            area_fmt(r["building_footprint"]),
            delta=f"+{area_fmt(abs(reserve_fz))} nad dopustnim",
            delta_color="inverse",
        )
    elif reserve_fz <= threshold_fz:
        top_row[0].metric(
            "Odtis stavb (FZ)",
            area_fmt(r["building_footprint"]),
            delta=f"⚠ MEJNO: {area_fmt(reserve_fz)} rezerve",
        )
    else:
        top_row[0].metric(
            "Odtis stavb (FZ)",
            area_fmt(r["building_footprint"]),
            delta=f"✅ OK: {area_fmt(reserve_fz)} rezerve",
        )

    # --- klet ---
    top_row[1].metric("Odtis kleti", area_fmt(r["basement_footprint"]), f"Nivojev: {r['basement_levels']}")

    # --- FZP ---
    top_row[2].metric("FZP (ocena)", pct_fmt(r["fzp"] * 100), f"Min: {pct_fmt(r['FZP_min'] * 100)}")

    # --- FI semafor: primerjava BTP_nadz z dopustnim (FI_limit * parcela) ---
    reserve_btp = r.get("fi_reserve_btp", 0.0)
    threshold_btp = 20.0  # m² BTP rezerve
    achieved_fi = r.get("FI", 0.0)
    limit_fi = r.get("FI_limit", 0.0)

    if reserve_btp < 0:
        top_row[3].metric(
            "FI (BTP/P)",
            f"{achieved_fi:.2f}",
            delta=f"+{area_fmt(abs(reserve_btp))} BTP nad dopustnim",
            delta_color="inverse",
        )
    elif reserve_btp <= threshold_btp:
        top_row[3].metric(
            "FI (BTP/P)",
            f"{achieved_fi:.2f}",
            delta=f"⚠ MEJNO: {area_fmt(reserve_btp)} BTP rezerve",
        )
    else:
        top_row[3].metric(
            "FI (BTP/P)",
            f"{achieved_fi:.2f}",
            delta=f"✅ OK: {area_fmt(reserve_btp)} BTP rezerve",
        )

    # --- stanovanja ---
    mode_tag = "AUTO" if r["units_mode"] == "AUTO" else "ROČNO"
    bottom_row[0].metric("Št. stanovanj", f"{r['units']}", mode_tag)

    # --- investicija ---
    bottom_row[1].metric("Skupna investicija", eur_fmt(r["econ"]["total_invest"]), eur_m2_fmt(r["econ"]["cost_per_m2_nfa"]))

    # --- margin ---
    margin_pct = r.get("econ", {}).get("margin_pct")
    if margin_pct is not None:
        bottom_row[2].metric("Margin %", pct_fmt(margin_pct * 100))
    else:
        bottom_row[2].metric("Margin %", "—")

    # --- status ---
    bottom_row[3].metric("Status", r["status"])

    if show_detail:
        with st.expander("Podrobnosti izračuna", expanded=False):
            st.write(f"- Parcela: **{area_fmt(r['P'])}**")
            st.write(f"- FI dosežen: **{achieved_fi:.2f}** | FI limit: **{limit_fi:.2f}** | Dopustni BTP: **{area_fmt(r.get('fi_allowed_btp', 0))}**")
            st.write(f"- Nadzemni BTP: **{area_fmt(r['btp_above'])}** (etaže: {r['floors']})")
            st.write(f"- Neto prodajna površina (NFA): **{area_fmt(r['nfa'])}** (neto/bruto: {net_to_gross:.2f})")
            st.write(f"- Povp. velikost stanovanja: **{r['avg_unit_m2']:.1f} m²**")
            st.write(f"- Parkiranje skupaj: **{r['pm_total']} PM** (stanovalci: {r['pm_residents']}, obiskovalci: {r['pm_visitors']})")
            st.write(f"- V kleti: **{r['pm_in_basement']} PM**, na terenu: **{r['pm_on_surface']} PM**")
            st.write(f"- Utrjene površine na terenu: **{area_fmt(r['surface_parking_area'])}**")
            st.write(f"- Raščen teren (ocena): **{area_fmt(r['growing_area'])}**")
            econ = r.get("econ", {})
            if econ:
                st.write(
                    f"- Ekonomika: margin **{pct_fmt(econ.get('margin_pct', 0.0) * 100)}** "
                    f"(prihr.: {eur_fmt(econ.get('revenue', 0.0))}, investicija: {eur_fmt(econ.get('total_invest', 0.0))})"
                )
