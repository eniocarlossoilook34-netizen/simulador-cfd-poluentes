# Simulador CFD 2D de Escoamento e Dispersão de Poluentes

## Objetivo Geral
Desenvolver um simulador numérico bidimensional que modele:
1. **Escoamento de água** via equações de Navier-Stokes
2. **Dispersão de poluentes** (esgoto) via equação de advecção-difusão
3. **Reações bioquímicas** (autodepuração)

Resultado: modelo documentado em nível de pesquisa para uso em mestrado.

---

## Escopo Técnico

### Física Modelada
- **Navier-Stokes 2D:** para campo de velocidade
  - Termos convectivo, difusivo e de pressão
  - Condições de contorno: entrada, saída, paredes
  
- **Advecção-Difusão 2D:** para concentração de poluentes (C)
  - ∂C/∂t + u·∇C = D∇²C + R(C)
  - D: coeficiente de difusão
  - R(C): termo de reação bioquímica
  
- **Reações simples:** decaimento de poluente
  - Modelo: dC/dt = -kC (decaimento de primeira ordem)
  - k: taxa de reação

### Método Numérico
- **Discretização:** Volumes Finitos estruturado
- **Malha:** Cartesiana 2D (nx × ny)
- **Temporal:** Euler explícito (simples) ou RK2 (mais robusto)
- **Espacial:** diferenças centrais (2ª ordem)

### Fonte de Poluente
- Lançamento contínuo em posição fixa (esgoto)
- Intensidade/concentração configurável

---

## Fases de Desenvolvimento

### Fase 1: Fundações CFD (Solver Navier-Stokes)
**Objetivo:** Validar solver de escoamento com teste conhecido (cavity flow)

- [ ] Implementar discretização FV para NS 2D
- [ ] Solver de pressão (SIMPLE ou similar)
- [ ] Condições de contorno
- [ ] Teste: driven cavity (Re=100, 400)
- [ ] Plotar campo de velocidade
- [ ] Validação contra resultado de literatura

**Saída esperada:** Campo de velocidade válido

### Fase 2: Transporte de Poluentes
**Objetivo:** Adicionar dispersão e validar com teste analítico

- [ ] Equação de advecção-difusão
- [ ] Integração temporal
- [ ] Implementar fonte pontual (esgoto)
- [ ] Teste: concentração em campo uniforme
- [ ] Comparar com solução semi-analítica

**Saída esperada:** Distribuição de concentração

### Fase 3: Reações Bioquímicas
**Objetivo:** Simular autodepuração

- [ ] Termo de reação (decaimento 1ª ordem)
- [ ] Extensão para modelo de Monod (biodegradação)
- [ ] Visualizar decaimento ao longo do rio

**Saída esperada:** Simulação realista de autodepuração

### Fase 4: Visualização e Análise
**Objetivo:** Ferramentas de pós-processamento

- [ ] Campos de velocidade (vetores, streamlines)
- [ ] Mapa de concentração (contourf)
- [ ] Gráficos temporais
- [ ] Salvar dados para análise
- [ ] Plotly para interatividade

**Saída esperada:** Visualizações 2D/3D

### Fase 5: Integração Web (Futura)
**Objetivo:** Interface para explorar parâmetros

- [ ] API Flask/FastAPI
- [ ] Formulário de entrada (malha, Re, fonte, etc.)
- [ ] Rodar simulação e retornar JSON
- [ ] Dashboard interativo

---

## Estrutura de Pastas

```
Projeto-Dispersão-Poluente-v2/
├── README.md                  # Guia geral
├── PROJETO.md                 # Este arquivo
├── docs/
│   ├── teoria.md              # Equações e métodos numéricos
│   ├── validação.md           # Detalhes de testes
│   └── resultados/            # Gráficos e dados
├── src/
│   ├── __init__.py
│   ├── solver_ns.py           # Navier-Stokes
│   ├── solver_advdiff.py      # Advecção-Difusão
│   ├── malha.py               # Geração e manipulação de malha
│   ├── condicoes.py           # Condições de contorno
│   ├── reacoes.py             # Reações bioquímicas
│   └── utils.py               # Funções auxiliares
├── casos/
│   ├── cavity_flow/
│   │   └── teste_cavity.py    # Validação: driven cavity
│   ├── dispersao_esgoto/
│   │   └── teste_dispersao.py # Simulação principal
│   └── reacoes/
│       └── teste_biodegradacao.py
├── visualizacao/
│   ├── plots.py               # Matplotlib
│   ├── plotly_dashboard.py    # Plotly interativo
│   └── animacao.py            # Animações
├── testes/
│   └── test_*.py              # Unit tests
├── dados/
│   └── (resultados salvos)
└── requirements.txt           # Dependências
```

---

## Dependências

```
numpy
scipy
matplotlib
plotly
pandas
pytest
```

---

## Referências e Benchmarks

### Navier-Stokes
- **Ghia et al. (1982):** Driven cavity flow (Re=100, 400, 1000)
  - Dados de referência para validação

### Advecção-Difusão
- **Convection-Dominated Problems:** solução analítica para campo uniforme
- **Teste: Pluma de poluente** em escoamento laminar

### Reações Bioquímicas
- **Decaimento de primeira ordem:** modelo simples
- **Modelo de Monod:** biodegradação limitada por oxigênio

---

## Status

- [x] Definição de escopo
- [ ] Fase 1: Solver NS
- [ ] Fase 2: Transporte
- [ ] Fase 3: Reações
- [ ] Fase 4: Visualização
- [ ] Fase 5: Web

---

## Notas de Pesquisa

Após cada fase, documentar:
- Equações implementadas
- Esquema numérico (ordem, estabilidade)
- Testes e validações
- Limitações e suposições
- Trabalhos futuros
