% analise_json_com_ajuste.m
% Script para análise dos dados do JSON com ajuste de reta linear
% Analisa ThorLabs (5 tomadas) e OSA Visível (por canal: RGB, R, G, B)
% Ajusta a melhor reta (regressão linear) para cada análise
%
% Autor: Jakson Almeida
% Data: 2026-02-01

clear; close all; clc;

%% Configurações
% Caminho do arquivo JSON
json_file = 'dados_todos_2026-02-01T21-04-19.765Z.json';

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

% Ajuste de reta para ThorLabs
% Verde
[p_green, S_green] = polyfit(duty_cycles, thorlabs_green_mean, 1);
[y_fit_green, delta_green] = polyval(p_green, duty_cycles, S_green);
R2_green = calcular_r2(thorlabs_green_mean, y_fit_green);

% Vermelho
[p_red, S_red] = polyfit(duty_cycles, thorlabs_red_mean, 1);
[y_fit_red, delta_red] = polyval(p_red, duty_cycles, S_red);
R2_red = calcular_r2(thorlabs_red_mean, y_fit_red);

% Azul
[p_blue, S_blue] = polyfit(duty_cycles, thorlabs_blue_mean, 1);
[y_fit_blue, delta_blue] = polyval(p_blue, duty_cycles, S_blue);
R2_blue = calcular_r2(thorlabs_blue_mean, y_fit_blue);

% Exibir parâmetros do ajuste
fprintf('\nThorLabs - Parâmetros do ajuste linear:\n');
fprintf('  Verde:    y = %.2fx + %.2f  (R² = %.4f)\n', p_green(1), p_green(2), R2_green);
fprintf('  Vermelho: y = %.2fx + %.2f  (R² = %.4f)\n', p_red(1), p_red(2), R2_red);
fprintf('  Azul:     y = %.2fx + %.2f  (R² = %.4f)\n', p_blue(1), p_blue(2), R2_blue);

% Plotar ThorLabs
figure('Position', [100, 100, 1200, 400]);
set(gcf, 'Color', 'white');

color_green = [0.2, 0.8, 0.2];
color_red = [0.9, 0.2, 0.2];
color_blue = [0.2, 0.4, 0.9];

% Gráfico 1: Verde
subplot(1, 3, 1);
hold on;
errorbar(duty_cycles, thorlabs_green_mean, thorlabs_green_std, 'o', ...
    'Color', color_green, 'LineWidth', 1.5, 'MarkerSize', 6, ...
    'MarkerFaceColor', color_green);
