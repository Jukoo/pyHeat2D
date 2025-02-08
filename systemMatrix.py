import sympy as sy
import numpy as np
from scipy.sparse.linalg import spsolve # solving a sparse matrix
from scipy import sparse

class SystemMatrix:
    def __init__(self):
        """
        """
        pass
        # Declaration of symbolic variables
        #self.source_term = source_term if source_term else lambda Toc: 0

    def generate_coefficients(self, source_term=None):
        """
        Generate the generic coefficients for the system matrix.
        """
        if source_term is None:
            source_term = lambda Toc, Xc, Yc, t: 0

        # Declaration symbolic variables
        TW, TE, TN, TS, TC, Toc = sy.symbols('TW TE TN TS TC Toc')
        a = sy.symbols('a')
        dx, dy, d_dt, t = sy.symbols('dx dy d_dt t')
        Xc, Yc = sy.symbols('Xc Yc')
        TBC, g = sy.symbols('TBC g')  # dirichlet and neumann condition
        aW, aE, aS, aN, bW, bE, bS, bN, cW, cE, cS, cN = sy.symbols('aW, aE, aS, aN, bW, bE, bS, bN, cW, cE, cS, cN')
        k, rho, Cp = sy.symbols('k rho Cp')

        # expressing temperatures with generic boundary conditions
        TW1 = aW * TW + bW * (2 * a * TBC - TC) + cW * (TC - g * dx * a)
        TE1 = aE * TE + bE * (2 * a * TBC - TC) + cE * (TC + g * dx * a)
        TS1 = aS * TS + bS * (2 * a * TBC - TC) + cS * (TC - g * dy * a)
        TN1 = aN * TN + bN * (2 * a * TBC - TC) + cN * (TC + g * dy * a)

        qE = -k * (TE1 - TC) / dx
        qW = -k * (TC - TW1) / dx
        qN = -k * (TN1 - TC) / dy
        qS = -k * (TC - TS1) / dy
        symbolic_source_term = source_term(Toc, Xc, Yc, t)

        fT = (qE - qW) / dx + (qN - qS) / dy + rho * Cp * (TC - a * Toc) * d_dt - a * symbolic_source_term
        # compute the coefficients for the system matrix
        dofs = sy.Matrix([TE, TW, TS, TN, TC])
        coefficients = {}
        print("#############################################")
        print(" Generic computation of the 5 coefficients for the system matrix ")
        for i in range(len(dofs)):
            coeff = fT.diff(dofs[i])
            coefficients[str(dofs[i])] = coeff
            print(f'c{str(dofs[i])} = {str(coeff)}')
        # Compute the right-hand side
        rhs = -fT.diff(a)
        print("#############################################")
        print(" The generic right-hand side is ")
        print(f'{rhs} = {str(rhs)}')
        print("#################################################")
        return coefficients, rhs

    def interior_contribution_matrix(self, ncx, ncy):
        # Design the interior contribution matrix aW, aE, aS, aN
        aW = np.ones((ncx, ncy))
        aW[0, :] = 0
        aE = np.ones((ncx, ncy))
        aE[ncx - 1, :] = 0
        aS = np.ones((ncx, ncy))
        aS[:, 0] = 0
        aN = np.ones((ncx, ncy))
        aN[:, ncy - 1] = 0

        return aW, aE, aS, aN

    def build_matrix(self, ncx, ncy, dx1, dy1, dt1, time, Xc1, Yc1, rho1, Cp1, k1, aW1, bW1, cW1, aE1, bE1, cE1, aS1, bS1, cS1, aN1, bN1, cN1, Toc1, TBC1, g1, source_term):
        """
        Assemble the system matrix and RHS vector for a 2D heat equation with mixed boundary conditions.
        Generate the generic coefficients for the system matrix.
        """
        if source_term is None:
            source_term = lambda Toc, Xc, Yc, t: 0

        # Declaration symbolic variables
        TW, TE, TN, TS, TC, Toc = sy.symbols('TW TE TN TS TC Toc')
        a = sy.symbols('a')
        dx, dy, dt, t = sy.symbols('dx dy dt t')
        Xc, Yc = sy.symbols('Xc Yc')
        TBC, g = sy.symbols('TBC g')  # dirichlet and neumann condition
        aW, aE, aS, aN, bW, bE, bS, bN, cW, cE, cS, cN = sy.symbols('aW, aE, aS, aN, bW, bE, bS, bN, cW, cE, cS, cN')
        k, rho, Cp = sy.symbols('k rho Cp')

        # expressing temperatures with generic boundary conditions
        TW1 = aW * TW + bW * (2 * a * TBC - TC) + cW * (TC - g * dx * a)
        TE1 = aE * TE + bE * (2 * a * TBC - TC) + cE * (TC + g * dx * a)
        TS1 = aS * TS + bS * (2 * a * TBC - TC) + cS * (TC - g * dy * a)
        TN1 = aN * TN + bN * (2 * a * TBC - TC) + cN * (TC + g * dy * a)

        qE = -k * (TE1 - TC) / dx
        qW = -k * (TC - TW1) / dx
        qN = -k * (TN1 - TC) / dy
        qS = -k * (TC - TS1) / dy
        symbolic_source_term = source_term(Toc, Xc, Yc, t)
        fT = (qE - qW) / dx + (qN - qS) / dy + rho * Cp * (TC - a * Toc)/dt - a * symbolic_source_term
        # compute the coefficients for the system matrix
        dofs = sy.Matrix([TE, TW, TS, TN, TC])
        coefficients = {}
        for i in range(len(dofs)):
            coeff = fT.diff(dofs[i])
            coefficients[str(dofs[i])] = coeff
        # Compute the right-hand side
        rhs = -fT.diff(a)
        # transform sy Matrix to numpy using lambdify
        cTW = sy.lambdify((aW, k, dx), coefficients["TW"], "numpy")
        cTW = cTW(aW1, k1, dx1)

        cTE = sy.lambdify((aE, k, dx), coefficients["TE"], "numpy")
        cTE = cTE(aE1, k1, dx1)

        cTS = sy.lambdify((aS, k, dy), coefficients["TS"], "numpy")
        cTS = cTS(aS1, k1, dy1)

        cTN = sy.lambdify((aN, k, dy), coefficients["TN"], "numpy")
        cTN = cTN(aN1, k1, dy1)

        cTC = sy.lambdify((dx, dy, dt, Xc, Yc, rho, Cp, k, bW, cW, bE, cE, bS, cS, bN, cN), coefficients["TC"], "numpy")
        cTC = cTC(dx1, dy1, dt1, Xc1, Yc1, rho1, Cp1, k1, bW1, cW1, bE1, cE1, bS1, cS1, bN1, cN1)

        rhs = sy.lambdify((dx, dy, dt, t, Xc, Yc, rho, Cp, k, bW, cW, bE, cE, bS, cS, bN, cN, Toc, TBC, g), rhs, "numpy")
        rhs = rhs(dx1, dy1, dt1, time, Xc1, Yc1, rho1, Cp1, k1, bW1, cW1, bE1, cE1, bS1, cS1, bN1, cN1, Toc1, TBC1, g1)
        rhs = rhs.flatten()

        # Indices for grid neighbors
        NumTe = np.arange(ncx * ncy).reshape((ncx, ncy))
        iTe = NumTe  # Center indices
        iTeW = np.zeros((ncx, ncy))
        iTeW[1:ncx, :] = NumTe[0:ncx - 1, :]
        iTeE = np.zeros((ncx, ncy))
        iTeE[0:ncx - 1, :] = NumTe[1:ncx, :]
        iTeS = np.zeros((ncx, ncy))
        iTeS[:, 1:ncy] = NumTe[:, 0:ncy - 1]
        iTeN = np.zeros((ncx, ncy))
        iTeN[:, 0:ncy - 1] = NumTe[:, 1:ncy]
        # Assemble the sparse matrix
        I = np.concatenate((iTe.flatten(), iTe.flatten(), iTe.flatten(), iTe.flatten(), iTe.flatten()))
        J = np.concatenate((iTe.flatten(), iTeW.flatten(), iTeE.flatten(), iTeN.flatten(), iTeS.flatten()))
        J = J.astype(int)  # Ensure indices are integers
        V = np.concatenate((cTC.flatten(), cTW.flatten(), cTE.flatten(), cTN.flatten(), cTS.flatten()))
        TM = sparse.csc_matrix((V, (I, J)), (ncx * ncy, ncx * ncy))

        return TM, rhs

    def solve_system(self, TM, rhs):
        Tc = spsolve(TM, rhs)
        return Tc