

# **Fundamentação Teórica da Análise Espectral, Arquitetura de OSAs e Calibração Inteligente para Sistemas de Baixo Custo (OSA Visível)**

## **2.1. Fundamentos da Espectroscopia Óptica e Análise de Matéria**

A espectroscopia óptica constitui o pilar fundamental para a caracterização da matéria, explorando a interação entre a radiação eletromagnética e as propriedades atômicas e moleculares de uma amostra. O Analisador de Espectro Óptico (OSA) de baixo custo, denominado "Osinha"/"OSA Visível", é projetado para operar na faixa de luz visível (VIS, 380–750 nm).1 Neste intervalo, a absorção de energia luminosa tipicamente desencadeia transições eletrônicas em moléculas ou íons, permitindo a identificação e quantificação de compostos químicos através de seus espectros característicos.

### **2.1.1. Interação Luz-Matéria: Transmissão e Absorção**

Quando a luz incide sobre uma amostra, ela pode ser transmitida, refletida ou absorvida. Em espectrofotometria, a análise primária foca na absorção. A luz branca, composta por todos os comprimentos de onda do espectro visível, tem sua intensidade reduzida de forma seletiva quando atravessa uma substância, resultando na cor percebida.1 Por exemplo, uma solução que absorve intensamente a luz verde parecerá vermelha ao observador. O objetivo do OSA é medir essa absorção seletiva em função do comprimento de onda.

### **2.1.2. Lei de Beer-Lambert: Base Quanti-Analítica da Espectrometria de Absorção**

A Lei de Beer-Lambert (também conhecida como Lei de Beer–Bouguer–Lambert, ou BBL) é a relação empírica que governa a atenuação da intensidade da radiação ao passar por um meio homogêneo.2 Ela estabelece uma relação direta e linear entre a absorbância de uma solução e a concentração da substância absorvente, bem como o caminho óptico percorrido pela luz.3  
A lei é expressa matematicamente como:

$$A \= \\epsilon cl$$

Onde $A$ representa a absorbância (adimensional), $\\epsilon$ é a absortividade molar (uma constante característica da substância em um dado comprimento de onda), $c$ é a concentração da substância em solução, e $l$ é o comprimento do caminho óptico.3  
Para que a Lei de Beer-Lambert seja válida, várias premissas devem ser satisfeitas.2 Estas incluem a necessidade de radiação monocromática, a ausência de interações entre as moléculas do soluto (o que geralmente requer baixas concentrações) e um meio macroscopicamente homogêneo. A alta correlação ($R^2 \\geq 0.93$) observada durante os experimentos de validação do OSA Visível com a diluição de glicerina 1 confirma que o sistema de baixo custo, quando devidamente calibrado, opera com a precisão necessária para manter a linearidade exigida pelo Beer-Lambert, tornando-o funcionalmente viável para aplicações quanti-analíticas na faixa visível.

### **2.1.3. O Princípio da Difração de Fraunhofer e Grades Ópticas**

A separação dos diferentes comprimentos de onda que incidem sobre o detector do OSA é realizada por um elemento dispersor, neste caso, uma grade de difração. A difração de Fraunhofer (também chamada de difração de campo distante) descreve o padrão de difração que ocorre quando as ondas planas incidem sobre o objeto dispersor e o padrão é observado a uma distância suficientemente longa ou no plano focal de uma lente de imagem, que é o arranjo típico de um espectrômetro.4  
A relação fundamental que governa a dispersão angular de uma grade de difração é dada pela Equação da Grade:

$$n\\lambda \= d(\\sin\\theta \+ \\sin\\alpha)$$

