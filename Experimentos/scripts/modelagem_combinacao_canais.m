% modelagem_combinacao_canais.m
% Script para modelagem combinando linearmente os canais R, G e B do OSA Visível
% 
% Para cada fonte (verde, vermelho, azul):
%   P_ThorLabs = α₁·f_R(x) + α₂·f_G(x) + α₃·f_B(x)
%   onde f_i(x) = a_i·x² + b_i·x + c_i (polinômios grau 2 de cada canal)
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
fprintf('=== Modelagem por Combinação de Canais (Grau 2) ===\n\n');
fprintf('Lendo dados de: %s\n', json_file);
json_text = fileread(json_file);
data = jsondecode(json_text);

%% Coletar dados
duty_cycles = 1:10;
fontes = {'green', 'red', 'blue'};
fontes_nomes = {'Verde', 'Vermelho', 'Azul'};
canais = {'x2', 'x3', 'x4'};  % Canal R, G, B
canais_nomes = {'R', 'G', 'B'};

% Estrutura para armazenar resultados
resultados = struct();

%% Para cada fonte, coletar dados e modelar
for fonte_idx = 1:length(fontes)
    fonte = fontes{fonte_idx};
    fonte_nome = fontes_nomes{fonte_idx};
    
    fprintf('\n=== Processando Fonte: %s ===\n', fonte_nome);
    
    % Coletar dados do ThorLabs (referência)
    thorlabs_data = zeros(5, 10);
    for tomada = 1:5
        tomada_str = sprintf('x%d', tomada);
        for dc = 1:10
            dc_str = sprintf('x%d', dc);
            thorlabs_data(tomada, dc) = str2double(data.data.thorlabs.(tomada_str).(dc_str).(fonte).intensity);
        end
    end
    P_thorlabs = mean(thorlabs_data, 1)';  % Média das 5 tomadas
    
    % Coletar dados dos 3 canais do OSA Visível (R, G, B)
    canais_data = struct();
    
    for canal_idx = 1:length(canais)
        canal = canais{canal_idx};
        canal_nome = canais_nomes{canal_idx};
        
        osa_data = zeros(5, 10);
        for tomada = 1:5
            tomada_str = sprintf('x%d', tomada);
            if ~isfield(data.data.osa_visivel, tomada_str)
                continue;
            end
            tomada_data = data.data.osa_visivel.(tomada_str);
            if ~isfield(tomada_data, canal)
                continue;
            end
            tipo_data = tomada_data.(canal);
            
            for dc = 1:10
                dc_str = sprintf('x%d', dc);
                if isfield(tipo_data, dc_str)
                    dc_data = tipo_data.(dc_str);
                    if ~isempty(dc_data.(fonte).intensity) && ischar(dc_data.(fonte).intensity)
                        osa_data(tomada, dc) = str2double(dc_data.(fonte).intensity);
                    else
                        osa_data(tomada, dc) = NaN;
                    end
                end
            end
        end
        
        % Média das 5 tomadas
        osa_mean = mean(osa_data, 1, 'omitnan')';
        
        % Ajustar polinômio grau 2
        valid = ~isnan(osa_mean);
        if sum(valid) >= 3
            [p, ~] = polyfit(duty_cycles(valid), osa_mean(valid), 2);
            y_poly = polyval(p, duty_cycles');
        else
            p = [NaN, NaN, NaN];
            y_poly = NaN(10, 1);
        end
        
        canais_data.(canal_nome).data = osa_mean;
        canais_data.(canal_nome).poly = p;
        canais_data.(canal_nome).y_poly = y_poly;
        
        fprintf('  Canal %s: y = %.4fx² + %.4fx + %.4f\n', canal_nome, p(1), p(2), p(3));
    end
    
    %% Combinação linear dos canais
    % Modelo: P_ThorLabs = α₁·f_R(x) + α₂·f_G(x) + α₃·f_B(x)
    % onde f_i(x) são os polinômios ajustados de cada canal
    
    fprintf('\n  Calculando combinação linear dos canais...\n');
    
    % Montar matriz de design com os polinômios avaliados
    X = [canais_data.R.y_poly, canais_data.G.y_poly, canais_data.B.y_poly];
    
    % Verificar se há dados válidos
    valid_rows = ~any(isnan(X), 2);
    if sum(valid_rows) < 3
        fprintf('  ERRO: Dados insuficientes para ajuste!\n');
        continue;
    end
    
    % Resolver sistema de mínimos quadrados para encontrar α₁, α₂, α₃
    alpha = (X(valid_rows,:)' * X(valid_rows,:)) \ (X(valid_rows,:)' * P_thorlabs(valid_rows));
    
    % Predição do modelo combinado
    P_modelo = X * alpha;
    
    % Métricas de erro
    R2 = calcular_r2(P_thorlabs(valid_rows), P_modelo(valid_rows));
    RMSE = sqrt(mean((P_thorlabs(valid_rows) - P_modelo(valid_rows)).^2));
    MAE = mean(abs(P_thorlabs(valid_rows) - P_modelo(valid_rows)));
    erro_perc = mean(abs((P_thorlabs(valid_rows) - P_modelo(valid_rows)) ./ P_thorlabs(valid_rows))) * 100;
    
    fprintf('\n  Coeficientes da combinação:\n');
    fprintf('    α₁ (Canal R) = %.4f\n', alpha(1));
    fprintf('    α₂ (Canal G) = %.4f\n', alpha(2));
    fprintf('    α₃ (Canal B) = %.4f\n', alpha(3));
    fprintf('\n  Métricas do modelo:\n');
    fprintf('    R² = %.4f\n', R2);
    fprintf('    RMSE = %.2f\n', RMSE);
    fprintf('    MAE = %.2f\n', MAE);
    fprintf('    Erro percentual médio = %.2f%%\n', erro_perc);
    
    % Armazenar resultados
    resultados.(fonte).P_thorlabs = P_thorlabs;
    resultados.(fonte).P_modelo = P_modelo;
    resultados.(fonte).alpha = alpha;
    resultados.(fonte).canais = canais_data;
    resultados.(fonte).R2 = R2;
    resultados.(fonte).RMSE = RMSE;
    resultados.(fonte).MAE = MAE;
    resultados.(fonte).erro_perc = erro_perc;
    resultados.(fonte).duty_cycles = duty_cycles;
end

%% Visualização dos resultados
fprintf('\n=== Gerando gráficos ===\n');

cores_fontes = [0.2 0.8 0.2; 0.9 0.2 0.2; 0.2 0.4 0.9];

% Figura 1: Comparação ThorLabs vs Modelo Combinado
figure('Position', [100, 100, 1400, 500]);
set(gcf, 'Color', 'white');

for fonte_idx = 1:length(fontes)
    fonte = fontes{fonte_idx};
    fonte_nome = fontes_nomes{fonte_idx};
    
    subplot(1, 3, fonte_idx);
    hold on; grid on;
    
    % Dados reais
    plot(resultados.(fonte).duty_cycles, resultados.(fonte).P_thorlabs, 'o', ...
        'Color', cores_fontes(fonte_idx,:), 'MarkerSize', 8, ...
        'LineWidth', 2, 'DisplayName', 'ThorLabs (real)');
    
    % Modelo combinado
    plot(resultados.(fonte).duty_cycles, resultados.(fonte).P_modelo, 's-', ...
        'Color', cores_fontes(fonte_idx,:) * 0.6, 'MarkerSize', 6, ...
        'LineWidth', 2, 'DisplayName', 'Modelo Combinado');
    
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    title(sprintf('%s\nR² = %.4f, RMSE = %.1f', fonte_nome, ...
        resultados.(fonte).R2, resultados.(fonte).RMSE), ...
        'FontSize', 12, 'FontWeight', 'bold');
    legend('Location', 'northwest', 'FontSize', 9);
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    hold off;
end

sgtitle('Modelo Combinado: ThorLabs vs OSA Visível (Canais R+G+B)', ...
    'FontSize', 14, 'FontWeight', 'bold');

output_file = 'Modelo_Combinacao_Canais_Comparacao.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico salvo em: %s\n', output_file);

