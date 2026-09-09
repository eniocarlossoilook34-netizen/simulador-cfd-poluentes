"""Teste rápido do solver NS - verificação básica."""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from malha import Malha2D
from solver_ns_completo import SolverNSCompleto


def teste_rapido():
    """Teste rápido com poucos passos."""
    print("\n" + "=" * 60)
    print("TESTE RAPIDO: SOLVER NAVIER-STOKES COMPLETO")
    print("=" * 60)

    # Setup pequeno para teste rápido
    malha = Malha2D(nx=32, ny=32, lx=1.0, ly=1.0)
    nu = 0.01
    dt = 0.001

    solver = SolverNSCompleto(malha, rho=1.0, nu=nu, dt=dt)

    print(f"\nSetup:")
    print(f"  Malha: 32x32")
    print(f"  Dominio: 1.0 x 1.0 m")
    print(f"  dt: {dt} s")
    print(f"  nu: {nu} m²/s")
    print(f"  Re: {1.0 * malha.lx / nu:.0f}")

    # Simulacao: 100 passos apenas
    print(f"\nSimulando 100 passos...")
    for step in range(100):
        # Parede superior em movimento (u_wall = 1.0 m/s)
        solver.passo_tempo(u_parede_top=1.0)

        if (step + 1) % 20 == 0:
            u_vel = solver.velocidade_media()
            E_k = solver.energia_cinetica()
            vortic_max = np.max(np.abs(solver.vorticity()))
            print(f"  Passo {step + 1:3d}: u={u_vel:.4f} m/s, E_k={E_k:.2e}, "
                  f"omega_max={vortic_max:.4f}")

    print("\n" + "=" * 60)
    print("RESULTADOS")
    print("=" * 60)
    print(f"Velocidade media final: {solver.velocidade_media():.4f} m/s")
    print(f"Energia cinetica: {solver.energia_cinetica():.2e} J/m³")
    print(f"Vorticidade maxima: {np.max(np.abs(solver.vorticity())):.4f}")
    print(f"Pressao media: {np.mean(solver.p):.2e} Pa")

    # Verifica se está convergindo
    if solver.velocidade_media() > 0.01:
        print("\n[OK] Solver funcionando - velocidade nao-zero detectada")
        return True
    else:
        print("\n[WARN] Velocidade muito baixa - verificar solver")
        return False


if __name__ == "__main__":
    sucesso = teste_rapido()
    sys.exit(0 if sucesso else 1)
