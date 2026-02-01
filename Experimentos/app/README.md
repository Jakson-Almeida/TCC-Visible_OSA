# Cadastro de dados do experimento (HTML + CSS + JS)

Página para preenchimento das tabelas de **Duty Cycle**, **comprimento de onda de pico (λ)** e **intensidade** dos LEDs verde, vermelho e azul, para os equipamentos **OSA Visível** e **ThorLabs**.

## Configuração da nova versão

- **Duty Cycle:** 1, 2, 3, …, 10%.
- **Equipamentos:** OSA Visível e ThorLabs, cada um com **5 tomadas** (repetições do experimento).
- **ThorLabs:** uma tabela por tomada (5 tabelas no total).
- **OSA Visível:** **4 tabelas por tomada** (20 tabelas no total), pois os dados passaram a vir de espectros separados:
  - **Combinado RGB** (espectro combinado);
  - **Canal R**, **Canal G** e **Canal B** (espectros extraídos e filtrados por canal da câmera do OSA Visível).

Antes os dados do OSA Visível vinham de um único espectro RGB; agora são 4 espectros por tomada (combinado + 3 canais).

## Uso

1. Abra `index.html` no navegador.
2. Escolha o equipamento (OSA Visível ou ThorLabs).
3. Selecione a **tomada** (1 a 5). No OSA Visível, selecione também o **espectro** (Combinado, Canal R, Canal G, Canal B).
4. Preencha λ de pico (nm) e intensidade para cada Duty Cycle e cada cor (verde, vermelho, azul).

## Observações

- Os dados são **salvos automaticamente** no navegador (localStorage).
- **Exportar CSV (tabela atual):** baixa a tabela visível (tomada e, no OSA, espectro atuais).
- **Exportar JSON (tudo):** baixa todos os dados (todas as tomadas e espectros).
- **Importar JSON:** restaura um backup em JSON (formato v2).
- **Limpar dados (equipamento atual):** apaga todas as tomadas (e espectros, no OSA) do equipamento selecionado.
