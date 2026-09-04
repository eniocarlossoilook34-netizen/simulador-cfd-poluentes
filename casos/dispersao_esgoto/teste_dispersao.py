"""
Simulação: Dispersão de Esgoto em Rio

Modelo:
- Escoamento 2D em canal (Rio)
- Lançamento pontual de esgoto (fonte de poluente)
- Dispersão por advecção-difusão
- Autodepuração (decaimento biológico)

Caso típico:
- Rio com escoamento laminar (Re ~ 100-1000)
- Lançamento contínuo de esgoto
- Monitorar concentração ao longo da distância
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../visualizacao'))

from malha import Malha2D
from solver_ns import SolverNavierStokes
from solver_advdiff import SolverAdveccaoDifusao
from plots import (
    plotar_campo_velocidade,
    plotar_concentracao,
    plotar_sobreposicao,
    plotar_perfil_horizontal,
    plotar_historico,
)


class CasoDispersaoEsgoto:
    """Simulação de dispersão de esgoto em rio."""

    def __init__(self, nx=100, ny=50, lx=20.0, ly=5.0, Re=500):
        """
        Inicializa simulação.

        Args:
            nx, ny (int): resolução de malha
            lx, ly (float): dimensões do domínio [m]
            Re (float): número de Reynolds
        """
        self.lx, self.ly = lx, ly
        self.Re = Re

        # Malha
        self.malha = Malha2D(nx=nx, ny=ny, lx=lx, ly=ly)

        # Parâmetros físicos
        L = 1.0  # comprimento característico
        U_ref = 1.0  # velocidade de referência [m/s]
        self.rho = 1000.0  # densidade [kg/m³]
        self.nu = U_ref * L / Re  # viscosidade cinemática
        self.dt = 0.001  # passo de tempo [s]

        # Solver Navier-Stokes
        self.solver_ns = SolverNavierStokes(
            self.malha, rho=self.rho, nu=self.nu, dt=self.dt
        )

        # Solver Advecção-Difusão (poluente)
        self.D_poluente = 0.01  # coeficiente de difusão [m²/s]
        self.k_decay = 0.1  # taxa de decaimento [1/s]
        self.solver_c = SolverAdveccaoDifusao(
            self.malha, D=self.D_poluente, dt=self.dt
        )
        self.solver_c.set_taxa_decaimento(self.k_decay)

        # Histórico
        self.time_history = []
        self.residuo_history = []
        self.conc_max_history = []
        self.conc_media_history = []

        print(f"\n{'='*70}")
        print(f"Simulação: Dispersão de Esgoto em Rio")
        print(f"{'='*70}")
        print(f"\nDomínio: {lx}×{ly} m")
        print(f"Malha: {nx}×{ny} células")
        print(f"Reynolds: {Re}")
        print(f"Viscosidade: ν = {self.nu:.2e} m²/s")
        print(f"Péclet (poluente): Pe = {U_ref*L/self.D_poluente:.2f}")

    def configurar_escoamento(self, u_entrada=1.0):
        """
        Configura escoamento no canal.

        Args:
            u_entrada (float): velocidade na entrada [m/s]
        """
        # Parede inferior e superior: não-deslizamento
        self.solver_ns.set_condicao_parede()

        # Entrada: velocidade uniforme
        self.solver_ns.u[0, :] = u_entrada

        # Saída: extrapolação (já feita no solver)
        print(f"\nConfiguração de escoamento:")
        print(f"  Velocidade de entrada: {u_entrada} m/s")
        print(f"  Paredes: não-deslizamento (u=0, v=0)")

    def configurar_fonte_esgoto(self, x_pos=5.0, y_pos=2.5, conc_esgoto=500.0):
        """
        Configura fonte de esgoto.

        Args:
            x_pos (float): posição em x (distância da entrada) [m]
            y_pos (float): posição em y (altura) [m]
            conc_esgoto (float): concentração de esgoto [kg/m³]
        """
        # Converte posições reais para índices de malha
        i_source = int(x_pos / self.malha.dx)
        j_source = int(y_pos / self.malha.dy)

        # Validação
        i_source = min(max(i_source, 1), self.malha.nx - 2)
        j_source = min(max(j_source, 1), self.malha.ny - 2)

        self.i_source = i_source
        self.j_source = j_source
        self.conc_esgoto = conc_esgoto

        print(f"\nConfiguração de fonte (esgoto):")
        print(f"  Posição: ({x_pos:.2f}, {y_pos:.2f}) m")
        print(f"  Índices: ({i_source}, {j_source})")
        print(f"  Concentração: {conc_esgoto} kg/m³")

    def executar(self, n_steps=5000, freq_fonte=10, freq_print=500):
        """
        Executa simulação.

        Args:
            n_steps (int): número de passos de tempo
            freq_fonte (int): frequência de injeção de esgoto
            freq_print (int): frequência de output
        """
        print(f"\n{'='*70}")
        print(f"Iniciando simulação ({n_steps} passos)...")
        print(f"{'='*70}\n")

        for step in range(n_steps):
            # Resolve Navier-Stokes
            self.solver_ns.passo_tempo()
            residuo = self.solver_ns.residuo()

            # Resolve advecção-difusão
            self.solver_c.passo_tempo(self.solver_ns.u, self.solver_ns.v)

            # Adiciona fonte (injeção contínua de esgoto)
            if step % freq_fonte == 0:
                self.solver_c.adicionar_fonte(
                    self.i_source, self.j_source, self.conc_esgoto, intensidade=0.5
                )

            # Armazena histórico
            self.time_history.append(step * self.dt)
            self.residuo_history.append(residuo)
            self.conc_max_history.append(self.solver_c.conc_max())
            self.conc_media_history.append(self.solver_c.conc_media())

            # Output
            if (step + 1) % freq_print == 0:
                print(
                    f"Passo {step+1}/{n_steps} | "
                    f"t={self.time_history[-1]:.2f}s | "
                    f"res={residuo:.2e} | "
                    f"C_max={self.conc_max_history[-1]:.2e} kg/m³ | "
                    f"C_med={self.conc_media_history[-1]:.2e} kg/m³"
                )

        print(f"\n{'='*70}")
        print(f"Simulação concluída!")
        print(f"{'='*70}\n")

    def exportar_resultados(self, diretorio="resultados"):
        """Salva resultados em arquivos."""
        os.makedirs(diretorio, exist_ok=True)

        # Campos finais
        arquivo_campos = os.path.join(diretorio, "campos_finais.npz")
        np.savez(
            arquivo_campos,
            u=self.solver_ns.u,
            v=self.solver_ns.v,
            p=self.solver_ns.p,
            C=self.solver_c.C,
            xp=self.malha.xp,
            yp=self.malha.yp,
        )

        # Histórico
        arquivo_historico = os.path.join(diretorio, "historico.npz")
        np.savez(
            arquivo_historico,
            time=np.array(self.time_history),
            residuo=np.array(self.residuo_history),
            conc_max=np.array(self.conc_max_history),
            conc_media=np.array(self.conc_media_history),
        )

        print(f"Resultados exportados em: {diretorio}/")
        print(f"  - {arquivo_campos}")
        print(f"  - {arquivo_historico}")

        return diretorio

    def plotar_resultados(self, diretorio="resultados"):
        """Gera gráficos dos resultados."""
        os.makedirs(diretorio, exist_ok=True)

        print(f"\nGerando visualizações...")

        # Campo de velocidade
        plotar_campo_velocidade(
            self.solver_ns.u,
            self.solver_ns.v,
            self.malha.xp,
            self.malha.yp,
            arquivo=os.path.join(diretorio, "velocidade.png"),
            titulo="Campo de Velocidade - Escoamento no Rio",
        )

        # Concentração de poluente
        plotar_concentracao(
            self.solver_c.C,
            self.malha.xp,
            self.malha.yp,
            arquivo=os.path.join(diretorio, "concentracao.png"),
            titulo="Concentração de Esgoto",
        )

        # Sobreposição: velocidade + concentração
        plotar_sobreposicao(
            self.solver_ns.u,
            self.solver_ns.v,
            self.solver_c.C,
            self.malha.xp,
            self.malha.yp,
            arquivo=os.path.join(diretorio, "sobreposicao.png"),
            titulo="Escoamento + Dispersão de Poluente",
        )

        # Perfil horizontal no ponto de lançamento
        plotar_perfil_horizontal(
            self.solver_c.C,
            self.malha.xp,
            self.malha.yp,
            j=self.j_source,
            arquivo=os.path.join(diretorio, "perfil_horizontal.png"),
            titulo="Perfil Horizontal de Concentração",
        )

        # Histórico de concentração
        plotar_historico(
            self.conc_max_history,
            chave="C_max [kg/m³]",
            arquivo=os.path.join(diretorio, "historico_conc_max.png"),
            titulo="Concentração Máxima vs Tempo",
        )

        plotar_historico(
            self.residuo_history,
            chave="Resíduo de Continuidade",
            arquivo=os.path.join(diretorio, "historico_residuo.png"),
            titulo="Convergência do Solver",
        )

        print(f"Visualizações salvas em: {diretorio}/")


def main():
    """Executa simulação exemplo."""

    # Cria caso
    caso = CasoDispersaoEsgoto(nx=100, ny=50, lx=20.0, ly=5.0, Re=500)

    # Configura escoamento
    caso.configurar_escoamento(u_entrada=1.0)

    # Configura fonte de esgoto
    caso.configurar_fonte_esgoto(x_pos=5.0, y_pos=2.5, conc_esgoto=500.0)

    # Executa simulação
    caso.executar(n_steps=5000, freq_fonte=10, freq_print=500)

    # Exporta e visualiza
    diretorio = caso.exportar_resultados(diretorio="resultados")
    caso.plotar_resultados(diretorio=diretorio)

    print(f"\n{'='*70}")
    print(f"Simulação finalizada com sucesso!")
    print(f"Dados salvos em: {diretorio}/")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
