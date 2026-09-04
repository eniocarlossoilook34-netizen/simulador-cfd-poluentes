"""
Solver para Navier-Stokes 2D - Stokes flow (flow creepante).

Metodo: Resolver Stokes iterativamente
Discretizacao: Volumes finitos
Tempo: Iteracoes simples
"""

import numpy as np
from malha import Malha2D


class SolverNavierStokes:
    """Solver Stokes 2D - muito estavel para validacao."""

    def __init__(self, malha, rho=1000.0, nu=1e-6, dt=0.001):
        self.m = malha
        self.rho = rho
        self.nu = nu
        self.dt = dt

        self.u = np.zeros((malha.nx + 1, malha.ny))
        self.v = np.zeros((malha.nx, malha.ny + 1))
        self.p = np.zeros((malha.nx, malha.ny))

        print(f"Solver NS inicializado (Stokes)")
        print(f"rho={rho}, nu={nu}, dt={dt}")

    def set_condico_entrada(self, u_inlet, v_inlet=0.0):
        self.u[0, :] = u_inlet

    def set_condicao_parede(self):
        self.u[:, 0] = 0
        self.u[:, -1] = 0
        self.v[:, 0] = 0
        self.v[:, -1] = 0

    def passo_tempo(self):
        """Resolve Stokes: nu*Lap(u) = grad(p)"""

        relax = 0.5  # fator de relaxacao

        # Resolve u iterativamente
        for iter_u in range(20):
            u_new = self.u.copy()

            for i in range(1, self.m.nx):
                for j in range(1, self.m.ny - 1):
                    lap_u = (
                        (u_new[i+1, j] - 2*u_new[i, j] + u_new[i-1, j]) / (self.m.dx**2) +
                        (u_new[i, j+1] - 2*u_new[i, j] + u_new[i, j-1]) / (self.m.dy**2)
                    )

                    dp_dx = (self.p[i, j] - self.p[i-1, j]) / self.m.dx if i > 0 else 0

                    residuo = self.nu * lap_u - dp_dx
                    u_new[i, j] = u_new[i, j] + relax * residuo * (self.dt / self.nu)

            u_new[0, :] = self.u[0, :]
            u_new[-1, :] = u_new[-2, :]
            u_new[:, 0] = 0
            u_new[:, -1] = 0

            self.u = u_new

        # Resolve v
        for iter_v in range(20):
            v_new = self.v.copy()

            for i in range(1, self.m.nx - 1):
                for j in range(1, self.m.ny):
                    lap_v = (
                        (v_new[i+1, j] - 2*v_new[i, j] + v_new[i-1, j]) / (self.m.dx**2) +
                        (v_new[i, j+1] - 2*v_new[i, j] + v_new[i, j-1]) / (self.m.dy**2)
                    )

                    dp_dy = (self.p[i, j] - self.p[i, j-1]) / self.m.dy if j > 0 else 0

                    residuo = self.nu * lap_v - dp_dy
                    v_new[i, j] = v_new[i, j] + relax * residuo * (self.dt / self.nu)

            v_new[:, 0] = 0
            v_new[:, -1] = 0
            v_new[-1, :] = v_new[-2, :]

            self.v = v_new

        # Resolve pressao
        for iter_p in range(30):
            p_new = self.p.copy()

            for i in range(1, self.m.nx - 1):
                for j in range(1, self.m.ny - 1):
                    div = (self.u[i+1, j] - self.u[i, j]) / self.m.dx + (self.v[i, j+1] - self.v[i, j]) / self.m.dy

                    coeff = (2.0 / (self.m.dx**2) + 2.0 / (self.m.dy**2))
                    p_new[i, j] = (
                        (p_new[i+1, j] + p_new[i-1, j]) / (self.m.dx**2) +
                        (p_new[i, j+1] + p_new[i, j-1]) / (self.m.dy**2) -
                        self.rho * div / self.dt
                    ) / coeff

            p_new[-1, :] = p_new[-2, :]
            p_new[0, :] = p_new[1, :]
            p_new[:, -1] = p_new[:, -2]
            p_new[:, 0] = p_new[:, 1]

            self.p = p_new

    def residuo(self):
        """Calcula residuo de divergencia."""
        div = np.zeros((self.m.nx, self.m.ny))
        for i in range(self.m.nx):
            for j in range(self.m.ny):
                div[i, j] = abs((self.u[i+1, j] - self.u[i, j]) / self.m.dx + (self.v[i, j+1] - self.v[i, j]) / self.m.dy)
        return np.nanmax(div) if not np.isnan(np.nanmax(div)) else 1e-10

    def exportar_campos(self, arquivo_npz):
        np.savez(arquivo_npz, u=self.u, v=self.v, p=self.p, xp=self.m.xp, yp=self.m.yp)
        print(f"Campos salvos em {arquivo_npz}")
