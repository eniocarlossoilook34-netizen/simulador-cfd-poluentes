"""
Calibração de parâmetros do modelo CFD com dados reais do Rio Tietê.

Otimização: ajusta D (dispersão) e k (decaimento) para minimizar erro
entre simulação e dados observados.
"""

import numpy as np
from scipy.optimize import minimize, differential_evolution
import sys
sys.path.insert(0, '../../src')
from malha import Malha2D
from solver_ns_simples import SolverEscoamentoPrescrito
from solver_advdiff import SolverAdveccaoDifusao
from dados_tiete import DadosTiete


class CalibradorTiete:
    """Calibração de parâmetros do modelo para Rio Tietê."""

    def __init__(self, n_pontos=20):
        """
        Inicializa calibrador.

        Args:
            n_pontos (int): número de pontos de monitoramento simulados
        """
        self.dados_tiete = DadosTiete()
        self.n_pontos = n_pontos

        # Domínio físico
        self.lx = self.dados_tiete.comprimento_dominio  # 100 m
        self.ly = self.dados_tiete.largura  # 50 m

        # Parâmetros para variar
        self.D_range = (0.001, 0.5)  # m²/s
        self.k_range = (0.0, 0.01)  # /s

        # Histórico de otimização
        self.historico = {
            'iteracao': [],
            'erro': [],
            'D': [],
            'k': [],
        }

    def simular_cenario(self, D, k, verbose=False):
        """
        Executa simulação com parâmetros (D, k).

        Args:
            D (float): coeficiente de dispersão [m²/s]
            k (float): taxa de decaimento [1/s]
            verbose (bool): imprime progresso

        Returns:
            dict: resultados da simulação (conc_max, conc_media, tempo)
        """
        nx, ny = 80, 40
        malha = Malha2D(nx=nx, ny=ny, lx=self.lx, ly=self.ly)

        # Escoamento uniforme (velocidade média do Tietê)
        escoamento = SolverEscoamentoPrescrito(
            malha,
            tipo='uniforme',
            u_ref=self.dados_tiete.u_media
        )

        # Solver de transporte
        dt = 0.5
        solver_c = SolverAdveccaoDifusao(malha, D=D, dt=dt)
        solver_c.set_taxa_decaimento(k)

        # Simulação: 150 segundos com lançamento no meio
        n_steps = 300
        conc_max_lista = []
        conc_media_lista = []
        tempo_lista = []

        # Posição de lançamento (esgoto)
        i_lancamento = nx // 4  # 25% do domínio
        j_lancamento = ny // 2  # meio da largura

        for passo in range(n_steps):
            t_atual = passo * dt

            # Lançamento de esgoto (10-30s)
            if 10 <= t_atual <= 30:
                solver_c.adicionar_fonte(i_lancamento, j_lancamento, 50.0)

            # Avança tempo
            solver_c.passo_tempo(escoamento.u, escoamento.v)

            # Coleta dados
            if passo % 2 == 0:  # a cada 1 segundo
                conc_max_lista.append(solver_c.conc_max())
                conc_media_lista.append(solver_c.conc_media())
                tempo_lista.append(t_atual)

        if verbose:
            print(f"  D={D:.4f}, k={k:.4f}: C_max={np.max(conc_max_lista):.1f}, "
                  f"tau_95={self._tempo_95(conc_max_lista, tempo_lista):.1f}s")

        return {
            'tempo': np.array(tempo_lista),
            'conc_max': np.array(conc_max_lista),
            'conc_media': np.array(conc_media_lista),
        }

    def _tempo_95(self, conc, tempo):
        """Calcula tempo de decaimento para 95% de redução."""
        conc_max_inicial = np.max(conc)
        limite = 0.05 * conc_max_inicial
        idx = np.where(conc < limite)[0]
        if len(idx) > 0:
            return tempo[idx[0]]
        return tempo[-1]

    def calcular_erro(self, D, k):
        """
        Calcula erro entre simulação e dados de referência.

        Args:
            D (float): dispersão
            k (float): decaimento

        Returns:
            float: erro RMSE normalizado
        """
        try:
            resultado = self.simular_cenario(D, k, verbose=False)
        except:
            return 1e6  # penalidade para simulações que falham

        # Dados de referência
        dados_ref = self.dados_tiete.gerar_dados_referencia()

        # Interpola dados de referência nos tempos simulados
        conc_max_ref_interp = np.interp(resultado['tempo'], dados_ref['tempo'],
                                         dados_ref['conc_max'])
        conc_media_ref_interp = np.interp(resultado['tempo'], dados_ref['tempo'],
                                           dados_ref['conc_media'])

        # RMSE normalizado
        erro_max = np.sqrt(np.mean((resultado['conc_max'] - conc_max_ref_interp) ** 2))
        erro_media = np.sqrt(np.mean((resultado['conc_media'] - conc_media_ref_interp) ** 2))

        # Peso: preferir ajuste de conc_max (mais sensível)
        erro_total = 0.7 * erro_max + 0.3 * erro_media

        return erro_total

    def otimizar(self, metodo='bayes', verbose=True):
        """
        Otimiza parâmetros D e k.

        Args:
            metodo (str): 'bayes' (recomendado) ou 'gradiente'
            verbose (bool): imprime progresso

        Returns:
            dict: parâmetros ótimos e histórico
        """
        if verbose:
            print("\n" + "=" * 60)
            print("CALIBRAÇÃO: Rio Tietê")
            print("=" * 60)
            print("Otimizando D (dispersão) e k (decaimento)...")
            print(f"D: {self.D_range[0]:.4f} - {self.D_range[1]:.4f} m²/s")
            print(f"k: {self.k_range[0]:.4f} - {self.k_range[1]:.4f} /s")
            print("=" * 60 + "\n")

        if metodo == 'bayes':
            bounds = [self.D_range, self.k_range]
            # Wrapper para desempacotar array [D, k]
            def objetivo(x):
                return self.calcular_erro(x[0], x[1])

            resultado = differential_evolution(
                objetivo,
                bounds,
                seed=42,
                maxiter=15,
                popsize=20,
                atol=1e-3,
                tol=1e-3,
                workers=1,
                updating='deferred',
                callback=self._callback_otimizacao if verbose else None
            )
            D_otim, k_otim = resultado.x
            erro_otim = resultado.fun

        else:  # gradiente
            x0 = [0.05, 0.002]
            resultado = minimize(
                self.calcular_erro,
                x0,
                method='Nelder-Mead',
                options={'maxiter': 50},
                callback=self._callback_otimizacao if verbose else None
            )
            D_otim, k_otim = resultado.x
            erro_otim = resultado.fun

        if verbose:
            print("\n" + "=" * 60)
            print("RESULTADOS DA OTIMIZAÇÃO")
            print("=" * 60)
            print(f"D ótimo: {D_otim:.4f} m²/s")
            print(f"k ótimo: {k_otim:.4f} /s (taxa de decaimento)")
            print(f"Erro RMSE: {erro_otim:.4f}")
            print("=" * 60 + "\n")

        return {
            'D_otimo': D_otim,
            'k_otimo': k_otim,
            'erro_minimo': erro_otim,
            'historico': self.historico,
        }

    def _callback_otimizacao(self, xk, convergence=None):
        """Callback para imprimir progresso."""
        if isinstance(xk, dict):  # differential_evolution
            D, k = xk['x']
            erro = xk['fun']
        else:
            D, k = xk
            erro = self.calcular_erro(D, k)

        iteracao = len(self.historico['iteracao'])
        self.historico['iteracao'].append(iteracao)
        self.historico['erro'].append(erro)
        self.historico['D'].append(D)
        self.historico['k'].append(k)

        if iteracao % 3 == 0:
            print(f"Iteração {iteracao}: D={D:.4f}, k={k:.4f}, erro={erro:.4f}")

    def validar_resultado(self, D, k):
        """
        Valida resultado final comparando com dados de referência.

        Args:
            D (float): dispersão calibrada
            k (float): decaimento calibrado
        """
        print("\n" + "=" * 60)
        print("VALIDAÇÃO FINAL")
        print("=" * 60)

        # Simulação
        resultado = self.simular_cenario(D, k, verbose=False)

        # Dados de referência
        dados_ref = self.dados_tiete.gerar_dados_referencia()

        # Interpolação
        conc_max_ref = np.interp(resultado['tempo'], dados_ref['tempo'],
                                 dados_ref['conc_max'])
        conc_media_ref = np.interp(resultado['tempo'], dados_ref['tempo'],
                                    dados_ref['conc_media'])

        # Métricas
        rmse_max = np.sqrt(np.mean((resultado['conc_max'] - conc_max_ref) ** 2))
        rmse_media = np.sqrt(np.mean((resultado['conc_media'] - conc_media_ref) ** 2))
        r2_max = 1 - np.sum((resultado['conc_max'] - conc_max_ref) ** 2) / \
                     np.sum((conc_max_ref - np.mean(conc_max_ref)) ** 2)

        print(f"RMSE (C_max): {rmse_max:.2f} kg/m³")
        print(f"RMSE (C_media): {rmse_media:.2f} kg/m³")
        print(f"R² (C_max): {r2_max:.4f}")

        if r2_max > 0.7:
            print("✓ VALIDAÇÃO EXCELENTE!")
        elif r2_max > 0.5:
            print("✓ VALIDAÇÃO BOA")
        else:
            print("⚠ VALIDAÇÃO FRACA - revisar parâmetros")

        print("=" * 60 + "\n")

        return {
            'rmse_max': rmse_max,
            'rmse_media': rmse_media,
            'r2_max': r2_max,
            'resultado': resultado,
        }


if __name__ == "__main__":
    calibrador = CalibradorTiete()

    # Executa otimização
    resultado_otim = calibrador.otimizar(metodo='bayes', verbose=True)

    # Valida resultado
    D_otim = resultado_otim['D_otimo']
    k_otim = resultado_otim['k_otimo']
    validacao = calibrador.validar_resultado(D_otim, k_otim)

    print(f"\nParâmetros Calibrados para Rio Tietê:")
    print(f"  D = {D_otim:.4f} m²/s")
    print(f"  k = {k_otim:.4f} /s")
