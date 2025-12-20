import streamlit as st
from pathlib import Path


def render_tab(inputs: dict) -> dict:
    if "layout_mode" not in st.session_state:
        st.session_state.layout_mode = "lamela"

    st.markdown("### Tipologije")

    button_cols = st.columns(3)

    layout_buttons = [
        {
            "label": "Lamelne stavbe",
            "caption": "Aktivno – lamelna zasnova",
            "image": Path("assets/p2.png"),
            "on_click": lambda: st.session_state.update({"layout_mode": "lamela"}),
            "type": "primary",
            "disabled": False,
        },
        {
            "label": "Kare / obroč (kmalu)",
            "caption": "Placeholder za prihodnjo zasnovo",
            "image": Path("assets/p1_g.png"),
            "on_click": None,
            "type": "secondary",
            "disabled": True,
        },
        {
            "label": "Točkovna zazidava (kmalu)",
            "caption": "Placeholder za prihodnjo zasnovo",
            "image": Path("assets/p3_g.png"),
            "on_click": None,
            "type": "secondary",
            "disabled": True,
        },
    ]

    for col, cfg in zip(button_cols, layout_buttons):
        with col:
            if cfg["image"].exists():
                st.image(str(cfg["image"]), use_column_width=True)
            if st.button(
                cfg["label"],
                type=cfg["type"],
                use_container_width=True,
                disabled=cfg["disabled"],
            ) and cfg["on_click"]:
                cfg["on_click"]()
            st.caption(cfg["caption"])

    return inputs
