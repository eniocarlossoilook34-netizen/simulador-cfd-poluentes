"""
Simulador CFD 2D de Escoamento e Dispersão de Poluentes.

Módulos:
- malha: Geração de malha cartesiana estruturada
- solver_ns: Solver para Navier-Stokes
- solver_advdiff: Solver para advecção-difusão (transporte)
"""

from .malha import Malha2D
from .solver_ns import SolverNavierStokes
from .solver_advdiff import SolverAdveccaoDifusao

__version__ = "0.1.0"
__author__ = "Projeto Dispersão Poluente"

__all__ = [
    'Malha2D',
    'SolverNavierStokes',
    'SolverAdveccaoDifusao',
]
