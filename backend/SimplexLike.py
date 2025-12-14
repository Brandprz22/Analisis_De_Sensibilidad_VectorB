import numpy as np

class SimplexLike:
    """
    Objeto mínimo para que CambioVectorB funcione cuando el usuario ingresa la tabla final.
    Debe exponer las mismas propiedades que tu clase Simplex usa/guarda.
    """
    def __init__(self, tablafinal, A, b, c, m, n):
        self.tablafinal = np.array(tablafinal, dtype=float)
        self.matrixA = np.array(A, dtype=float)
        self.matrixB = np.array(b, dtype=float)
        self.matrixC = np.array(c, dtype=float)
        self.restriction = int(m)
        self.variables = int(n)