Nesta equação, $n$ representa a ordem de difração (geralmente $n=1$ é utilizado), $\\lambda$ é o comprimento de onda da luz, $d$ é a constante da grade (espaçamento entre as linhas, $d \= 1\\,\\mu\\text{m}$ para a grade de $1000 \\cdot \\text{linhas} / \\text{mm}$ usada no Osinha) 1, $\\alpha$ é o ângulo de incidência da luz na grade, e $\\theta$ é o ângulo de difração.  
A relação entre o comprimento de onda ($\\lambda$) e a posição física do pixel ($x$) no detector, resultante dessa dispersão, é inerentemente não linear, pois envolve funções trigonométricas de ângulo. No entanto, em sistemas compactos de baixo custo, como o "Osinha", o detector captura apenas uma porção angular muito pequena do espectro. Esta limitação angular permite que o mapeamento seja modelado, em primeira aproximação, por uma **Regressão Linear** ($\\lambda(x) \= a x \+ b$).5 Reconhece-se que essa simplificação linear requer uma calibração rigorosa e absoluta, que é justamente fornecida pelos pontos de referência de lasers de comprimento de onda conhecido, como será detalhado nas seções subsequentes.1

## **2.2. Análise de Espectro Óptico (OSA): Arquiteturas e Metrologia Padrão**

O Analisador de Espectro Óptico (OSA) é um instrumento essencial para medir a distribuição de potência óptica em função do comprimento de onda.6

### **2.2.1. Definição e Arquitetura do OSA Visível**

Historicamente, OSAs utilizavam arquiteturas baseadas em monocromadores sintonizáveis (varredura), onde um filtro óptico ajustável resolvia os componentes espectrais individualmente. Em contraste, o OSA Visível utiliza uma arquitetura baseada em array de detetores (grade/CMOS), que captura todo o espectro simultaneamente, melhorando a velocidade de aquisição.8  
O hardware do espectrômetro "Osinha" 1 se baseia em uma solução de baixo custo, aproveitando a fabricação aditiva (impressão 3D) para construir a estrutura óptica. O uso da impressão 3D reduz drasticamente os custos e permite a personalização rápida do design, superando a necessidade de polimento de precisão laboriosa, comum em óptica tradicional.10  
Os componentes principais são:

1. **Estrutura Impressa em 3D:** Proporciona a geometria necessária para o caminho óptico, fenda, e posicionamento da grade e do sensor.1  
2. **Grade de Difração:** Responsável por separar os comprimentos de onda, com $1000 \\cdot \\text{linhas} / \\text{mm}$.1  
3. **Detector:** Uma Webcam USB, utilizando um sensor CMOS de $640 \\times 480$ pixels.

O sinal de luz, depois de disperso, é discretizado pelo sensor CMOS. A intensidade digital no pixel $(x,y)$ é representada pela equação de amostragem 1:

$$I(x,y) \= \\sum\_{k=0}^{255} k \\cdot P(k|x,y)$$

Onde $k$ é o nível de intensidade (de 0 a 255\) e $P(k|x,y)$ é a probabilidade do pixel $(x,y)$ registrar a intensidade $k$.

### **2.2.2. Metrologia de OSAs: Padrões e a Justificativa para a Solução de Baixo Custo**

A calibração de OSAs de alta precisão é regida por normas internacionais, como a IEC 62129, que detalham procedimentos para garantir a rastreabilidade da medição de comprimento de onda e potência.7 Métodos tradicionais de calibração utilizados em equipamentos de laboratório envolvem:

1. **Fontes de Referência Estáveis:** Uso de *lasers* altamente estabilizados, cujos comprimentos de onda são monitorados simultaneamente por um *wavemeter* de altíssima acurácia.12  
2. **Células de Gás:** Utilização de células de referência (e.g., HCN) que fornecem picos de absorção fixos e bem conhecidos em faixas específicas.12  
3. **Modelagem Polinomial Avançada:** Empregando lâmpadas de arco (neon, argônio) para gerar múltiplos picos espectrais conhecidos, ajustados por polinômios de segunda ou terceira ordem para mapear a relação comprimento de onda-pixel.5

