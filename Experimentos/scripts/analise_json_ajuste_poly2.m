% analise_json_ajuste_poly2.m
% Script para análise dos dados do JSON com ajuste misto
% - ThorLabs: Ajuste linear para todos
% - OSA Visível canais RGB e R: Polinômio grau 2 para VERMELHO, linear para verde/azul
% - OSA Visível canais G e B: Ajuste linear para todos
%
% Autor: Jakson Almeida
% Data: 2026-01-29

clear; close all; clc;

%% Configurações
json_file = 'dados_todos_finalmente_completo_2026-02-01T23-19-33.690Z.json';

if ~exist(json_file, 'file')
    error('Arquivo JSON não encontrado: %s', json_file);
end

%% Leitura do JSON
fprintf('=== Análise com Ajuste Misto (Linear e Polinomial) ===\n\n');
fprintf('Lendo dados de: %s\n', json_file);
json_text = fileread(json_file);
data = jsondecode(json_text);

%% Processar ThorLabs (5 tomadas) - AJUSTE LINEAR
fprintf('\n=== Processando ThorLabs (Ajuste Linear) ===\n');

duty_cycles = 1:10;
thorlabs_green = zeros(5, 10);
thorlabs_red = zeros(5, 10);
thorlabs_blue = zeros(5, 10);

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

% Ajuste LINEAR para ThorLabs (todos)
[p_green, S_green] = polyfit(duty_cycles, thorlabs_green_mean, 1);
[y_fit_green, ~] = polyval(p_green, duty_cycles, S_green);
R2_green = calcular_r2(thorlabs_green_mean, y_fit_green);

[p_red, S_red] = polyfit(duty_cycles, thorlabs_red_mean, 1);
[y_fit_red, ~] = polyval(p_red, duty_cycles, S_red);
R2_red = calcular_r2(thorlabs_red_mean, y_fit_red);

[p_blue, S_blue] = polyfit(duty_cycles, thorlabs_blue_mean, 1);
[y_fit_blue, ~] = polyval(p_blue, duty_cycles, S_blue);
R2_blue = calcular_r2(thorlabs_blue_mean, y_fit_blue);

fprintf('\nThorLabs - Ajuste Linear:\n');
fprintf('  Verde:    y = %.2fx + %.2f  (R² = %.4f)\n', p_green(1), p_green(2), R2_green);
fprintf('  Vermelho: y = %.2fx + %.2f  (R² = %.4f)\n', p_red(1), p_red(2), R2_red);
fprintf('  Azul:     y = %.2fx + %.2f  (R² = %.4f)\n', p_blue(1), p_blue(2), R2_blue);

% Plotar ThorLabs
plotar_thorlabs(duty_cycles, thorlabs_green_mean, thorlabs_green_std, ...
    thorlabs_red_mean, thorlabs_red_std, thorlabs_blue_mean, thorlabs_blue_std, ...
    p_green, p_red, p_blue, y_fit_green, y_fit_red, y_fit_blue, ...
    R2_green, R2_red, R2_blue);

%% Processar OSA Visível por canal
fprintf('\n=== Processando OSA Visível ===\n');

canal_tipos = {'x1', 'x2', 'x3', 'x4'};
canal_nomes = {'RGB (Todos os Canais)', 'Canal R', 'Canal G', 'Canal B'};

% Definir quais canais usam polinômio grau 2 para vermelho
% x1 (RGB) e x2 (R) usam grau 2 para vermelho
canais_poly2_red = {'x1', 'x2'};

color_green = [0.2, 0.8, 0.2];
color_red = [0.9, 0.2, 0.2];
color_blue = [0.2, 0.4, 0.9];

