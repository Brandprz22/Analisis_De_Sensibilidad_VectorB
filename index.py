import streamlit as st
from frontend.styles import inject_css
from frontend.view_size import render_size_form
from frontend.view_sensitive import show_b_change
from frontend.view_model import (
    render_model_inputs,
    show_solve,
    show_manual_table
)

def main():
    st.set_page_config(page_title="Analisis Sensibilidad - b", layout="wide")
    inject_css()

    st.title("Análisis de sensibilidad: Cambio en el vector b")

    render_size_form()
    render_model_inputs()

    tipo = st.session_state.get("tipo_obj", "Maximizar")

    if tipo == "Maximizar":
        show_solve()
    else:
        show_manual_table()

    show_b_change()

if __name__ == "__main__":
    main()

