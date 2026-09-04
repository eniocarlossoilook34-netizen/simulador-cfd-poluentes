# 🌊 Simulador CFD 2D de Escoamento e Dispersão de Poluentes

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Active%20Development-brightgreen)]()

Simulador numérico bidimensional para modelar **escoamento de água**, **dispersão de poluentes** e **autodepuração em rios** usando **Dinâmica dos Fluidos Computacional (CFD)**.

Desenvolvido como **projeto de pesquisa em nível de mestrado** com foco em documentação, validação e reprodutibilidade.

---

## 🎯 Objetivo

Criar uma ferramenta de simulação robusta que permita estudar:

- ✅ **Escoamento de água** em rios e canais
- ✅ **Dispersão de poluentes** (esgoto, contaminantes)
- ✅ **Processos de autodepuração** (reações bioquímicas)
- ✅ **Validação contra benchmarks** conhecidos

**Resultado**: Base sólida para pesquisa em mestrado com metodologia clara e código reprodutível.

---

## 📊 Exemplos de Simulação

### Dispersão de Esgoto em Rio

**Configuração:**
- Domínio: 24 m × 6 m
- Tempo: 150 segundos
- Lançamento: esgoto em (6 m, 3 m)
- Escoamento: uniforme 1.0 m/s

**Resultados:**

| Campo | Valor |
|-------|-------|
| Concentração máxima | 435 kg/m³ |
| Concentração média | 8.23 kg/m³ |
| Tempo de decaimento (95%) | 59.9 s |
| Distância transportada | 150 m |

**Visualizações:**

```
Campo de Velocidade          Concentração de Poluente
┌─────────────────┐          ┌─────────────────┐
│   ────→ ────→   │          │   ████░░░░░░░   │
│   ────→ ────→   │          │   ████░░░░░░░   │
│   ────→ ────→   │    +     │   ██░░░░░░░░░   │
│   ────→ ────→   │          │   ░░░░░░░░░░░   │
│   ────→ ────→   │          │   ░░░░░░░░░░░   │
└─────────────────┘          └─────────────────┘

Escoamento (uniforme)        Dispersão + Reações
```

---

## 🚀 Quick Start

### 1. Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/simulador-cfd-poluentes.git
cd simulador-cfd-poluentes

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt
```

### 2. Execute Simulação

```bash
# Simulação principal: dispersão de esgoto
python casos/dispersao_esgoto/teste_dispersao_v2.py

# Resultado: 6 gráficos em resultados_v2/
```

### 3. Visualize Resultados

Os gráficos são salvos automaticamente em `resultados_v2/`:
- `velocidade.png` — Campo de velocidade
- `concentracao.png` — Distribuição de poluente
- `sobreposicao.png` — Velocidade + Concentração
- `perfil_lancamento.png` — Perfil na fonte
- `historico_conc_max.png` — Máxima ao longo do tempo
- `historico_conc_media.png` — Média ao longo do tempo

---

## 📁 Estrutura do Projeto

```
simulador-cfd-poluentes/
│
├── src/                          # Código principal
│   ├── malha.py                  # Grid estruturado 2D
│   ├── solver_ns_simples.py      # Escoamento prescrito
│   ├── solver_advdiff.py         # Transporte + reações
│   └── __init__.py
│
├── casos/                        # Casos de teste
│   ├── cavity_flow/
│   │   └── teste_cavity.py       # Validação Ghia (1982)
│   └── dispersao_esgoto/
│       └── teste_dispersao_v2.py # Simulação principal
│
├── visualizacao/                 # Pós-processamento
│   └── plots.py                  # Matplotlib + Plotly
│
├── docs/                         # Documentação
│   ├── teoria.md                 # Fundações matemáticas
│   ├── validacao.md              # Estratégia de testes
│   └── resultados/               # Dados de referência
│
├── README.md                     # Este arquivo
├── PROJETO.md                    # Plano de desenvolvimento
├── requirements.txt              # Dependências
└── .gitignore                    # Configuração Git
```

---

## 🔬 Metodologia

### Equações Governantes

**Navier-Stokes 2D (incompressível):**
```
∇·u = 0
ρ(∂u/∂t + u·∇u) = -∇p + μ∇²u
```

**Advecção-Difusão com Reações:**
```
∂C/∂t + u·∇C = D∇²C + R(C)
```

onde `R(C) = -k·C` (decaimento de primeira ordem)

### Método Numérico

- **Discretização**: Volumes Finitos estruturado
- **Grid**: Escalonado (staggered)
- **Temporal**: Euler explícito
- **Validação**: Benchmarks clássicos (Ghia et al. 1982)

---

## 📚 Referências Bibliográficas

### CFD Geral
- Ferziger & Peric (2002) — *Computational Methods for Fluid Dynamics*
- Versteeg & Malalasekera (2007) — *An Introduction to Computational Fluid Dynamics*

### Benchmarks
- **Ghia et al. (1982)** — "High-Re solutions for incompressible flow using the Navier-Stokes equations and a multigrid method" — *J. Comput. Phys.*, 48(3), 387–411

### Transporte & Reações
- Bird, Stewart, Lightfoot (2002) — *Transport Phenomena*
- Chapra & Canale (2010) — *Numerical Methods for Engineers*

---

## 🛠️ Dependências

```
numpy>=1.20.0
scipy>=1.7.0
matplotlib>=3.4.0
plotly>=5.0.0
pandas>=1.3.0
pytest>=6.2.0
```

Instale com: `pip install -r requirements.txt`

---

## 💻 Uso Avançado

### Customizar Simulação

```python
from src import Malha2D, SolverEscoamentoPrescrito, SolverAdveccaoDifusao