for tipo_idx = 1:length(canal_tipos)
    tipo = canal_tipos{tipo_idx};
    tipo_nome = canal_nomes{tipo_idx};
    
    fprintf('\nProcessando: %s\n', tipo_nome);
    
    % Verificar se este canal usa polinômio grau 2 para vermelho
    usar_poly2_red = ismember(tipo, canais_poly2_red);
    
    % Inicializar arrays
    osa_green = zeros(5, 10);
    osa_red = zeros(5, 10);
    osa_blue = zeros(5, 10);
    
    % Coletar dados
    for tomada = 1:5
        tomada_str = sprintf('x%d', tomada);
        
        if ~isfield(data.data.osa_visivel, tomada_str)
            continue;
        end
        
        tomada_data = data.data.osa_visivel.(tomada_str);
        
        for dc = 1:10
            dc_str = sprintf('x%d', dc);
            
            if ~isfield(tomada_data, dc_str)
                continue;
            end
            
            dc_data = tomada_data.(dc_str);
            
            if ~isfield(dc_data, tipo)
                continue;
            end
            
            tipo_data = dc_data.(tipo);
            
            % Converter valores
            if ~isempty(tipo_data.green.intensity) && ischar(tipo_data.green.intensity)
                osa_green(tomada, dc) = str2double(tipo_data.green.intensity);
            else
                osa_green(tomada, dc) = NaN;
            end
            
            if ~isempty(tipo_data.red.intensity) && ischar(tipo_data.red.intensity)
                osa_red(tomada, dc) = str2double(tipo_data.red.intensity);
            else
                osa_red(tomada, dc) = NaN;
            end
            
            if ~isempty(tipo_data.blue.intensity) && ischar(tipo_data.blue.intensity)
                osa_blue(tomada, dc) = str2double(tipo_data.blue.intensity);
            else
                osa_blue(tomada, dc) = NaN;
            end
        end
    end
    
    % Calcular médias e desvios
    osa_green_mean = mean(osa_green, 1, 'omitnan');
    osa_green_std = std(osa_green, 0, 1, 'omitnan');
    osa_red_mean = mean(osa_red, 1, 'omitnan');
    osa_red_std = std(osa_red, 0, 1, 'omitnan');
    osa_blue_mean = mean(osa_blue, 1, 'omitnan');
    osa_blue_std = std(osa_blue, 0, 1, 'omitnan');
    
    % Encontrar índices válidos
    valid_green = ~isnan(osa_green_mean);
    valid_red = ~isnan(osa_red_mean);
    valid_blue = ~isnan(osa_blue_mean);
    
    % Ajuste para VERDE (sempre linear)
    if sum(valid_green) >= 2
        [p_osa_green, S_osa_green] = polyfit(duty_cycles(valid_green), osa_green_mean(valid_green), 1);
        [y_fit_osa_green, ~] = polyval(p_osa_green, duty_cycles(valid_green), S_osa_green);
        R2_osa_green = calcular_r2(osa_green_mean(valid_green), y_fit_osa_green);
        grau_green = 1;
    else
        p_osa_green = [NaN, NaN];
        y_fit_osa_green = [];
        R2_osa_green = NaN;
        grau_green = 1;
    end
    
    % Ajuste para VERMELHO (grau 2 para x1 e x2, linear para x3 e x4)
    if usar_poly2_red && sum(valid_red) >= 3
        % Ajuste POLINOMIAL GRAU 2
        [p_osa_red, S_osa_red] = polyfit(duty_cycles(valid_red), osa_red_mean(valid_red), 2);
        [y_fit_osa_red, ~] = polyval(p_osa_red, duty_cycles(valid_red), S_osa_red);
        R2_osa_red = calcular_r2(osa_red_mean(valid_red), y_fit_osa_red);
        grau_red = 2;
    elseif sum(valid_red) >= 2
        % Ajuste LINEAR
        [p_osa_red, S_osa_red] = polyfit(duty_cycles(valid_red), osa_red_mean(valid_red), 1);
        [y_fit_osa_red, ~] = polyval(p_osa_red, duty_cycles(valid_red), S_osa_red);
        R2_osa_red = calcular_r2(osa_red_mean(valid_red), y_fit_osa_red);
        grau_red = 1;
    else
        p_osa_red = [NaN, NaN];
        y_fit_osa_red = [];
        R2_osa_red = NaN;
        grau_red = 1;
    end
    
    % Ajuste para AZUL (sempre linear)
    if sum(valid_blue) >= 2
        [p_osa_blue, S_osa_blue] = polyfit(duty_cycles(valid_blue), osa_blue_mean(valid_blue), 1);
        [y_fit_osa_blue, ~] = polyval(p_osa_blue, duty_cycles(valid_blue), S_osa_blue);
        R2_osa_blue = calcular_r2(osa_blue_mean(valid_blue), y_fit_osa_blue);
        grau_blue = 1;
    else
        p_osa_blue = [NaN, NaN];
        y_fit_osa_blue = [];
        R2_osa_blue = NaN;
        grau_blue = 1;
    end
    
    % Exibir parâmetros
    fprintf('\n  %s - Parâmetros do ajuste:\n', tipo_nome);
    if ~isnan(p_osa_green(1))
        fprintf('    Verde:    y = %.2fx + %.2f  (R² = %.4f) [Linear]\n', ...
            p_osa_green(1), p_osa_green(2), R2_osa_green);
    else
        fprintf('    Verde:    Dados insuficientes\n');
    end
    
    if ~isnan(p_osa_red(1))
        if grau_red == 2
            fprintf('    Vermelho: y = %.2fx² + %.2fx + %.2f  (R² = %.4f) [Grau 2]\n', ...
                p_osa_red(1), p_osa_red(2), p_osa_red(3), R2_osa_red);
        else
            fprintf('    Vermelho: y = %.2fx + %.2f  (R² = %.4f) [Linear]\n', ...
                p_osa_red(1), p_osa_red(2), R2_osa_red);
        end
    else
        fprintf('    Vermelho: Dados insuficientes\n');
    end
    
    if ~isnan(p_osa_blue(1))
        fprintf('    Azul:     y = %.2fx + %.2f  (R² = %.4f) [Linear]\n', ...
            p_osa_blue(1), p_osa_blue(2), R2_osa_blue);
    else
        fprintf('    Azul:     Dados insuficientes\n');
    end
    
    % Plotar OSA Visível
    plotar_osa(duty_cycles, osa_green_mean, osa_green_std, osa_red_mean, osa_red_std, ...
        osa_blue_mean, osa_blue_std, valid_green, valid_red, valid_blue, ...
        p_osa_green, p_osa_red, p_osa_blue, y_fit_osa_green, y_fit_osa_red, ...
        y_fit_osa_blue, R2_osa_green, R2_osa_red, R2_osa_blue, ...
        grau_green, grau_red, grau_blue, tipo_nome, color_green, color_red, color_blue);
