% modelagem_linear.m
% Script para modelagem linear pura do OSA Visível em relação ao ThorLabs
% Modelo: P(λ) = a·Pr + b·Pg + c·Pb + d
%
% Onde:
%   Pr, Pg, Pb: valores medidos pelo OSA Visível (canais R, G, B)
%   P(λ): potência espectral real medida pelo ThorLabs
%   a, b, c, d: constantes globais (ganhos) independentes de λ
%
% Autor: Jakson Almeida
% Data: 2026-02-01

clear; close all; clc;

%% Configurações
% Caminho do arquivo JSON
json_file = 'dados_todos_finalmente_completo_2026-02-01T23-19-33.690Z.json';

% Verificar se o arquivo existe
if ~exist(json_file, 'file')
    error('Arquivo JSON não encontrado: %s', json_file);
end

%% Leitura do JSON
fprintf('=== Modelagem Linear Pura: P(λ) = a·Pr + b·Pg + c·Pb + d ===\n\n');
fprintf('Lendo dados de: %s\n', json_file);
json_text = fileread(json_file);
data = jsondecode(json_text);

%% Coletar todos os dados para cada cor
fprintf('\nColetando dados...\n');

% Arrays para armazenar dados de todas as tomadas e duty cycles
% Estrutura: [tomada, duty_cycle]
cores = {'green', 'red', 'blue'};
cor_nomes = {'Verde', 'Vermelho', 'Azul'};

% Para cada cor, vamos criar vetores com todos os dados
dados_cor = struct();

for cor_idx = 1:length(cores)
    cor = cores{cor_idx};
    
    % Vetores para armazenar dados desta cor
    P_thorlabs = [];  % Potência ThorLabs (referência)
    Pr_osa = [];      % Canal R do OSA
    Pg_osa = [];      % Canal G do OSA
    Pb_osa = [];      % Canal B do OSA
    
    % Iterar sobre todas as tomadas (1-5) e duty cycles (1-10)
    for tomada = 1:5
        tomada_str = sprintf('x%d', tomada);
        
        % Verificar se a tomada existe em ambos os equipamentos
        if ~isfield(data.data.thorlabs, tomada_str) || ...
           ~isfield(data.data.osa_visivel, tomada_str)
            continue;
        end
        
        thorlabs_tomada = data.data.thorlabs.(tomada_str);
        osa_tomada = data.data.osa_visivel.(tomada_str);
        
        for dc = 1:10
            dc_str = sprintf('x%d', dc);
            
            % Verificar se o duty cycle existe
            if ~isfield(thorlabs_tomada, dc_str)
                continue;
            end
            
            % Dados ThorLabs
            thorlabs_dc = thorlabs_tomada.(dc_str);
            p_thor = str2double(thorlabs_dc.(cor).intensity);
            
            % Dados OSA Visível (canais R, G, B - tipo 2, 3, 4)
            % Canal R (tipo 2)
            if isfield(osa_tomada, 'x2') && isfield(osa_tomada.x2, dc_str)
                pr = str2double(osa_tomada.x2.(dc_str).(cor).intensity);
            else
                pr = NaN;
            end
            
            % Canal G (tipo 3)
            if isfield(osa_tomada, 'x3') && isfield(osa_tomada.x3, dc_str)
                pg = str2double(osa_tomada.x3.(dc_str).(cor).intensity);
            else
                pg = NaN;
            end
            
            % Canal B (tipo 4)
            if isfield(osa_tomada, 'x4') && isfield(osa_tomada.x4, dc_str)
                pb = str2double(osa_tomada.x4.(dc_str).(cor).intensity);
            else
                pb = NaN;
            end
            
            % Adicionar aos vetores apenas se todos os valores são válidos
            if ~isnan(p_thor) && ~isnan(pr) && ~isnan(pg) && ~isnan(pb) && ...
               ~isempty(p_thor) && ~isempty(pr) && ~isempty(pg) && ~isempty(pb)
                P_thorlabs = [P_thorlabs; p_thor];
                Pr_osa = [Pr_osa; pr];
                Pg_osa = [Pg_osa; pg];
                Pb_osa = [Pb_osa; pb];
            end
        end
    end
    
    % Armazenar dados desta cor
    dados_cor.(cor).P_thorlabs = P_thorlabs;
    dados_cor.(cor).Pr_osa = Pr_osa;
    dados_cor.(cor).Pg_osa = Pg_osa;
    dados_cor.(cor).Pb_osa = Pb_osa;
    dados_cor.(cor).n_amostras = length(P_thorlabs);
    
    fprintf('  %s: %d amostras coletadas\n', cor_nomes{cor_idx}, length(P_thorlabs));