plot(duty_cycles, y_fit_green, '-', 'Color', color_green, 'LineWidth', 2);
xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
title('LED Verde - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
text(1.5, max(thorlabs_green_mean)*0.9, ...
    sprintf('y = %.2fx + %.2f\nR² = %.4f', p_green(1), p_green(2), R2_green), ...
    'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');
grid on;
xlim([0, 11]);
set(gca, 'FontSize', 10);
hold off;

% Gráfico 2: Vermelho
subplot(1, 3, 2);
hold on;
errorbar(duty_cycles, thorlabs_red_mean, thorlabs_red_std, 'o', ...
    'Color', color_red, 'LineWidth', 1.5, 'MarkerSize', 6, ...
    'MarkerFaceColor', color_red);
plot(duty_cycles, y_fit_red, '-', 'Color', color_red, 'LineWidth', 2);
xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
title('LED Vermelho - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
text(1.5, max(thorlabs_red_mean)*0.9, ...
    sprintf('y = %.2fx + %.2f\nR² = %.4f', p_red(1), p_red(2), R2_red), ...
    'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');
grid on;
xlim([0, 11]);
set(gca, 'FontSize', 10);
hold off;

% Gráfico 3: Azul
subplot(1, 3, 3);
hold on;
errorbar(duty_cycles, thorlabs_blue_mean, thorlabs_blue_std, 'o', ...
    'Color', color_blue, 'LineWidth', 1.5, 'MarkerSize', 6, ...
    'MarkerFaceColor', color_blue);
plot(duty_cycles, y_fit_blue, '-', 'Color', color_blue, 'LineWidth', 2);
xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
title('LED Azul - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
text(1.5, max(thorlabs_blue_mean)*0.9, ...
    sprintf('y = %.2fx + %.2f\nR² = %.4f', p_blue(1), p_blue(2), R2_blue), ...
    'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');
grid on;
xlim([0, 11]);
set(gca, 'FontSize', 10);
hold off;

sgtitle('ThorLabs - Média de 5 Tomadas com Ajuste Linear', 'FontSize', 14, 'FontWeight', 'bold');

% Salvar figura
output_file = 'ThorLabs_JSON_ajuste_linear.png';
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
    
    % Encontrar índices válidos (não NaN)
    valid_green = ~isnan(osa_green_mean);
    valid_red = ~isnan(osa_red_mean);
    valid_blue = ~isnan(osa_blue_mean);
    
    % Ajuste de reta para OSA Visível (apenas pontos válidos)
    % Verde
    if sum(valid_green) >= 2
        [p_osa_green, S_osa_green] = polyfit(duty_cycles(valid_green), osa_green_mean(valid_green), 1);
        [y_fit_osa_green, ~] = polyval(p_osa_green, duty_cycles(valid_green), S_osa_green);
        R2_osa_green = calcular_r2(osa_green_mean(valid_green), y_fit_osa_green);
    else
        p_osa_green = [NaN, NaN];
        y_fit_osa_green = [];
        R2_osa_green = NaN;
    end
    
    % Vermelho
    if sum(valid_red) >= 2
        [p_osa_red, S_osa_red] = polyfit(duty_cycles(valid_red), osa_red_mean(valid_red), 1);
        [y_fit_osa_red, ~] = polyval(p_osa_red, duty_cycles(valid_red), S_osa_red);
        R2_osa_red = calcular_r2(osa_red_mean(valid_red), y_fit_osa_red);
    else
        p_osa_red = [NaN, NaN];
        y_fit_osa_red = [];
        R2_osa_red = NaN;
    end
    
    % Azul
    if sum(valid_blue) >= 2
        [p_osa_blue, S_osa_blue] = polyfit(duty_cycles(valid_blue), osa_blue_mean(valid_blue), 1);
        [y_fit_osa_blue, ~] = polyval(p_osa_blue, duty_cycles(valid_blue), S_osa_blue);
        R2_osa_blue = calcular_r2(osa_blue_mean(valid_blue), y_fit_osa_blue);
    else
        p_osa_blue = [NaN, NaN];
        y_fit_osa_blue = [];
        R2_osa_blue = NaN;
    end
    
    % Exibir parâmetros do ajuste
    fprintf('\n  %s - Parâmetros do ajuste linear:\n', tipo_nome);
    if ~isnan(p_osa_green(1))
        fprintf('    Verde:    y = %.2fx + %.2f  (R² = %.4f)\n', p_osa_green(1), p_osa_green(2), R2_osa_green);
    else
        fprintf('    Verde:    Dados insuficientes\n');
    end
    if ~isnan(p_osa_red(1))
        fprintf('    Vermelho: y = %.2fx + %.2f  (R² = %.4f)\n', p_osa_red(1), p_osa_red(2), R2_osa_red);
    else
        fprintf('    Vermelho: Dados insuficientes\n');
    end
    if ~isnan(p_osa_blue(1))
        fprintf('    Azul:     y = %.2fx + %.2f  (R² = %.4f)\n', p_osa_blue(1), p_osa_blue(2), R2_osa_blue);
    else
        fprintf('    Azul:     Dados insuficientes\n');
    end
    
    % Plotar OSA Visível
    figure('Position', [100, 100, 1200, 400]);
    set(gcf, 'Color', 'white');
    
    % Gráfico 1: Verde
    subplot(1, 3, 1);
    hold on;
    errorbar(duty_cycles, osa_green_mean, osa_green_std, 'o', ...
        'Color', color_green, 'LineWidth', 1.5, 'MarkerSize', 6, ...
        'MarkerFaceColor', color_green);
    if sum(valid_green) >= 2
        plot(duty_cycles(valid_green), y_fit_osa_green, '-', 'Color', color_green, 'LineWidth', 2);
        text(1.5, max(osa_green_mean(valid_green))*0.9, ...
            sprintf('y = %.2fx + %.2f\nR² = %.4f', p_osa_green(1), p_osa_green(2), R2_osa_green), ...
            'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');
    end
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    title('LED Verde - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
    grid on;
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    hold off;
    
    % Gráfico 2: Vermelho
    subplot(1, 3, 2);
    hold on;
    errorbar(duty_cycles, osa_red_mean, osa_red_std, 'o', ...
        'Color', color_red, 'LineWidth', 1.5, 'MarkerSize', 6, ...
        'MarkerFaceColor', color_red);
    if sum(valid_red) >= 2
        plot(duty_cycles(valid_red), y_fit_osa_red, '-', 'Color', color_red, 'LineWidth', 2);
        text(1.5, max(osa_red_mean(valid_red))*0.9, ...
            sprintf('y = %.2fx + %.2f\nR² = %.4f', p_osa_red(1), p_osa_red(2), R2_osa_red), ...
            'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');
    end
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    title('LED Vermelho - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
    grid on;
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    hold off;
    
    % Gráfico 3: Azul
    subplot(1, 3, 3);
    hold on;
    errorbar(duty_cycles, osa_blue_mean, osa_blue_std, 'o', ...
        'Color', color_blue, 'LineWidth', 1.5, 'MarkerSize', 6, ...
        'MarkerFaceColor', color_blue);
    if sum(valid_blue) >= 2
        plot(duty_cycles(valid_blue), y_fit_osa_blue, '-', 'Color', color_blue, 'LineWidth', 2);
        text(1.5, max(osa_blue_mean(valid_blue))*0.9, ...
            sprintf('y = %.2fx + %.2f\nR² = %.4f', p_osa_blue(1), p_osa_blue(2), R2_osa_blue), ...
            'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');
    end
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    title('LED Azul - Intensidade vs Duty Cycle', 'FontSize', 12, 'FontWeight', 'bold');
    grid on;
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    hold off;
    
    % Título geral
    tipo_nome_safe = strrep(tipo_nome, ' ', '_');
    sgtitle(sprintf('OSA Visível - %s (Média de 5 Tomadas com Ajuste Linear)', tipo_nome), ...
        'FontSize', 14, 'FontWeight', 'bold');
    
    % Salvar figura
    output_file = sprintf('OSA_Visivel_%s_JSON_ajuste_linear.png', tipo_nome_safe);
    print(output_file, '-dpng', '-r300');
    fprintf('  Gráfico salvo em: %s\n', output_file);
end

fprintf('\n=== Análise concluída! ===\n');

%% Função auxiliar para calcular R²
function R2 = calcular_r2(y_obs, y_pred)
    % Calcula o coeficiente de determinação R²
    % R² = 1 - (SS_res / SS_tot)
    % onde SS_res = soma dos quadrados dos resíduos
    %      SS_tot = soma total dos quadrados
    
    SS_res = sum((y_obs - y_pred).^2);
    SS_tot = sum((y_obs - mean(y_obs)).^2);
    
    R2 = 1 - (SS_res / SS_tot);
end
