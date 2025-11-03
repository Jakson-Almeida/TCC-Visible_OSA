

# **Relatório Técnico Especializado: A Função Crítica dos Analisadores de Espectro Óptico na Faixa Visível (VIS)**

## **1\. Fundamentos da Espectroscopia e a Região UV-Visível**

### **1.1. O Espectro Eletromagnético e a Definição da Faixa VIS**

O Analisador de Espectro Óptico (OSA) é um instrumento metrológico cuja importância reside na sua capacidade de quantificar a distribuição de potência da radiação eletromagnética em função do comprimento de onda ($\\lambda$). Tradicionalmente, o campo de estudo da espectrofotometria Ultravioleta-Visível (UV-Vis) abrange a região que vai de aproximadamente $190 \\text{ nm}$ a $900 \\text{ nm}$.1 Dentro deste intervalo, a faixa visível (VIS) é estritamente definida, compreendendo comprimentos de onda entre aproximadamente $400 \\text{ nm}$ (violeta) e $700 \\text{ nm}$ (vermelho).  
Esta região espectral é particularmente crítica, pois as transições de energia atômicas e moleculares que ocorrem neste domínio são a base de diversas aplicações químicas, biológicas e de metrologia de cor. A radiação UV e VIS possui energia suficiente para induzir transições entre diferentes níveis de energia eletrônica em moléculas.1

### **1.2. Interação Luz-Matéria: Transições Eletrônicas e Cromóforos**

Quando a radiação eletromagnética interage com a matéria, diversos fenômenos podem ocorrer, incluindo reflexão, espalhamento, absorção, fluorescência/fosforescência (absorção e reemissão) e reações fotoquímicas.1 A espectroscopia UV-Vis foca primariamente na **absorção** de fótons.  
A absorção de luz por uma molécula resulta no aumento da sua energia potencial total. A energia total de uma molécula é a soma de suas energias eletrônica, vibracional e rotacional, conforme expresso por:  
$$E\_{total} \= E\_{electronic} \+ E\_{vibrational} \+ E\_{rotational}$$  
A absorção de fótons na faixa UV-Vis excita um elétron em uma estrutura molecular, conhecida como cromóforo, a um orbital de maior energia.2 No caso de cromóforos orgânicos, são assumidos quatro tipos de transições, incluindo a transição $\\pi–\\pi^\*$.2 A energia requerida para a transição eletrônica corresponde à energia do fóton incidente, definindo o comprimento de onda em que a absorção máxima ocorre. Em soluções, a superposição de níveis vibracionais e rotacionais sobre os níveis eletrônicos, combinada com interações soluto-solvente, resulta em bandas de absorção largas, caracterizando o espectro observado.1  
A relevância do OSA-VIS está intrinsecamente ligada à capacidade de **quantificar a presença de compostos** ou **biomarcadores** que exibem absorção seletiva nesta faixa. Por exemplo, a utilização da faixa visível (em especial o vermelho, $660 \\text{ nm}$) para diagnósticos, como na oximetria de pulso 3, não é acidental, mas sim uma consequência direta das diferenças de absorção espectral entre a hemoglobina oxigenada e a desoxigenada. Essa sensibilidade à composição química enfatiza a necessidade fundamental de calibração ultra-precisa do eixo de comprimento de onda ($\\lambda$). Um desvio mínimo no mapeamento espectral pode resultar em erros significativos na medição da concentração, particularmente em regiões de alta inclinação do espectro de absorção.

### **1.3. Princípios Fundamentais da Metrologia Espectral**

