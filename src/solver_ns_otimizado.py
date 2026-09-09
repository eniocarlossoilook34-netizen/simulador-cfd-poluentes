"""
Solver Navier-Stokes 2D Otimizado - Numba JIT + Vetorização NumPy.

Otimizações:
  1. Numba @njit para loops críticos (10-30x mais rápido)
  2. Vetorização NumPy para operações de Poisson
  3. Pré-alocação de arrays
  4. Evitar cópias desnecessárias

Speedup esperado: 10-30x comparado ao solver_ns_completo.py
"""

import numpy as np
from numba import njit, prange
import time


@njit(parallel=True)
def _adveccao_difusao_u_numba(u, v, u_star, dx, dy, nu, dt, nx, ny):
    """Calcula u* com Numba JIT (paralelizado)."""
    for i in prange(1, nx):
        for j in range(1, ny - 1):
            # Velocidades
            u_c = (u[i, j] + u[i + 1, j]) * 0.5
            v_c = (v[i, j] + v[i, j + 1]) * 0.5

            # Derivadas
            du_dx = (u[i + 1, j] - u[i - 1, j]) / (2 * dx)
            du_dy = (u[i, j + 1] - u[i, j - 1]) / (2 * dy)
            d2u_dx2 = (u[i + 1, j] - 2 * u[i, j] + u[i - 1, j]) / (dx * dx)
            d2u_dy2 = (u[i, j + 1] - 2 * u[i, j] + u[i, j - 1]) / (dy * dy)

            # RHS
            rhs = -u_c * du_dx - v_c * du_dy + nu * (d2u_dx2 + d2u_dy2)
            u_star[i, j] = u[i, j] + dt * rhs


@njit(parallel=True)
def _adveccao_difusao_v_numba(u, v, v_star, dx, dy, nu, dt, nx, ny):
    """Calcula v* com Numba JIT (paralelizado)."""
    for i in prange(1, nx - 1):
        for j in range(1, ny):
            # Velocidades
            u_c = (u[i, j] + u[i + 1, j]) * 0.5
            v_c = (v[i, j] + v[i, j + 1]) * 0.5

            # Derivadas
            dv_dx = (v[i + 1, j] - v[i - 1, j]) / (2 * dx)
            dv_dy = (v[i, j + 1] - v[i, j - 1]) / (2 * dy)
            d2v_dx2 = (v[i + 1, j] - 2 * v[i, j] + v[i - 1, j]) / (dx * dx)
            d2v_dy2 = (v[i, j + 1] - 2 * v[i, j] + v[i, j - 1]) / (dy * dy)

            # RHS
            rhs = -u_c * dv_dx - v_c * dv_dy + nu * (d2v_dx2 + d2v_dy2)
            v_star[i, j] = v[i, j] + dt * rhs


@njit(parallel=True)
def _poisson_sor_numba(p, u_star, v_star, rhs, dx, dy, rho, dt, omega, max_iter, tol, nx, ny):
    """Resolve Poisson com SOR (Numba JIT)."""
    residuo_medio = 1.0
    iteracao = 0

    # Pré-calcula coeficientes
    coef = 2.0 * (1.0 / (dx * dx) + 1.0 / (dy * dy))
    factor_x = 1.0 / (dx * dx)
    factor_y = 1.0 / (dy * dy)

    # RHS da equação
    rhs[:] = 0.0
    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            div = ((u_star[i + 1, j] - u_star[i, j]) / dx +
                   (v_star[i, j + 1] - v_star[i, j]) / dy)
            rhs[i, j] = (rho / dt) * div

    # Iteração SOR
    while residuo_medio > tol and iteracao < max_iter:
        residuo = 0.0

        for i in prange(1, nx - 1):
            for j in range(1, ny - 1):
                soma = (p[i + 1, j] + p[i - 1, j]) * factor_x + \
                       (p[i, j + 1] + p[i, j - 1]) * factor_y
                p_novo = (soma - rhs[i, j]) / coef
                p[i, j] = p[i, j] + omega * (p_novo - p[i, j])
                residuo += (p_novo - p[i, j]) ** 2

        residuo_medio = np.sqrt(residuo) / (nx * ny)
        iteracao += 1

    return residuo_medio


@njit(parallel=True)
def _correcao_velocidade_numba(u, v, p, u_star, v_star, dx, dy, rho, dt, nx, ny):
    """Atualiza velocidade com gradiente de pressão (Numba)."""
    for i in prange(1, nx):
        for j in range(ny):
            dp_dx = (p[i, j] - p[i - 1, j]) / dx
            u[i, j] = u_star[i, j] - (dt / rho) * dp_dx

    for i in prange(nx):
        for j in range(1, ny):
            dp_dy = (p[i, j] - p[i, j - 1]) / dy
            v[i, j] = v_star[i, j] - (dt / rho) * dp_dy


