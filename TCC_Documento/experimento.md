# Experimentos de validação do processo de calibração (OSA Visível / Osinha)

Este documento reúne **3 sugestões viáveis de experimentos** para validar o processo de calibração do **OSA Visível** (espectrômetro “Osinha” + software), conforme descrito no seu TCC: **ajuste preliminar com luz branca** (orientação espacial via centróide e regressão linear) e **ancoragem absoluta com lasers** de referência (**532 nm** e **650 nm**), resultando na relação:

\[
\lambda(x) = a\cdot x + b
\]

e avaliação de acurácia (por exemplo) via **erro RMS**.

---

## Experimento 1 — Comparação direta com OSA comercial (validação cruzada do eixo \(\lambda\))

**Objetivo:** comparar, para a mesma fonte óptica, o espectro obtido pelo **OSA comercial** do laboratório e pelo **OSA Visível**, verificando:
- concordância do eixo de comprimento de onda;
- repetibilidade do mapeamento \(\lambda(x)\) após calibração.

**Instrumentos e materiais (viáveis em laboratório):**
- OSA comercial do laboratório (referência);
- OSA Visível (Osinha + webcam) e o software desenvolvido;
- Fonte(s) óptica(s) com espectros característicos (use o que vocês tiverem):  
  - LEDs coloridos (azul/verde/vermelho),  
  - laser(s) de referência,  
  - lâmpadas com linhas (se disponível),  
  - laser de diodo com driver estável;
- Acoplamento/apoio mecânico: fibra óptica, colimador, difusor ou suporte para manter geometria reprodutível.

**Procedimento sugerido:**
1. **Preparação/estabilização:** ligar a fonte e aguardar estabilização térmica (ex.: 5–10 min, depende da fonte).
2. **Calibração do OSA Visível:** executar o fluxo completo (luz branca + lasers 532/650 nm), salvar \(a\) e \(b\), registrar data/hora.
3. **Aquisição no OSA comercial:** medir o espectro e registrar pico(s) em \(\lambda\), largura (FWHM, se disponível) e potência (se aplicável).
4. **Aquisição no OSA Visível:** medir a mesma fonte, exportar \(I(\lambda)\) e registrar pico(s), forma espectral e condições de captura (exposição/ganho, ROI).
5. **Repetibilidade:** repetir o passo 4 várias vezes (ex.: \(n \ge 10\)) sem alterar montagem; depois repetir após desmontar/remontar (ex.: 3 montagens).

**Métricas e análise (o que reportar):**
- **Erro em comprimento de onda:**  
  \[
  \Delta\lambda = \lambda_{\text{Visível}} - \lambda_{\text{OSA}}
  \]
  para cada pico/linha (relatar média e desvio padrão).
- **Repetibilidade:** desvio padrão de \(\lambda_{\text{Visível}}\) em múltiplas aquisições (mesma montagem) e variação após remontagem.
- **Acurácia global:** se houver múltiplos picos/linhas, calcular erro RMS em relação ao OSA comercial.

**Observação prática:** manter a geometria de entrada (posição/ângulo/acoplamento) o mais constante possível. Se o OSA comercial operar em faixa mais ampla, restringir a comparação à faixa efetiva do Osinha (VIS, tipicamente 380–750 nm).

---

## Experimento 2 — Validação com fontes de picos/linhas conhecidas (linearidade e erro nas extremidades)

**Objetivo:** validar o mapeamento \(\lambda(x)\) ao longo do VIS usando referências com comprimentos de onda conhecidos (picos/linhas estreitas), verificando:
- linearidade do modelo;
- aumento de erro próximo às extremidades (abaixo de 400 nm e acima de 700 nm).

**Opções de fontes (escolher as viáveis no laboratório):**
- **Lasers adicionais** (ex.: 405 nm, 450 nm, 635/638 nm, 808 nm — usar apenas se a resposta do sensor permitir);
- **LEDs de banda “mais estreita”** (azul/verde/âmbar/vermelho profundo) com datasheet do pico dominante (\(\lambda_d\)) e FWHM típica;
- **Lâmpada fluorescente/mercúrio** (se disponível) para linhas discretas; alternativamente lâmpadas de descarga do laboratório.

