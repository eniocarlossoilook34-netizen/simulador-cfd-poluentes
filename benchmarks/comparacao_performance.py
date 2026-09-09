"""
Benchmark: Comparação entre solver NS normal vs otimizado.

Mostra speedup obtido com Numba JIT + vetorização.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from malha import Malha2D
from solver_ns_completo import SolverNSCompleto
from solver_ns_otimizado import SolverNSOtimizado
import time
import numpy as np


def benchmark_solver(SolverClass, nome, n_passos=100, malha=None):
    """Executa benchmark de um solver."""
    print(f"\n{'=' * 60}")
    print(f"Benchmarking: {nome}")
    print(f"{'=' * 60}")
    print(f"Passos: {n_passos}")
    print(f"Malha: {malha.nx}x{malha.ny}")

    # Criar solver
    solver = SolverClass(malha, rho=1.0, nu=0.01, dt=0.001)

    # Warm-up (para compilação JIT)
    if "Otimizado" in nome:
        print("Warm-up (compilação JIT)...")
        for _ in range(5):
            solver.passo_tempo(u_parede_top=1.0)

    # Benchmark
    print(f"Executando {n_passos} passos...")
    t_start = time.perf_counter()

    for step in range(n_passos):
        solver.passo_tempo(u_parede_top=1.0)
        if (step + 1) % max(10, n_passos // 5) == 0:
            t_elapsed = time.perf_counter() - t_start
            taxa = (step + 1) / t_elapsed
            print(f"  {step + 1:4d}/{n_passos} passos - {taxa:.1f} passos/s")

    t_total = time.perf_counter() - t_start
    tempo_passo = t_total / n_passos * 1000  # ms

    print(f"\nResultados:")
    print(f"  Tempo total: {t_total:.2f}s")
    print(f"  Tempo/passo: {tempo_passo:.2f} ms")
    print(f"  Taxa: {n_passos/t_total:.1f} passos/s")

    return {
        'nome': nome,
        'tempo_total': t_total,
        'tempo_passo': tempo_passo,
        'taxa': n_passos / t_total,
    }


def main():
    print("\n" + "#" * 60)
    print("# BENCHMARK: NS COMPLETO vs NS OTIMIZADO")
    print("#" * 60)

    # Setup da malha
    nx, ny = 64, 64
    malha = Malha2D(nx=nx, ny=ny, lx=1.0, ly=1.0)

    n_passos = 200

    # Benchmark 1: Normal (poucos passos, é lento)
    print("\n[1/2] Solver NS Completo (não-otimizado)...")
    print("      Rodando apenas 50 passos (é muito lento)...")
    resultado1 = benchmark_solver(SolverNSCompleto, "NS Completo", n_passos=50, malha=malha)

    # Extrapolate para 200 passos
    tempo_passo_normal = resultado1['tempo_passo']
    tempo_total_estimado = tempo_passo_normal * 200

    print(f"\n      Estimativa para 200 passos: {tempo_total_estimado:.2f}s")

    # Benchmark 2: Otimizado
    print("\n[2/2] Solver NS Otimizado (Numba JIT)...")
    resultado2 = benchmark_solver(SolverNSOtimizado, "NS Otimizado", n_passos=n_passos, malha=malha)

    # Comparação
    print("\n" + "=" * 60)
    print("RESUMO COMPARATIVO")
    print("=" * 60)

    speedup = tempo_passo_normal / resultado2['tempo_passo']
    speedup_estimado = tempo_total_estimado / (resultado2['tempo_passo'] * 200)

    print(f"\nSolver Normal:")
    print(f"  Tempo/passo: {tempo_passo_normal:.2f} ms")
    print(f"  Taxa (estimada): {1000/tempo_passo_normal:.1f} passos/s")

    print(f"\nSolver Otimizado:")
    print(f"  Tempo/passo: {resultado2['tempo_passo']:.2f} ms")
    print(f"  Taxa: {resultado2['taxa']:.1f} passos/s")

    print(f"\nSpeedup:")
    print(f"  Medido (50 passos): {speedup:.1f}x")
    print(f"  Estimado (200 passos): {speedup_estimado:.1f}x")

    print(f"\nMelhoria de Performance:")
    print(f"  Redução de tempo: {100*(1 - 1/speedup):.1f}%")
    print(f"  Aceleração: {speedup:.1f}x mais rápido")

    # Análise de overhead
    print(f"\n" + "-" * 60)
    print("BREAKDOWN TEMPORAL (NS Otimizado, 200 passos):")
    print("-" * 60)

    if hasattr(resultado2, 'temps'):
        print(f"Advecção-Difusão: {resultado2.get('tempo_advdif', 0):.3f}s")
        print(f"Poisson (SOR):    {resultado2.get('tempo_poisson', 0):.3f}s")
        print(f"Correção Pressão: {resultado2.get('tempo_correcao', 0):.3f}s")
    else:
        print("(Dados de breakdown não disponíveis)")

    print("\n" + "=" * 60)

    return speedup


if __name__ == "__main__":
    speedup = main()

    # Saída resumida
    print(f"\n[RESULTADO FINAL]")
    print(f"Speedup alcançado: {speedup:.1f}x")
    if speedup > 10:
        print("Status: EXCELENTE - Otimização muito bem-sucedida!")
    elif speedup > 5:
        print("Status: MUITO BOM")
    elif speedup > 2:
        print("Status: BOM")
    else:
        print("Status: RAZOÁVEL")