class SolverNSOtimizado:
    """Solver NS otimizado com Numba JIT."""

    def __init__(self, malha, rho=1000.0, nu=1e-6, dt=0.01):
        """
        Inicializa solver otimizado.

        Args:
            malha: malha 2D
            rho: densidade
            nu: viscosidade cinemática
            dt: passo temporal
        """
        self.m = malha
        self.rho = rho
        self.nu = nu
        self.dt = dt

        # Campos
        self.u = np.zeros((malha.nx + 1, malha.ny))
        self.v = np.zeros((malha.nx, malha.ny + 1))
        self.u_star = np.zeros_like(self.u)
        self.v_star = np.zeros_like(self.v)
        self.p = np.zeros((malha.nx, malha.ny))
        self.rhs = np.zeros((malha.nx, malha.ny))

        # Parâmetros SOR
        self.max_iter_poisson = 100
        self.tol_poisson = 1e-4
        self.omega = 1.8

        # Timer
        self.tempo_advdif = 0.0
        self.tempo_poisson = 0.0
        self.tempo_correcao = 0.0
        self.n_passos = 0

        print(f"Solver NS Otimizado (Numba JIT) inicializado")
        print(f"  rho={rho}, nu={nu}, dt={dt}")
        print(f"  Grid: u{self.u.shape}, v{self.v.shape}, p{self.p.shape}")

    def passo_tempo(self, u_parede_top=0.0):
        """Um passo temporal completo."""
        t0 = time.perf_counter()

        # Etapa 1: Advecção-Difusão (Numba JIT)
        t1 = time.perf_counter()
        self.u_star = self.u.copy()
        self.v_star = self.v.copy()

        _adveccao_difusao_u_numba(self.u, self.v, self.u_star,
                                  self.m.dx, self.m.dy, self.nu, self.dt,
                                  self.m.nx, self.m.ny)

        _adveccao_difusao_v_numba(self.u, self.v, self.v_star,
                                  self.m.dx, self.m.dy, self.nu, self.dt,
                                  self.m.nx, self.m.ny)

        self.tempo_advdif += time.perf_counter() - t1

        # Etapa 2: Poisson (Numba JIT)
        t2 = time.perf_counter()
        _poisson_sor_numba(self.p, self.u_star, self.v_star, self.rhs,
                           self.m.dx, self.m.dy, self.rho, self.dt,
                           self.omega, self.max_iter_poisson, self.tol_poisson,
                           self.m.nx, self.m.ny)
        self.tempo_poisson += time.perf_counter() - t2

        # Etapa 3: Correção (Numba JIT)
        t3 = time.perf_counter()
        _correcao_velocidade_numba(self.u, self.v, self.p, self.u_star, self.v_star,
                                   self.m.dx, self.m.dy, self.rho, self.dt,
                                   self.m.nx, self.m.ny)
        self.tempo_correcao += time.perf_counter() - t3

        # Condições de contorno
        self.set_condicao_parede()
        self.set_condicao_saida()

        if u_parede_top != 0.0:
            self.u[:, -1] = u_parede_top

        self.n_passos += 1

    def set_condicao_parede(self):
        """No-slip nas paredes."""
        self.u[:, 0] = 0.0
        self.u[:, -1] = 0.0
        self.v[:, 0] = 0.0
        self.v[:, -1] = 0.0

    def set_condicao_saida(self):
        """Extrapolação na saída."""
        self.u[-1, :] = self.u[-2, :]
        self.v[-1, :] = self.v[-2, :]

    def velocidade_media(self):
        """Velocidade média."""
        u_c = (self.u[:-1, :] + self.u[1:, :]) * 0.5
        v_c = (self.v[:, :-1] + self.v[:, 1:]) * 0.5
        return np.sqrt(np.mean(u_c) ** 2 + np.mean(v_c) ** 2)

    def energia_cinetica(self):
        """Energia cinética."""
        u_c = (self.u[:-1, :] + self.u[1:, :]) * 0.5
        v_c = (self.v[:, :-1] + self.v[:, 1:]) * 0.5
        return 0.5 * self.rho * np.mean(u_c ** 2 + v_c ** 2)

    def tempo_medio_passo(self):
        """Tempo médio por passo (ms)."""
        if self.n_passos == 0:
            return 0.0
        return 1000 * (self.tempo_advdif + self.tempo_poisson + self.tempo_correcao) / self.n_passos

    def resumo_performance(self):
        """Resumo de performance."""
        print("\n" + "=" * 60)
        print("PERFORMANCE - SOLVER NS OTIMIZADO")
        print("=" * 60)
        print(f"Total de passos: {self.n_passos}")
        print(f"Tempo advecção-difusão: {self.tempo_advdif:.3f}s ({100*self.tempo_advdif/(self.tempo_advdif + self.tempo_poisson + self.tempo_correcao):.1f}%)")
        print(f"Tempo Poisson (SOR): {self.tempo_poisson:.3f}s ({100*self.tempo_poisson/(self.tempo_advdif + self.tempo_poisson + self.tempo_correcao):.1f}%)")
        print(f"Tempo correção pressão: {self.tempo_correcao:.3f}s ({100*self.tempo_correcao/(self.tempo_advdif + self.tempo_poisson + self.tempo_correcao):.1f}%)")
        print(f"Tempo médio por passo: {self.tempo_medio_passo():.2f} ms")
        print(f"Taxa: {1/self.tempo_medio_passo()*1000:.1f} passos/s")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    from malha import Malha2D
    import sys

    print("\n" + "#" * 60)
    print("# BENCHMARK: SOLVER NS OTIMIZADO vs NÃO-OTIMIZADO")
    print("#" * 60 + "\n")

    # Setup
    malha = Malha2D(nx=64, ny=64, lx=1.0, ly=1.0)
    solver = SolverNSOtimizado(malha, rho=1.0, nu=0.01, dt=0.001)

    print("Rodando 500 passos...")
    import time
    t_start = time.perf_counter()

    for step in range(500):
        solver.passo_tempo(u_parede_top=1.0)
        if (step + 1) % 100 == 0:
            print(f"  {step + 1} passos: u={solver.velocidade_media():.4f}, "
                  f"tempo/passo={solver.tempo_medio_passo():.2f}ms")

    t_total = time.perf_counter() - t_start

    print(f"\nTempo total: {t_total:.2f}s")
    print(f"Tempo médio: {t_total/500*1000:.2f}ms/passo")
    print(f"Taxa: {500/t_total:.1f} passos/s")

    solver.resumo_performance()
