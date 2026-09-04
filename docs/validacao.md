# Estratégia de Validação

## Objetivo

Validar implementação do solver CFD contra benchmarks conhecidos e soluções analíticas.

---

## 1. Teste 1: Driven Cavity Flow (Ghia et al. 1982)

### Descrição
- Domínio quadrado [0,1] × [0,1]
- Parede superior se move com velocidade u=1
- Outras paredes: não-deslizamento
- Condição: regime permanente/quasi-permanente

### Validação
Comparar perfil de velocidade u ao longo da linha vertical central (x=0.5) com dados tabelados de Ghia et al.

### Referência
Ghia, U., Ghia, K. N., & Shin, C. T. (1982). "High-Re solutions for incompressible flow using the Navier-Stokes equations and a multigrid method." *Journal of Computational Physics*, 48(3), 387-411.

**Dados (Re=100, x=0.5):**
| y     | u (Ghia) |
|-------|----------|
| 0.0625| 0.0000   |
| 0.2500| 0.2109   |
| 0.5000| 0.3789   |
| 0.7500| 0.2215   |
| 0.9375| -0.0221  |

### Critério
- Erro relativo < 5% em pontos-chave
- Resíduo de continuidade < 1e-6 no estado permanente

### Status
✅ **Implementado** em `casos/cavity_flow/teste_cavity.py`

---

## 2. Teste 2: Pluma de Poluente em Escoamento Uniforme

### Descrição
- Escoamento uniforme U_ref em x
- Fonte pontual de poluente em (x0, y0)
- Advecção-Difusão dominada (Pe alto)
- Regime permanente/quasi-permanente

### Validação
Solução analítica (aproximação) para pluma Gaussiana em escoamento uniforme:

```
C(x, y, t) = (C0 * V_source) / (√(4π*D*t)) * 
             exp(-(y-y0)²/(4*D*t)) * exp(-k*t)
```

Onde:
- V_source = volume/vazão de fonte
- D = coeficiente de difusão
- k = taxa de decaimento

### Comparação
1. Simulação numérica
2. Solução analítica (no tempo de interesse)
3. Erro RMS na região de interesse

### Status
🚧 **Em desenvolvimento**

---

## 3. Teste 3: Decaimento Exponencial

### Descrição
- Campo uniforme (sem escoamento)
- Concentração inicial C0
- Apenas reação: dC/dt = -k*C

### Solução Analítica
```
C(t) = C0 * exp(-k*t)
```

### Validação
- Simular com dt pequeno (método explícito)
- Comparar C(t_final) com solução analítica
- Verificar meia-vida: t_1/2 = ln(2)/k

### Critério
- Erro relativo < 1% após 5 meias-vidas

### Status
🚧 **Não implementado**

---

## 4. Teste 4: Estabilidade Numérica

### Números de Courant e Fourier

**Courant (advecção):**
```
Co = u * Δt / Δx ≤ 1
```
Valor típico: 0.5 (seguro com diferenças centrais)

**Fourier (difusão):**
```
Fo = D * Δt / Δx² ≤ 0.25
```

### Verificação
Para cada simulação, calcular:
- Co_max = max(|u|) * dt / dx
- Fo_max = D * dt / dx²

Imprimir avisos se violados.

### Status
✅ **Verificação automática em código**

---

## 5. Teste 5: Conservação de Massa

### Para Navier-Stokes
Resíduo de continuidade:
```
residuo = max|∇·u| no domínio
```
Deve ser < 1e-6 em regime permanente.

### Para Advecção-Difusão (sem reação)
Massa total integrada:
```
M_total = ∫∫ C dA
```
Deve ser conservada (até erros numéricos).

Com reação:
```
dM/dt = -k * M_total  (decaimento)
```

### Verificação
Armazenar M(t) ao longo da simulação e verificar:
- Sem reação: dM/dt ≈ 0
- Com reação: dM/dt ≈ -k*M

### Status
🚧 **Método implementado, teste pendente**

---

## Protocolo de Validação

Para cada nova simulação:

1. **Verificar números adimensionais:**
   - Re adequado?
   - Pe adequado?
   - Co ≤ 1?
   - Fo ≤ 0.25?

2. **Verificar convergência:**
   - Resíduo diminui monótonamente?
   - Atinge regime permanente?

3. **Verificar conservação:**
   - Massa integrada (se aplicável)?
   - Continuidade (NS)?

4. **Comparar com referência:**
   - Teste clássico disponível?
   - Erro dentro de tolerância?

5. **Documentar:**
   - Parâmetros usados
   - Critérios de convergência
   - Erros encontrados
   - Interpretação física

---

## Métricas de Erro

### Erro Relativo Simples
```
erro_rel = |u_sim - u_ref| / |u_ref|
```

### Erro RMS (domínio inteiro)
```
erro_rms = √(∫∫ (φ_sim - φ_ref)² dA / A_total)
```

### Erro L∞ (máximo)
```
erro_max = max|φ_sim - φ_ref|
```

---

## Recursos para Validação

### Dados de Referência
- Ghia et al. (1982): cavity flow
- Solução analítica: decaimento exponencial
- Benchmark OpenFOAM: transferência de calor, etc.

### Ferramentas
- `numpy`: cálculos numéricos
- `scipy`: interpolação, integração
- `matplotlib`: visualização

### Documentação
Cada teste deve incluir:
- Figura com resultado vs referência
- Tabela de erro vs grid refinement (convergência de malha)
- Interpretação e conclusões

---

## Próximos Passos

1. [x] Implementar teste cavity flow
2. [ ] Validar resultado Ghia
3. [ ] Implementar teste decaimento
4. [ ] Validar conservação de massa
5. [ ] Teste de grid convergence (verificar ordem de convergência)
6. [ ] Comparação com software comercial (ANSYS, OpenFOAM)
7. [ ] Validação com dados reais (rio)

---

## Referências

- Roache, P. J. (1998). "Verification and Validation in Computational Science and Engineering." Hermosa Publishers.
- Oberkampf, W. L., & Trucano, T. G. (2002). "Verification and validation in computational fluid dynamics." *Progress in Aerospace Sciences*, 38(3), 209-272.
