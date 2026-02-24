---
title: "Análise Descritiva com Python"
date: "2025-09-11"
readTime: "8 min"
tag: "Python · Estatística"
description: "Um guia prático de análise descritiva aplicado ao dataset de gorjetas — cobrindo medidas de tendência central, dispersão, correlação e visualização exploratória."
---

A análise descritiva é o primeiro passo em qualquer processo de exploração de dados. Seu objetivo é resumir, organizar e compreender as características principais de um conjunto de informações, permitindo que possamos responder perguntas como:

- O que aconteceu nos dados?
- Quais são os valores típicos ou centrais?
- Existe muita variação ou os dados são consistentes?
- Há padrões, tendências ou outliers que chamam atenção?
- Como diferentes grupos se comportam dentro da base?

Nesta etapa, não buscamos prever o futuro ou explicar causalidades profundas, mas sim **entender o presente dos dados** de forma clara e estruturada.

---

## 1. Introdução ao Dataset de Gorjetas

Vamos aplicar os conceitos de análise descritiva no dataset de gorjetas de um restaurante. O objetivo é entender o comportamento das gorjetas, identificar variáveis que influenciam os valores e explorar padrões nos dados.

```python
import pandas as pd
import numpy as np
from scipy.stats import mode
import matplotlib.pyplot as plt
import seaborn as sns

# Importando os dados
url = 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv'
dados = pd.read_csv(url)

# Dimensões e resumo
print("Dimensões do dataset:", dados.shape)
print(dados.describe())
print(dados.isnull().sum())
```

O dataset contém **244 registros** com 7 variáveis: valor total da conta, gorjeta, sexo, se fumam, dia da semana, período (almoço/jantar) e tamanho da mesa.

---

## 2. Medidas de Tendência Central

As medidas de tendência central identificam valores representativos do conjunto de dados. Respondem: *"qual é o valor típico dos meus dados?"*

| Medida | Quando usar |
|--------|-------------|
| **Média Aritmética** | Dados simétricos sem outliers |
| **Média Ponderada** | Valores com importâncias diferentes |
| **Mediana** | Ideal com outliers ou distribuições assimétricas |
| **Moda** | Dados categóricos ou valor mais comum |

```python
valores = dados['tip']

media_aritmetica = np.mean(valores)
pesos = dados['total_bill']
media_ponderada = np.average(valores, weights=pesos)
mediana = np.median(valores)
moda = mode(valores, keepdims=True).mode[0]
```

**Resultados:**
- Média Aritmética: **$3.00**
- Média Ponderada (total da conta): **$3.42**
- Média Ponderada (homens): **$3.53**
- Média Ponderada (mulheres): **$3.18**
- Mediana: **$2.90**
- Moda: **$2.00**

---

## 3. Medidas de Dispersão

As medidas de dispersão mostram quão espalhados estão os dados em torno do valor central. Respondem: *"quão consistentes são meus dados?"*

```python
amplitude = valores.max() - valores.min()
variancia = valores.var()
desvio_padrao = valores.std()
cv = (desvio_padrao / media_aritmetica) * 100
iqr = valores.quantile(0.75) - valores.quantile(0.25)
```

**Resultados:**
- Amplitude: **9.00**
- Variância: **1.91**
- Desvio Padrão: **1.38**
- Coeficiente de Variação: **46.15%**
- IQR: **1.56**

---

## 4. Distribuição dos Dados

A análise da distribuição mostra como os dados estão espalhados e onde se concentram. Usamos três visualizações principais: **histograma**, **boxplot** e **curva de densidade**.

```python
# Histograma
sns.histplot(valores, kde=True, bins=20)
plt.title('Histograma das Gorjetas')
plt.show()

# Boxplot
sns.boxplot(x=valores)
plt.title('Boxplot das Gorjetas')
plt.show()

# Curva de densidade
sns.kdeplot(valores, fill=True)
plt.title('Curva de Densidade das Gorjetas')
plt.show()
```

---

## 5. Análise de Correlação

A análise de correlação mede como duas variáveis se relacionam. Responde: *"quando uma variável muda, a outra muda também?"*

- **Pearson**: mede relação linear entre variáveis contínuas. Varia entre -1 e 1.
- **Spearman**: avalia relação monotônica. Mais robusta a outliers e dados ordinais.

```python
corr_pearson = dados[['total_bill', 'tip']].corr(method='pearson')
corr_spearman = dados[['total_bill', 'tip']].corr(method='spearman')
```

**Resultados:**
- Pearson: **0.676**
- Spearman: **0.679**

Correlação moderada-forte: contas maiores tendem a gerar gorjetas proporcionalmente maiores.

---

## 6. Análise Categórica

Ela ajuda a responder: *"como diferentes grupos ou categorias se comportam nos meus dados?"*

```python
# Média de gorjetas por dia
media_por_dia = dados.groupby('day')['tip'].mean()

# Média de gorjetas por sexo
media_por_sexo = dados.groupby('sex')['tip'].mean()
```

**Gorjeta média por dia:**
- Sexta: $2.73 | Sábado: $2.99 | **Domingo: $3.26** | Quinta: $2.77

**Gorjeta média por sexo:**
- Feminino: $2.83 | Masculino: $3.09

---

## Principais Resultados

Após a análise descritiva completa, identificamos:

**Medidas Centrais:** gorjeta média de $3.00, mediana de $2.90, distribuição ligeiramente assimétrica à direita.

**Dispersão:** coeficiente de variação de 46% (variabilidade moderada), com alguns outliers acima de $8.

**Correlações:** forte relação entre valor da conta e gorjeta (0.68) — contas maiores geram gorjetas proporcionalmente maiores.

**Diferenças por Grupos:** homens dão gorjetas ligeiramente maiores; domingos apresentam gorjetas mais altas em média. Vale notar que a proporção de homens na amostra é aproximadamente o dobro da de mulheres, o que pode influenciar os resultados.

---

## Conclusão

A análise descritiva revelou padrões importantes no comportamento das gorjetas. Esses insights formam a base para análises mais avançadas, como modelagem preditiva ou testes de hipóteses. **A análise descritiva é sempre o ponto de partida para compreender qualquer dataset de forma sólida e fundamentada.**

---

## Bibliografia

**Livros:**
- Wheelan, C. (2016). *Estatística: O que é, para que serve, como funciona.*
- Bruce, P. & Bruce, A. (2019). *Estatística Prática para Cientistas de Dados.*
- McKinney, W. (2017). *Python for Data Analysis.* O'Reilly Media.
- VanderPlas, J. (2016). *Python Data Science Handbook.* O'Reilly Media.

**Recursos Online:**
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)
- [Towards Data Science](https://towardsdatascience.com)
- [Kaggle](https://kaggle.com)