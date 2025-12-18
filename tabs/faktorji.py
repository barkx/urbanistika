import streamlit as st
from core import compute
from ui_dashboard import render_dashboard

def render_tab(inputs: dict):
    st.subheader("Faktorji")
    c1, c2, c3 = st.columns(3)
    with c1:
        inputs["fi"] = st.number_input("FI", min_value=0.10, step=0.01, value=float(inputs["fi"]))
    with c2:
        inputs["fz"] = st.number_input("FZ", min_value=0.05, max_value=1.00, step=0.01, value=float(inputs["fz"]))
    with c3:
        inputs["fzp_min_pct"] = st.number_input("Minimalni FZP (%)", min_value=0, max_value=100, step=1, value=int(inputs["fzp_min_pct"]))

    st.caption("FZ omeji projekcijo stavb. FZP postane omejitev, ko se klet razširi izven tlorisa stavb.")
    r = compute(inputs)
    render_dashboard(r, net_to_gross=inputs["net_to_gross"])
    return inputs