end

%% Resolver modelo linear para cada cor separadamente
fprintf('\n=== Calculando ganhos do modelo linear ===\n');

resultados = struct();

for cor_idx = 1:length(cores)
    cor = cores{cor_idx};
    cor_nome = cor_nomes{cor_idx};
    
    fprintf('\n--- LED %s ---\n', cor_nome);
    
    % Extrair dados
    Y = dados_cor.(cor).P_thorlabs;  % Variável dependente (ThorLabs)
    Pr = dados_cor.(cor).Pr_osa;
    Pg = dados_cor.(cor).Pg_osa;
    Pb = dados_cor.(cor).Pb_osa;
    
    % Montar matriz de design [Pr, Pg, Pb, 1]
    X = [Pr, Pg, Pb, ones(size(Pr))];
    
    % Resolver sistema usando mínimos quadrados: β = (X'X)^(-1) X'Y
    % onde β = [a; b; c; d]
    beta = (X' * X) \ (X' * Y);
    
    a = beta(1);
    b = beta(2);
    c = beta(3);
    d = beta(4);
    
    % Calcular P(λ) usando o modelo
    P_modelo = X * beta;
    
    % Calcular métricas de erro
    R2 = calcular_r2(Y, P_modelo);
    RMSE = sqrt(mean((Y - P_modelo).^2));
    MAE = mean(abs(Y - P_modelo));
    erro_percentual_medio = mean(abs((Y - P_modelo) ./ Y)) * 100;
    
    % Armazenar resultados
    resultados.(cor).a = a;
    resultados.(cor).b = b;
    resultados.(cor).c = c;
    resultados.(cor).d = d;
    resultados.(cor).R2 = R2;
    resultados.(cor).RMSE = RMSE;
    resultados.(cor).MAE = MAE;
    resultados.(cor).erro_perc = erro_percentual_medio;
    resultados.(cor).P_thorlabs = Y;
    resultados.(cor).P_modelo = P_modelo;
    
    % Exibir resultados
    fprintf('Modelo: P(λ) = %.4f·Pr + %.4f·Pg + %.4f·Pb + %.4f\n', a, b, c, d);
    fprintf('Métricas:\n');
    fprintf('  R² = %.6f\n', R2);
    fprintf('  RMSE = %.2f\n', RMSE);
    fprintf('  MAE = %.2f\n', MAE);
    fprintf('  Erro percentual médio = %.2f%%\n', erro_percentual_medio);
end

%% Plotar resultados comparativos
fprintf('\n=== Gerando gráficos ===\n');

% Cores para os gráficos
color_green = [0.2, 0.8, 0.2];
color_red = [0.9, 0.2, 0.2];
color_blue = [0.2, 0.4, 0.9];
cores_plot = {color_green, color_red, color_blue};

% Figura 1: Comparação ThorLabs vs Modelo
figure('Position', [100, 100, 1400, 400]);
set(gcf, 'Color', 'white');

for cor_idx = 1:length(cores)
    cor = cores{cor_idx};
    cor_nome = cor_nomes{cor_idx};
    cor_plot = cores_plot{cor_idx};
    
    Y = resultados.(cor).P_thorlabs;
    P_modelo = resultados.(cor).P_modelo;
    
    subplot(1, 3, cor_idx);
    hold on;
    
    % Plotar linha diagonal (ajuste perfeito)
    max_val = max([Y; P_modelo]);
    min_val = min([Y; P_modelo]);
    plot([min_val, max_val], [min_val, max_val], 'k--', 'LineWidth', 1.5);
    
    % Plotar pontos
    scatter(Y, P_modelo, 40, cor_plot, 'filled', 'MarkerEdgeColor', 'k', ...
        'MarkerFaceAlpha', 0.6, 'LineWidth', 0.5);
    
    xlabel('ThorLabs (Referência)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('OSA Visível (Modelo)', 'FontSize', 11, 'FontWeight', 'bold');
    title(sprintf('LED %s', cor_nome), 'FontSize', 12, 'FontWeight', 'bold');
    
    % Adicionar caixa de texto com métricas
    text_str = sprintf('R² = %.4f\nRMSE = %.1f\nErro = %.2f%%', ...
        resultados.(cor).R2, resultados.(cor).RMSE, resultados.(cor).erro_perc);
    text(min_val + 0.05*(max_val-min_val), max_val - 0.15*(max_val-min_val), ...
        text_str, 'FontSize', 9, 'BackgroundColor', 'white', ...
        'EdgeColor', 'black', 'LineWidth', 1);
    
    grid on;
    axis equal;
    xlim([min_val, max_val]);
    ylim([min_val, max_val]);
    set(gca, 'FontSize', 10);
    hold off;
end

sgtitle('Modelo Linear: ThorLabs vs OSA Visível Modelado', ...
    'FontSize', 14, 'FontWeight', 'bold');

% Salvar figura
output_file = 'Modelo_Linear_Comparacao.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico salvo em: %s\n', output_file);

% Figura 2: Resíduos
figure('Position', [100, 100, 1400, 400]);
set(gcf, 'Color', 'white');

for cor_idx = 1:length(cores)
    cor = cores{cor_idx};
    cor_nome = cor_nomes{cor_idx};
    cor_plot = cores_plot{cor_idx};
    
    Y = resultados.(cor).P_thorlabs;
    P_modelo = resultados.(cor).P_modelo;
    residuos = Y - P_modelo;
    
    subplot(1, 3, cor_idx);
    hold on;
    
    % Linha zero
    plot([min(Y), max(Y)], [0, 0], 'k--', 'LineWidth', 1.5);
    
    % Plotar resíduos
    scatter(Y, residuos, 40, cor_plot, 'filled', 'MarkerEdgeColor', 'k', ...
        'MarkerFaceAlpha', 0.6, 'LineWidth', 0.5);
    
    xlabel('ThorLabs (Referência)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Resíduo (ThorLabs - Modelo)', 'FontSize', 11, 'FontWeight', 'bold');
    title(sprintf('LED %s', cor_nome), 'FontSize', 12, 'FontWeight', 'bold');
    
    grid on;
    set(gca, 'FontSize', 10);
    hold off;
end

sgtitle('Análise de Resíduos do Modelo Linear', ...
    'FontSize', 14, 'FontWeight', 'bold');

% Salvar figura
output_file = 'Modelo_Linear_Residuos.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico salvo em: %s\n', output_file);

