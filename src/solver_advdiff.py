"""
Solver para equação de advecção-difusão 2D.

Equação: ∂C/∂t + u·∇C = D∇²C + R(C)
- C: concentração de poluente
- u, v: velocidades do escoamento (de NS)
- D: coeficiente de difusão
- R(C): termo de reação
"""

import numpy as np


class SolverAdveccaoDifusao:
    """Solver para advecção-difusão com campo de velocidade dado."""

    def __init__(self, malha, D=1e-6, dt=0.001):
        """
        Inicializa solver de transporte.

        Args:
            malha (Malha2D): malha do domínio
            D (float): coeficiente de difusão [m²/s]
            dt (float): passo de tempo [s]
        """
        self.m = malha #malha 2D
        self.D = D #coeficiente de difusão
        self.dt = dt #passo de tempo

        # Campo de concentração (nos centros das células)
        self.C = np.zeros((malha.nx, malha.ny))# campo de concentração inicializado com zeros
        self.C_old = np.zeros_like(self.C)# campo de concentração do passo anterior

        # Parâmetro de decaimento (biodegradação)
        self.k = 0.0  # taxa de decaimento [1/s]

        print(f"Solver Adveccao-Difusao inicializado")
        print(f"D={D}, dt={dt}")

    def set_taxa_decaimento(self, k):
        """Define taxa de decaimento de primeira ordem R(C) = -k*C."""
        self.k = k # Taxa de decaimento de primeira ordem
        print(f"Taxa de decaimento: k={k} [1/s]")

    def adicionar_fonte(self, i, j, concentracao, intensidade=1.0):
        """
        Adiciona fonte pontual de poluente.

        Args:
            i (int): índice x da célula
            j (int): índice y da célula
            concentracao (float): concentração da fonte [kg/m³]
            intensidade (float): fração da célula afetada [0, 1]
        """
        if 0 <= i < self.m.nx and 0 <= j < self.m.ny:# para garantir que os índices estão dentro dos limites da malha
            self.C[i, j] += concentracao * intensidade# Adiciona a concentração da fonte à célula especificada, multiplicada pela intensidade

    def adicionar_fonte_linha(self, i, j_start, j_end, concentracao):
        """
        Adiciona fonte distribuída em linha (entrada lateral).

        Args:
            i (int): índice x
            j_start (int): índice y inicial
            j_end (int): índice y final
            concentracao (float): concentração
        """
        for j in range(max(0, j_start), min(self.m.ny, j_end + 1)):# para garantir que os índices estão dentro dos limites da malha
            self.C[i, j] += concentracao# Adiciona a concentração da fonte à célula especificada

    def passo_tempo(self, u, v):
        """
        Avança um passo de tempo usando Euler explícito.

        Args:
            u (np.ndarray): velocidade em x (nx+1, ny)
            v (np.ndarray): velocidade em y (nx, ny+1)
        """
        self.C_old = self.C.copy()
        C_new = self.C.copy()

        for i in range(1, self.m.nx - 1):# para cada célula interna da malha (excluindo as bordas)
            for j in range(1, self.m.ny - 1):# para cada célula interna da malha (excluindo as bordas)
                # Interpolação de velocidades nos centros das células
                u_centro = (u[i, j] + u[i + 1, j]) / 2# Interpolação da velocidade em x no centro da célula
                v_centro = (v[i, j] + v[i, j + 1]) / 2

                # Termo de advecção (diferenças centrais, 2ª ordem)
                dC_dx = (self.C[i + 1, j] - self.C[i - 1, j]) / (2 * self.m.dx)
                dC_dy = (self.C[i, j + 1] - self.C[i, j - 1]) / (2 * self.m.dy)

                # Termo de difusão (diferenças centrais, 2ª ordem)
                d2C_dx2 = (self.C[i + 1, j] - 2*self.C[i, j] + self.C[i - 1, j]) / (self.m.dx**2)
                d2C_dy2 = (self.C[i, j + 1] - 2*self.C[i, j] + self.C[i, j - 1]) / (self.m.dy**2)

                # Termo de reação (decaimento de 1ª ordem)
                reacao = -self.k * self.C[i, j]

                # Euler explícito: dC/dt = -u·∇C + D∇²C + R(C)
                dC_dt = (
                    -u_centro * dC_dx -
                    v_centro * dC_dy +
                    self.D * (d2C_dx2 + d2C_dy2) +
                    reacao
                )

                C_new[i, j] = self.C[i, j] + self.dt * dC_dt

        # Condições de contorno
        # Entrada (x=0): concentração prescrita ou fluxo
        C_new[0, :] = C_new[0, :]  # pode ser ajustada

        # Saída (x=Lx): extrapolação
        C_new[-1, :] = C_new[-2, :]

        # Paredes (y=0, y=Ly): fluxo nulo ∂C/∂n = 0
        C_new[:, 0] = C_new[:, 1]
        C_new[:, -1] = C_new[:, -2]

        self.C = C_new

    def passo_tempo_upwind(self, u, v):
        """
        Versão com upwind (mais estável para Pe alto).

        Usa upstream weighting para termos convectivos.
        """
        self.C_old = self.C.copy()
        C_new = self.C.copy()

        for i in range(1, self.m.nx - 1):
            for j in range(1, self.m.ny - 1):
                # Velocidades nos centros
                u_centro = (u[i, j] + u[i + 1, j]) / 2
                v_centro = (v[i, j] + v[i, j + 1]) / 2

                # Termo de advecção (upwind)
                if u_centro >= 0:
                    dC_dx = (self.C[i, j] - self.C[i - 1, j]) / self.m.dx
                else:
                    dC_dx = (self.C[i + 1, j] - self.C[i, j]) / self.m.dx

                if v_centro >= 0:
                    dC_dy = (self.C[i, j] - self.C[i, j - 1]) / self.m.dy
                else:
                    dC_dy = (self.C[i, j + 1] - self.C[i, j]) / self.m.dy

                # Difusão (centrado)
                d2C_dx2 = (self.C[i + 1, j] - 2*self.C[i, j] + self.C[i - 1, j]) / (self.m.dx**2)
                d2C_dy2 = (self.C[i, j + 1] - 2*self.C[i, j] + self.C[i, j - 1]) / (self.m.dy**2)

                # Reação
                reacao = -self.k * self.C[i, j]

                # RHS
                dC_dt = (
                    -u_centro * dC_dx -
                    v_centro * dC_dy +
                    self.D * (d2C_dx2 + d2C_dy2) +
                    reacao
                )

                C_new[i, j] = self.C[i, j] + self.dt * dC_dt

        # Condições de contorno
        C_new[0, :] = C_new[0, :]
        C_new[-1, :] = C_new[-2, :]
        C_new[:, 0] = C_new[:, 1]
        C_new[:, -1] = C_new[:, -2]

        self.C = C_new

    def condicao_entrada(self, C_inlet):
        """Define concentração de entrada (x=0)."""
        self.C[0, :] = C_inlet

    def exportar_campo(self, arquivo_npz):
        """Salva concentração em arquivo NPZ."""
        np.savez(arquivo_npz, C=self.C, xp=self.m.xp, yp=self.m.yp)
        print(f"Campo C salvo em {arquivo_npz}")

    def conc_media(self):
        """Retorna concentração média no domínio."""
        return np.mean(self.C)

    def conc_max(self):
        """Retorna concentração máxima."""
        return np.max(self.C)

    def conc_integral(self):
        """Retorna massa total integrada."""
        return np.sum(self.C) * self.m.volume_celula()


# Teste
if __name__ == "__main__":
    from malha import Malha2D

    m = Malha2D(nx=50, ny=50, lx=10.0, ly=1.0)
    solver = SolverAdveccaoDifusao(m, D=1e-6, dt=0.0001)

    # Fonte de poluente
    solver.adicionar_fonte(5, 25, 100.0)
    solver.set_taxa_decaimento(0.01)

    print("Simulação de transporte...")
    for t in range(100):
        # Simulando velocidade constante
        u = np.ones((m.nx + 1, m.ny)) * 0.1
        v = np.zeros((m.nx, m.ny + 1))

        solver.passo_tempo(u, v)

        if t % 20 == 0:
            print(f"t={t}: C_max={solver.conc_max():.2e}, C_media={solver.conc_media():.2e}")