O custo desses métodos e dos equipamentos comerciais é proibitivo, variando de mais de $30.000 a mais de $100.000 para modelos de alta performance.1 Diante dessa realidade, o projeto "OSA Visível" representa uma abordagem estratégica para democratizar a análise espectral. A substituição da instrumentação metrológica de ponta pela **inteligência algorítmica** (visão computacional) permite alcançar uma acurácia funcional ($\\pm 1.8$ nm) a um custo total inferior a $200, justificando a inovação do processo de calibração automatizada.  
Table 2.1: Comparativo de Requisitos Metrológicos: OSA Comercial vs. OSA Visível

| Modelo (Referência) | Faixa Espectral (nm) | Custo Estimado (USD) | Acurácia Típica | Método de Calibração |
| :---- | :---- | :---- | :---- | :---- |
| OSA201C (Thorlabs) 1 | 350–1100 | \> $30,000 | Sub-nm | Interno, Rastreado a Padrões |
| AQ6380 (Yokogawa) 1 | 350–1750 | $100,000–200,000 | Sub-pm | Padrões de Gás/Wavemeter 12 |
| **OSA Visível (Osinha)** 1 | **380–750** | **\< $200** | **$\\pm 1.8$ nm (RMS)** | **Híbrido (Visão Computacional \+ Laser)** |

## **2.3. Fundamentação do Mapeamento Comprimento de Onda-Pixel**

A calibração de comprimento de onda, ou calibração espectral, é o processo crucial que estabelece a correspondência exata entre o índice de pixel no sensor CMOS (coordenada $x$) e o valor absoluto do comprimento de onda ($\\lambda$).

### **2.3.1. O Desafio da Relação $\\lambda(x)$: Dispersão Física e Distorções do Sistema**

A transformação do ângulo de difração ($\\theta$) em posição de pixel ($x$) é influenciada pela geometria do sistema e pelas imperfeições do hardware. Em espectrômetros construídos com peças COTS (Commercial Off-The-Shelf) e impressão 3D, existem fontes de erro que desviam a relação $\\lambda(x)$ do ideal, como desalinhamentos angulares da grade, curvatura de campo do sensor e tolerâncias mecânicas na montagem.1

### **2.3.2. A Modelagem de Primeira Ordem: Regressão Linear ($\\lambda(x) \= a \\cdot x \+ b$)**

Para simplificar o processamento e, dado que o OSA Visível opera em uma faixa espectral relativamente estreita (380–750 nm), o mapeamento é modelado com um ajuste de primeira ordem.5 A relação linear entre o pixel e o comprimento de onda é definida por:

$$\\lambda(x) \= a \\cdot x \+ b$$

Onde $a$ é o fator de dispersão (nm/pixel) e $b$ é o offset de comprimento de onda.  
O método de calibração do OSA Visível utiliza o princípio de Mínimos Quadrados (Least Squares) para determinar $a$ e $b$, mas com uma ênfase particular na calibração por pontos fixos. Os lasers de referência Verde ($\\lambda\_{\\text{verd}} \= 532$ nm) e Vermelho ($\\lambda\_{\\text{verm}} \= 650$ nm) fornecem dois pontos metrológicos de ancoragem absoluta.1  
Os coeficientes $a$ e $b$ são calculados diretamente a partir da posição dos picos de intensidade desses lasers ($x\_{\\text{verd}}$ e $x\_{\\text{verm}}$) 1:

$$a \= \\frac{\\lambda\_{\\text{verm}} \- \\lambda\_{\\text{verd}}}{x\_{\\text{verm}} \- x\_{\\text{verd}}}, \\quad b \= \\lambda\_{\\text{verd}} \- a \\cdot x\_{\\text{verd}}$$  
Utilizar dois pontos fixos é fundamental. Um único ponto definiria apenas o *offset* $b$, mas deixaria a taxa de dispersão $a$ (nm/pixel) sujeita a erros sistêmicos. A determinação de ambos os parâmetros por dois pontos de referência garante que o escalonamento da dispersão angular seja corretamente aplicado em toda a faixa de operação do espectrômetro, minimizando o erro de inclinação.1

### **2.3.3. Metrologia de Acurácia: O Conceito de Erro RMS**

