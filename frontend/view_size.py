import streamlit as st
from frontend.sessions import init_template

def render_size_form():
    with st.container(border=True):
        st.subheader("1. Tamaño del problema")

        with st.form("form_tamano", border=False):
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                n = st.number_input("Numero de variables (n)", min_value=1, max_value=20, value=2, step=1)

            with col2:
                m = st.number_input("Numero de restricciones (m)", min_value=1, max_value=20, value=2, step=1)

            with col3:
                st.selectbox("Tipo", ["Maximizar", "Minimizar"], key="tipo_obj")

            submitted = st.form_submit_button("Crear plantilla")

        if submitted:
            init_template(int(n), int(m))
            st.success(f"Plantilla creada con n={int(n)} y m={int(m)}")

        tipo = st.session_state.get("tipo_obj", "Maximizar")
        signo_fijo = "<=" if tipo == "Maximizar" else ">="
        st.caption(f"Regla fija: si es {tipo}, las restricciones se interpretan como '{signo_fijo}'.")
