"""
Solver Navier-Stokes 2D Incompressível - Método Fractional-Step.

Equações:
  ∇·u = 0                                    (continuidade)
  ∂u/∂t + u·∇u = -∇p + ν∇²u + f            (quantidade de movimento)

Método: Fractional-Step (Chorin, 1967)
  1. Passo de advecção-difusão (velocidade intermediária)
  2. Correção de pressão (Poisson)
  3. Projeção (atualização de velocidade)

Resolução de Poisson: SOR (Successive Over-Relaxation)
"""

import numpy as np
from scipy.ndimage import convolve


class SolverNSCompleto:
    """Solver Navier-Stokes 2D incompressível com Fractional-Step."""

    def __init__(self, malha, rho=1000.0, nu=1e-6, dt=0.01):
        """
        Inicializa solver NS completo.

        Args:
            malha (Malha2D): malha estruturada 2D
            rho (float): densidade [kg/m³]
            nu (float): viscosidade cinemática [m²/s]
            dt (float): passo temporal [s]
        """
        self.m = malha
        self.rho = rho
        self.nu = nu
        self.dt = dt

        # Campos de velocidade (grid escalonado)
        # u em faces verticais: (nx+1, ny)
        # v em faces horizontais: (nx, ny+1)
        self.u = np.zeros((malha.nx + 1, malha.ny))
        self.v = np.zeros((malha.nx, malha.ny + 1))
        self.u_star = np.zeros_like(self.u)
        self.v_star = np.zeros_like(self.v)

        # Pressão (centros de células)
        self.p = np.zeros((malha.nx, malha.ny))
        self.p_old = np.zeros_like(self.p)

        # Número de iterações SOR
        self.max_iter_poisson = 100
        self.tol_poisson = 1e-4
        self.omega = 1.8  # fator de relaxação SOR (1 < omega < 2)

        # Forças externas
        self.fx = np.zeros((malha.nx, malha.ny))
        self.fy = np.zeros((malha.nx, malha.ny))

        # Histórico de resíduos
        self.residuos_poisson = []

        print(f"Solver NS Completo inicializado")
        print(f"  rho={rho} kg/m³, nu={nu} m²/s, dt={dt} s")
        print(f"  Grid escalonado: u({self.u.shape}), v({self.v.shape}), p({self.p.shape})")

    def set_condicao_velocidade_entrada(self, u_inlet, v_inlet=0.0):
        """Define velocidade na entrada (x=0)."""
        self.u[0, :] = u_inlet
        self.v[0, :] = v_inlet

    def set_condicao_velocidade_saida(self, extrapolacao=True):
        """
        Condição de saída: extrapolação de velocidade ou Neumann.

        Args:
            extrapolacao (bool): True = extrapolação, False = Neumann
        """
        if extrapolacao:
            self.u[-1, :] = self.u[-2, :]
            self.v[-1, :] = self.v[-2, :]

    def set_condicao_parede(self, tipo='noslip'):
        """
        Condições nas paredes (y=0, y=Ly).

        Args:
            tipo (str): 'noslip' (u=v=0) ou 'freeslip' (v=0, du/dy=0)
        """
        if tipo == 'noslip':
            # y=0: u e v = 0
            self.u[:, 0] = 0.0
            self.v[:, 0] = 0.0
            self.u[:, 1] = 0.0

            # y=Ly: u e v = 0
            self.u[:, -1] = 0.0
            self.v[:, -1] = 0.0
            self.v[:, -2] = 0.0

        elif tipo == 'freeslip':
            # y=0: v=0, du/dy=0 (slip)
            self.v[:, 0] = 0.0
            # u[:, 0] already satisfies du/dy=0 by symmetry

            # y=Ly: v=0
            self.v[:, -1] = 0.0

    def _adveccao_difusao_u(self):
        """Calcula velocidade intermediária u* (advecção + difusão)."""
        u, v, nu, dt, dx, dy = self.u, self.v, self.nu, self.dt, self.m.dx, self.m.dy

        self.u_star = u.copy()

        for i in range(1, self.m.nx):
            for j in range(1, self.m.ny - 1):
                # Velocidade nos centros (interpolação)
                u_centro = (u[i, j] + u[i + 1, j]) / 2
                v_centro = (v[i, j] + v[i, j + 1]) / 2

                # Advecção (diferenças centrais, 2ª ordem)
                du_dx = (u[i + 1, j] - u[i - 1, j]) / (2 * dx)
                du_dy = (u[i, j + 1] - u[i, j - 1]) / (2 * dy)

                # Difusão (diferenças centrais, 2ª ordem)
                d2u_dx2 = (u[i + 1, j] - 2 * u[i, j] + u[i - 1, j]) / (dx ** 2)
                d2u_dy2 = (u[i, j + 1] - 2 * u[i, j] + u[i, j - 1]) / (dy ** 2)

                # Termo de advecção-difusão
                rhs = -u_centro * du_dx - v_centro * du_dy + nu * (d2u_dx2 + d2u_dy2)

                # Euler explícito
                self.u_star[i, j] = u[i, j] + dt * rhs + dt * self.fx[i, j] / self.rho

    def _adveccao_difusao_v(self):
        """Calcula velocidade intermediária v* (advecção + difusão)."""
        u, v, nu, dt, dx, dy = self.u, self.v, self.nu, self.dt, self.m.dx, self.m.dy

        self.v_star = v.copy()

        for i in range(1, self.m.nx - 1):
            for j in range(1, self.m.ny):
                # Velocidade nos centros
                u_centro = (u[i, j] + u[i + 1, j]) / 2
                v_centro = (v[i, j] + v[i, j + 1]) / 2

                # Advecção
                dv_dx = (v[i + 1, j] - v[i - 1, j]) / (2 * dx)
                dv_dy = (v[i, j + 1] - v[i, j - 1]) / (2 * dy)

                # Difusão
                d2v_dx2 = (v[i + 1, j] - 2 * v[i, j] + v[i - 1, j]) / (dx ** 2)
                d2v_dy2 = (v[i, j + 1] - 2 * v[i, j] + v[i, j - 1]) / (dy ** 2)

                # Termo de advecção-difusão
                rhs = -u_centro * dv_dx - v_centro * dv_dy + nu * (d2v_dx2 + d2v_dy2)

                # Euler explícito
                self.v_star[i, j] = v[i, j] + dt * rhs + dt * self.fy[i, j] / self.rho

    def _poisson_sor(self):
        """
        Resolve equação de Poisson para pressão usando SOR.

        Equação: ∇²p = (rho/dt) * (∇·u*)

        Onde u* é a velocidade intermediária.
        """
        dx, dy, dt, rho = self.m.dx, self.m.dy, self.dt, self.rho
        nx, ny = self.m.nx, self.m.ny

        # Lado direito: divergência de u*
        rhs = np.zeros((nx, ny))
        for i in range(1, nx - 1):
            for j in range(1, ny - 1):
                div_u_star = ((self.u_star[i + 1, j] - self.u_star[i, j]) / dx +
                              (self.v_star[i, j + 1] - self.v_star[i, j]) / dy)
                rhs[i, j] = (rho / dt) * div_u_star

        # Iteração SOR
        p = self.p.copy()
        residuo_medio = 1.0
        iteracao = 0

        while residuo_medio > self.tol_poisson and iteracao < self.max_iter_poisson:
            residuo = 0.0

            for i in range(1, nx - 1):
                for j in range(1, ny - 1):
                    # Stencil de 5 pontos para Laplaciano
                    soma = ((p[i + 1, j] + p[i - 1, j]) / (dx ** 2) +
                            (p[i, j + 1] + p[i, j - 1]) / (dy ** 2))

                    coef = 2 * (1 / (dx ** 2) + 1 / (dy ** 2))

                    # SOR: correção com fator omega
                    p_novo = (soma - rhs[i, j]) / coef
                    p[i, j] = p[i, j] + self.omega * (p_novo - p[i, j])

                    # Calcula resíduo
                    residuo += abs(p_novo - p[i, j]) ** 2

            residuo_medio = np.sqrt(residuo) / (nx * ny)
            iteracao += 1

        self.p = p
        self.residuos_poisson.append(residuo_medio)

        if iteracao >= self.max_iter_poisson:
            print(f"  ⚠ Poisson: {iteracao} iterações (tol={residuo_medio:.2e})")

    def _correcao_velocidade(self):
        """Atualiza velocidade usando gradiente de pressão."""
        dt, rho, dx, dy = self.dt, self.rho, self.m.dx, self.m.dy

        # Gradiente de pressão em u (faces verticais)
        for i in range(1, self.m.nx):
            for j in range(self.m.ny):
                dp_dx = (self.p[i, j] - self.p[i - 1, j]) / dx
                self.u[i, j] = self.u_star[i, j] - (dt / rho) * dp_dx

        # Gradiente de pressão em v (faces horizontais)
        for i in range(self.m.nx):
            for j in range(1, self.m.ny):
                dp_dy = (self.p[i, j] - self.p[i, j - 1]) / dy
                self.v[i, j] = self.v_star[i, j] - (dt / rho) * dp_dy

    def passo_tempo(self, u_parede_top=0.0):
        """
        Executa um passo de tempo completo (Fractional-Step).

        Args:
            u_parede_top (float): velocidade da parede superior
        """
        # Etapa 1: Advecção-Difusão
        self._adveccao_difusao_u()
        self._adveccao_difusao_v()

        # Etapa 2: Resolução de Poisson
        self._poisson_sor()

        # Etapa 3: Correção de Pressão
        self._correcao_velocidade()

        # Condições de contorno
        self.set_condicao_parede(tipo='noslip')
        self.set_condicao_velocidade_saida()

        # Parede superior em movimento
        if u_parede_top != 0.0:
            self.u[:, -1] = u_parede_top

    def Reynolds(self, u_ref, L_ref):
        """Calcula número de Reynolds."""
        return u_ref * L_ref / self.nu

    def velocidade_media(self):
        """Retorna velocidade média do domínio."""
        u_centro = (self.u[:-1, :] + self.u[1:, :]) / 2
        v_centro = (self.v[:, :-1] + self.v[:, 1:]) / 2
        return np.sqrt(np.mean(u_centro) ** 2 + np.mean(v_centro) ** 2)

    def energia_cinetica(self):
        """Calcula energia cinética total."""
        u_centro = (self.u[:-1, :] + self.u[1:, :]) / 2
        v_centro = (self.v[:, :-1] + self.v[:, 1:]) / 2
        vel_sq = u_centro ** 2 + v_centro ** 2
        return 0.5 * self.rho * np.mean(vel_sq)

    def vorticity(self):
        """Calcula vorticidade ω = ∂v/∂x - ∂u/∂y."""
        dx, dy = self.m.dx, self.m.dy
        u_centro = (self.u[:-1, :] + self.u[1:, :]) / 2
        v_centro = (self.v[:, :-1] + self.v[:, 1:]) / 2

        # Derivadas
        dv_dx = np.zeros_like(u_centro)
        du_dy = np.zeros_like(u_centro)

        for i in range(1, self.m.nx - 1):
            for j in range(1, self.m.ny - 1):
                dv_dx[i, j] = (self.v[i + 1, j] - self.v[i - 1, j]) / (2 * dx)
                du_dy[i, j] = (self.u[i, j + 1] - self.u[i, j - 1]) / (2 * dy)

        return dv_dx - du_dy

    def resumo(self):
        """Imprime resumo do estado atual."""
        print("\n" + "=" * 60)
        print("SOLVER NAVIER-STOKES (FRACTIONAL-STEP)")
        print("=" * 60)
        print(f"Densidade: {self.rho} kg/m³")
        print(f"Viscosidade: {self.nu} m²/s")
        print(f"Reynolds: {self.Reynolds(self.velocidade_media(), self.m.lx):.0f}")
        print(f"Velocidade média: {self.velocidade_media():.4f} m/s")
        print(f"Energia cinética: {self.energia_cinetica():.2e} J/m³")
        print(f"Pressão média: {np.mean(self.p):.2e} Pa")
        print(f"Iterações Poisson último passo: {len(self.residuos_poisson)}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    from malha import Malha2D

    # Teste: flow uniforme com parede
    malha = Malha2D(nx=40, ny=40, lx=1.0, ly=1.0)
    solver = SolverNSCompleto(malha, rho=1.0, nu=0.01, dt=0.001)

    # Condição inicial: fluxo uniforme
    solver.u[0, :] = 1.0

    print("Simulando 10 passos...")
    for t in range(10):
        solver.passo_tempo()
        if t % 5 == 0:
            print(f"  Passo {t}: u_media={solver.velocidade_media():.4f}, "
                  f"E_k={solver.energia_cinetica():.2e}")

    solver.resumo()
    print("OK!")
