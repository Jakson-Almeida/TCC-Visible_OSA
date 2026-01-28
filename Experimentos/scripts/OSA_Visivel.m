% OSA_Visivel.m
% Script para análise dos dados do OSA Visível
% Gera gráficos de Intensidade vs Duty Cycle para cada cor (Verde, Vermelho, Azul)
%
% Autor: Análise de dados experimentais
% Data: 2026-01-28

clear; close all; clc;

%% Configurações
% Caminho do arquivo CSV
csv_file = 'dados_osa_visivel_2026-01-28T20-11-25.773Z.csv';

% Verificar se o arquivo existe
if ~exist(csv_file, 'file')
    error('Arquivo CSV não encontrado: %s', csv_file);
end

%% Leitura dos dados
fprintf('Lendo dados de: %s\n', csv_file);

% Ler o arquivo CSV
% O MATLAB pode ter problemas com aspas, então vamos ler como texto primeiro
fid = fopen(csv_file, 'r');
if fid == -1
    error('Não foi possível abrir o arquivo: %s', csv_file);
end

% Ler cabeçalho
header_line = fgetl(fid);
headers = strsplit(header_line, ',');

% Remover aspas dos cabeçalhos
for i = 1:length(headers)
    headers{i} = strrep(headers{i}, '"', '');
end

% Ler dados
data_lines = {};
line_count = 0;
while ~feof(fid)
    line = fgetl(fid);
    if ischar(line) && ~isempty(line)
        line_count = line_count + 1;
        data_lines{line_count} = line;
    end
end
fclose(fid);

% Processar dados
num_rows = length(data_lines);
duty_cycle = zeros(num_rows, 1);
green_intensity = zeros(num_rows, 1);
red_intensity = zeros(num_rows, 1);
blue_intensity = zeros(num_rows, 1);

for i = 1:num_rows
    % Separar valores por vírgula
    values = strsplit(data_lines{i}, ',');
    
    % Remover aspas e converter para números
    duty_cycle(i) = str2double(strrep(values{1}, '"', ''));
    green_intensity(i) = str2double(strrep(values{3}, '"', ''));  % Coluna 3: Green_intensity
    red_intensity(i) = str2double(strrep(values{5}, '"', ''));    % Coluna 5: Red_intensity
    blue_intensity(i) = str2double(strrep(values{7}, '"', ''));    % Coluna 7: Blue_intensity
end

fprintf('Dados carregados: %d pontos\n', num_rows);

%% Criar gráficos
% Configurações de figura
figure('Position', [100, 100, 1200, 400]);
set(gcf, 'Color', 'white');

% Cores para os gráficos
color_green = [0.2, 0.8, 0.2];   % Verde
color_red = [0.9, 0.2, 0.2];     % Vermelho
color_blue = [0.2, 0.4, 0.9];    % Azul

% Gráfico 1: Verde
subplot(1, 3, 1);
plot(duty_cycle, green_intensity, 'o-', 'Color', color_green, ...
     'LineWidth', 2, 'MarkerSize', 6, 'MarkerFaceColor', color_green);
xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
title('LED Verde - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
grid on;
xlim([0, 105]);
set(gca, 'FontSize', 10);

% Gráfico 2: Vermelho
subplot(1, 3, 2);
plot(duty_cycle, red_intensity, 'o-', 'Color', color_red, ...
     'LineWidth', 2, 'MarkerSize', 6, 'MarkerFaceColor', color_red);
xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
title('LED Vermelho - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
grid on;
xlim([0, 105]);
set(gca, 'FontSize', 10);

% Gráfico 3: Azul
subplot(1, 3, 3);
plot(duty_cycle, blue_intensity, 'o-', 'Color', color_blue, ...
     'LineWidth', 2, 'MarkerSize', 6, 'MarkerFaceColor', color_blue);
xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
title('LED Azul - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
grid on;
xlim([0, 105]);
set(gca, 'FontSize', 10);

% Ajustar layout
sgtitle('OSA Visível - Análise de Intensidade por Duty Cycle', ...
        'FontSize', 14, 'FontWeight', 'bold');

% Salvar figura
output_file = 'OSA_Visivel_intensidade_vs_dutycycle.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico salvo em: %s\n', output_file);

%% Estatísticas básicas
fprintf('\n=== Estatísticas ===\n');
fprintf('Verde:\n');
fprintf('  Média: %.2f\n', mean(green_intensity));
fprintf('  Desvio padrão: %.2f\n', std(green_intensity));
fprintf('  Mínimo: %.2f (Duty Cycle: %.0f%%)\n', min(green_intensity), duty_cycle(green_intensity == min(green_intensity)));
fprintf('  Máximo: %.2f (Duty Cycle: %.0f%%)\n', max(green_intensity), duty_cycle(green_intensity == max(green_intensity)));

fprintf('\nVermelho:\n');
fprintf('  Média: %.2f\n', mean(red_intensity));
fprintf('  Desvio padrão: %.2f\n', std(red_intensity));
fprintf('  Mínimo: %.2f (Duty Cycle: %.0f%%)\n', min(red_intensity), duty_cycle(red_intensity == min(red_intensity)));
fprintf('  Máximo: %.2f (Duty Cycle: %.0f%%)\n', max(red_intensity), duty_cycle(red_intensity == max(red_intensity)));

fprintf('\nAzul:\n');
fprintf('  Média: %.2f\n', mean(blue_intensity));
fprintf('  Desvio padrão: %.2f\n', std(blue_intensity));
fprintf('  Mínimo: %.2f (Duty Cycle: %.0f%%)\n', min(blue_intensity), duty_cycle(blue_intensity == min(blue_intensity)));
fprintf('  Máximo: %.2f (Duty Cycle: %.0f%%)\n', max(blue_intensity), duty_cycle(blue_intensity == max(blue_intensity)));

fprintf('\nAnálise concluída!\n');
