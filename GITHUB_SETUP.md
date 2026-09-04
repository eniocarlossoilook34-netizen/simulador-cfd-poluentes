# 📤 Guia: Como Postar Projeto no GitHub

## Passo 1: Preparação Local

### 1.1 Inicialize Git (se ainda não fez)

```bash
cd "Projeto Dispersão Poluente v2"
git init
git config user.name "Seu Nome"
git config user.email "seu-email@example.com"
```

### 1.2 Crie arquivo `.gitignore` (já existe)

Certifique que `.gitignore` está no diretório raiz com:
```
__pycache__/
*.pyc
venv/
resultados*/
*.npz
```

### 1.3 Renomeie README

```bash
# Renomeie para o padrão GitHub
mv README_GITHUB.md README.md
```

---

## Passo 2: Crie Repositório no GitHub

### 2.1 Acesse GitHub

1. Vá para https://github.com/new
2. Faça login (crie conta se não tiver)

### 2.2 Configure Repositório

| Campo | Valor |
|-------|-------|
| Repository name | `simulador-cfd-poluentes` |
| Description | `Simulador CFD 2D de escoamento e dispersão de poluentes em rios` |
| Public/Private | **Public** (melhor para portfólio) |
| Initialize | ❌ **Deixe vazio** |
| License | MIT (já temos) |

### 2.3 Clique "Create repository"

Você receberá um comando como:
```bash
git remote add origin https://github.com/seu-usuario/simulador-cfd-poluentes.git
git branch -M main
git push -u origin main
```

---

## Passo 3: Faça Primeiro Commit

```bash
# Na pasta do projeto
cd "Projeto Dispersão Poluente v2"

# Adicione todos os arquivos
git add .

# Commit inicial
git commit -m "Initial commit: Simulador CFD 2D com documentação completa"
```

---

## Passo 4: Suba para GitHub

```bash
# Configure remote (copie o comando que GitHub mostrou)
git remote add origin https://github.com/seu-usuario/simulador-cfd-poluentes.git

# Envie para GitHub
git branch -M main
git push -u origin main
```

---

## Passo 5: Otimizações pós-commit

### 5.1 Adicione Badge de Status no README

No topo do README.md, você já tem:
```markdown
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
```

Outras opções:
```markdown
[![GitHub Stars](https://img.shields.io/github/stars/seu-usuario/simulador-cfd-poluentes)](https://github.com/seu-usuario/simulador-cfd-poluentes)
[![GitHub Issues](https://img.shields.io/github/issues/seu-usuario/simulador-cfd-poluentes)](https://github.com/seu-usuario/simulador-cfd-poluentes/issues)
```

### 5.2 Adicione Imagens ao README

Para incluir screenshots dos resultados:

1. **Copie imagens geradas** para pasta `docs/images/`:
```bash
mkdir docs/images
cp resultados_v2/*.png docs/images/
```

2. **Commit as imagens**:
```bash
git add docs/images/
git commit -m "Add simulation result visualizations"
git push
```

3. **Referencie no README**:
```markdown
### Exemplos de Simulação

![Campo de Velocidade](docs/images/velocidade.png)
![Concentração de Poluente](docs/images/concentracao.png)
![Escoamento + Dispersão](docs/images/sobreposicao.png)
```

---

## Passo 6: Organize Issues e Milestones (Opcional)

### 6.1 Crie Issues para Futuros Desenvolvimentos

No GitHub → Issues → New Issue:

```markdown
# Title: Implementar Navier-Stokes Completo

## Description
Implementar solver NS robusto com método SIMPLE ou similar.

## Labels
enhancement, feature

## Milestone
v2.0
```

Ideias de issues:
- [ ] Adicionar modelo de turbulência (k-ε)
- [ ] Validação contra dados reais
- [ ] Comparação com OpenFOAM
- [ ] Interface gráfica (GUI)
- [ ] Parallelização (GPU)

---

## Passo 7: Crie GitHub Pages (Documentação Online)

### 7.1 Habilite GitHub Pages

1. Repo → Settings → Pages
2. Source: **Deploy from a branch**
3. Branch: **main** / folder: **docs**
4. Clique Save

### 7.2 Crie `docs/index.md`

```markdown
# Simulador CFD 2D

Documentação online do projeto.

## Seções
- [Teoria](teoria.md)
- [Validação](validacao.md)
- [Resultados](resultados.md)
```

Seu site fica em: `https://seu-usuario.github.io/simulador-cfd-poluentes/`

---

## Passo 8: Checklist Final para GitHub

Antes de considerar "pronto":

- [ ] README.md bem formatado com badges
- [ ] LICENSE MIT incluído
- [ ] .gitignore funcional
- [ ] Código comentado e organizado
- [ ] `requirements.txt` atualizado
- [ ] Pelo menos 1 simulação rodando (`teste_dispersao_v2.py`)
- [ ] Documentação em `docs/`
- [ ] Exemplos claros de uso
- [ ] Imagens dos resultados adicionadas

---

## Comandos Git Úteis Daqui em Diante

```bash
# Ver status
git status

# Verificar commits
git log --oneline

# Fazer novo commit
git add .
git commit -m "Descrição da mudança"
git push

# Criar branch para nova feature
git checkout -b feature/nova-feature
git push -u origin feature/nova-feature

# Mais tarde: fazer Pull Request no GitHub
```

---

## Dicas para Bom Repositório

✅ **Fazer:**
- Commits pequenos e bem descritos
- README claro e atualizado
- Issues bem documentadas
- Projetos com milestones

❌ **Evitar:**
- Commits grandes de uma vez
- Descrições vagas ("update", "fix")
- Código sem documentação
- Dados binários grandes

---

## Links Úteis

- 📖 GitHub Help: https://docs.github.com
- 🔧 Git Cheat Sheet: https://github.github.com/training-kit/
- 📝 Commit Conventions: https://conventionalcommits.org/

---

**Parabéns! Seu projeto está pronto para GitHub! 🚀**

Compartilhe o link e deixe que a comunidade veja seu trabalho! 

Links para compartilhar:
- GitHub: `https://github.com/seu-usuario/simulador-cfd-poluentes`
- Documentação: `https://seu-usuario.github.io/simulador-cfd-poluentes/`
