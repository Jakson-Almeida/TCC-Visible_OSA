# TCC-Visible_OSA

## Sobre o Projeto

Este é um projeto de Trabalho de Conclusão de Curso (TCC) focado no desenvolvimento de um **Analisador de Espectro Óptico (OSA) de baixo custo** para a faixa visível do espectro eletromagnético.

## Descrição

O projeto apresenta o desenvolvimento de um Analisador de Espectro Óptico (OSA) de baixo custo para espectros de luz visível (380-750 nm), combinando um espectrômetro impresso em 3D ("Osinha") e um software customizado ("OSA Visível"). O processo de calibração emprega técnicas de visão computacional para mapear a relação comprimento de onda-posição de pixel.

## Objetivos

- [x] Desenvolver espectrômetro 3D-printed de baixo custo
- [x] Implementar software "OSA Visível" para análise espectral
- [x] Calibração automatizada via visão computacional
- [x] Reduzir custos de $30.000+ (OSA comercial) para menos de $200
- [x] Alcançar precisão de calibração de ±2 nm
- [ ] Interface intuitiva para visualização em tempo real
- [ ] Exportação de dados para análise

## Tecnologias

- **Hardware**: Espectrômetro 3D-printed "Osinha"
- **Software**: Python com OpenCV e Pillow
- **Visão Computacional**: Cálculo de centróide, thresholding de intensidade
- **Calibração**: Regressão linear para mapeamento comprimento de onda-pixel
- **Fontes de Luz**: Luz branca e lasers (532 nm e 650 nm)

## Metodologia

1. **Calibração**: Utilização de fontes de luz conhecidas (luz branca e lasers)
2. **Processamento de Imagem**: Técnicas de visão computacional para análise espectral
3. **Mapeamento**: Relação comprimento de onda-posição de pixel via regressão linear
4. **Validação**: Experimentos com fontes de luz controladas

## Aplicações

- Análise espectral educacional
- Pesquisa em óptica
- Desenvolvimento de soluções de baixo custo para laboratórios
- Democratização do acesso à análise espectral

## Estrutura do Projeto

```
TCC-Visible_OSA/
├── README.md
├── docs/           # Documentação do projeto
├── src/            # Código fonte do software "OSA Visível"
├── data/           # Dados de calibração e espectros
├── tests/          # Testes automatizados
└── requirements.txt # Dependências Python
```

## Como Executar

*Em desenvolvimento...*

## Contribuição

Este é um projeto acadêmico desenvolvido como parte do TCC.

## Autores

**Jakson Almeida** - Faculdade de Engenharia Elétrica, Universidade Federal de Juiz de Fora, MG
- Email: jakson.almeida@estudante.ufjf.br

## Licença

Este projeto está sob licença acadêmica para fins educacionais.

---

*Última atualização: Janeiro 2025*