Os OSAs quantificam o comportamento da luz transmitida ou refletida pela amostra em relação à luz incidente.  
**Transmissão e Absorbância:** A Transmitância ($T$) é definida como a razão entre a intensidade da radiação transmitida ($I$) e a intensidade da radiação incidente ($I\_0$), e é frequentemente expressa como uma porcentagem.1  
$$T \= \\frac{I}{I\_0} \\quad \\text{ou} \\quad \\%T \= \\frac{I}{I\_0} \\times 100$$  
A Absorbância ($A$) é o parâmetro preferido para a quantificação, pois se relaciona linearmente com a concentração e o caminho óptico (conforme a Lei de Beer-Lambert).1  
$$A \= \-\\log T$$  
Embora o OSA meça primariamente a potência óptica ($I$) em função de $\\lambda$ 4, a determinação de $A$ a partir de $I$ e $I\_0$ permite a quantificação precisa de analitos, através da Lei de Beer-Lambert ($A \= \\epsilon \\cdot b \\cdot c$).  
É crucial distinguir a funcionalidade de um OSA de um espectrofotômetro tradicional de bancada. O termo OSA é frequentemente empregado para medir a distribuição espectral de potência de uma fonte de luz (Potência vs. $\\lambda$) 4, sendo amplamente utilizado em telecomunicações para caracterizar lasers. Já o espectrofotômetro UV-Vis mede a interação da luz com a amostra, quantificando Absorbância ou Transmitância.1 No contexto da caracterização de sensores de fibra óptica, como LPGs e FBGs, o OSA atua como um **interrogador espectral**, medindo a atenuação ou o pico de reflexão.5 Portanto, a calibração do instrumento desenvolvida pelo TCC deve obrigatoriamente garantir a precisão nas duas dimensões metrológicas: a escala de **Potência (Eixo Y)** e a escala de **Wavelength (Eixo X)**, replicando a complexa funcionalidade de um OSA comercial.4  
A precisão metrológica é desafiada por diversas fontes de incerteza, como a luz parasita (*stray light*), que é a luz que atinge o detector em comprimentos de onda indesejados, erro de comprimento de onda e desvios da Lei de Beer-Lambert, que podem ocorrer em altas concentrações.2

## **2\. Arquitetura e Funcionamento do Analisador de Espectro Óptico (OSA)**

### **2.1. Definição e Componentes Críticos do OSA**

Um Analisador de Espectro Óptico (OSA) é um instrumento de precisão projetado para medir e exibir a distribuição de **potência óptica** de uma fonte de luz sobre um determinado intervalo de comprimento de onda.4 Os três parâmetros-chave quantificados por um OSA são o comprimento de onda, o nível de potência e a Relação Sinal-Ruído Óptico (*Optical Signal-to-Noise Ratio* \- OSNR).4 A curva resultante é exibida com a potência no eixo vertical (Y) e o comprimento de onda no eixo horizontal (X).  
A arquitetura de um espectrofotômetro moderno UV-Vis, que compartilha muitos princípios com um OSA de banda larga, inclui 1:

1. **Uma Fonte de Luz:** Gera radiação de banda larga no espectro UV-Visível.  
2. **Um Dispositivo de Dispersão:** Separa a radiação em comprimentos de onda constituintes (e.g., monocromador ou grade de difração).  
3. **Uma Área de Amostra:** Onde a luz interage com o material.  
4. **Um ou Mais Detectores:** Para medir a intensidade da radiação transmitida ou refletida.

### **2.2. Fontes de Luz para Espectroscopia UV-Vis**

A seleção da fonte de luz é crucial para cobrir o espectro desejado 1:

* **Lâmpada de Deutério ($\\text{D}\_2$):** Tradicionalmente usada para fornecer um contínuo de alta intensidade na região UV ($185 \\text{ nm}$ a $400 \\text{ nm}$).  
* **Lâmpada de Tungstênio-Halogênio:** Fornece boa intensidade sobre o espectro visível e parte do UV ($350 \\text{ nm}$ a $3000 \\text{ nm}$).  
* **Lâmpada Xenon Flash (tendência moderna):** Oferece alta intensidade de $185 \\text{ nm}$ a $2500 \\text{ nm}$, eliminando a necessidade de duas lâmpadas separadas. Emite luz em pulsos curtos, resultando em longa vida útil e protegendo amostras fotossensíveis.1