end

fprintf('\n=== Análise concluída! ===\n');

%% Função para plotar ThorLabs
function plotar_thorlabs(duty_cycles, green_mean, green_std, red_mean, red_std, ...
    blue_mean, blue_std, p_green, p_red, p_blue, y_fit_green, y_fit_red, y_fit_blue, ...
    R2_green, R2_red, R2_blue)

    color_green = [0.2, 0.8, 0.2];
    color_red = [0.9, 0.2, 0.2];
    color_blue = [0.2, 0.4, 0.9];
    
    figure('Position', [100, 100, 1200, 400]);
    set(gcf, 'Color', 'white');
    
    % Verde
    subplot(1, 3, 1);
    hold on;
    errorbar(duty_cycles, green_mean, green_std, 'o', ...
        'Color', color_green, 'LineWidth', 1.5, 'MarkerSize', 6, ...
        'MarkerFaceColor', color_green);
    plot(duty_cycles, y_fit_green, '-', 'Color', color_green, 'LineWidth', 2);
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    title('LED Verde', 'FontSize', 12, 'FontWeight', 'bold');
    text(1.5, max(green_mean)*0.9, ...
        sprintf('y = %.2fx + %.2f\nR² = %.4f', p_green(1), p_green(2), R2_green), ...
        'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');
    grid on;
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    hold off;
    
    % Vermelho
    subplot(1, 3, 2);
    hold on;
    errorbar(duty_cycles, red_mean, red_std, 'o', ...
        'Color', color_red, 'LineWidth', 1.5, 'MarkerSize', 6, ...
        'MarkerFaceColor', color_red);
    plot(duty_cycles, y_fit_red, '-', 'Color', color_red, 'LineWidth', 2);
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    title('LED Vermelho', 'FontSize', 12, 'FontWeight', 'bold');
    text(1.5, max(red_mean)*0.9, ...
        sprintf('y = %.2fx + %.2f\nR² = %.4f', p_red(1), p_red(2), R2_red), ...
        'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');
    grid on;
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    hold off;
    
    % Azul
    subplot(1, 3, 3);
    hold on;
    errorbar(duty_cycles, blue_mean, blue_std, 'o', ...
        'Color', color_blue, 'LineWidth', 1.5, 'MarkerSize', 6, ...
        'MarkerFaceColor', color_blue);
    plot(duty_cycles, y_fit_blue, '-', 'Color', color_blue, 'LineWidth', 2);
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    title('LED Azul', 'FontSize', 12, 'FontWeight', 'bold');
    text(1.5, max(blue_mean)*0.9, ...
        sprintf('y = %.2fx + %.2f\nR² = %.4f', p_blue(1), p_blue(2), R2_blue), ...
        'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');
    grid on;
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    hold off;
    
    sgtitle('ThorLabs - Ajuste Linear (Média de 5 Tomadas)', 'FontSize', 14, 'FontWeight', 'bold');
    
    output_file = 'ThorLabs_JSON_ajuste_linear.png';
    print(output_file, '-dpng', '-r300');
    fprintf('Gráfico ThorLabs salvo em: %s\n', output_file);
