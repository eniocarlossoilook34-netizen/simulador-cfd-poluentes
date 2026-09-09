"""
Validação contra Ghia et al. (1982) - Driven Cavity Flow.

Benchmark clássico: fluxo em cavidade quadrada com parede superior em movimento.
Compara velocidades numéricas contra dados de referência de Ghia.

Referência:
  Ghia, U., Ghia, K. N., Shin, C. T. (1982)
  "High-Re solutions for incompressible flow using the Navier-Stokes equations
  and a multigrid method"
  Journal of Computational Physics, 48(3), 387-411
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from malha import Malha2D
from solver_ns_completo import SolverNSCompleto


# Dados de referência Ghia et al. (1982) para Re=100
GHIA_RE100 = {
    'y': np.array([0.0, 0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5,
                   0.5625, 0.625, 0.6875, 0.75, 0.8125, 0.875, 0.9375, 1.0]),
    'u_centerline': np.array([0.0, -0.03717, -0.04192, -0.04775, -0.06434, -0.07119,
                              -0.07682, -0.07290, -0.02221, 0.02135, 0.07156, 0.12317,
                              0.16077, 0.17507, 0.17507, 0.05454, 0.0]),
}

GHIA_RE100_V = {
    'x': np.array([0.0, 0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5,
                   0.5625, 0.625, 0.6875, 0.75, 0.8125, 0.875, 0.9375, 1.0]),
    'v_centerline': np.array([0.0, 0.09233, 0.12317, 0.12317, 0.13546, 0.16622, 0.20920,
                              0.22810, 0.20920, 0.13546, 0.05454, -0.03891, -0.07682,
                              -0.09428, -0.07682, -0.02135, 0.0]),
}


def teste_cavity_flow(reynolds=100, nx=64, ny=64, n_steps=5000):
    """
    Simula driven cavity flow e compara com Ghia.

    Args:
        reynolds (float): número de Reynolds
        nx, ny (int): resolução da malha
        n_steps (int): número de passos temporais
    """
    print("\n" + "=" * 70)
    print(f"VALIDACAO: DRIVEN CAVITY FLOW (Re={reynolds})")
    print("=" * 70)

    # Setup
    lx, ly = 1.0, 1.0
    malha = Malha2D(nx=nx, ny=ny, lx=lx, ly=ly)

    # Viscosidade para Re = u*L / nu
    u_wall = 1.0
    nu = u_wall * lx / reynolds

    print(f"Parametros:")
    print(f"  Malha: {nx}x{ny}")
    print(f"  u_parede: {u_wall} m/s")
    print(f"  nu: {nu:.2e} m²/s")
    print(f"  Re: {reynolds}")

    # Solver
    dt = 0.01 * (malha.dx ** 2) / nu  # CFL stability
    solver = SolverNSCompleto(malha, rho=1.0, nu=nu, dt=dt)

    print(f"  dt: {dt:.2e} s (CFL-safe)")

    # Condicao inicial: velocidade zero
    # Condicao de contorno: parede superior (y=1) com u=1
    # Outras paredes: no-slip (u=v=0)

    # Simulacao
    print(f"\nSimulando {n_steps} passos temporais...")
    energia_historia = []

    for step in range(n_steps):
        # Parede superior em movimento
        solver.u[:, -1] = u_wall

        # Outras paredes: no-slip (já aplicado em set_condicao_parede)
        solver.set_condicao_parede(tipo='noslip')

        # Passo
        solver.passo_tempo()

        # Histórico
        E_k = solver.energia_cinetica()
        energia_historia.append(E_k)

        if (step + 1) % 500 == 0:
            print(f"  Passo {step + 1:4d}: E_k={E_k:.2e}, u_media={solver.velocidade_media():.4f}")

    print("\n" + "-" * 70)
    print("CONVERGENCIA")
    print("-" * 70)
    print(f"Energia cinética inicial: {energia_historia[0]:.2e}")
    print(f"Energia cinética final: {energia_historia[-1]:.2e}")
    print(f"Redução: {100 * (1 - energia_historia[-1] / energia_historia[0]):.1f}%")

    # Comparacao com Ghia
    print("\n" + "-" * 70)
    print("COMPARACAO COM GHIA ET AL. (1982)")
    print("-" * 70)

    # Extrai perfis
    u_centro = (solver.u[:-1, :] + solver.u[1:, :]) / 2
    v_centro = (solver.v[:, :-1] + solver.v[:, 1:]) / 2

    # Velocidade u na linha central (x=0.5)
    i_centro = nx // 2
    u_centerline_sim = u_centro[i_centro, :]
    y_sim = malha.yc

    # Velocidade v na linha central (y=0.5)
    j_centro = ny // 2
    v_centerline_sim = v_centro[:, j_centro]
    x_sim = malha.xc

    # Comparação U
    print("\nVelocidade U (na linha x=0.5):")
    print(f"{'y':>6s} | {'U_Ghia':>10s} | {'U_Sim':>10s} | {'Erro':>10s}")
    print("-" * 45)

    # Interpola Ghia para a malha atual
    y_ghia = GHIA_RE100['y']
    u_ghia = GHIA_RE100['u_centerline']

    u_ghia_interp = np.interp(y_sim, y_ghia, u_ghia)
    erro_u = np.abs(u_centerline_sim - u_ghia_interp)
    rmse_u = np.sqrt(np.mean(erro_u ** 2))

    for j in range(0, len(y_sim), max(1, len(y_sim) // 10)):
        print(f"{y_sim[j]:6.3f} | {u_ghia_interp[j]:10.5f} | {u_centerline_sim[j]:10.5f} | {erro_u[j]:10.5f}")

    print(f"\nRMSE(U): {rmse_u:.2e}")

    # Comparação V
    print("\nVelocidade V (na linha y=0.5):")
    print(f"{'x':>6s} | {'V_Ghia':>10s} | {'V_Sim':>10s} | {'Erro':>10s}")
    print("-" * 45)

    x_ghia = GHIA_RE100_V['x']
    v_ghia = GHIA_RE100_V['v_centerline']

    v_ghia_interp = np.interp(x_sim, x_ghia, v_ghia)
    erro_v = np.abs(v_centerline_sim - v_ghia_interp)
    rmse_v = np.sqrt(np.mean(erro_v ** 2))

    for i in range(0, len(x_sim), max(1, len(x_sim) // 10)):
        print(f"{x_sim[i]:6.3f} | {v_ghia_interp[i]:10.5f} | {v_centerline_sim[i]:10.5f} | {erro_v[i]:10.5f}")

    print(f"\nRMSE(V): {rmse_v:.2e}")

    # Validacao
    print("\n" + "=" * 70)
    if rmse_u < 0.05 and rmse_v < 0.05:
        print("VALIDACAO: [OK] EXCELENTE - RMSE < 0.05")
    elif rmse_u < 0.1 and rmse_v < 0.1:
        print("VALIDACAO: [OK] BOA - RMSE < 0.1")
    else:
        print("VALIDACAO: [WARN] FRACA - RMSE > 0.1")
    print("=" * 70 + "\n")

    return {
        'solver': solver,
        'energia_historia': np.array(energia_historia),
        'rmse_u': rmse_u,
        'rmse_v': rmse_v,
        'u_sim': u_centerline_sim,
        'v_sim': v_centerline_sim,
        'y_sim': y_sim,
        'x_sim': x_sim,
    }


if __name__ == "__main__":
    # Teste com Re=100 (menor computação)
    resultado = teste_cavity_flow(reynolds=100, nx=64, ny=64, n_steps=5000)

    print(f"\nResultados:")
    print(f"  RMSE(U): {resultado['rmse_u']:.2e}")
    print(f"  RMSE(V): {resultado['rmse_v']:.2e}")

    # Opcional: Re=400 (mais desafiador)
    # resultado2 = teste_cavity_flow(reynolds=400, nx=128, ny=128, n_steps=10000)
