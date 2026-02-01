% analise_json.m
% Script para análise dos dados do JSON gerado automaticamente
% Analisa ThorLabs (5 tomadas) e OSA Visível (por canal: RGB, R, G, B)
%
% Autor: Jakson Almeida
% Data: 2026-02-01

clear; close all; clc;

%% Configurações
% Caminho do arquivo JSON
json_file = 'dados_todos_2026-02-01T21-23-25.372Z.json';

% Verificar se o arquivo existe
if ~exist(json_file, 'file')
    error('Arquivo JSON não encontrado: %s', json_file);
end

%% Leitura do JSON
fprintf('Lendo dados de: %s\n', json_file);
json_text = fileread(json_file);
data = jsondecode(json_text);

%% Processar ThorLabs (5 tomadas)
fprintf('\n=== Processando ThorLabs ===\n');

% Inicializar arrays para médias das 5 tomadas
duty_cycles = 1:10;
thorlabs_green = zeros(5, 10);  % 5 tomadas x 10 duty cycles
thorlabs_red = zeros(5, 10);
thorlabs_blue = zeros(5, 10);

% Coletar dados de cada tomada
for tomada = 1:5
    tomada_str = sprintf('x%d', tomada);
    tomada_data = data.data.thorlabs.(tomada_str);
    
    for dc = 1:10
        dc_str = sprintf('x%d', dc);
        dc_data = tomada_data.(dc_str);
        
        thorlabs_green(tomada, dc) = str2double(dc_data.green.intensity);
        thorlabs_red(tomada, dc) = str2double(dc_data.red.intensity);
        thorlabs_blue(tomada, dc) = str2double(dc_data.blue.intensity);
    end
end

% Calcular médias e desvios padrão
thorlabs_green_mean = mean(thorlabs_green, 1);
thorlabs_green_std = std(thorlabs_green, 0, 1);
thorlabs_red_mean = mean(thorlabs_red, 1);
thorlabs_red_std = std(thorlabs_red, 0, 1);
thorlabs_blue_mean = mean(thorlabs_blue, 1);
thorlabs_blue_std = std(thorlabs_blue, 0, 1);

% Plotar ThorLabs
figure('Position', [100, 100, 1200, 400]);
set(gcf, 'Color', 'white');

color_green = [0.2, 0.8, 0.2];
color_red = [0.9, 0.2, 0.2];
color_blue = [0.2, 0.4, 0.9];

% Gráfico 1: Verde
subplot(1, 3, 1);
errorbar(duty_cycles, thorlabs_green_mean, thorlabs_green_std, 'o-', ...
    'Color', color_green, 'LineWidth', 2, 'MarkerSize', 6, ...
    'MarkerFaceColor', color_green);
xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
title('LED Verde - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
grid on;
xlim([0, 11]);
set(gca, 'FontSize', 10);

% Gráfico 2: Vermelho
subplot(1, 3, 2);
errorbar(duty_cycles, thorlabs_red_mean, thorlabs_red_std, 'o-', ...
    'Color', color_red, 'LineWidth', 2, 'MarkerSize', 6, ...
    'MarkerFaceColor', color_red);
xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
title('LED Vermelho - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
grid on;
xlim([0, 11]);
set(gca, 'FontSize', 10);

% Gráfico 3: Azul
subplot(1, 3, 3);
errorbar(duty_cycles, thorlabs_blue_mean, thorlabs_blue_std, 'o-', ...
    'Color', color_blue, 'LineWidth', 2, 'MarkerSize', 6, ...
    'MarkerFaceColor', color_blue);
xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
title('LED Azul - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
grid on;
xlim([0, 11]);
set(gca, 'FontSize', 10);

sgtitle('ThorLabs - Média de 5 Tomadas', 'FontSize', 14, 'FontWeight', 'bold');

% Salvar figura
output_file = 'ThorLabs_JSON_intensidade_vs_dutycycle.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico ThorLabs salvo em: %s\n', output_file);

%% Processar OSA Visível por canal
fprintf('\n=== Processando OSA Visível ===\n');

% Tipos de canal
canal_tipos = {'x1', 'x2', 'x3', 'x4'};  % RGB, R, G, B
canal_nomes = {'RGB (Todos os Canais)', 'Canal R', 'Canal G', 'Canal B'};

for tipo_idx = 1:length(canal_tipos)
    tipo = canal_tipos{tipo_idx};
    tipo_nome = canal_nomes{tipo_idx};
    
    fprintf('\nProcessando: %s\n', tipo_nome);
    
    % Inicializar arrays para médias das 5 tomadas
    osa_green = zeros(5, 10);
    osa_red = zeros(5, 10);
    osa_blue = zeros(5, 10);
    
    % Coletar dados de cada tomada
    for tomada = 1:5
        tomada_str = sprintf('x%d', tomada);
        
        % Verificar se a tomada existe
        if ~isfield(data.data.osa_visivel, tomada_str)
            fprintf('  Aviso: Tomada %d não encontrada\n', tomada);
            continue;
        end
        
        tomada_data = data.data.osa_visivel.(tomada_str);
        
        % Verificar se o tipo existe
        if ~isfield(tomada_data, tipo)
            fprintf('  Aviso: Tipo %s não encontrado na tomada %d\n', tipo, tomada);
            continue;
        end
        
        tipo_data = tomada_data.(tipo);
        
        for dc = 1:10
            dc_str = sprintf('x%d', dc);
            
            if isfield(tipo_data, dc_str)
                dc_data = tipo_data.(dc_str);
                
                % Converter valores, tratando strings vazias
                if ~isempty(dc_data.green.intensity) && ischar(dc_data.green.intensity)
                    osa_green(tomada, dc) = str2double(dc_data.green.intensity);
                else
                    osa_green(tomada, dc) = NaN;
                end
                
                if ~isempty(dc_data.red.intensity) && ischar(dc_data.red.intensity)
                    osa_red(tomada, dc) = str2double(dc_data.red.intensity);
                else
                    osa_red(tomada, dc) = NaN;
                end
                
                if ~isempty(dc_data.blue.intensity) && ischar(dc_data.blue.intensity)
                    osa_blue(tomada, dc) = str2double(dc_data.blue.intensity);
                else
                    osa_blue(tomada, dc) = NaN;
                end
            end
        end
    end
    
    % Calcular médias e desvios padrão (ignorando NaN)
    osa_green_mean = mean(osa_green, 1, 'omitnan');
    osa_green_std = std(osa_green, 0, 1, 'omitnan');
    osa_red_mean = mean(osa_red, 1, 'omitnan');
    osa_red_std = std(osa_red, 0, 1, 'omitnan');
    osa_blue_mean = mean(osa_blue, 1, 'omitnan');
    osa_blue_std = std(osa_blue, 0, 1, 'omitnan');
    
    % Plotar OSA Visível
    figure('Position', [100, 100, 1200, 400]);
    set(gcf, 'Color', 'white');
    
    % Gráfico 1: Verde
    subplot(1, 3, 1);
    errorbar(duty_cycles, osa_green_mean, osa_green_std, 'o-', ...
        'Color', color_green, 'LineWidth', 2, 'MarkerSize', 6, ...
        'MarkerFaceColor', color_green);
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    title('LED Verde - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
    grid on;
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    
    % Gráfico 2: Vermelho
    subplot(1, 3, 2);
    errorbar(duty_cycles, osa_red_mean, osa_red_std, 'o-', ...
        'Color', color_red, 'LineWidth', 2, 'MarkerSize', 6, ...
        'MarkerFaceColor', color_red);
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    title('LED Vermelho - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
    grid on;
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    
    % Gráfico 3: Azul
    subplot(1, 3, 3);
    errorbar(duty_cycles, osa_blue_mean, osa_blue_std, 'o-', ...
        'Color', color_blue, 'LineWidth', 2, 'MarkerSize', 6, ...
        'MarkerFaceColor', color_blue);
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    title('LED Azul - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
    grid on;
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    
    % Título geral
    tipo_nome_safe = strrep(tipo_nome, ' ', '_');
    sgtitle(sprintf('OSA Visível - %s (Média de 5 Tomadas)', tipo_nome), ...
        'FontSize', 14, 'FontWeight', 'bold');
    
    % Salvar figura
    output_file = sprintf('OSA_Visivel_%s_JSON_intensidade_vs_dutycycle.png', tipo_nome_safe);
    print(output_file, '-dpng', '-r300');
    fprintf('Gráfico salvo em: %s\n', output_file);
    
    % Estatísticas
    fprintf('\n  Estatísticas para %s:\n', tipo_nome);
    fprintf('  Verde - Média: %.2f, Desvio: %.2f\n', ...
        mean(osa_green_mean, 'omitnan'), mean(osa_green_std, 'omitnan'));
    fprintf('  Vermelho - Média: %.2f, Desvio: %.2f\n', ...
        mean(osa_red_mean, 'omitnan'), mean(osa_red_std, 'omitnan'));
    fprintf('  Azul - Média: %.2f, Desvio: %.2f\n', ...
        mean(osa_blue_mean, 'omitnan'), mean(osa_blue_std, 'omitnan'));
end

fprintf('\n=== Análise concluída! ===\n');
