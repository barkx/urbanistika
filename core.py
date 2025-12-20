import math

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def compute_avg_unit_size_m2(inputs: dict) -> float:
    t = inputs["typologies"]
    total_share = sum(x["share_pct"] for x in t)
    if total_share <= 0:
        return float(inputs["default_avg_unit_m2"])

    avg = 0.0
    for x in t:
        w = x["share_pct"] / total_share
        avg += w * x["avg_m2"]
    return max(10.0, avg)

def compute_units(inputs: dict, building_footprint: float) -> dict:
    floors = int(inputs["st_etas_nadz"])
    net_to_gross = float(inputs["net_to_gross"])
    avg_unit_m2 = compute_avg_unit_size_m2(inputs)

    btp_above = building_footprint * floors
    nfa = btp_above * clamp01(net_to_gross)
    units_auto = int(max(1, math.floor(nfa / max(10.0, avg_unit_m2))))

    return {
        "floors": floors,
        "btp_above": btp_above,
        "nfa": nfa,
        "avg_unit_m2": avg_unit_m2,
        "units_auto": units_auto,
    }

def compute_economics(inputs: dict, r: dict) -> dict:
    land_price = float(inputs["land_price_eur_m2"])
    cost_above = float(inputs["cost_above_eur_m2"])
    cost_below = float(inputs["cost_below_eur_m2"])
    soft_pct = float(inputs["soft_cost_pct"]) / 100.0
    sales_price_m2 = float(inputs["sales_price_eur_m2"])

    P = float(r["P"])
    btp_above = float(r["btp_above"])
    btp_below = float(r["basement_footprint"]) * int(r["basement_levels"])
    nfa = float(r["nfa"])

    land_cost = P * land_price
    hard_cost = btp_above * cost_above + btp_below * cost_below
    soft_cost = (land_cost + hard_cost) * soft_pct
    total_invest = land_cost + hard_cost + soft_cost

    cost_per_m2_nfa = total_invest / max(1.0, nfa)

    revenue = nfa * sales_price_m2
    margin_abs = revenue - total_invest
    margin_pct = (margin_abs / revenue) if revenue > 0 else 0.0

    return {
        "land_cost": land_cost,
        "hard_cost": hard_cost,
        "soft_cost": soft_cost,
        "total_invest": total_invest,
        "btp_below": btp_below,
        "sales_price_m2": sales_price_m2,
        "revenue": revenue,
        "margin_abs": margin_abs,
        "margin_pct": margin_pct,
        "cost_per_m2_nfa": cost_per_m2_nfa,
    }

def compute(inputs: dict) -> dict:
    P = float(inputs["parcela_m2"])

    FI_limit = float(inputs["fi"])
    FZ = float(inputs["fz"])
    FZP_min = float(inputs["fzp_min_pct"]) / 100.0

    n_lamel = int(inputs["stevilo_lamel"])
    L = float(inputs["dolzina_lamele_m"])
    W = float(inputs["sirina_lamele_m"])
    building_footprint = n_lamel * L * W

    # Nadzemni program (BTP, NFA, št. stanovanj)
    u = compute_units(inputs, building_footprint)

    # FI kontrola: primerjamo nadzemni BTP (klet se ne šteje) z dopustnim (FI_limit * P)
    btp_above = float(u["btp_above"])
    fi_allowed_btp = FI_limit * P
    fi_reserve_btp = fi_allowed_btp - btp_above
    FI_achieved = (btp_above / P) if P else 0.0
    fi_ok = btp_above <= fi_allowed_btp + 1e-9

    # FZ kontrola
    fz_max_footprint = FZ * P
    fz_ok = building_footprint <= fz_max_footprint + 1e-9

    # Stanovanja AUTO/ROČNO
    if inputs["units_mode"] == "AUTO":
        units = int(inputs["st_stanovanj"] or u["units_auto"])
    else:
        units = int(inputs["st_stanovanj"])

    # Parkiranje
    pm_per_unit = float(inputs["pm_na_stanovanje"])
    pm_total = int(math.ceil(units * pm_per_unit))

    visitor_share = float(inputs["visitor_share"])
    pm_visitors = int(math.ceil(pm_total * visitor_share))
    pm_residents = int(pm_total - pm_visitors)

    # Parkirni parametri
    area_per_pm_garage = float(inputs["area_per_pm_garage_m2"])
    area_per_pm_surface = float(inputs["area_per_pm_surface_m2"])
    eff_k1 = float(inputs["garage_eff_k1"])
    eff_k2 = float(inputs["garage_eff_k2"])
    ramp_add = float(inputs["ramp_footprint_m2"])
    surface_mult = float(inputs["surface_mult"])

    scenario = str(inputs["scenario"])

    if scenario == "K-1":
        basement_levels = 1
        pm_in_basement = pm_total
        pm_on_surface = 0
    elif scenario == "K-1 + teren":
        basement_levels = 1
        pm_in_basement = pm_residents
        pm_on_surface = pm_visitors
    else:
        basement_levels = 2
        pm_in_basement = pm_total
        pm_on_surface = 0

    eff = eff_k1 if basement_levels == 1 else eff_k2
    garage_area_total = (pm_in_basement * area_per_pm_garage) / max(eff, 0.01)

    basement_footprint = garage_area_total / basement_levels + ramp_add
    basement_footprint = min(basement_footprint, P)

    surface_parking_area = pm_on_surface * area_per_pm_surface * surface_mult

    growing_area = max(0.0, P - basement_footprint - surface_parking_area)
    fzp = (growing_area / P) if P else 0.0
    fzp_ok = fzp >= FZP_min - 1e-9

    basement_exceeds_building = basement_footprint > building_footprint + 1e-9

    # Status (prioriteta neskladnosti)
    if not fi_ok:
        status = "NESKLADNO (FI)"
    elif not fz_ok:
        status = "NESKLADNO (FZ)"
    elif not fzp_ok:
        status = "NESKLADNO (FZP)"
    else:
        if scenario == "K-2":
            status = "OPTIMALNO"
        elif scenario == "K-1 + teren":
            status = "MEJNO / KOMPROMIS"
        else:
            status = "TVEGANO (FZP postane omejitev)" if basement_exceeds_building else "POGOJNO (lahko OK)"

    r = {
        "P": P,

        # FI
        "FI_limit": FI_limit,
        "FI": FI_achieved,
        "fi_allowed_btp": fi_allowed_btp,
        "fi_reserve_btp": fi_reserve_btp,
        "fi_ok": fi_ok,

        # FZ / FZP
        "FZ": FZ,
        "FZP_min": FZP_min,
        "building_footprint": building_footprint,
        "fz_max_footprint": fz_max_footprint,
        "fz_ok": fz_ok,

        # program
        "units": units,
        "units_auto": u["units_auto"],
        "units_mode": inputs["units_mode"],
        "floors": u["floors"],
        "btp_above": btp_above,
        "nfa": u["nfa"],
        "avg_unit_m2": u["avg_unit_m2"],

        # parking
        "pm_total": pm_total,
        "pm_residents": pm_residents,
        "pm_visitors": pm_visitors,

        "scenario": scenario,
        "basement_levels": basement_levels,
        "pm_in_basement": pm_in_basement,
        "pm_on_surface": pm_on_surface,

        "basement_footprint": basement_footprint,
        "surface_parking_area": surface_parking_area,
        "growing_area": growing_area,

        "fzp": fzp,
        "fzp_ok": fzp_ok,
        "basement_exceeds_building": basement_exceeds_building,
        "status": status,
    }

    r["econ"] = compute_economics(inputs, r)
    return r
