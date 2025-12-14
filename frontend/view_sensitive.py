import streamlit as st
import numpy as np
from backend.CambioVectorB import CambioVectorB
from backend.Simplex import Simplex
from backend.SolbyLib import solve_min_geq
from frontend.sessions import has_base_result


# ==================== FUNCIONES AUXILIARES DE FORMATO ====================
def show_vector(values, name: str):
    """ESTA FUNCION SIRVE PARA MOSTRAR UN VECTOR DE FORMA ITERATIVA"""
    for i, val in enumerate(values, start=1):
        st.write(f"{name}{i} = {val:.3f}")


def _latex_matrix(M):
    """ESTA FUNCION SIRVE PARA CONVERTIR UNA MATRIZ A FORMATO LATEX"""
    M = np.array(M, dtype=float)
    rows = [" & ".join([f"{v:.3f}" for v in row]) for row in M]
    body = r" \\ ".join(rows)
    return r"\begin{bmatrix}" + body + r"\end{bmatrix}"


def _latex_vector(v):
    """ESTA FUNCION SIRVE PARA CONVERTIR UN VECTOR A FORMATO LATEX"""
    v = np.array(v, dtype=float).reshape(-1, 1)
    rows = [f"{v[i,0]:.3f}" for i in range(v.shape[0])]
    body = r" \\ ".join(rows)
    return r"\begin{bmatrix}" + body + r"\end{bmatrix}"


# ==================== FUNCIONES DE PRESENTACION DE RESULTADOS ====================
def show_process_b(res: dict):
    """ESTA FUNCION SIRVE PARA MOSTRAR EL PROCESO DE MULTIPLICACION B^-1 * b'"""
    st.markdown("### Proceso: $x_B' = B^{-1} b'$")

    B_inv = res["B_inv"]
    b_vec = res["b_nuevo"]
    xB = res["xB_nueva"]

    st.latex(r"x_B' = B^{-1} b'")
    st.latex(_latex_matrix(B_inv) + r"\," + _latex_vector(b_vec) + r" \;=\; " + _latex_vector(xB))


def show_summary_b(res: dict, title="**Resultado con b'**"):
    """ESTA FUNCION SIRVE PARA MOSTRAR UN RESUMEN DEL RESULTADO"""
    st.markdown(title)
    st.write("Factible (base actual)?", "Si!" if res["factible"] else "Lamentablemente no")
    st.write("Base sigue óptima?", "Si!" if res["base_sigue_optima"] else "Lamentablemente no")


# ==================== CASO 1: CUANDO LA BASE SIGUE SIENDO OPTIMA ====================
def show_calcule(res):
    """ESTA FUNCION SIRVE PARA MOSTRAR LOS CALCULOS CUANDO LA BASE ES FACTIBLE"""
    show_summary_b(res, title="**Resultado con b'**")

    st.markdown("**x' (variables originales)**")
    show_vector(res["x_nueva"], "x")
    st.write("Z' =", f"{res['z_nueva']:.3f}")
    show_process_b(res)


# ==================== CASO 2: CUANDO SE NECESITA RE-OPTIMIZAR ====================
def show_recalcule(res):
    """ESTA FUNCION SIRVE PARA MOSTRAR EL PROCESO DE RE-OPTIMIZACION"""
    show_summary_b(res, title="**Resultado con b' (antes de reoptimizar)**")
    show_process_b(res)

    st.markdown("### Re-resolver desde cero")

    tipo = st.session_state.get("tipo_obj", "Maximizar")

    # Un solo botón: el método depende del tipo
    label = "Re-resolver (Simplex)" if tipo == "Maximizar" else "Re-resolver (Solver)"
    help_txt = (
        "Maximizar: re-resuelve con tu implementación Simplex (caso Max con <=)."
        if tipo == "Maximizar"
        else "Minimizar: re-resuelve con solver (caso Min con >=)."
    )

    if st.button(label, use_container_width=True, key="btn_reresolver", help=help_txt):
        A = st.session_state["A"]
        c = st.session_state["c"]
        b_new = res["b_nuevo"]

        if tipo == "Maximizar":
            n = st.session_state["n"]
            m = st.session_state["m"]

            sx = Simplex(A, b_new, c, m, n)
            sx.solve()
            x_new, s_new, z_new = sx.get_solution()
            tabla_new = sx.get_tabla()

            st.session_state["resultado_b_reresuelto"] = {
                "metodo": "simplex",
                "x": x_new,
                "s": s_new,
                "z": z_new,
                "tabla": tabla_new,
            }
        else:
            out = solve_min_geq(A=A, b=b_new, c=c)

            st.session_state["resultado_b_reresuelto"] = {
                "metodo": "solver",
                **out,
            }

    if "resultado_b_reresuelto" not in st.session_state:
        return

    out = st.session_state["resultado_b_reresuelto"]

    st.markdown("**Resultado re-resuelto**")

    if out["metodo"] == "simplex":
        st.write("Z* (nuevo) =", f"{out['z']:.3f}")
        st.markdown("**x* (nuevo)**")
        for j, val in enumerate(out["x"], start=1):
            st.write(f"x{j} = {val:.3f}")

        st.markdown("**s* (nuevo)**")
        for i, val in enumerate(out["s"], start=1):
            st.write(f"s{i} = {val:.3f}")

        st.markdown("**Tabla final (Simplex)**")
        st.dataframe(out["tabla"], use_container_width=True)

    else:
        if out["success"]:
            st.write("Z* (nuevo) =", f"{out['z']:.3f}")
            st.markdown("**x* (nuevo)**")
            for j, val in enumerate(out["x"], start=1):
                st.write(f"x{j} = {val:.3f}")
        else:
            st.error(f"No se pudo resolver: {out['message']}")


# ==================== PASO 4: CAMBIO EN EL VECTOR B ====================
def show_b_change():
    """ESTA FUNCION SIRVE PARA APLICAR CAMBIO AL VECTOR B"""
    if not has_base_result():
        return

    with st.container(border=True):
        st.subheader("4. Cambio en el vector b")

        m = st.session_state["m"]
        cols = st.columns(m) if m > 1 else [st]
        b_new = []
        for i in range(m):
            b_new.append(
                cols[i].number_input(
                    f"b{i+1}'",
                    value=float(st.session_state["b"][i]),
                    key=f"b_new_{i}",
                )
            )

        evaluar = st.button("Evaluar cambio en b")

        if evaluar:
            # Limpia resultados previos para que no se mezclen con otro b'
            if "resultado_b" in st.session_state:
                del st.session_state["resultado_b"]
            if "resultado_b_solver" in st.session_state:
                del st.session_state["resultado_b_solver"]
            if "resultado_b_reresuelto" in st.session_state:
                del st.session_state["resultado_b_reresuelto"]

            sx = st.session_state["simplex"]
            analizador = CambioVectorB(sx)
            res = analizador.evalue(b_new)
            st.session_state["resultado_b"] = res

        if "resultado_b" not in st.session_state:
            return

        res = st.session_state["resultado_b"]

        if res["base_sigue_optima"]:
            show_calcule(res)
        else:
            show_recalcule(res)