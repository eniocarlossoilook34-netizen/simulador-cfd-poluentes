"""
Geracao e manipulacao de malha 2D.

Malha estruturada cartesiana com staggered grid:
- Velocidades u, v definidas nas faces
- Pressao p, concentracao C definidas nos centros das celulas
"""

import numpy as np


class Malha2D:
    """Malha estruturada 2D com grid escalonado (staggered)."""

    def __init__(self, nx, ny, lx, ly):
        """
        Inicializa malha cartesiana.

        Args:
            nx (int): numero de celulas em x
            ny (int): numero de celulas em y
            lx (float): comprimento do dominio em x [m]
            ly (float): comprimento do dominio em y [m]
        """
        self.nx = nx
        self.ny = ny
        self.lx = lx
        self.ly = ly

        self.dx = lx / nx
        self.dy = ly / ny

        x_p = np.linspace(self.dx/2, lx - self.dx/2, nx)
        y_p = np.linspace(self.dy/2, ly - self.dy/2, ny)
        self.xp, self.yp = np.meshgrid(x_p, y_p, indexing='ij')

        x_u = np.linspace(0, lx, nx+1)
        y_u = np.linspace(self.dy/2, ly - self.dy/2, ny)
        self.xu, self.yu = np.meshgrid(x_u, y_u, indexing='ij')

        x_v = np.linspace(self.dx/2, lx - self.dx/2, nx)
        y_v = np.linspace(0, ly, ny+1)
        self.xv, self.yv = np.meshgrid(x_v, y_v, indexing='ij')

        print(f"Malha criada: {nx}x{ny} celulas")
        print(f"Dominio: [{0}, {lx}] x [{0}, {ly}]")
        print(f"Espacamento: dx={self.dx:.4f}, dy={self.dy:.4f}")

    def volume_celula(self):
        """Retorna volume de cada celula."""
        return self.dx * self.dy

    def area_face_x(self):
        """Retorna area das faces em x (perpendicular a x)."""
        return self.dy

    def area_face_y(self):
        """Retorna area das faces em y (perpendicular a y)."""
        return self.dx

    def info(self):
        """Imprime informacoes da malha."""
        print(f"\n=== Informacoes da Malha ===")
        print(f"Numero de celulas: {self.nx} x {self.ny} = {self.nx*self.ny}")
        print(f"Tamanho do dominio: {self.lx} x {self.ly}")
        print(f"Espacamento: dx = {self.dx}, dy = {self.dy}")
        print(f"Volume por celula: {self.volume_celula()}")


if __name__ == "__main__":
    m = Malha2D(nx=50, ny=50, lx=1.0, ly=1.0)
    m.info()