A acurácia do mapeamento comprimento de onda-pixel é avaliada utilizando o Erro Quadrático Médio (Root Mean Square Error – RMS), uma métrica padrão na metrologia espectral que quantifica a magnitude média do erro entre os valores medidos e os valores de referência.5  
O processo híbrido de calibração do OSA Visível demonstrou uma melhoria significativa de precisão: a calibração preliminar baseada em luz branca resultou em um erro RMS de $\\pm 2.1$ nm, que foi subsequentemente refinado para **$\\pm 1.8$ nm** após o ajuste absoluto utilizando os lasers de referência.1  
O erro RMS final de $\\pm 1.8$ nm valida a escolha do modelo de primeira ordem para esta aplicação. Embora não atinja a precisão de sub-picômetros de OSAs comerciais sofisticados, esta acurácia é mais do que suficiente para distinguir picos espectrais largos na faixa visível e satisfazer os requisitos de aplicações quantitativas baseadas na Lei de Beer-Lambert, como comprovado pelos altos coeficientes de determinação ($R^2$) nos ensaios com glicerina.1  
Table 2.2: Parâmetros Chave da Calibração Linear do OSA Visível

| Parâmetro Metrológico | Ajuste Preliminar (Luz Branca) | Ajuste Final (Lasers 532/650 nm) | Significado Físico |
| :---- | :---- | :---- | :---- |
| Coeficiente $a$ (nm/pixel) 1 | \-0.060825 | 1.475 | Taxa de dispersão (nm por pixel) |
| Coeficiente $b$ (nm) 1 | 203.1368 | 195.7 | Intercepto (Wavelength Offset) |
| Erro RMS 1 | $\\pm 2.1$ nm | $\\pm 1.8$ nm | Acurácia final da calibração |

## **2.4. Aplicação de Visão Computacional para Calibração Automatizada**

A Visão Computacional é o diferencial tecnológico que permite ao OSA Visível executar calibrações de forma automatizada, robusta e precisa, substituindo métodos manuais demorados ou dependentes de hardware dedicado.

### **2.4.1. Processamento Digital do Sinal Espectral (Imagens CMOS)**

O pipeline de processamento digital é crucial para extrair o dado espectral da imagem bruta capturada pela webcam. Uma etapa inicial essencial é a Média Temporal (Frame Averaging). Em sensores CMOS de baixo custo, o ruído aleatório (como ruído de disparo ou ruído térmico) é significativo. Para a calibração com lasers, o software captura $N=20$ quadros em um curto intervalo e calcula a intensidade média $\\bar{I}(x,y)$ 1:

$$\\bar{I}(x,y) \= \\frac{1}{N}\\sum\_{i=1}^{N} I\_i(x,y)$$

O cálculo da média temporal melhora drasticamente a Relação Sinal-Ruído (SNR), permitindo a detecção mais precisa dos picos de intensidade dos lasers. Após a média, a imagem é convertida para escala de cinza, simplificando a análise da intensidade luminosa.1

### **2.4.2. Segmentação e Limiarização Adaptativa de Imagem (Método de Otsu)**

Para isolar o espectro (o sinal de interesse) do fundo escuro e do ruído residual da imagem, é necessária uma etapa de segmentação. O **Método de Otsu** é um algoritmo automático de limiarização global que opera maximizando a variância entre classes (foreground vs. background) no histograma de intensidade da imagem.16  
O Otsu calcula o limiar ótimo $T$ que melhor divide os pixels da imagem em duas classes, garantindo que o sinal espectral, mesmo que difuso, seja completamente capturado. Isso resulta em uma máscara binária $M(x,y)$:

$$M(x,y) \= \\begin{cases} I\_{gray}(x,y), & \\text{se } I\_{gray}(x,y) \\geq T \\\\ 0, & \\text{caso contrário} \\end{cases}$$  
1  
A aplicação de um limiar adaptativo torna o processo de calibração robusto a variações na iluminação da fonte de luz branca e às condições ambientais, eliminando a necessidade de ajustes manuais do limiar.

### **2.4.3. Localização de Fontes: Centróide e Detecção de Picos**

