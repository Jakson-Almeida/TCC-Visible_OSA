# 📊 Visualizador de Calibração Espectral OSA → ThorLabs

Script Python para visualizar e aplicar o modelo de calibração espectral do OSA Visível.

## 📌 Modelo geral (recomendado)

Se existir **`modelo_geral_parametros.csv`** (gerado por `modelagem_espectral_geral.m`), o visualizador usa automaticamente o **modelo geral**:

- **Fórmula:** P_ThorLabs(λ) = β₁(λ)·Pr(λ) + β₂(λ)·Pg(λ) + β₃(λ)·Pb(λ)
- **Independente de duty cycle e fonte de luz** — válido para **espectros quaisquer** (faixa não saturada).
- Basta carregar os 3 canais RGB do OSA; não é necessário informar duty nem LED.

Se o arquivo não existir, o visualizador usa o modelo por fonte (Verde/Vermelho/Azul) com duty cycle.

## 🎯 Funcionalidades

1. **Seleção de Arquivos**: Carregue 3 arquivos de espectros (canais R, G, B do OSA)
2. **Espectro de Referência**: Opcional — importe um espectro de referência (ex.: ThorLabs) para comparar com o calibrado
3. **Escolha de Fonte**: Selecione qual LED está sendo medido (Verde, Vermelho, Azul)
4. **Ajuste de Duty Cycle**: Defina o duty cycle de 1% a 10%
5. **Visualização Dupla**:
   - Gráfico 1: Canais RGB originais do OSA
   - Gráfico 2: Espectro calibrado (e referência, se importada) com gradiente de cores espectrais
6. **Comparação**: Com referência ativa, exibe RMSE e erro médio relativo na barra de status
7. **Estatísticas**: Mostra pico máximo e comprimento de onda

---

## 🚀 Como Usar

### 1. Pré-requisitos

```bash
pip install numpy pandas matplotlib scipy
```

### 2. Estrutura de Arquivos Necessária

Certifique-se de que os arquivos de modelo estão no mesmo diretório:
- `modelo_verde_parametros.csv`
- `modelo_vermelho_parametros.csv`
- `modelo_azul_parametros.csv`

### 3. Executar o Visualizador

```bash
python calibration_viewer.py
```

### 4. Passo a Passo na Interface

1. **Selecionar Arquivos**:
   - Clique em "Canal R" → selecione `spectrum_r_XXX.txt`
   - Clique em "Canal G" → selecione `spectrum_g_XXX.txt`
   - Clique em "Canal B" → selecione `spectrum_b_XXX.txt`

2. **Espectro de Referência (opcional)**:
   - Clique em "Espectro referência" e escolha um arquivo (ex.: espectro ThorLabs no mesmo duty/fonte)
   - Marque "Mostrar referência" para exibir no gráfico
   - Use "Limpar ref." para remover

3. **Configurar Parâmetros**:
   - Marque a fonte LED sendo medida (Verde/Vermelho/Azul)
   - Ajuste o slider de Duty Cycle (1-10%)

4. **Processar**:
   - Clique em "▶ Processar e Visualizar"
   - Aguarde a geração dos gráficos
   - Se houver referência, a barra de status mostrará RMSE e erro médio (%)

---

## 📁 Formato dos Arquivos de Entrada

Os arquivos de espectro devem estar no formato:

```
comprimento_onda_metros;intensidade
3.72700000000000e-07;2.10317460317460
3.74175000000000e-07;2.34126984126984
...
```

- **Separador**: ponto e vírgula (`;`)
- **Coluna 1**: Comprimento de onda em metros (notação científica)
- **Coluna 2**: Intensidade (valores decimais)

---

## 🔬 Como Funciona o Modelo

Para cada comprimento de onda λ no espectro:

### 1. Polinômios de 2ª ordem para cada canal:
```
y_R(d) = a_R·d² + b_R·d + c_R
y_G(d) = a_G·d² + b_G·d + c_G
y_B(d) = a_B·d² + b_B·d + c_B
```

### 2. Combinação linear (calibração):
```
P_ThorLabs(d, λ) = α₁·y_R(d) + α₂·y_G(d) + α₃·y_B(d)
```

Onde:
- `d` = duty cycle
- `a, b, c` = coeficientes polinomiais (variam com λ)
- `α₁, α₂, α₃` = coeficientes de calibração (variam com λ)

---

## 📊 Exemplo de Uso

### Caso de Uso: Medir LED Verde em 5% Duty Cycle

```
1. Arquivos:
   - Canal R: modelagem/Visible_OSA/peqs_1/Verde/spectrum_r_005.txt
   - Canal G: modelagem/Visible_OSA/peqs_1/Verde/spectrum_g_005.txt
   - Canal B: modelagem/Visible_OSA/peqs_1/Verde/spectrum_b_005.txt

2. Fonte: Verde

3. Duty: 5%

4. Resultado esperado:
   - Pico em ~516 nm
   - Intensidade calibrada ~5900 u.a.
   - Erro < 1% comparado ao ThorLabs
```

---

## 🎨 Visualização

### Gráfico 1: Canais RGB Originais
- Mostra as leituras brutas dos 3 canais do OSA
- Cores: vermelho, verde, azul

### Gráfico 2: Espectro Calibrado
- Espectro convertido para unidades ThorLabs
- Gradiente de cores espectrais (físicas)
- Linha preta = espectro calibrado

---

## ⚙️ Parâmetros Ajustáveis

| Parâmetro | Faixa | Descrição |
|-----------|-------|-----------|
| **Fonte** | Verde/Vermelho/Azul | LED sendo medido |
| **Duty Cycle** | 1-10% | Ciclo de trabalho do PWM |

---

## 📈 Validação

Para validar, compare com dados conhecidos:

```python
# Exemplo: LED Verde, Duty 5%, λ=516 nm
# Esperado (JSON): 5868.29
# Modelo prevê: 5829.90
# Erro: 0.7% ✅
```

---

## 🐛 Solução de Problemas

### Erro: "Arquivo de modelo não encontrado"
- Certifique-se de que os CSVs estão no mesmo diretório
- Verifique os nomes: `modelo_verde_parametros.csv`, etc.

### Erro: "Grades de comprimento de onda incompatíveis"
- Os 3 arquivos devem ter a mesma grade espectral
- Devem ser da mesma tomada e duty cycle

### Gráfico não aparece
- Verifique se matplotlib está instalado
- Tente: `pip install --upgrade matplotlib`

---

## 📝 Notas

- **Faixa Válida**: 373-681 nm (interseção ThorLabs/OSA)
- **Resolução**: ~1.5 nm (grade do OSA Visível)
- **Precisão**: Tipicamente < 4% de erro
- **Tempo de Processamento**: < 2 segundos

---

## 🎓 Referência

Este visualizador implementa o modelo desenvolvido em:
- `modelagem_espectral_completa.m`
- Parâmetros exportados via CSV

Para mais detalhes sobre o modelo, consulte:
- `modelagem_espectral_completa_resumo.txt`
- `modelo_osa_calibrado.m`

---

## 📧 Suporte

Para dúvidas ou problemas, consulte:
1. Este README
2. Código-fonte comentado em `calibration_viewer.py`
3. Documentação do modelo em `modelagem_espectral_completa.m`
