import copy
import streamlit as st


def render_tab(inputs: dict) -> dict:
    st.subheader("Comparison")

    presets = st.session_state.setdefault("project_presets", [])
    st.markdown(
        "Shranite trenutne projektne nastavitve kot **prednastavitev**, da jih lahko primerjate ali obnovite pozneje.")

    name_col, save_col = st.columns([3, 1])
    with name_col:
        preset_name = st.text_input("Ime prednastavitve", value=st.session_state.get("last_preset_name", ""))
    with save_col:
        save_disabled = not preset_name.strip()
        if st.button("Shrani", disabled=save_disabled):
            snapshot = copy.deepcopy(inputs)
            presets.append({"name": preset_name.strip(), "inputs": snapshot})
            st.session_state.project_presets = presets
            st.session_state.last_preset_name = preset_name.strip()
            st.success(f"Prednastavitev '{preset_name.strip()}' je shranjena.")

    if presets:
        st.markdown("#### Shranjene prednastavitve")
        for idx, preset in enumerate(presets):
            col_label, col_load = st.columns([4, 1])
            with col_label:
                st.markdown(f"**{preset['name']}**")
            with col_load:
                if st.button("Naloži", key=f"load_{idx}"):
                    st.session_state.inputs = copy.deepcopy(preset["inputs"])
                    st.success(f"Prednastavitev '{preset['name']}' je naložena.")
                    st.rerun()
    else:
        st.info("Ni shranjenih prednastavitev. Ustvari prvo z vnosom imena in klikom na 'Shrani'.")

    return inputs