A visão computacional é usada para duas tarefas críticas de localização: o centróide para o espectro contínuo e a detecção de pico para os lasers de referência.  
**Cálculo do Centróide:** O centróide $(x\_c, y\_c)$ representa o centro de massa ponderado pela intensidade dos pixels ativos dentro da máscara $M$.18  
$$x\_c \= \\frac{\\sum\_{x,y} x \\cdot M(x,y)}{\\sum\_{x,y} M(x,y)}, \\quad y\_c \= \\frac{\\sum\_{x,y} y \\cdot M(x,y)}{\\sum\_{x,y} M(x,y)}$$  
1  
Este cálculo é vital, pois o espectrômetro "Osinha", devido à sua construção 3D com tolerâncias inerentes, pode apresentar um desalinhamento rotacional do espectro no sensor CMOS. O centróide fornece um ponto de referência central que permite à regressão linear preliminar definir corretamente a orientação espacial da linha espectral na imagem (a inclinação da reta $y=mx+c$), compensando o desalinhamento mecânico antes da calibração absoluta.  
Detecção de Picos: Para os lasers de referência, a posição de comprimento de onda é determinada pelo pixel de máxima intensidade. A posição do pico ($x\_{peak}$) é determinada pelo argumento máximo da função intensidade $I(x)$ ao longo da linha espectral 1:

$$x\_{peak} \= \\arg \\max\_{x} \\, I(x)$$

Esta precisão na localização dos picos é o que garante a acurácia metrológica final da calibração, fornecendo os pontos fixos necessários para a determinação dos coeficientes $a$ e $b$.1  
Table 2.3: Algoritmos de Visão Computacional Aplicados à Calibração

| Algoritmo (Referência) | Propósito | Impacto Metrológico | Justificativa para Baixo Custo |
| :---- | :---- | :---- | :---- |
| Média Temporal 1 | Aumento do SNR | Reduz erro aleatório na intensidade | Mitiga o ruído inerente a sensores CMOS de baixo custo. |
| Limiarização Otsu 1 | Segmentação ROI espectral | Isolamento do sinal de interesse | Automatiza o processo, tornando-o robusto a variações de iluminação. |
| Cálculo de Centróide 1 | Localização geométrica | Define a orientação espacial da dispersão | Compensa desalinhamentos mecânicos da estrutura 3D. |
| Regressão Linear 1 | Mapeamento $\\lambda(x)$ | Converte pixel para nm com precisão funcional. | Eficácia metrológica com baixo custo computacional. |

## **2.5. O Processo Híbrido de Calibração do OSA Visível**

O processo de calibração do "OSA Visível" é um método híbrido que combina a inteligência da visão computacional com referências metrológicas de comprimento de onda conhecido, garantindo a acurácia dentro do limite de custo estabelecido.

### **2.5.1. Etapa 1: Calibração Preliminar com Luz Branca (Ajuste da Orientação Espacial)**

O primeiro passo utiliza o espectro contínuo de uma fonte de luz branca.1 O objetivo desta fase é obter um ajuste inicial do espectro na imagem, crucial para compensar a geometria imperfeita da montagem 3D.

1. O software captura um quadro, converte-o para escala de cinza e aplica o método de Otsu para segmentação.  
2. É calculado o centróide $(x\_c, y\_c)$ da nuvem de pixels ativos. A localização do centróide fornece o ponto central do espectro na imagem.1  
3. Uma regressão linear é aplicada à nuvem de pontos ativa para determinar a inclinação da reta espectral ($y \= m x \+ c$). Essa reta define o eixo de dispersão.  
4. Os parâmetros preliminares $a$ e $b$ da relação $\\lambda(x)$ são calculados com base nesta orientação inicial, resultando em um erro RMS de $\\pm 2.1$ nm.1 Esta etapa estabelece uma correlação linear entre a intensidade dos pixels e sua posição na imagem.

### **2.5.2. Etapa 2: Calibração Absoluta com Lasers de Comprimento de Onda Conhecido**