%% Exibir tabela de ganhos
fprintf('\n=== Tabela de Ganhos do Modelo ===\n');
fprintf('%-10s | %10s | %10s | %10s | %10s\n', 'Cor', 'a (Pr)', 'b (Pg)', 'c (Pb)', 'd (offset)');
fprintf('-----------|------------|------------|------------|------------\n');
for cor_idx = 1:length(cores)
    cor = cores{cor_idx};
    cor_nome = cor_nomes{cor_idx};
    fprintf('%-10s | %10.4f | %10.4f | %10.4f | %10.2f\n', ...
        cor_nome, resultados.(cor).a, resultados.(cor).b, ...
        resultados.(cor).c, resultados.(cor).d);
end

%% Salvar resultados em arquivo
fprintf('\n=== Salvando resultados ===\n');

% Salvar em arquivo MAT
save('resultados_modelagem_linear.mat', 'resultados', 'dados_cor');
fprintf('Resultados salvos em: resultados_modelagem_linear.mat\n');

% Salvar ganhos em arquivo de texto
fid = fopen('ganhos_modelo_linear.txt', 'w');
fprintf(fid, 'Modelo Linear Puro: P(lambda) = a*Pr + b*Pg + c*Pb + d\n\n');
fprintf(fid, 'Ganhos calculados:\n');
fprintf(fid, '%-10s | %10s | %10s | %10s | %10s | %10s | %10s\n', ...
    'Cor', 'a (Pr)', 'b (Pg)', 'c (Pb)', 'd (offset)', 'R²', 'RMSE');
fprintf(fid, '-----------|------------|------------|------------|------------|------------|------------\n');
for cor_idx = 1:length(cores)
    cor = cores{cor_idx};
    cor_nome = cor_nomes{cor_idx};
    fprintf(fid, '%-10s | %10.4f | %10.4f | %10.4f | %10.2f | %10.6f | %10.2f\n', ...
        cor_nome, resultados.(cor).a, resultados.(cor).b, ...
        resultados.(cor).c, resultados.(cor).d, ...
        resultados.(cor).R2, resultados.(cor).RMSE);
end
fclose(fid);
fprintf('Ganhos salvos em: ganhos_modelo_linear.txt\n');

fprintf('\n=== Modelagem concluída! ===\n');

%% Função auxiliar para calcular R²
function R2 = calcular_r2(y_obs, y_pred)
    % Calcula o coeficiente de determinação R²
    SS_res = sum((y_obs - y_pred).^2);
    SS_tot = sum((y_obs - mean(y_obs)).^2);
    R2 = 1 - (SS_res / SS_tot);
end