**Procedimento sugerido:**
1. Calibrar o OSA Visível com luz branca + lasers 532/650 nm.
2. Para cada fonte de teste, adquirir \(N\) quadros e aplicar média temporal (ex.: \(N=20\), como no método), exportando \(I(\lambda)\).
3. Extrair o pico principal \(\lambda_{\text{med}}\) (arg max) e, quando fizer sentido, estimar FWHM (em nm).
4. Repetir para ao menos 5 fontes distribuídas ao longo do VIS (incluindo regiões próximas às bordas).

**Métricas e análise (o que reportar):**
- **Erro por ponto:**  
  \[
  \Delta\lambda_i = \lambda_{\text{med},i} - \lambda_{\text{ref},i}
  \]
  onde \(\lambda_{\text{ref}}\) vem do laser/datasheet/linha conhecida.
- **Curva de erro vs. \(\lambda\):** gráfico de \(\Delta\lambda\) em função de \(\lambda_{\text{ref}}\), destacando tendência de erro nas extremidades.
- **Erro RMS:** consolidar um RMS global (idealmente com 3–5+ pontos).

**Observação prática:** LEDs têm banda larga (FWHM tipicamente dezenas de nm), então o “pico de referência” pode variar com corrente/temperatura; nesse caso, o experimento é ótimo para **consistência** e **tendências**, enquanto lasers/linhas de descarga são melhores como referência absoluta.

---
**Nota:** Descontinuado.

## Experimento 3 — Validação quantitativa por Beer-Lambert (aplicação real + consistência espectral)

**Objetivo:** validar se, após calibração, o OSA Visível produz medidas consistentes para aplicações quantitativas baseadas em **absorbância**, reproduzindo um ensaio tipo Beer-Lambert com amostras de concentração controlada (ex.: diluição de glicerina, como citado no texto).

**Instrumentos e materiais (viáveis):**
- Fonte(s) de iluminação (LED(s) ou luz branca) com montagem reprodutível;
- Suporte de amostra (cuveta, célula ou caminho óptico fixo), idealmente com comprimento \(l\) conhecido/constante;
- Solução de teste: ex. diluições de glicerina em água (10–30% v/v) ou outra solução segura/disponível com variação controlada de absorção/espalhamento;
- OSA Visível calibrado (e, opcionalmente, instrumento de referência como espectrofotômetro UV-Vis, se existir).

**Procedimento sugerido:**
1. Calibrar o OSA Visível (luz branca + lasers 532/650 nm) e manter a montagem fixa.
2. Medir um **espectro de referência** \(I_0(\lambda)\) (sem amostra, ou com branco/solvente).
3. Para cada concentração \(c\), medir \(I(\lambda)\) com a amostra e calcular:
   \[
   T(\lambda)=\frac{I(\lambda)}{I_0(\lambda)}
   \]
4. Calcular a absorbância:
   \[
   A(\lambda) = -\log(T(\lambda))
   \]
5. Selecionar comprimentos de onda (ou regiões) de interesse e construir curvas \(A\) vs. \(c\) (ajuste linear), reportando \(R^2\).

**Métricas e análise (o que reportar):**
- **Linearidade Beer-Lambert:** \(R^2\) do ajuste \(A=\epsilon c l\) para \(\lambda\) selecionados.
- **Repetibilidade:** variação de \(A(\lambda)\) em medições repetidas (mesma amostra/configuração).
- **Impacto da calibração espectral:** repetir o experimento (ou parte dele) após recalibrar e verificar se picos/vales se mantêm em \(\lambda\) consistente.

**Observação prática:** controlar exposição/ganho da câmera, intensidade da fonte e posicionamento da amostra. Mesmo sem calibração absoluta do eixo \(Y\), usar a razão \(I/I_0\) reduz sensibilidade a variações de intensidade e favorece validação de consistência.

---

## Recomendações gerais (segurança e reprodutibilidade)

- **Segurança com lasers:** usar óculos apropriados (especialmente para 532 nm) e evitar alinhamentos com feixe livre na altura dos olhos.
- **Reprodutibilidade mecânica:** registrar ROI, distância fonte–entrada, e ajustes físicos (ângulos/altura), pois pequenas mudanças podem deslocar o espectro na webcam.
- **Registro de parâmetros:** documentar resolução/FPS/exposição/ganho, \(N\) de quadros na média temporal e versão do software, permitindo repetição por terceiros.

