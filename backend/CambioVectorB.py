import numpy


class CambioVectorB:
    def __init__(self, simplex):
        self.simplex = simplex

        self.tabla = simplex.tablafinal
        self.A = simplex.matrixA
        self.b = simplex.matrixB
        self.C = simplex.matrixC
        self.m = simplex.restriction
        self.n = simplex.variables

        self.col_basic = self.get_col_bas()
        self.B_inv = self.get_B_inv()

        self.basic_per_row = self.get_basic_per_row()
        self.cB = self.get_cB()

        self.c_ext = numpy.concatenate([self.C, numpy.zeros(self.m)])

    def get_basic_per_row(self, tol=1e-9):
        """
        Regresa un vector tamaño m:
        basic_per_row[i] = índice de columna de la variable básica en la fila i (orden arriba->abajo).
        """
        basic = [-1] * self.m

        for j in range(self.n + self.m):
            col = self.tabla[:self.m, j]

            # vector unidad con tolerancia
            ones = numpy.isclose(col, 1.0, atol=tol)
            zeros = numpy.isclose(col, 0.0, atol=tol)

            if ones.sum() == 1 and zeros.sum() == (self.m - 1):
                i = int(numpy.argmax(col))  # fila donde está el 1
                basic[i] = j  # esa columna es básica en esa fila

        # Si alguna fila quedó sin básica, la tabla no está en forma canónica
        if any(v == -1 for v in basic):
            raise ValueError("No se pudo identificar variable básica por fila. Revisa la tabla final.")

        return numpy.array(basic, dtype=int)

    def get_cB(self):
        """
        Construye cB en el orden de arriba->abajo (filas).
        Si la básica es holgura (j >= n), su costo es 0.
        """
        cB = numpy.zeros(self.m)
        for i in range(self.m):
            j = int(self.basic_per_row[i])
            if j < self.n:
                cB[i] = self.C[j]
            else:
                cB[i] = 0.0
        return cB

    def get_col_bas(self):
        indices = []
        for j in range(self.n + self.m):
            col = self.tabla[:self.m,j]
            if numpy.count_nonzero(col) == 1 and numpy.isclose(col.max(), 1.0):
                indices.append(j)
        return indices


    def get_B_inv(self):
        return self.tabla[:self.m,self.n:self.n+self.m].copy()


    def evalue(self, b_nuevo):
        b_nuevo = numpy.array(b_nuevo, dtype=float)
        Xb_nueva = self.B_inv @ b_nuevo

        #Se verifica si todos los valores son positivos
        factible = numpy.all(Xb_nueva >= 0)

        x_completa = numpy.zeros(self.n + self.m)
        # Construir x_completa usando el orden correcto por fila
        for i in range(self.m):
            j = self.basic_per_row[i]
            x_completa[j] = Xb_nueva[i]
            
        x_vars_orig = x_completa[:self.n]

        new_z = float(self.c_ext @ x_completa)


        dic_respuesta = {
            "x_nueva": x_vars_orig,
            "z_nueva": new_z,
            "factible": factible,
            "base_sigue_optima": factible,
            # datos crudos de la multiplicación
            "B_inv": self.B_inv,  # matriz B^{-1}
            "b_nuevo": b_nuevo,  # vector b' usado
            "xB_nueva": Xb_nueva,  # resultado x_B' = B^{-1} b'
            "x_completa": x_completa,  # x completo (básicas + no básicas)
            "basic_per_row": self.basic_per_row,  # qué variable es básica en cada fila
            "cB": self.cB,  # vector de costos de básicas (orden filas)
        }


        return dic_respuesta