% Figura 2: Contribuição de cada canal
figure('Position', [100, 100, 1400, 500]);
set(gcf, 'Color', 'white');

for fonte_idx = 1:length(fontes)
    fonte = fontes{fonte_idx};
    fonte_nome = fontes_nomes{fonte_idx};
    
    subplot(1, 3, fonte_idx);
    
    % Contribuições de cada canal
    contrib_R = resultados.(fonte).canais.R.y_poly * resultados.(fonte).alpha(1);
    contrib_G = resultados.(fonte).canais.G.y_poly * resultados.(fonte).alpha(2);
    contrib_B = resultados.(fonte).canais.B.y_poly * resultados.(fonte).alpha(3);
    
    hold on; grid on;
    plot(duty_cycles, contrib_R, 'r-', 'LineWidth', 2, 'DisplayName', ...
        sprintf('Canal R (α=%.2f)', resultados.(fonte).alpha(1)));
    plot(duty_cycles, contrib_G, 'g-', 'LineWidth', 2, 'DisplayName', ...
        sprintf('Canal G (α=%.2f)', resultados.(fonte).alpha(2)));
    plot(duty_cycles, contrib_B, 'b-', 'LineWidth', 2, 'DisplayName', ...
        sprintf('Canal B (α=%.2f)', resultados.(fonte).alpha(3)));
    plot(duty_cycles, resultados.(fonte).P_modelo, 'k--', 'LineWidth', 2.5, ...
        'DisplayName', 'Soma Total');
    
    xlabel('Duty Cycle (%)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Contribuição à Intensidade', 'FontSize', 11, 'FontWeight', 'bold');
    title(sprintf('Fonte: %s', fonte_nome), 'FontSize', 12, 'FontWeight', 'bold');
    legend('Location', 'northwest', 'FontSize', 8);
    xlim([0, 11]);
    set(gca, 'FontSize', 10);
    hold off;
