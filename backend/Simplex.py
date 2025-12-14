import  numpy

class Simplex:

    def __init__(self,MatrixA,MatrixB,MatrixC, restriction, variables):
        self.matrixA = numpy.array(MatrixA, dtype=float)
        self.matrixB = numpy.array(MatrixB, dtype=float)
        self.matrixC = numpy.array(MatrixC, dtype=float)
        self.restriction = restriction
        self.variables = variables
        self.tablafinal = numpy.zeros((self.restriction+1,self.variables+self.restriction+1), dtype=float)

    def initialTable(self):
        m = self.restriction
        n = self.variables

        #Se agrega el vector C
        matrixC_aux = -numpy.array(self.matrixC, dtype=float)
        self.tablafinal[m,:n] = matrixC_aux
        self.tablafinal[m, -1] = 0.0 #Se asigna valor de la sol de c

        #Se copia la matriz a
        self.tablafinal[:m,:n] = self.matrixA

        #Se agrega la matriz identidad
        self.tablafinal[:m, n:n+m] = numpy.eye(m)

        #Se agrega el vector b
        self.tablafinal[:m, -1] = self.matrixB

    def choose_variable_ent(self):
        vectorC = self.tablafinal[self.restriction,:-1]
        n_col_piv = int(numpy.argmin(vectorC))
        more_negative_value = vectorC[n_col_piv]

        if more_negative_value >= 0:
            return -1

        return n_col_piv

    def choose_variable_leave(self, n_col_piv):
        m = self.restriction

        vectorb = self.tablafinal[:m,-1]
        col_piv = self.tablafinal[:m,n_col_piv]

        list_cos = []

        #Se calcula el cosciente de forma iterativa
        for i in range(m):
            a_ij = col_piv[i]
            b_i = vectorb[i]
            #Unicamente se considera valores pos
            if a_ij > 0:
                cosciente = b_i/a_ij
            else:
                cosciente = numpy.inf
            list_cos.append(cosciente)

        n_row_piv = int(numpy.argmin(list_cos))
        if list_cos[n_row_piv] == numpy.inf:
            return -1

        return n_row_piv

    def pivot(self, n_row_piv, n_col_piv):
        v_pivot = self.tablafinal[n_row_piv, n_col_piv]

        #Se normaliza la fila pivote
        factor_norm = v_pivot**(-1)
        piv_row = self.tablafinal[n_row_piv]
        new_row = factor_norm * (numpy.array(piv_row))
        self.tablafinal[n_row_piv] = new_row

        #Se hacen 0's los demas valores de columnas iterando con el resto de filas
        for i in range(self.restriction+1):
            if i != n_row_piv:
                factor = self.tablafinal[i,n_col_piv]
                new_row = self.tablafinal[i] - factor*self.tablafinal[n_row_piv]
                self.tablafinal[i] = new_row

    def solve(self):
        self.initialTable()
        should_cont = True
        while should_cont:
            n_col_piv = self.choose_variable_ent()
            if n_col_piv == -1:
                should_cont = False
                break

            n_row_piv = self.choose_variable_leave(n_col_piv)
            if n_row_piv == -1:
                should_cont = False
                break

            self.pivot(n_row_piv, n_col_piv)

    def get_solution(self):
        m = self.restriction
        n = self.variables

        solucion = numpy.zeros(n + m)

        # Buscamos columnas que sean vector unidad (1 en una fila, 0 en las demás)
        for j in range(n + m):
            col = self.tablafinal[:m, j]  # solo filas de restricciones
            if numpy.count_nonzero(col) == 1 and numpy.isclose(col.max(), 1.0):
                fila = numpy.argmax(col)
                solucion[j] = self.tablafinal[fila, -1]

        x = solucion[:n]      # variables originales
        s = solucion[n:]      # holguras
        z = self.tablafinal[m, -1]  # valor óptimo de la FO

        return x, s, z

    def get_tabla(self):
        return self.tablafinal.tolist()