# Criar malha
malha = Malha2D(nx=120, ny=60, lx=24.0, ly=6.0)

# Escoamento (uniforme, parabólico ou cortante)
escoamento = SolverEscoamentoPrescrito(
    malha, tipo="parabolico", u_ref=1.5
)

# Transporte com reações
solver_c = SolverAdveccaoDifusao(malha, D=0.05, dt=0.01)
solver_c.set_taxa_decaimento(k=0.05)

# Simulação
for t in range(10000):
    solver_c.passo_tempo(escoamento.u, escoamento.v)
    if t % 100 == 0:
        solver_c.adicionar_fonte(i=50, j=30, concentracao=500.0)
```

### Parâmetros Físicos Importantes

| Parâmetro | Símbolo | Típico | Unidade |
|-----------|---------|--------|---------|
| Densidade | ρ | 1000 | kg/m³ |
| Viscosidade cinemática | ν | 1e-6 | m²/s |
| Coef. difusão | D | 0.01-0.1 | m²/s |
| Taxa decaimento | k | 0.01-0.1 | 1/s |
| Reynolds | Re | 100-10000 | - |
| Péclet | Pe | 10-1000 | - |

---

## ✅ Validação

### Testes Implementados

1. **Driven Cavity Flow** (Ghia et al. 1982)
   - Re = 100, 400, 1000
   - Compara com solução numérica clássica
   - Status: ✅ Validação disponível

2. **Dispersão de Poluente**
   - Campo uniforme
   - Fonte pontual
   - Status: ✅ Simulação rodando

3. **Biodegradação**
   - Decaimento exponencial
   - Status: ✅ Implementado

---

## 🎓 Para Mestrado/Pesquisa

Este projeto foi estruturado especificamente para pesquisa acadêmica:

- **Reprodutibilidade**: Código comentado, parâmetros explícitos
- **Validação**: Comparação com benchmarks conhecidos
- **Escalabilidade**: Hierarquia de modelos (uniforme → parabólico → NS completo)
- **Documentação**: Teoria, metodologia, referências

### Sugestões de Pesquisa

1. **Validar contra dados reais** de rios
2. **Comparar modelos** (uniforme vs parabólico vs NS)
3. **Estudar efeito** de parâmetros (D, k, Re)
4. **Implementar turbulência** (modelo k-ε)
5. **Otimizar** lançamento de esgoto (problema inverso)

---

## 📝 Licença

MIT License — Veja [LICENSE](LICENSE) para detalhes.

---

## 👤 Autor

**Enio Carlos** — Projeto de Mestrado  
Disciplinas: Saneamento e Meio Ambiente | Biologia Sanitária e Ambiental

---

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:

1. Faça fork do repositório
2. Crie uma branch (`git checkout -b feature/sua-feature`)
3. Commit suas mudanças (`git commit -m 'Add some feature'`)
4. Push para a branch (`git push origin feature/sua-feature`)
5. Abra um Pull Request

---

## 📞 Contato & Suporte

Para dúvidas ou sugestões:
- 📧 Email: eniocarlossoilook34@gmail.com
- 🐙 GitHub: [seu-usuario]
- 📚 Documentação: Veja `docs/` para teoria detalhada

---

## 🙏 Agradecimentos

- Ghia et al. (1982) por benchmark clássico
- Community de CFD por referências e inspiração

---

**Desenvolvido com ❤️ para pesquisa em Saneamento Ambiental**

*"Simulando a natureza para proteger a natureza"*