A Etapa 2 é a fase de ancoragem metrológica. Após a calibração inicial que alinha espacialmente o espectro, os lasers de referência são utilizados para mapear essa reta de dispersão preliminar aos comprimentos de onda absolutos conhecidos.  
São utilizados dois lasers, Verde (532 nm) e Vermelho (650 nm).1

1. O software captura 20 quadros e aplica a média temporal para maximizar o SNR e a precisão.  
2. A posição exata dos picos de intensidade dos lasers ($x\_{532}$ e $x\_{650}$) é determinada pelo cálculo do Arg Max.1  
3. Utilizando as coordenadas absolutas (pico de pixel, comprimento de onda real), o software calcula os coeficientes finais $a$ e $b$ que definem a relação $\\lambda(x) \= a x \+ b$.

Essa correspondência entre as posições dos picos na reta de calibração e os comprimentos de onda reais garante que a dispersão (nm/pixel) seja corretamente escalada em toda a faixa de operação do OSA, culminando na precisão final de $\\pm 1.8$ nm.1 A utilização de dois pontos fixos é essencial para definir inequivocamente tanto o *offset* quanto a dispersão da reta linear.

### **2.5.3. Validação Experimental do Sistema: Ensaio de Beer-Lambert**

A validação experimental provou que a calibração automatizada é metrologicamente válida para aplicações quantitativas. O ensaio de diluição de glicerina em água (faixa de 10–30% v/v) demonstrou que o sistema é capaz de medir a absorbância com alta fidelidade.1  
Os espectros de absorção obtidos mostraram picos característicos em 511 nm (verde) e 620 nm (vermelho). A correlação entre os dados experimentais de absorbância e as concentrações teóricas (aplicando o princípio Beer-Lambert) resultou em coeficientes de determinação ($R^2$) consistentemente altos, variando entre 0.93 e 0.99 para diferentes fontes de luz (LEDs azul, verde e vermelho) e espessuras de amostra.1 Este resultado valida empiricamente que a acurácia de $\\pm 1.8$ nm obtida pela calibração híbrida é suficiente para o propósito de análise espectral de baixo custo.  
A principal limitação desse modelo reside na escolha da regressão linear de primeira ordem, que, embora funcional na faixa visível, pode introduzir erros sistemáticos maiores nas extremidades do espectro (abaixo de 400 nm e acima de 700 nm), onde a não-linearidade da Equação de Difração de Fraunhofer se manifesta mais intensamente. Trabalhos futuros devem, portanto, explorar a incorporação de modelos não lineares (polinômios de ordem superior) para aprimorar a precisão nessas regiões.1 Outras avenidas de desenvolvimento incluem a expansão da faixa espectral para o infravermelho próximo (750–1100 nm), o que exigirá a adaptação do sensor CMOS e uma nova reavaliação dos parâmetros metrológicos e algorítmicos.1

#### **Works cited**

