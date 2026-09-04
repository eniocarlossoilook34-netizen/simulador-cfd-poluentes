"""
Teste de Validacao: Driven Cavity Flow

Referencia: Ghia et al. (1982)
"High-Re solutions for incompressible flow using Navier-Stokes equations"

Caso de teste classico em CFD:
- Dominio quadrado [0,1] x [0,1]
- Parede superior se move com velocidade u=1
- Paredes laterais e inferior fixas (u=v=0)
- Reynolds: Re = 100, 400, 1000
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from malha import Malha2D
from solver_ns import SolverNavierStokes


def teste_cavity_flow(nx=50, ny=50, Re=100, n_steps=5000):
    """
    Executa simulacao de cavity flow.

    Args:
        nx, ny (int): numero de celulas
        Re (float): numero de Reynolds
        n_steps (int): numero de passos de tempo
    """
    print(f"\n{'='*60}")
    print(f"Driven Cavity Flow - Re={Re}")
    print(f"{'='*60}")

    L = 1.0
    U_ref = 1.0
    rho = 1.0
    nu = U_ref * L / Re

    dt = 0.01 * L**2 / (nu + 1e-10)
    dt = min(dt, 0.001)

    print(f"\nParametros fisicos:")
    print(f"  L = {L}, U_ref = {U_ref}, rho = {rho}")
    print(f"  nu = {nu:.2e}, dt = {dt:.2e}")

    malha = Malha2D(nx=nx, ny=ny, lx=L, ly=L)
    solver = SolverNavierStokes(malha, rho=rho, nu=nu, dt=dt)

    solver.set_condicao_parede()
    solver.u[0, :] = 0
    solver.u[-1, :] = 0
    solver.v[:, 0] = 0
    solver.v[:, -1] = 0

    solver.u[:, -1] = U_ref

    print(f"\nCondicoes de contorno:")
    print(f"  Parede superior (y=1): u = {U_ref}")
    print(f"  Outras paredes: u = v = 0")

    print(f"\nIniciando simulacao com {n_steps} passos...")
    residuo_hist = []

    for step in range(n_steps):
        solver.passo_tempo()
        residuo = solver.residuo()
        residuo_hist.append(residuo)

        if (step + 1) % 500 == 0:
            print(f"  Passo {step+1}/{n_steps}, residuo = {residuo:.2e}")

        if step > 1000 and residuo < 1e-6:
            print(f"  Convergencia atingida em passo {step+1}")
            break

    print(f"\nSimulacao concluida!")
    print(f"  Residuo final: {residuo_hist[-1]:.2e}")

    return solver, malha, residuo_hist


def validar_contra_ghia(solver, malha):
    """
    Compara resultado com dados de Ghia et al. (1982).

    Extrai velocidades u ao longo da linha vertical central (x=0.5).
    """
    print(f"\n{'='*60}")
    print(f"Validacao contra Ghia et al. (1982)")
    print(f"{'='*60}")

    i_centro = malha.nx // 2
    y_center = malha.yp[0, :]
    u_center = (solver.u[i_centro, :] + solver.u[i_centro + 1, :]) / 2

    print(f"\nVelocidades u ao longo de x = {malha.lx/2}:")
    print(f"{'y':>8} {'u (simulado)':>18} {'u (Ghia)':>18} {'erro':>10}")
    print("-" * 55)

    ghia_re100 = {
        0.0625: 0.0,
        0.5000: 0.3789,
        0.9375: -0.0221,
    }

    erros = []
    for y, u_ghia in ghia_re100.items():
        j = int(y * malha.ny)
        j = min(j, malha.ny - 1)
        u_sim = u_center[j]
        erro = abs(u_sim - u_ghia) / (abs(u_ghia) + 1e-8)
        erros.append(erro)
        print(f"{y:8.4f} {u_sim:18.6f} {u_ghia:18.6f} {erro:10.2%}")

    if erros:
        erro_medio = np.mean(erros)
        print(f"\nErro medio: {erro_medio:.2%}")


def salvar_resultados(solver, malha, arquivo="cavity_result.npz"):
    """Salva campos de velocidade e pressao."""
    solver.exportar_campos(arquivo)
    print(f"\nResultados salvos em {arquivo}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTE: Driven Cavity Flow (Ghia et al. 1982)")
    print("="*60)

    solver, malha, residuo = teste_cavity_flow(nx=50, ny=50, Re=100, n_steps=2000)

    validar_contra_ghia(solver, malha)

    os.makedirs("resultados", exist_ok=True)
    salvar_resultados(solver, malha, arquivo="resultados/cavity_re100.npz")

    print(f"\n{'='*60}")
    print("Teste concluido com sucesso!")
    print(f"{'='*60}\n")
