"""
Visualização de resultados CFD com Matplotlib.

Plots:
- Campos de velocidade (vetores, magnitude, streamlines)
- Campos de pressão (contourf)
- Concentração de poluentes
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import TwoSlopeNorm


def plotar_campo_velocidade(u, v, xp, yp, arquivo=None, titulo="Campo de Velocidade"):
    """
    Plota campo de velocidade como vetores.

    Args:
        u, v (np.ndarray): componentes de velocidade
        xp, yp (np.ndarray): coordenadas dos centros das células
        arquivo (str): caminho para salvar figura
        titulo (str): título do gráfico
    """
    # Interpola velocidades nos centros
    u_centro = (u[:-1, :] + u[1:, :]) / 2
    v_centro = (v[:, :-1] + v[:, 1:]) / 2

    # Subamostramento para clareza
    n_subsample = max(1, min(u_centro.shape[0], u_centro.shape[1]) // 15)
    i_sub = np.arange(0, u_centro.shape[0], n_subsample)
    j_sub = np.arange(0, u_centro.shape[1], n_subsample)

    fig, ax = plt.subplots(figsize=(10, 8))

    # Magnitude de velocidade como background
    vel_mag = np.sqrt(u_centro**2 + v_centro**2)
    im = ax.contourf(xp, yp, vel_mag, levels=20, cmap='viridis')

    # Vetores de velocidade (meshgrid para broadcast correto)
    i_mesh, j_mesh = np.meshgrid(i_sub, j_sub, indexing='ij')
    ax.quiver(xp[i_mesh, j_mesh], yp[i_mesh, j_mesh],
              u_centro[i_mesh, j_mesh], v_centro[i_mesh, j_mesh],
              scale=50, scale_units='inches', alpha=0.7)

    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_title(titulo)
    ax.set_aspect('equal')
    cbar = plt.colorbar(im, ax=ax, label='|U| [m/s]')

    if arquivo:
        plt.savefig(arquivo, dpi=150, bbox_inches='tight')
        print(f"Figura salva: {arquivo}")
    else:
        plt.show()

    plt.close()


def plotar_streamlines(u, v, xp, yp, arquivo=None, titulo="Linhas de Fluxo"):
    """
    Plota linhas de corrente (streamlines).

    Args:
        u, v (np.ndarray): componentes de velocidade
        xp, yp (np.ndarray): coordenadas
        arquivo (str): caminho para salvar
        titulo (str): título
    """
    # Interpola velocidades
    u_centro = (u[:-1, :] + u[1:, :]) / 2
    v_centro = (v[:, :-1] + v[:, 1:]) / 2

    fig, ax = plt.subplots(figsize=(10, 8))

    vel_mag = np.sqrt(u_centro**2 + v_centro**2)
    im = ax.contourf(xp, yp, vel_mag, levels=20, cmap='viridis')

    # Streamlines
    lw = 2 * vel_mag / (vel_mag.max() + 1e-10)  # espessura proporcional à velocidade
    ax.streamplot(xp, yp, u_centro, v_centro, density=1.5, linewidth=lw, color='white', arrowsize=1.5)

    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_title(titulo)
    ax.set_aspect('equal')
    plt.colorbar(im, ax=ax, label='|U| [m/s]')

    if arquivo:
        plt.savefig(arquivo, dpi=150, bbox_inches='tight')
        print(f"Figura salva: {arquivo}")
    else:
        plt.show()

    plt.close()


def plotar_pressao(p, xp, yp, arquivo=None, titulo="Campo de Pressão"):
    """
    Plota campo de pressão.

    Args:
        p (np.ndarray): pressão
        xp, yp (np.ndarray): coordenadas
        arquivo (str): caminho para salvar
        titulo (str): título
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Normalizador simétrico (pressões negativas e positivas)
    vmin, vmax = np.percentile(p, [1, 99])
    norm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)

    im = ax.contourf(xp, yp, p, levels=30, cmap='RdBu_r', norm=norm)

    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_title(titulo)
    ax.set_aspect('equal')
    cbar = plt.colorbar(im, ax=ax, label='p [Pa]')

    if arquivo:
        plt.savefig(arquivo, dpi=150, bbox_inches='tight')
        print(f"Figura salva: {arquivo}")
    else:
        plt.show()

    plt.close()


