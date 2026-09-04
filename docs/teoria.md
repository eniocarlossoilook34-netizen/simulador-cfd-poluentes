# Fundamentos Teóricos

## 1. Equações de Navier-Stokes 2D

As equações de conservação de massa e quantidade de movimento para um fluido incompressível:

### Conservação de Massa (Continuidade)
```
∇·u = 0
∂u/∂x + ∂v/∂y = 0
```

Onde: u, v = componentes de velocidade em x, y

### Conservação de Quantidade de Movimento
```
ρ(∂u/∂t + u·∇u) = -∇p + μ∇²u
ρ(∂v/∂t + v·∇v) = -∇p + μ∇²v
```

Expandido:
```
ρ(∂u/∂t + u·∂u/∂x + v·∂u/∂y) = -∂p/∂x + μ(∂²u/∂x² + ∂²u/∂y²)
ρ(∂v/∂t + u·∂v/∂x + v·∂v/∂y) = -∂p/∂y + μ(∂²v/∂x² + ∂²v/∂y²)
```

Onde:
- ρ = densidade do fluido (kg/m³)
- p = pressão (Pa)
- μ = viscosidade dinâmica (Pa·s)
- ν = μ/ρ = viscosidade cinemática (m²/s)

### Número de Reynolds
```
Re = ρ·U·L / μ = U·L / ν
```
- U = velocidade característica
- L = comprimento característico

Re >> 1: escoamento turbulento (ou com separação)
Re << 1: escoamento laminar (Stokes)

---

## 2. Equação de Advecção-Difusão

Transporte de espécie (concentração de poluente C):

```
∂C/∂t + u·∇C = D∇²C + R(C)
```

Expandido:
```
∂C/∂t + u·∂C/∂x + v·∂C/∂y = D(∂²C/∂x² + ∂²C/∂y²) + R(C)
```

Onde:
- C = concentração [kg/m³ ou mol/m³]
- D = coeficiente de difusão molecular [m²/s]
- u·∇C = termo de **advecção** (transporte pelo escoamento)
- D∇²C = termo de **difusão** (dispersão por gradientes)
- R(C) = termo de **reação** (biodegradação, fotodegradação)

### Número de Péclet
```
Pe = U·L / D
```
- Pe >> 1: advecção dominante (frentes nítidas)
- Pe << 1: difusão dominante (distribuição suave)
- Pe ~ 1: processos balanceados

---

## 3. Modelos de Reação

### 3.1 Decaimento de Primeira Ordem (Simples)
```
R(C) = -k·C
```
- k = taxa de decaimento [1/s]
- Solução: C(t) = C₀·exp(-k·t)
- Meia-vida: t₁/₂ = ln(2)/k

### 3.2 Modelo de Monod (Biodegradação com Oxigênio)
```
R(C) = -μ_max · (C/(K_s + C)) · (O/(K_O + O))
```
- μ_max = taxa máxima de biodegradação
- K_s = constante de meia-saturação (poluente)
- O = concentração de oxigênio dissolvido
- K_O = constante de meia-saturação (oxigênio)

---

## 4. Método de Volumes Finitos

### Princípio
Discretiza o domínio em volumes (células) e integra as equações sobre cada volume.

### Forma Integral da Advecção-Difusão
```
∫_V (∂C/∂t) dV + ∮_S (u·n)·C dS = ∫_V D∇²C dV + ∫_V R(C) dV
```

Aplicando o teorema da divergência:
```
V·(dC/dt) + Σ(F_face · C_face) = Σ(D·∇C·A_face) + V·R(C)
```

### Discretização Espacial
Para uma célula (i,j) com vizinhos E (leste), W (oeste), N (norte), S (sul):

**Fluxo advectivo:** diferenças centrais (2ª ordem)
```
F_E ≈ (u_E·C_E + u_i·C_i)/2
```

**Fluxo difusivo:** diferenças centrais
```
D_flux_E ≈ D·(C_E - C_i)/Δx
```

### Discretização Temporal
**Euler explícito:**
```
C_n+1 = C_n + Δt · RHS_n
```
Estável se: Δt ≤ Δt_crit (Courant-Friedrichs-Lewy)

**Número de Courant:**
```
Co = u·Δt / Δx ≤ 1
```

---

## 5. Condições de Contorno

### Para Navier-Stokes
1. **Entrada (inlet):** velocidade prescrita (u, v = const)
2. **Saída (outlet):** pressão zero ou gradiente zero
3. **Parede (wall):** não-deslizamento (u=0, v=0) ou deslizamento

### Para Advecção-Difusão
1. **Entrada:** concentração prescrita
2. **Saída:** fluxo zero (ou convectivo)
3. **Parede:** fluxo nulo (∂C/∂n = 0) ou absorção

---

## 6. Algoritmo Geral (SIMPLE)

Para cada passo temporal:

1. **Guess inicial:** u*, v*, p*
2. **Resolver momentos:** obter u', v' com p*
3. **Corrição de pressão:** resolver Poisson (∇²p_corr)
4. **Atualizar:** u, v, p
5. **Resolver advecção-difusão:** C_n+1
6. **Próximo passo:** t → t+Δt

---

## 7. Referências

- **Ferziger & Peric (2002):** "Computational Methods for Fluid Dynamics"
- **Versteeg & Malalasekera (2007):** "An Introduction to Computational Fluid Dynamics"
- **Ghia et al. (1982):** "High-Re solutions for incompressible flow using NS equations"
- **Bird, Stewart, Lightfoot (2002):** "Transport Phenomena" (biodegradação)

---

## Próximas Etapas

1. Implementar malha e estrutura de dados
2. Implementar solucionador SIMPLE para NS
3. Validar com driven cavity (Ghia et al.)
4. Adicionar equação de advecção-difusão
5. Testar com pluma de poluente
6. Implementar reações
7. Visualizar e documentar resultados