Em sistemas de espectroscopia baseados em visão computacional, como aqueles que utilizam plataformas de *smartphone*, o *flash* LED branco nativo atua como fonte. Este LED opera especificamente na faixa VIS, tipicamente de $400 \\text{ nm}$ a $700 \\text{ nm}$.3

### **2.3. Tipologias Instrumentais e Métricas de Desempenho**

O projeto óptico de um OSA ou espectrofotômetro afeta diretamente sua precisão.1

* **Espectrofotômetro de Feixe Simples:** Possui design mais simples e menor custo. A luz passa pela amostra e depois pelo detector. Requer uma medição separada da linha de base (*baseline*) ou da amostra em branco, o que pode introduzir imprecisão se a intensidade da luz flutuar entre as medições.  
* **Espectrofotômetro de Feixe Duplo:** A luz do monocromador é dividida em um feixe de referência e um feixe de amostra. A medição da amostra é corrigida em tempo real para flutuações do instrumento, resultando em medições altamente precisas.1

OSAs de laboratório exigem especificações rigorosas, como baixa divergência de feixe (e.g., $0.2 \\text{ rad}$) e sistemas complexos de *trigger* (e.g., Schmitt Trigger com tensões mínimas e máximas definidas) para garantir a sincronização e a qualidade dos dados adquiridos.7  
A arquitetura de feixe duplo e o uso de lâmpadas Xenon pulsadas para compensar flutuações de fonte de luz representam a engenharia de precisão metrológica em hardware.1 Os sistemas de calibração baseados em visão computacional, frequentemente construídos com componentes de baixo custo (e.g., câmeras CMOS), não possuem esses mecanismos ópticos de compensação. O papel fundamental da visão computacional neste contexto é, portanto, ir além da mera conversão de pixel para $\\lambda$. O algoritmo de calibração deve ser robusto o suficiente para realizar a **compensação de instabilidade da fonte de luz** e a **correção de ruído** via *software*, replicando as funções que os sistemas ópticos de alto custo executam em hardware.  
Além disso, a detecção espectral em sistemas baseados em *smartphone* depende do sensor CMOS da câmera. Embora os sensores de silício sejam sensíveis até $900 \\text{ nm}$, as câmeras de consumo incluem um filtro infravermelho (IR filter) para limitar a resposta intencionalmente à faixa VIS ($400 \\text{ nm}$ a $700 \\text{ nm}$).3 Esta limitação define o domínio de operação do sistema, mas introduz um desafio algorítmico. O sensor utiliza uma matriz de Bayer (filtros RGB) para formação digital da cor, exigindo que a calibração por visão computacional lide com a resposta espectral não-linear de cada pixel RGB ao longo da distribuição de potência, o que é o cerne do problema da tese.

## **3\. O OSA como Ferramenta Central na Caracterização de Sensores de Fibra Óptica**

### **3.1. Sensores Ópticos Baseados em Fibra e a Importância do OSA**

Os Analisadores de Espectro Óptico (OSAs) são cruciais para a pesquisa e desenvolvimento de sensores ópticos baseados em fibra, pois atuam como o principal *interrogador espectral*. Tais sensores monitoram parâmetros ambientais, como temperatura, pressão, tensão (*strain*) e índice de refração (RI), através da modulação do comprimento de onda da luz.9  
No contexto de laboratórios que constroem sensores como as *Long-Period Gratings* (LPGs) e *Fiber Bragg Gratings* (FBGs), o OSA é a ferramenta fundamental para a caracterização experimental e a quantificação da sensibilidade.5

### **3.2. Mecanismos de Sensoriamento e Medição Espectral**

O mecanismo de detecção varia de acordo com o sensor:

* **Fiber Bragg Gratings (FBG):** O FBG é um refletor seletivo de comprimento de onda. O OSA mede o comprimento de onda de pico refletido ($\\lambda\_B$). Variações em $\\lambda\_B$ são diretamente proporcionais às mudanças de temperatura ou tensão que alteram o período da rede cristalina.5  
* **Long-Period Gratings (LPG):** O LPG promove o acoplamento de potência do modo de núcleo para os modos de revestimento (*cladding modes*), resultando em picos de atenuação no espectro de transmissão. O OSA mede a variação do comprimento de onda de atenuação e a amplitude desses picos, que são altamente sensíveis a variações no índice de refração externo ou à curvatura (*bending*) da fibra.6

### **3.3. Quantificação de Sensibilidade e Padrão Metrológico**

O OSA (como o ANDO AQ6317C) é o instrumento de referência utilizado para quantificar a sensibilidade dos sensores.5 A sua função é registrar com precisão as minúsculas mudanças espectrais induzidas por uma variável física.6  
A precisão do OSA permite a quantificação rigorosa das características do sensor, como demonstrado em testes sob pressão estática em sensores baseados em FBG.11 Nesses experimentos, o aumento da pressão levou a um deslocamento do comprimento de onda (o *redshift*) e a uma diminuição simultânea da amplitude do espectro. O OSA permitiu estabelecer relações lineares quantitativas:

* Variação do comprimento de onda em função da pressão (e.g., $0.037 \\text{ nm/kPa}$).  
* Variação da amplitude do espectro em função da pressão (e.g., $0.306 \\text{ dB/kPa}$).11

O uso de um OSA robusto é essencial para a análise do acoplamento de potência, como em sistemas complexos que combinam LPG e *Photonic Crystal Fiber* (LPG-PCF).10  
As medidas de sensibilidade, como $0.037 \\text{ nm/kPa}$, obtidas com OSAs comerciais, servem como o padrão ouro metrológico. O desenvolvimento de um interrogador espectral de baixo custo calibrado por visão computacional visa replicar essa precisão na medição do $\\lambda\_{shift}$ e da variação de amplitude. A calibração é a etapa crucial para garantir que o sistema alternativo atinja a resolução metrológica (frequentemente inferior a $0.1 \\text{ nm}$) necessária para detectar os pequenos deslocamentos induzidos pelo sensoriamento.  
Além disso, a capacidade de medição do OSA deve ser robusta em ambos os eixos (Wavelength e Amplitude). A medição simultânea do $\\lambda\_{shift}$ e da variação de amplitude permite a diferenciação e compensação de efeitos cruzados, como a distinção entre variação de tensão e temperatura, que pode ser crucial para sistemas de multiplexação.9 Uma calibração fraca na escala de intensidade (Eixo Y) comprometerá a capacidade do sensor de desvincular variáveis e compensar o ruído térmico.  
O Quadro 3.3 resume os parâmetros espectrais monitorados em sensores de fibra óptica pelo OSA de referência.  
Tabela 3.3: Parâmetros Espectrais Monitorados pelo OSA em Sensores de Fibra

| Sensor Óptico | Princípio de Sensoriamento | Parâmetro Espectral Monitorado pelo OSA | Exemplo de Sensibilidade (Referência) |
| :---- | :---- | :---- | :---- |
| FBG | Tensão, Temperatura, Pressão | Comprimento de Onda de Pico Refletido ($\\lambda\_B$ shift) | $0.037 \\text{ nm/kPa}$ (Pressão Estática) |
| LPG | Índice de Refração, Curvatura | Comprimento de Onda de Atenuação e Variação de Amplitude | Dependente da RIU e geometria (e.g., $\\text{dB/RIU}$) |
| FBG (Caracterização de Pressão) | Pressão Estática | Variação de Amplitude de Pico (Atenuação) | $0.306 \\text{ dB/kPa}$ (Pressão Estática) |

## **4\. Aplicações Transversais dos OSAs na Faixa Visível (VIS) e UV-Visível**

A importância dos OSAs transcende o laboratório de pesquisa em sensores de fibra, estendendo-se a setores de alta tecnologia, saúde e manufatura, especialmente na faixa VIS e UV-Visível.