def plotar_concentracao(C, xp, yp, arquivo=None, titulo="Concentração de Poluente"):
    """
    Plota campo de concentração.

    Args:
        C (np.ndarray): concentração [kg/m³]
        xp, yp (np.ndarray): coordenadas
        arquivo (str): caminho para salvar
        titulo (str): título
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.contourf(xp, yp, C, levels=20, cmap='YlOrRd')

    # Contornos
    cs = ax.contour(xp, yp, C, levels=10, colors='black', alpha=0.3, linewidths=0.5)
    ax.clabel(cs, inline=True, fontsize=8)

    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_title(titulo)
    ax.set_aspect('equal')
    cbar = plt.colorbar(im, ax=ax, label='C [kg/m³]')

    if arquivo:
        plt.savefig(arquivo, dpi=150, bbox_inches='tight')
        print(f"Figura salva: {arquivo}")
    else:
        plt.show()

    plt.close()


def plotar_sobreposicao(u, v, C, xp, yp, arquivo=None, titulo="Velocidade + Concentração"):
    """
    Plota velocidade com concentração como contourf.

    Args:
        u, v (np.ndarray): velocidade
        C (np.ndarray): concentração
        xp, yp (np.ndarray): coordenadas
        arquivo (str): caminho para salvar
        titulo (str): título
    """
    u_centro = (u[:-1, :] + u[1:, :]) / 2
    v_centro = (v[:, :-1] + v[:, 1:]) / 2

    fig, ax = plt.subplots(figsize=(12, 8))

    # Background: concentração
    im = ax.contourf(xp, yp, C, levels=20, cmap='YlOrRd', alpha=0.8)

    # Vetores de velocidade (subamostrados)
    n_subsample = max(1, min(u_centro.shape[0], u_centro.shape[1]) // 12)
    i_sub = np.arange(0, u_centro.shape[0], n_subsample)
    j_sub = np.arange(0, u_centro.shape[1], n_subsample)
    i_mesh, j_mesh = np.meshgrid(i_sub, j_sub, indexing='ij')

    ax.quiver(xp[i_mesh, j_mesh], yp[i_mesh, j_mesh],
              u_centro[i_mesh, j_mesh], v_centro[i_mesh, j_mesh],
              scale=30, scale_units='inches', alpha=0.6, color='darkblue', width=0.003)

    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_title(titulo)
    ax.set_aspect('equal')
    cbar = plt.colorbar(im, ax=ax, label='C [kg/m³]')

    if arquivo:
        plt.savefig(arquivo, dpi=150, bbox_inches='tight')
        print(f"Figura salva: {arquivo}")
    else:
        plt.show()

    plt.close()


def plotar_perfil_horizontal(C, xp, yp, j, arquivo=None, titulo="Perfil Horizontal"):
    """
    Plota perfil de concentração ao longo de uma linha horizontal.

    Args:
        C (np.ndarray): concentração
        xp, yp (np.ndarray): coordenadas
        j (int): índice de linha (y)
        arquivo (str): caminho para salvar
        titulo (str): título
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    x = xp[:, 0]
    ax.plot(x, C[:, j], 'b-', linewidth=2, label=f'y = {yp[0, j]:.3f}')
    ax.fill_between(x, C[:, j], alpha=0.3)

    ax.set_xlabel('x [m]')
    ax.set_ylabel('C [kg/m³]')
    ax.set_title(titulo)
    ax.grid(True, alpha=0.3)
    ax.legend()

    if arquivo:
        plt.savefig(arquivo, dpi=150, bbox_inches='tight')
        print(f"Figura salva: {arquivo}")
    else:
        plt.show()

    plt.close()


def plotar_historico(dados, chave='residuo', arquivo=None, titulo="Histórico"):
    """
    Plota histórico temporal de uma quantidade.

    Args:
        dados (list): lista de valores
        chave (str): nome da quantidade
        arquivo (str): caminho para salvar
        titulo (str): título
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.semilogy(dados, 'b-', linewidth=1.5)
    ax.set_xlabel('Passo de Tempo')
    ax.set_ylabel(chave)
    ax.set_title(titulo)
    ax.grid(True, alpha=0.3, which='both')

    if arquivo:
        plt.savefig(arquivo, dpi=150, bbox_inches='tight')
        print(f"Figura salva: {arquivo}")
    else:
        plt.show()

    plt.close()


if __name__ == "__main__":
    # Exemplo: carrega dados salvos e plota
    dados = np.load("cavity_result.npz")
    u = dados['u']
    v = dados['v']
    p = dados['p']
    xp = dados['xp']
    yp = dados['yp']

    plotar_campo_velocidade(u, v, xp, yp, arquivo="velocidade.png")
    plotar_streamlines(u, v, xp, yp, arquivo="streamlines.png")
    plotar_pressao(p, xp, yp, arquivo="pressao.png")

    print("Visualizações geradas!")
