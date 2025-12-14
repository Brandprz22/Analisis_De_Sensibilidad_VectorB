import numpy as np
from scipy.optimize import linprog



def solve_min_geq(A, b, c, bounds=None, method="highs"):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    A_ub = -A
    b_ub = -b

    if bounds is None:
        bounds = [(0, None)] * c.shape[0]

    res = linprog(c=c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method=method)

    out = {
        "success": bool(res.success),
        "status": int(res.status),
        "message": str(res.message),
        "x": None,
        "z": None,
    }

    if res.success:
        out["x"] = res.x
        out["z"] = float(res.fun)

    return out