### **4.1. Telecomunicações e Caracterização de Fontes Ópticas**

Embora as redes de telecomunicações de longa distância utilizem predominantemente bandas no Infravermelho Próximo (NIR, como as bandas C, L e O) 4, o OSA é indispensável na caracterização e manutenção de todos os componentes ópticos.

* **Multiplexação (WDM/DWDM):** Em redes de Multiplexação por Divisão de Comprimento de Onda Densa (DWDM), que dependem de espaçamento preciso, o OSA monitora a precisão do comprimento de onda para garantir que os canais estejam corretamente separados, prevenindo a interferência (*crosstalk*) e mantendo a integridade do sinal.4  
* **Qualidade do Sinal:** O OSA mede o OSNR, um parâmetro crítico para redes de longa distância que utilizam amplificação em linha.4 Também é utilizado para detectar ruído indesejado ou bandas laterais que possam degradar a qualidade do sinal.8  
* **Caracterização de Lasers/LEDs:** OSAs são essenciais para avaliar a estabilidade e a "limpeza" de uma fonte de luz, medindo parâmetros como precisão de comprimento de onda, largura espectral (*spectral width*) e a taxa de supressão de modo lateral (*Side-Mode Suppression Ratio* \- SMSR).8 Modelos de OSA de ampla faixa, como o AQ6374E, cobrem de $350 \\text{ nm}$ a $1750 \\text{ nm}$, integrando o VIS com as bandas de comunicação.12

### **4.2. Controle de Qualidade Industrial e Análise de Materiais**

OSAs e espectrofotômetros UV-Vis são vitais em P\&D e manufatura para diversos setores, incluindo segurança, análise de gases/produtos químicos, microscopia e eletrônicos de consumo.12

* **Análise de Filmes Finos:** A espectroscopia VIS é utilizada para metrologia de materiais. O OSA é empregado para medir padrões de interferência em filmes transparentes ou opacos, permitindo a determinação precisa da espessura do filme.13 O processo envolve a medição da intensidade da luz que periodicamente muda devido aos fenômenos de interferência construtiva e destrutiva.13  
* **Colorimetria e Displays:** A espectroscopia na faixa VIS é fundamental para a metrologia de cor em eletrônicos de consumo, como *displays*.12 A calibração precisa da emissão de cor e luminosidade de LEDs ou outras fontes de luz requer um OSA otimizado para a faixa VIS, como o AQ6373E ($350 \\text{ nm}$ a $1200 \\text{ nm}$).12

### **4.3. Biotecnologia, Saúde e Diagnóstico Point-of-Care (POC)**

A espectrofotometria UV-Vis é amplamente adotada em bioquímica e química para identificação e quantificação de compostos, desde que sejam cromóforos.2

* **Oximetria de Pulso:** Um exemplo proeminente da aplicação VIS/NIR é a oximetria, que mede a saturação de oxigênio na hemoglobina ($\\text{SpO}\_2$). A técnica se baseia na absorção diferencial da luz em $660 \\text{ nm}$ (visível vermelho) e $940 \\text{ nm}$ (NIR).3 O rácio das absorbâncias nestes dois comprimentos de onda específicos define o nível de oxigenação.  
* **Plataformas de Diagnóstico POC Baseadas em Smartphones:** A miniaturização da espectroscopia para plataformas de *smartphone* aproveita o flash LED (fonte, $400 \\text{ nm}$ a $700 \\text{ nm}$) e a câmera CMOS (detector) para realizar diagnósticos de baixo custo. Isso foi demonstrado na gravação do espectro de transmissão de tecido humano (dedo) e na criação de oxímetros de pulso por refletância.3