1. sbaconf.tex  
2. Beer–Lambert law \- Wikipedia, accessed November 10, 2025, [https://en.wikipedia.org/wiki/Beer%E2%80%93Lambert\_law](https://en.wikipedia.org/wiki/Beer%E2%80%93Lambert_law)  
3. Beer-Lambert Law | Transmittance & Absorbance \- Edinburgh Instruments, accessed November 10, 2025, [https://www.edinst.com/resource/the-beer-lambert-law/](https://www.edinst.com/resource/the-beer-lambert-law/)  
4. Fraunhofer diffraction \- Wikipedia, accessed November 10, 2025, [https://en.wikipedia.org/wiki/Fraunhofer\_diffraction](https://en.wikipedia.org/wiki/Fraunhofer_diffraction)  
5. A CLOSER LOOK AT SPECTROGRAPHIC WAVELENGTH CALIBRATION Marie Bøe Henriksen1,2, Fred Sigernes1,2 and Tor Arne Johansen1, accessed November 10, 2025, [http://kho.unis.no/doc/MarieCalibrationWhisper2022.pdf](http://kho.unis.no/doc/MarieCalibrationWhisper2022.pdf)  
6. Spectrum analyzer \- Wikipedia, accessed November 10, 2025, [https://en.wikipedia.org/wiki/Spectrum\_analyzer](https://en.wikipedia.org/wiki/Spectrum_analyzer)  
7. IEC 62129:2006 \- Calibration of optical spectrum analyzers \- iTeh Standards, accessed November 10, 2025, [https://standards.iteh.ai/catalog/standards/iec/e5137235-b156-4b86-8102-62e567484e3a/iec-62129-2006](https://standards.iteh.ai/catalog/standards/iec/e5137235-b156-4b86-8102-62e567484e3a/iec-62129-2006)  
8. Optical Spectrum Analysis | Keysight, accessed November 10, 2025, [https://www.keysight.com/us/en/assets/3120-1501/application-notes/5963-7145.pdf](https://www.keysight.com/us/en/assets/3120-1501/application-notes/5963-7145.pdf)  
9. Welcome to » Open Fiber Spectrometer \- gaudi.ch, accessed November 10, 2025, [http://www.gaudi.ch/GaudiLabs/?page\_id=825](http://www.gaudi.ch/GaudiLabs/?page_id=825)  
10. Optical Device Fabrication with 3D printing | Explore Technologies \- Stanford, accessed November 10, 2025, [https://techfinder.stanford.edu/technology/optical-device-fabrication-3d-printing](https://techfinder.stanford.edu/technology/optical-device-fabrication-3d-printing)  
11. Three-dimensional printing in ophthalmology and eye care: current applications and future developments \- PMC \- PubMed Central, accessed November 10, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9247992/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9247992/)  
12. Calibration of grating based optical spectrum analyzers Osama Terra & Hatem Hussein \- ResearchGate, accessed November 10, 2025, [https://www.researchgate.net/profile/Osama-Terra/publication/282900283\_Calibration\_of\_grating\_based\_optical\_spectrum\_analyzers/links/5a1a44aaa6fdcc50adeaee96/Calibration-of-grating-based-optical-spectrum-analyzers.pdf](https://www.researchgate.net/profile/Osama-Terra/publication/282900283_Calibration_of_grating_based_optical_spectrum_analyzers/links/5a1a44aaa6fdcc50adeaee96/Calibration-of-grating-based-optical-spectrum-analyzers.pdf)  
13. Calibration of grating based optical spectrum analyzers \- ResearchGate, accessed November 10, 2025, [https://www.researchgate.net/publication/282900283\_Calibration\_of\_grating\_based\_optical\_spectrum\_analyzers](https://www.researchgate.net/publication/282900283_Calibration_of_grating_based_optical_spectrum_analyzers)  
14. Improved Wavelength Calibration by Modeling the Spectrometer \- PubMed, accessed November 10, 2025, [https://pubmed.ncbi.nlm.nih.gov/35726593/](https://pubmed.ncbi.nlm.nih.gov/35726593/)  
15. Improved Wavelength Calibration by Modeling the Spectrometer ..., accessed November 10, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9597159/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9597159/)  
16. Otsu's method \- Wikipedia, accessed November 10, 2025, [https://en.wikipedia.org/wiki/Otsu%27s\_method](https://en.wikipedia.org/wiki/Otsu%27s_method)  
17. Otsu's Thresholding Technique \- LearnOpenCV, accessed November 10, 2025, [https://learnopencv.com/otsu-thresholding-with-opencv/](https://learnopencv.com/otsu-thresholding-with-opencv/)  
18. Spectral centroid \- Wikipedia, accessed November 10, 2025, [https://en.wikipedia.org/wiki/Spectral\_centroid](https://en.wikipedia.org/wiki/Spectral_centroid)  
19. Spectral Centroiding and Calibration \- Python for Astronomers, accessed November 10, 2025, [https://prappleizer.github.io/Tutorials/Centroiding/centroiding\_tutorial.html](https://prappleizer.github.io/Tutorials/Centroiding/centroiding_tutorial.html)