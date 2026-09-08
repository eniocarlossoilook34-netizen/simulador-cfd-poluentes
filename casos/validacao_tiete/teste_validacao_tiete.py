"""
Teste completo: Validação do modelo CFD com dados reais do Rio Tietê.

Etapas:
1. Carrega dados reais do Rio Tietê
2. Executa simulação com parâmetros iniciais
3. Calibra modelo usando otimização Bayesiana
4. Valida resultado final
5. Salva gráficos comparativos
"""

import numpy as np
import sys
sys.path.insert(0, '../../src')
sys.path.insert(0, '../../visualizacao')

from dados_tiete import DadosTiete
from calibracao import CalibradorTiete
from plots import plotar_historico

import matplotlib.pyplot as plt
from pathlib import Path


def teste_validacao_tiete():
    """Executa validação completa com dados do Rio Tietê."""

    print("\n" + "#" * 70)
    print("# VALIDAÇÃO CFD COM DADOS REAIS DO RIO TIETÊ")
    print("#" * 70 + "\n")

    # ==============================================================
    # ETAPA 1: Carrega dados do Rio Tietê
    # ==============================================================
    print("[1/4] Carregando dados do Rio Tietê...")
    dados = DadosTiete()
    dados.resumo()

    # ==============================================================
    # ETAPA 2: Simulação com parâmetros iniciais
    # ==============================================================
    print("\n[2/4] Simulação com parâmetros iniciais...")
    calibrador = CalibradorTiete()

    # Parâmetros iniciais (baseline)
    D_inicial = 0.05  # m²/s
    k_inicial = 0.002  # /s

    print(f"  D_inicial = {D_inicial} m²/s")
    print(f"  k_inicial = {k_inicial} /s")

    resultado_inicial = calibrador.simular_cenario(D_inicial, k_inicial, verbose=True)

    # ==============================================================
    # ETAPA 3: Calibração por otimização
    # ==============================================================
    print("\n[3/4] Otimizando parâmetros (Bayesian optimization)...")
    resultado_otim = calibrador.otimizar(metodo='bayes', verbose=True)

    D_otim = resultado_otim['D_otimo']
    k_otim = resultado_otim['k_otimo']
    erro_otim = resultado_otim['erro_minimo']

    print(f"\nParâmetros calibrados:")
    print(f"  D_calibrado = {D_otim:.4f} m²/s")
    print(f"  k_calibrado = {k_otim:.4f} /s")
    print(f"  Erro RMSE: {erro_otim:.4f}")

    # ==============================================================
    # ETAPA 4: Validação final
    # ==============================================================
    print("\n[4/4] Validação final...")
    validacao = calibrador.validar_resultado(D_otim, k_otim)

    # ==============================================================
    # ETAPA 5: Gráficos de comparação
    # ==============================================================
    print("\nGerando visualizações...")

    # Cria diretório de resultados
    Path('resultados_validacao').mkdir(exist_ok=True)

    # Gráfico 1: Histórico de otimização
    historico = resultado_otim['historico']
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    ax = axes[0]
    ax.plot(historico['iteracao'], historico['erro'], 'b-o', linewidth=2)
    ax.set_xlabel('Iteração')
    ax.set_ylabel('Erro RMSE')
    ax.set_title('Convergência da Otimização')
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(historico['iteracao'], historico['D'], 'g-s', linewidth=2)
    ax.axhline(D_inicial, color='r', linestyle='--', label=f'Inicial: {D_inicial}')
    ax.axhline(D_otim, color='b', linestyle='--', label=f'Ótimo: {D_otim:.4f}')
    ax.set_xlabel('Iteração')
    ax.set_ylabel('D [m²/s]')
    ax.set_title('Evolução de D (Dispersão)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    ax.plot(historico['iteracao'], historico['k'], 'm-^', linewidth=2)
    ax.axhline(k_inicial, color='r', linestyle='--', label=f'Inicial: {k_inicial}')
    ax.axhline(k_otim, color='b', linestyle='--', label=f'Ótimo: {k_otim:.4f}')
    ax.set_xlabel('Iteração')
    ax.set_ylabel('k [/s]')
    ax.set_title('Evolução de k (Decaimento)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('resultados_validacao/historico_otimizacao.png', dpi=150, bbox_inches='tight')
    print("  ✓ Salvo: historico_otimizacao.png")
    plt.close()

    # Gráfico 2: Comparação de resultados
    resultado_otimizado = validacao['resultado']
    dados_ref = dados.gerar_dados_referencia()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # C_max
    ax = axes[0]
    ax.plot(dados_ref['tempo'], dados_ref['conc_max'], 'k-', linewidth=2, label='Referência')
    ax.plot(resultado_inicial['tempo'], resultado_inicial['conc_max'], 'r--', linewidth=2,
            label=f'Inicial (D={D_inicial}, k={k_inicial})', alpha=0.7)
    ax.plot(resultado_otimizado['tempo'], resultado_otimizado['conc_max'], 'b-', linewidth=2,
            label=f'Calibrado (D={D_otim:.4f}, k={k_otim:.4f})')
    ax.set_xlabel('Tempo [s]')
    ax.set_ylabel('Concentração máxima [kg/m³]')
    ax.set_title(f'Validação: C_max (R²={validacao["r2_max"]:.3f})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # C_media
    ax = axes[1]
    conc_media_ref = np.interp(resultado_inicial['tempo'], dados_ref['tempo'],
                                dados_ref['conc_media'])
    ax.plot(resultado_inicial['tempo'], conc_media_ref, 'k-', linewidth=2, label='Referência')
    ax.plot(resultado_inicial['tempo'], resultado_inicial['conc_media'], 'r--', linewidth=2,
            label='Inicial', alpha=0.7)
    ax.plot(resultado_otimizado['tempo'], resultado_otimizado['conc_media'], 'b-', linewidth=2,
            label='Calibrado')
    ax.set_xlabel('Tempo [s]')
    ax.set_ylabel('Concentração média [kg/m³]')
    ax.set_title(f'Validação: C_media (RMSE={validacao["rmse_media"]:.2f})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('resultados_validacao/comparacao_validacao.png', dpi=150, bbox_inches='tight')
    print("  ✓ Salvo: comparacao_validacao.png")
    plt.close()

    # ==============================================================
    # RESUMO FINAL
    # ==============================================================
    print("\n" + "=" * 70)
    print("RESUMO DA VALIDAÇÃO")
    print("=" * 70)
    print(f"\nRio: {dados.nome_rio}, São Paulo")
    print(f"Largura: {dados.largura} m | Profundidade: {dados.profundidade} m")
    print(f"Vazão média: {dados.vazao_media} m³/s | Velocidade: {dados.u_media:.3f} m/s")

    print(f"\nParâmetros Iniciais:")
    print(f"  D = {D_inicial} m²/s")
    print(f"  k = {k_inicial} /s")

    print(f"\nParâmetros Calibrados:")
    print(f"  D = {D_otim:.4f} m²/s ({100*(D_otim-D_inicial)/D_inicial:+.1f}% mudança)")
    print(f"  k = {k_otim:.4f} /s ({100*(k_otim-k_inicial)/k_inicial:+.1f}% mudança)")

    print(f"\nMétricas de Validação:")
    print(f"  RMSE (C_max): {validacao['rmse_max']:.2f} kg/m³")
    print(f"  RMSE (C_media): {validacao['rmse_media']:.2f} kg/m³")
    print(f"  R² (C_max): {validacao['r2_max']:.4f}")

    if validacao['r2_max'] > 0.7:
        status = "✓ EXCELENTE"
    elif validacao['r2_max'] > 0.5:
        status = "✓ BOA"
    else:
        status = "⚠ FRACA"
    print(f"  Status: {status}")

    print(f"\nResultados salvos em: resultados_validacao/")
    print("=" * 70 + "\n")

    return {
        'dados': dados,
        'D_otim': D_otim,
        'k_otim': k_otim,
        'validacao': validacao,
    }


if __name__ == "__main__":
    resultado = teste_validacao_tiete()

    # Pronto para usar com o modelo!
    print("✓ Validação concluída com sucesso!")
    print(f"Use estes parâmetros no seu modelo CFD:")
    print(f"  solver.D = {resultado['D_otim']:.4f}  # m²/s")
    print(f"  solver.k = {resultado['k_otim']:.4f}  # /s")
