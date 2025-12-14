import streamlit as st
import numpy as np
import pandas as pd
from backend.Simplex import Simplex
from backend.SimplexLike import SimplexLike
from frontend.sessions import has_template, save_base_result, has_base_result


# ==================== FUNCIONES DE FORMATO LATEX ====================
def _latex_fo(c, tipo):
    """ESTA FUNCION SIRVE PARA DAR FORMATO LATEX A LA FUNCION OBJETIVO"""
    terms = [f"{c[j]}x_{{{j+1}}}" for j in range(len(c))]
    lhs = " + ".join(terms) if terms else ""
    return rf"\text{{{tipo}}}\quad Z = {lhs}"

def _latex_restr(A_row, i, signo, b_i):
    """ESTA FUNCION SIRVE PARA DAR FORMATO LATEX A LAS RESTRCICIONES"""
    terms = [f"{A_row[j]}x_{{{j+1}}}" for j in range(len(A_row))]
    lhs = " + ".join(terms) if terms else ""
    return rf"\text{{Restriccion {i+1}:}}\quad {lhs} {signo} {b_i}"

def format_solution(x, s):
    """ESTA FUNCION SIRVE PARA DESCOMPONER VARIABLES DE HOLGURA Y ORIGINALES"""
    st.markdown("**Variables originales (x):**")
    for i, val in enumerate(x, start=1):
        st.write(f"x{i} = {val:.3f}")

    st.markdown("**Holguras (s):**")
    for i, val in enumerate(s, start=1):
        st.write(f"s{i} = {val:.3f}")


# ==================== PASO 2: CAPTURA DE COEFICIENTES ====================
def render_model_inputs():
    """ESTA FUNCION SIRVE PARA MOSTRAR Y GUARDAR LOS COEFICIENTES DEL EJERCICIO"""
    if not has_template():
        st.info("Primero define # de variables y # de restricciones, después presiona 'Crear plantilla'.")
        return

    with st.container(border=True):
        n = st.session_state["n"]
        m = st.session_state["m"]

        tipo = st.session_state.get("tipo_obj", "Maximizar")
        signo = "<=" if tipo == "Maximizar" else ">="

        st.subheader("2. Captura de coeficientes")

        # -------------------------
        # Función objetivo
        # -------------------------
        st.markdown("**Funcion objetivo**")
        cols_c = st.columns(n) if n > 1 else [st]
        for j in range(n):
            st.session_state["c"][j] = cols_c[j].number_input(
                f"c{j+1} (coeficiente de x{j+1})",
                value=float(st.session_state["c"][j]),
                key=f"c_{j}",
            )
        st.latex(_latex_fo(st.session_state["c"], tipo))

        st.write("---")

        # -------------------------
        # Restricciones
        # -------------------------
        st.markdown("**Sujeto a:**")
        st.caption(f"Signo fijo por tipo: {signo}")

        for i in range(m):
            row = st.columns(n + 1)

            for j in range(n):
                st.session_state["A"][i][j] = row[j].number_input(
                    f"a{i+1}{j+1}",
                    value=float(st.session_state["A"][i][j]),
                    key=f"a_{i}_{j}",
                )

            st.session_state["b"][i] = row[n].number_input(
                f"b{i+1}",
                value=float(st.session_state["b"][i]),
                key=f"b_{i}",
            )

            st.latex(_latex_restr(st.session_state["A"][i], i, signo, st.session_state["b"][i]))


# ==================== PASO 3A: CAPTURA MANUAL DE TABLA ====================
def show_manual_table():
    """ESTA FUNCION SIRVE PARA CAPTURAR TABLA FINAL SIMPLEX"""
    with st.container(border=True):
        n = st.session_state["n"]
        m = st.session_state["m"]

        st.subheader("3. Tabla final óptima (ingreso manual)")

        st.info("Para Minimizar / >=, ingresa la tabla final óptima. Debe tener m+1 filas y (n+m+1) columnas.")

        col_names = [f"x{j + 1}" for j in range(n)] + [f"s{i + 1}" for i in range(m)] + ["RHS"]
        row_names = [f"R{i + 1}" for i in range(m)] + ["Z"]  # en tu Simplex, Z suele estar abajo

        # MANERA DE EDITAR LA TABLA
        df0 = pd.DataFrame(np.zeros((m + 1, n + m + 1)), columns=col_names, index=row_names)
        df_tabla = st.data_editor(df0, use_container_width=True, num_rows="fixed")

        if st.button("Usar esta tabla", use_container_width=True):
            tabla = df_tabla.to_numpy(dtype=float)

            # Se crea una especie de falso simplex
            A = st.session_state["A"]
            b = st.session_state["b"]
            c = st.session_state["c"]

            sx = SimplexLike(tabla, A, b, c, m, n)

            save_base_result(sx, x=[], s=[], z=float(tabla[m, -1]) if tabla.shape[0] == m + 1 else 0.0,
                             tabla=tabla.tolist())
            st.success("Tabla cargada. Ya puedes pasar al Paso 4 (cambio en b).")


# ==================== PASO 3B: RESOLVER CON SIMPLEX ====================
def show_solve():
    """ESTA FUNCION SIRVE PARA RESOLVER EL PROBLEMA BASE CON SIMPLEX"""
    if not has_template():
        return

    with st.container(border=True):
        n = st.session_state["n"]
        m = st.session_state["m"]
        tipo = st.session_state.get("tipo_obj", "Maximizar")

        st.subheader("3. Resolver problema base")

        # Botón para resolver el ejercicio
        colA, colB = st.columns([1, 2])
        with colA:
            resolver = st.button("Resolver (Simplex)", use_container_width=True)

        # Si se presiona el boton de resolver, por consiguiente se resuelve
        if resolver:
            if tipo != "Maximizar":
                st.error("En este proyecto, el Simplex implementado se usara solo para Maximizar.")
                return

            A = np.array(st.session_state["A"], dtype=float)
            b = np.array(st.session_state["b"], dtype=float)
            c = np.array(st.session_state["c"], dtype=float)

            sx = Simplex(A, b, c, m, n)
            sx.solve()
            x, s, z = sx.get_solution()
            tabla = sx.get_tabla()

            save_base_result(sx, x, s, z, tabla)
            st.success("Problema base resuelto.")

        # Al tener el resultado, se formatea para presentacion.
        if has_base_result():
            res = st.session_state["resultado_base"]

            st.markdown("**Resultado base**")
            st.write("Z* =", f"{res['z']:.3f}")

            format_solution(res["x"], res["s"])

            st.markdown("**Tabla final optima**")
            tabla = np.array(res["tabla"], dtype=float)
            # Reordenar: fila Z (última) arriba
            tabla_reordered = np.vstack([tabla[-1, :], tabla[:-1, :]])
            # Crear nombres de columnas: x1..xn, s1..sm, RHS(b)
            n = st.session_state["n"]
            m = st.session_state["m"]
            col_names = [f"x{j + 1}" for j in range(n)] + [f"s{i + 1}" for i in range(m)] + ["RHS"]
            # Nombres de filas: Z, R1..Rm
            row_names = ["Z"] + [f"R{i + 1}" for i in range(m)]
            df = pd.DataFrame(tabla_reordered, columns=col_names, index=row_names)

            # Mostrar tabla final
            st.dataframe(df, use_container_width=True)