end

sgtitle('Contribuição de Cada Canal (R, G, B) por Fonte', ...
    'FontSize', 14, 'FontWeight', 'bold');

output_file = 'Modelo_Combinacao_Canais_Contribuicoes.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico salvo em: %s\n', output_file);

% Figura 3: Resíduos
figure('Position', [100, 100, 1400, 500]);
set(gcf, 'Color', 'white');

for fonte_idx = 1:length(fontes)
    fonte = fontes{fonte_idx};
    fonte_nome = fontes_nomes{fonte_idx};
    
    residuos = resultados.(fonte).P_thorlabs - resultados.(fonte).P_modelo;
    
    subplot(1, 3, fonte_idx);
    hold on; grid on;
    
    scatter(resultados.(fonte).P_thorlabs, residuos, 80, ...
        cores_fontes(fonte_idx,:), 'filled', 'MarkerFaceAlpha', 0.6);
    plot([min(resultados.(fonte).P_thorlabs), max(resultados.(fonte).P_thorlabs)], ...
        [0, 0], 'k--', 'LineWidth', 2);
    
    xlabel('ThorLabs (real)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Resíduo', 'FontSize', 11, 'FontWeight', 'bold');
    title(sprintf('%s\nMAE = %.1f', fonte_nome, resultados.(fonte).MAE), ...
        'FontSize', 12, 'FontWeight', 'bold');
    set(gca, 'FontSize', 10);
    hold off;
end

sgtitle('Análise de Resíduos - Modelo Combinado', ...
    'FontSize', 14, 'FontWeight', 'bold');

output_file = 'Modelo_Combinacao_Canais_Residuos.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico salvo em: %s\n', output_file);

%% Salvar resultados
fprintf('\n=== Salvando resultados ===\n');