end

%% Função para plotar OSA Visível
function plotar_osa(duty_cycles, green_mean, green_std, red_mean, red_std, ...
    blue_mean, blue_std, valid_green, valid_red, valid_blue, ...
    p_green, p_red, p_blue, y_fit_green, y_fit_red, y_fit_blue, ...
    R2_green, R2_red, R2_blue, grau_green, grau_red, grau_blue, ...
    tipo_nome, color_green, color_red, color_blue)

    figure('Position', [100, 100, 1200, 400]);
    set(gcf, 'Color', 'white');
    
    % Verde
    subplot(1, 3, 1);
    hold on;
    errorbar(duty_cycles, green_mean, green_std, 'o', ...
        'Color', color_green, 'LineWidth', 1.5, 'MarkerSize', 6, ...
        'MarkerFaceColor', color_green);
    if sum(valid_green) >= 2
        plot(duty_cycles(valid_green), y_fit_green, '-', 'Color', color_green, 'LineWidth', 2);
        text(1.5, max(green_mean(valid_green))*0.9, ...
            sprintf('y = %.2fx + %.2f\nR² = %.4f', p_green(1), p_green(2), R2_green), ...
            'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');
    end
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    title('LED Verde', 'FontSize', 12, 'FontWeight', 'bold');
    grid on;
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    hold off;
    
    % Vermelho
    subplot(1, 3, 2);
    hold on;
    errorbar(duty_cycles, red_mean, red_std, 'o', ...
        'Color', color_red, 'LineWidth', 1.5, 'MarkerSize', 6, ...
        'MarkerFaceColor', color_red);
    if sum(valid_red) >= 2
        plot(duty_cycles(valid_red), y_fit_red, '-', 'Color', color_red, 'LineWidth', 2);
        if grau_red == 2
            text(1.5, max(red_mean(valid_red))*0.9, ...
                sprintf('y = %.2fx² + %.2fx + %.2f\nR² = %.4f', ...
                p_red(1), p_red(2), p_red(3), R2_red), ...
                'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');
        else
            text(1.5, max(red_mean(valid_red))*0.9, ...
                sprintf('y = %.2fx + %.2f\nR² = %.4f', p_red(1), p_red(2), R2_red), ...
                'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');
        end
    end
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    if grau_red == 2
        title('LED Vermelho (Grau 2)', 'FontSize', 12, 'FontWeight', 'bold');
    else
        title('LED Vermelho', 'FontSize', 12, 'FontWeight', 'bold');
    end
    grid on;
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    hold off;
    
    % Azul
    subplot(1, 3, 3);
    hold on;
    errorbar(duty_cycles, blue_mean, blue_std, 'o', ...
        'Color', color_blue, 'LineWidth', 1.5, 'MarkerSize', 6, ...
        'MarkerFaceColor', color_blue);
    if sum(valid_blue) >= 2
        plot(duty_cycles(valid_blue), y_fit_blue, '-', 'Color', color_blue, 'LineWidth', 2);
        text(1.5, max(blue_mean(valid_blue))*0.9, ...
            sprintf('y = %.2fx + %.2f\nR² = %.4f', p_blue(1), p_blue(2), R2_blue), ...
            'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');
    end
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    title('LED Azul', 'FontSize', 12, 'FontWeight', 'bold');
    grid on;
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    hold off;
    
    tipo_nome_safe = strrep(tipo_nome, ' ', '_');
    sgtitle(sprintf('OSA Visível - %s (Média de 5 Tomadas)', tipo_nome), ...
        'FontSize', 14, 'FontWeight', 'bold');
    
    output_file = sprintf('OSA_Visivel_%s_ajuste_misto.png', tipo_nome_safe);
    print(output_file, '-dpng', '-r300');
    fprintf('  Gráfico salvo em: %s\n', output_file);
end

%% Função auxiliar para calcular R²
function R2 = calcular_r2(y_obs, y_pred)
    SS_res = sum((y_obs - y_pred).^2);
    SS_tot = sum((y_obs - mean(y_obs)).^2);
    R2 = 1 - (SS_res / SS_tot);
end