A convergência tecnológica, que transforma espectrômetros de laboratório caros em plataformas portáteis e acessíveis, gera uma demanda crítica por calibração eficiente e automática. O desenvolvimento de um método de calibração por visão computacional habilita diretamente essa transição industrial para dispositivos POC.  
No entanto, a precisão da metrologia nestes sistemas portáteis é fundamental. No caso da oximetria, um erro de *wavelength accuracy* no ponto crítico de $660 \\text{ nm}$ (região VIS) resultará em um erro de medição de absorção que será amplificado na razão ratiométrica, impactando negativamente a precisão do diagnóstico de $\\text{SpO}\_2$. Isso sublinha a natureza absolutamente crítica da calibração precisa do eixo $\\lambda$ na faixa visível, que é o foco central do TCC.  
O Quadro 4.3 resume as principais aplicações metrológicas do OSA na faixa VIS.  
Tabela 4.3: Aplicações Transversais da Espectroscopia VIS/UV-Vis e o Papel do OSA

| Domínio de Aplicação | Função Metrológica do OSA | Parâmetros Críticos Medidos | Relevância para a Faixa VIS |
| :---- | :---- | :---- | :---- |
| Industrial/Material Science | Controle de Qualidade de Produtos | Absorbância, Padrão de Interferência | Medição de espessura de filmes finos transparentes e revestimentos 13 |
| Biomédico (POC) | Diagnóstico Não Invasivo | Transmitância/Absorbância ($660 \\text{ nm}$) | Oximetria de Pulso e Espectroscopia de Tecido Humano 3 |
| Eletrônica de Consumo | Caracterização de Displays e Fontes | Distribuição de Potência Espectral | Colorimetria e Eficiência de LEDs (400–700 nm) 12 |
| Telecomunicações | Qualidade de Transmissão Óptica | Wavelength Accuracy, OSNR, SMSR | Caracterização de Lasers/LEDs de banda larga (350–1750 nm) 4 |

## **5\. Integração de Visão Computacional para Calibração de OSAs**

### **5.1. O Paralelo entre Metrologia de Bancada e Espectrômetros Baseados em Câmera CMOS**

O projeto do TCC baseia-se na premissa de que componentes de baixo custo, como a câmera CMOS de um *smartphone* e um LED, podem replicar a funcionalidade de medição de um OSA de laboratório.3 O princípio é o mesmo: a luz, após interagir com a amostra ou sensor, é dispersa (geralmente por uma grade de transmissão simples) e, em vez de atingir um detector de varredura ou um *array* de fotodiodos especializado, é capturada pelo sensor CMOS.3 O sensor CMOS, que é um detector de intensidade, torna-se o principal *array* de detecção espectral do sistema.

### **5.2. O Desafio Metrológico da Calibração no VIS**

O desafio metrológico primário em sistemas de visão é a conversão precisa dos dados de imagem (coordenada de pixel) em dados espectrais (comprimento de onda, $\\lambda$).3  
O sensor CMOS, embora otimizado para o VIS ($400 \\text{ nm}$ a $700 \\text{ nm}$) devido ao filtro IR 3, captura a informação através de uma matriz de filtros Bayer (RGB). Isso significa que a medição não é puramente espectral, mas sim uma resposta de cor que deve ser desmembrada. O processo de dispersão óptica mapeia $\\lambda$ para uma posição física no sensor ($p$). A relação entre $p$ e $\\lambda$ não é trivialmente linear e é altamente suscetível a desalinhamentos físicos da grade de difração, à temperatura e a não-uniformidades na montagem.

### **5.3. A Função Essencial da Visão Computacional**

A visão computacional é o motor que realiza a **conversão de pixel-para-wavelength**.3 Esta etapa é o cerne da calibração, transformando uma imagem de difração (dados de pixel RGB) em um espectro quantitativo (Intensidade vs. $\\lambda$).  
Os métodos de calibração por visão geralmente envolvem:

1. **Localização Geométrica:** Uso de algoritmos de processamento de imagem para identificar e isolar a linha de difração na imagem.3  
2. **Mapeamento Espectral:** Utilização de fontes de calibração de referência (e.g., lâmpadas de vapor ou LEDs de pico estreito com comprimentos de onda conhecidos) para criar uma função de mapeamento (tipicamente um ajuste polinomial) entre a coordenada do pixel e o comprimento de onda conhecido.  
3. **Processamento de Dados:** Conversão digital da imagem e extração da curva quantitativa de intensidade vs. comprimento de onda.3

Ao contrário dos OSAs tradicionais, que garantem a precisão através de componentes ópticos e eletrônicos caros (monocromadores de alta qualidade, arquiteturas de feixe duplo) 1, o método do TCC utiliza software (visão computacional) para compensar as deficiências inerentes ao hardware óptico de baixo custo, como desalinhamentos na montagem ou não-linearidades introduzidas por lentes simples. Essa abordagem representa uma **mudança de paradigma metrológico**, onde a garantia de precisão migra da engenharia óptica de *hardware* para a engenharia algorítmica de *software*.

### **5.4. Vantagens Estratégicas e o Objetivo Final do TCC**

A calibração por visão computacional tem vantagens estratégicas importantes:

* **Correção de Não-Linearidades e Acessibilidade:** O algoritmo pode corrigir as distorções e não-uniformidades da resposta espectral do sensor CMOS, permitindo que dispositivos acessíveis se tornem instrumentos espectrais precisos, viabilizando plataformas de diagnóstico *in-situ* e *Point-of-Care* (POC) em ambientes com recursos limitados.3  
* **Atingindo a Resolução Metrológica:** O teste final da calibração reside na sua capacidade de atingir a precisão necessária para aplicações críticas. Para a metrologia de sensores de fibra, o sistema deve ser capaz de detectar deslocamentos minúsculos (e.g., $\\Delta\\lambda \< 0.1 \\text{ nm}$).11 A câmera CMOS oferece alta resolução espacial (muitos pixels), mas é o algoritmo de visão que deve traduzir essa resolução espacial em uma **alta resolução espectral eficaz**. O sucesso do TCC será, portanto, medido pela capacidade da calibração via visão computacional de produzir uma *resolução de comprimento de onda eficaz* que seja comparável à de um OSA comercial, validando a nova metodologia como um interrogador viável para a detecção precisa de eventos de sensoriamento de baixa amplitude (nm/kPa).

## **Conclusões**

O Analisador de Espectro Óptico na faixa visível (OSA-VIS) é uma ferramenta indispensável para a metrologia moderna. Sua aplicação se estende desde a caracterização fundamental de sensores de fibra óptica, como LPGs e FBGs (onde quantifica a sensibilidade em termos de deslocamento de comprimento de onda e variação de amplitude com precisões da ordem de $0.037 \\text{ nm/kPa}$) 11, até aplicações industriais (colorimetria, filmes finos) e biomédicas (oximetria, diagnósticos POC).3  
A necessidade de precisão na faixa visível é crítica, especialmente em medições ratiométricas como a oximetria de pulso, onde um erro mínimo na calibração do comprimento de onda (eixo $\\lambda$) pode levar a erros diagnósticos significativos.  
O TCC, ao desenvolver um processo de calibração por visão computacional para espectrômetros de baixo custo, está abordando diretamente a necessidade tecnológica de migrar a garantia de precisão do *hardware* de bancada para o *software* algorítmico. O foco deste trabalho deve ser o desenvolvimento de um algoritmo de calibração robusto que seja capaz de corrigir as não-linearidades e imperfeições inerentes aos componentes de consumo (CMOS e LEDs), garantindo que a **resolução de comprimento de onda eficaz** do sistema atinja o rigor metrológico exigido para a pesquisa em sensores ópticos. A validação bem-sucedida dessa calibração estabeleceria o sistema de visão computacional como um interrogador espectral viável e acessível.

#### **Works cited**

