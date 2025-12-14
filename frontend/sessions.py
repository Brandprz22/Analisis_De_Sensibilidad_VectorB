import streamlit as st

KEYS_TEMPLATE = ["n", "m", "A", "b", "c"]
KEYS_RESULTS = ["simplex", "resultado_base"]


def has_template():
    return all(k in st.session_state for k in KEYS_TEMPLATE)


def clear_results():
    for k in KEYS_RESULTS:
        st.session_state.pop(k, None)


def init_template(n, m):
    st.session_state["n"] = int(n)
    st.session_state["m"] = int(m)

    st.session_state["A"] = [[0.0 for _ in range(int(n))] for _ in range(int(m))]
    st.session_state["b"] = [0.0 for _ in range(int(m))]
    st.session_state["c"] = [0.0 for _ in range(int(n))]

    clear_results()


def save_base_result(simplex, x, s, z, tabla):
    st.session_state["simplex"] = simplex
    st.session_state["resultado_base"] = {
        "x": x,
        "s": s,
        "z": z,
        "tabla": tabla,
    }


def has_base_result():
    return "resultado_base" in st.session_state


def clear_b_results():
    if "resultado_b" in st.session_state:
        del st.session_state["resultado_b"]
    if "resultado_b_dual" in st.session_state:
        del st.session_state["resultado_b_dual"]

