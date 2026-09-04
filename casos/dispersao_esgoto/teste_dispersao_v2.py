"""
Simulacao: Dispersao de Esgoto em Rio - Versao 2

Usa escoamento prescrito (velocidade constante) + transporte

Modelo:
- Rio com escoamento uniforme
- Lancamento pontual de esgoto (fonte de poluente)
- Dispersao por adveccao-difusao
- Autodepuracao (decaimento biologico)
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../visualizacao'))

from malha import Malha2D
from solver_ns_simples import SolverEscoamentoPrescrito
from solver_advdiff import SolverAdveccaoDifusao
from plots import (
    plotar_campo_velocidade,
    plotar_concentracao,
    plotar_sobreposicao,
    plotar_perfil_horizontal,
    plotar_historico,
)


class CasoDispersaoEsgotoV2:
    """Simulacao pragmatica de dispersao de esgoto."""

    def __init__(self, nx=100, ny=50, lx=20.0, ly=5.0, u_ref=1.0):
        """
        Inicializa simulacao.

        Args:
            nx, ny (int): resolucao de malha
            lx, ly (float): dimensoes do dominio [m]
            u_ref (float): velocidade de referencia [m/s]
        """
        self.lx, self.ly = lx, ly
        self.u_ref = u_ref

        # Malha
        self.malha = Malha2D(nx=nx, ny=ny, lx=lx, ly=ly)

        # Escoamento prescrito (uniforme)
        self.escoamento = SolverEscoamentoPrescrito(
            self.malha, tipo="uniforme", u_ref=u_ref
        )

        # Transporte de poluente
        self.D_poluente = 0.05  # coeficiente de difusao [m2/s]
        self.k_decay = 0.05  # taxa de decaimento [1/s]
        self.solver_c = SolverAdveccaoDifusao(
            self.malha, D=self.D_poluente, dt=0.01
        )
        self.solver_c.set_taxa_decaimento(self.k_decay)

        # Historico
        self.time_history = []
        self.conc_max_history = []
        self.conc_media_history = []

        print(f"\n{'='*70}")
        print(f"Simulacao: Dispersao de Esgoto em Rio (Versao 2)")
        print(f"{'='*70}")
        print(f"\nDominio: {lx}x{ly} m")
        print(f"Malha: {nx}x{ny} celulas")
        print(f"Velocidade de escoamento: {u_ref} m/s")
        print(f"Difusao: D = {self.D_poluente} m2/s")
        print(f"Decaimento: k = {self.k_decay} 1/s")
        print(f"Peclet (adveccao vs difusao): Pe = {u_ref*lx/self.D_poluente:.1f}")

    def configurar_fonte_esgoto(self, x_pos=5.0, y_pos=2.5, conc_esgoto=500.0):
        """
        Configura fonte de esgoto.

        Args:
            x_pos (float): posicao em x (distancia da entrada) [m]
            y_pos (float): posicao em y (altura) [m]
            conc_esgoto (float): concentracao de esgoto [kg/m3]
        """
        i_source = int(x_pos / self.malha.dx)
        j_source = int(y_pos / self.malha.dy)

        i_source = min(max(i_source, 1), self.malha.nx - 2)
        j_source = min(max(j_source, 1), self.malha.ny - 2)

        self.i_source = i_source
        self.j_source = j_source
        self.conc_esgoto = conc_esgoto

        print(f"\nFonte de esgoto:")
        print(f"  Posicao: ({x_pos:.2f}, {y_pos:.2f}) m")
        print(f"  Indice: ({i_source}, {j_source})")
        print(f"  Concentracao: {conc_esgoto} kg/m3")

    def executar(self, t_simulacao=100.0, freq_fonte=5):
        """
        Executa simulacao.

        Args:
            t_simulacao (float): tempo total de simulacao [s]
            freq_fonte (int): frequencia de injecao de esgoto
        """
        dt = self.solver_c.dt
        n_steps = int(t_simulacao / dt)

        print(f"\n{'='*70}")
        print(f"Iniciando simulacao ({t_simulacao:.1f} segundos, {n_steps} passos)...")
        print(f"{'='*70}\n")

        for step in range(n_steps):
            # Resolve adveccao-difusao com campo prescrito
            self.solver_c.passo_tempo(self.escoamento.u, self.escoamento.v)

            # Injecao continua de esgoto
            if step % freq_fonte == 0:
                self.solver_c.adicionar_fonte(
                    self.i_source, self.j_source, self.conc_esgoto, intensidade=0.3
                )

            # Historico
            self.time_history.append(step * dt)
            self.conc_max_history.append(self.solver_c.conc_max())
            self.conc_media_history.append(self.solver_c.conc_media())

            # Output
            if (step + 1) % 100 == 0:
                print(
                    f"Passo {step+1}/{n_steps} | "
                    f"t={self.time_history[-1]:.1f}s | "
                    f"C_max={self.conc_max_history[-1]:.2e} kg/m3 | "
                    f"C_med={self.conc_media_history[-1]:.2e} kg/m3"
                )

        print(f"\n{'='*70}")
        print(f"Simulacao concluida!")
        print(f"{'='*70}\n")

    def exportar_resultados(self, diretorio="resultados"):
        """Salva resultados em arquivos."""
        os.makedirs(diretorio, exist_ok=True)

        # Campos finais
        arquivo_campos = os.path.join(diretorio, "campos_finais.npz")
        np.savez(
            arquivo_campos,
            u=self.escoamento.u,
            v=self.escoamento.v,
            p=self.escoamento.p,
            C=self.solver_c.C,
            xp=self.malha.xp,
            yp=self.malha.yp,
        )

        # Historico
        arquivo_historico = os.path.join(diretorio, "historico.npz")
        np.savez(
            arquivo_historico,
            time=np.array(self.time_history),
            conc_max=np.array(self.conc_max_history),
            conc_media=np.array(self.conc_media_history),
        )

        print(f"Resultados exportados em: {diretorio}/")
        print(f"  - {arquivo_campos}")
        print(f"  - {arquivo_historico}")

        return diretorio

    def plotar_resultados(self, diretorio="resultados"):
        """Gera graficos dos resultados."""
        os.makedirs(diretorio, exist_ok=True)

        print(f"\nGerando visualizacoes...")

        # Campo de velocidade
        plotar_campo_velocidade(
            self.escoamento.u,
            self.escoamento.v,
            self.malha.xp,
            self.malha.yp,
            arquivo=os.path.join(diretorio, "velocidade.png"),
            titulo="Campo de Velocidade - Rio com Escoamento Uniforme",
        )

        # Concentracao de poluente
        plotar_concentracao(
            self.solver_c.C,
            self.malha.xp,
            self.malha.yp,
            arquivo=os.path.join(diretorio, "concentracao.png"),
            titulo="Concentracao de Esgoto (poluente)",
        )

        # Sobreposicao
        plotar_sobreposicao(
            self.escoamento.u,
            self.escoamento.v,
            self.solver_c.C,
            self.malha.xp,
            self.malha.yp,
            arquivo=os.path.join(diretorio, "sobreposicao.png"),
            titulo="Escoamento + Dispersao de Poluente",
        )

        # Perfil em y na posicao de lancamento
        if self.j_source < self.malha.ny - 1:
            plotar_perfil_horizontal(
                self.solver_c.C,
                self.malha.xp,
                self.malha.yp,
                j=self.j_source,
                arquivo=os.path.join(diretorio, "perfil_lancamento.png"),
                titulo="Perfil de Concentracao na Altura de Lancamento",
            )

        # Historicos
        plotar_historico(
            self.conc_max_history,
            chave="C_max [kg/m3]",
            arquivo=os.path.join(diretorio, "historico_conc_max.png"),
            titulo="Concentracao Maxima vs Tempo",
        )

        plotar_historico(
            self.conc_media_history,
            chave="C_media [kg/m3]",
            arquivo=os.path.join(diretorio, "historico_conc_media.png"),
            titulo="Concentracao Media vs Tempo",
        )

        print(f"Visualizacoes salvas em: {diretorio}/")


def main():
    """Exemplo de uso."""

    # Cria caso
    caso = CasoDispersaoEsgotoV2(
        nx=120, ny=60, lx=24.0, ly=6.0, u_ref=1.0
    )

    # Configura fonte de esgoto
    caso.configurar_fonte_esgoto(x_pos=6.0, y_pos=3.0, conc_esgoto=500.0)

    # Executa simulacao (100 segundos)
    caso.executar(t_simulacao=150.0, freq_fonte=3)

    # Exporta e visualiza
    diretorio = caso.exportar_resultados(diretorio="resultados_v2")
    caso.plotar_resultados(diretorio=diretorio)

    print(f"\n{'='*70}")
    print(f"Simulacao finalizada com sucesso!")
    print(f"Dados salvos em: {diretorio}/")
    print(f"{'='*70}\n")

    # Imprime resumo
    print(f"RESUMO FISICO:")
    print(f"  Concentracao maxima final: {caso.conc_max_history[-1]:.2e} kg/m3")
    print(f"  Concentracao media final: {caso.conc_media_history[-1]:.2e} kg/m3")
    print(f"  Tempo de decaimento (95%): {-np.log(0.05)/caso.k_decay:.1f} s")
    print(f"  Distancia transportada: {caso.u_ref * caso.time_history[-1]:.1f} m")


if __name__ == "__main__":
    main()