1. The Basics of UV-Vis Spectroscopy \- Agilent, accessed November 3, 2025, [https://www.agilent.com/cs/library/primers/public/primer-uv-vis-basics-5980-1397en-agilent.pdf](https://www.agilent.com/cs/library/primers/public/primer-uv-vis-basics-5980-1397en-agilent.pdf)  
2. Ultraviolet–visible spectroscopy \- Wikipedia, accessed November 3, 2025, [https://en.wikipedia.org/wiki/Ultraviolet%E2%80%93visible\_spectroscopy](https://en.wikipedia.org/wiki/Ultraviolet%E2%80%93visible_spectroscopy)  
3. Smartphone-based optical spectroscopic platforms for biomedical ..., accessed November 3, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC8086480/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8086480/)  
4. Optical Spectrum Analyzers (OSA) | VIAVI Solutions Inc., accessed November 3, 2025, [https://www.viavisolutions.com/en-us/products/optical-spectrum-analyzers-osa](https://www.viavisolutions.com/en-us/products/optical-spectrum-analyzers-osa)  
5. EXPERIMENTAL CHARACTERIZATION OF THE OPTICAL FIBER, accessed November 3, 2025, [https://www.scientificbulletin.upb.ro/rev\_docs\_arhiva/full04f\_672529.pdf](https://www.scientificbulletin.upb.ro/rev_docs_arhiva/full04f_672529.pdf)  
6. Reflection spectrum of the SCFBG measured by an OSA. \- ResearchGate, accessed November 3, 2025, [https://www.researchgate.net/figure/Reflection-spectrum-of-the-SCFBG-measured-by-an-OSA\_fig4\_23140819](https://www.researchgate.net/figure/Reflection-spectrum-of-the-SCFBG-measured-by-an-OSA_fig4_23140819)  
7. Optical Spectrum Analyzers \- Thorlabs, accessed November 3, 2025, [https://www.thorlabs.com/newgrouppage9.cfm?objectgroup\_id=5276](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=5276)  
8. Optical Spectrum Analyzer: Applications, Benefits, And Top Models \- Tomarok Engineering, accessed November 3, 2025, [https://tomarok.com/optical-spectrum-analyzer/](https://tomarok.com/optical-spectrum-analyzer/)  
9. Optical Fiber Based Temperature Sensors: A Review \- MDPI, accessed November 3, 2025, [https://www.mdpi.com/2673-3269/4/1/13](https://www.mdpi.com/2673-3269/4/1/13)  
10. Simultaneous measurement of refractive index and temperature, accessed November 3, 2025, [https://pubs.aip.org/aip/rsi/article/84/7/075004/360460/Simultaneous-measurement-of-refractive-index-and](https://pubs.aip.org/aip/rsi/article/84/7/075004/360460/Simultaneous-measurement-of-refractive-index-and)  
11. High-Resolution FBG-Based Fiber-Optic Sensor with Temperature ..., accessed November 3, 2025, [https://www.mdpi.com/1424-8220/19/23/5285](https://www.mdpi.com/1424-8220/19/23/5285)  
12. Optical Spectrum Analyzer \- keith Electronics, accessed November 3, 2025, [https://keithelectronics.com/optical-spectrum-analyzer/](https://keithelectronics.com/optical-spectrum-analyzer/)  
13. A Miniaturized and Fast System for Thin Film Thickness Measurement \- MDPI, accessed November 3, 2025, [https://www.mdpi.com/2076-3417/10/20/7284](https://www.mdpi.com/2076-3417/10/20/7284)  
14. Application Note: Thickness Measurements of Opaque and Transparent Films or Coatings with WLI | Bruker, accessed November 3, 2025, [https://www.bruker.com/en/products-and-solutions/test-and-measurement/3d-optical-profilers/resource-library/an-583-thickness-measurements-of-opaque-and-transparent-films-or-coatings-with-wli.html](https://www.bruker.com/en/products-and-solutions/test-and-measurement/3d-optical-profilers/resource-library/an-583-thickness-measurements-of-opaque-and-transparent-films-or-coatings-with-wli.html)