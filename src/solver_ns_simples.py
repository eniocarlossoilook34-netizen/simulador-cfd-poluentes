"""
Solver de escoamento prescrito (velocidade conhecida).

Para casos onde o campo de velocidade eh determinado ou simplificado:
- Entrada em x: velocidade constante U_ref
- Escoamento uniforme ou parabolico
- Parede: condicao de deslizamento nula

Uso: quando NS complexo nao eh necessario
"""

import numpy as np
from malha import Malha2D


class SolverEscoamentoPrescrito:
    """Campo de velocidade prescrito para transporte."""

    def __init__(self, malha, tipo="uniforme", u_ref=1.0, v_ref=0.0):
        """
        Inicializa campo de velocidade prescrito.

        Args:
            malha (Malha2D): malha do dominio
            tipo (str): "uniforme", "parabolico", "cortante"
            u_ref (float): velocidade em x de referencia
            v_ref (float): velocidade em y de referencia
        """
        self.m = malha
        self.tipo = tipo
        self.u_ref = u_ref
        self.v_ref = v_ref

        # Campos de velocidade
        self.u = np.zeros((malha.nx + 1, malha.ny))
        self.v = np.zeros((malha.nx, malha.ny + 1))
        self.p = np.zeros((malha.nx, malha.ny))

        self._gerar_campo()

        print(f"Escoamento prescrito inicializado")
        print(f"Tipo: {tipo}, U_ref={u_ref}, V_ref={v_ref}")

    def _gerar_campo(self):
        """Gera campo de velocidade prescrito."""

        if self.tipo == "uniforme":
            self._campo_uniforme()
        elif self.tipo == "parabolico":
            self._campo_parabolico()
        elif self.tipo == "cortante":
            self._campo_cortante()
        else:
            self._campo_uniforme()

    def _campo_uniforme(self):
        """Escoamento uniforme: u=U_ref, v=0."""
        self.u[:, :] = self.u_ref
        self.v[:, :] = self.v_ref

    def _campo_parabolico(self):
        """Escoamento Poiseuille (parabolico em y)."""
        for j in range(self.m.ny):
            y_norm = self.m.yp[0, j] / self.m.ly
            # Perfil parabolico: u(y) = u_ref * 4*y*(1-y)
            u_perfil = self.u_ref * 4 * y_norm * (1 - y_norm)
            self.u[:, j] = u_perfil

    def _campo_cortante(self):
        """Escoamento com cisalhamento linear."""
        for j in range(self.m.ny):
            y_norm = self.m.yp[0, j] / self.m.ly
            self.u[:, j] = self.u_ref * y_norm

    def exportar_campos(self, arquivo_npz):
        """Salva campos em arquivo NPZ."""
        np.savez(arquivo_npz, u=self.u, v=self.v, p=self.p,
                 xp=self.m.xp, yp=self.m.yp)
        print(f"Campos de velocidade salvos em {arquivo_npz}")


if __name__ == "__main__":
    m = Malha2D(nx=50, ny=50, lx=10.0, ly=1.0)

    # Teste: escoamento uniforme
    escoamento = SolverEscoamentoPrescrito(m, tipo="uniforme", u_ref=1.0)
    print(f"\nVelocidade media em u: {np.mean(escoamento.u):.4f}")
    print(f"Velocidade media em v: {np.mean(escoamento.v):.4f}")

    # Teste: escoamento parabolico
    escoamento_parab = SolverEscoamentoPrescrito(m, tipo="parabolico", u_ref=1.0)
    print(f"\nParabolico - Velocidade media: {np.mean(escoamento_parab.u):.4f}")