save('resultados_combinacao_canais.mat', 'resultados');
fprintf('Resultados salvos em: resultados_combinacao_canais.mat\n');

% Salvar parâmetros em texto
fid = fopen('parametros_combinacao_canais.txt', 'w');
fprintf(fid, 'Modelo de Combinação Linear dos Canais R, G, B\n');
fprintf(fid, '==============================================\n\n');
fprintf(fid, 'Para cada fonte: P_ThorLabs = α₁·f_R(x) + α₂·f_G(x) + α₃·f_B(x)\n');
fprintf(fid, 'onde f_i(x) = a_i·x² + b_i·x + c_i (polinômios grau 2)\n\n');

for fonte_idx = 1:length(fontes)
    fonte = fontes{fonte_idx};
    fonte_nome = fontes_nomes{fonte_idx};
    
    fprintf(fid, '\n--- Fonte: %s ---\n', fonte_nome);
    fprintf(fid, '\nPolinômios dos canais:\n');
    fprintf(fid, '  Canal R: y = %.4fx² + %.4fx + %.4f\n', ...
        resultados.(fonte).canais.R.poly(1), ...
        resultados.(fonte).canais.R.poly(2), ...
        resultados.(fonte).canais.R.poly(3));
    fprintf(fid, '  Canal G: y = %.4fx² + %.4fx + %.4f\n', ...
        resultados.(fonte).canais.G.poly(1), ...
        resultados.(fonte).canais.G.poly(2), ...
        resultados.(fonte).canais.G.poly(3));
    fprintf(fid, '  Canal B: y = %.4fx² + %.4fx + %.4f\n', ...
        resultados.(fonte).canais.B.poly(1), ...
        resultados.(fonte).canais.B.poly(2), ...
        resultados.(fonte).canais.B.poly(3));
    
    fprintf(fid, '\nCoeficientes da combinação linear:\n');
    fprintf(fid, '  α₁ (Canal R) = %.4f\n', resultados.(fonte).alpha(1));
    fprintf(fid, '  α₂ (Canal G) = %.4f\n', resultados.(fonte).alpha(2));
    fprintf(fid, '  α₃ (Canal B) = %.4f\n', resultados.(fonte).alpha(3));
    
    fprintf(fid, '\nMétricas do modelo:\n');
    fprintf(fid, '  R² = %.4f\n', resultados.(fonte).R2);
    fprintf(fid, '  RMSE = %.2f\n', resultados.(fonte).RMSE);
    fprintf(fid, '  MAE = %.2f\n', resultados.(fonte).MAE);
    fprintf(fid, '  Erro percentual médio = %.2f%%\n', resultados.(fonte).erro_perc);
end

fclose(fid);
fprintf('Parâmetros salvos em: parametros_combinacao_canais.txt\n');

fprintf('\n=== Modelagem concluída! ===\n');

%% Resumo final
fprintf('\n=== RESUMO DOS MODELOS ===\n');
for fonte_idx = 1:length(fontes)
    fonte = fontes{fonte_idx};
    fonte_nome = fontes_nomes{fonte_idx};
    fprintf('\n%s:\n', fonte_nome);
    fprintf('  P = %.3f·f_R(x) + %.3f·f_G(x) + %.3f·f_B(x)\n', ...
        resultados.(fonte).alpha(1), ...
        resultados.(fonte).alpha(2), ...
        resultados.(fonte).alpha(3));
    fprintf('  R² = %.4f, RMSE = %.2f, Erro = %.2f%%\n', ...
        resultados.(fonte).R2, ...
        resultados.(fonte).RMSE, ...
        resultados.(fonte).erro_perc);
end

%% Função auxiliar
function R2 = calcular_r2(y_obs, y_pred)
    SS_res = sum((y_obs - y_pred).^2);
    SS_tot = sum((y_obs - mean(y_obs)).^2);
    R2 = 1 - (SS_res / SS_tot);
end
