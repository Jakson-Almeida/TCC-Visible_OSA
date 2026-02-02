% modelagem_espectral_ordem4.m
% Script para modelagem ESPECTRAL de ordem 4 do OSA Visível em relação ao ThorLabs
% 
% Modelo: P(λ) = Σ(aᵢ·λⁱ)·Pr + Σ(bᵢ·λⁱ)·Pg + Σ(cᵢ·λⁱ)·Pb + Σ(dᵢ·λⁱ)
%         onde i = 0, 1, 2, 3, 4 (polinômio de ordem 4)
%
% Autor: Jakson Almeida
% Data: 2026-01-29

clear; clc; close all;

%% Configurações
json_file = 'dados_todos_finalmente_completo_2026-02-01T23-19-33.690Z.json';

%% Leitura do JSON
fprintf('=== Modelagem Espectral - Ordem 4 ===\n\n');
fprintf('Lendo dados de: %s\n', json_file);

% Ler arquivo JSON
json_text = fileread(json_file);
dados = jsondecode(json_text);

%% Coletar TODOS os dados
fprintf('\nColetando dados...\n');

% Arrays para armazenar todos os dados
lambda_thorlabs = [];
P_thorlabs = [];
lambda_osa = [];
Pr_osa = [];
Pg_osa = [];
Pb_osa = [];
fonte_labels = {};
duty_cycle = [];
tomada_id = [];

% Contadores de debug
n_total_tentativas = 0;
n_descartadas_lambda = 0;
n_descartadas_pr = 0;
n_descartadas_pg = 0;
n_descartadas_pb = 0;

% Iterar sobre as tomadas (1-5)
for t_idx = 1:5
    tomada = ['x', num2str(t_idx)];
    
    if ~isfield(dados.data.thorlabs, tomada)
        continue;
    end
    
    % Iterar sobre duty cycles (1-10)
    for dc_valor = 1:10
        dc_campo = ['x', num2str(dc_valor)];
        
        if ~isfield(dados.data.thorlabs.(tomada), dc_campo)
            continue;
        end
        
        % Iterar sobre as fontes
        fontes = {'green', 'red', 'blue'};
        for fonte_idx = 1:length(fontes)
            fonte = fontes{fonte_idx};
            
            n_total_tentativas = n_total_tentativas + 1;
            
            % Dados ThorLabs (sempre presente)
            if ~isfield(dados.data.thorlabs.(tomada).(dc_campo), fonte)
                continue;
            end
            
            thorlabs_data = dados.data.thorlabs.(tomada).(dc_campo).(fonte);
            
            if ~isfield(thorlabs_data, 'peak_nm') || ~isfield(thorlabs_data, 'intensity')
                continue;
            end
            if isempty(thorlabs_data.peak_nm) || isempty(thorlabs_data.intensity)
                continue;
            end
            
            lambda_th = str2double(thorlabs_data.peak_nm);
            P_th = str2double(thorlabs_data.intensity);
            
            if isnan(lambda_th) || isnan(P_th)
                continue;
            end
            
            % Verificar se OSA Visível existe
            if ~isfield(dados.data.osa_visivel, tomada) || ...
               ~isfield(dados.data.osa_visivel.(tomada), dc_campo)
                continue;
            end
            
            % Buscar lambda do OSA (do canal RGB - canal "x1")
            lambda_osa_val = NaN;
            if isfield(dados.data.osa_visivel.(tomada).(dc_campo), 'x1')
                if isfield(dados.data.osa_visivel.(tomada).(dc_campo).x1, fonte)
                    osa_rgb = dados.data.osa_visivel.(tomada).(dc_campo).x1.(fonte);
                    if isfield(osa_rgb, 'peak_nm') && ~isempty(osa_rgb.peak_nm)
                        lambda_osa_val = str2double(osa_rgb.peak_nm);
                    end
                end
            end
            
            if isnan(lambda_osa_val)
                n_descartadas_lambda = n_descartadas_lambda + 1;
                continue;
            end
            
            % Buscar intensidades dos canais R, G, B separados
            Pr_val = NaN;
            if isfield(dados.data.osa_visivel.(tomada).(dc_campo), 'x2')
                if isfield(dados.data.osa_visivel.(tomada).(dc_campo).x2, fonte)
                    r_data = dados.data.osa_visivel.(tomada).(dc_campo).x2.(fonte);
                    if isfield(r_data, 'intensity') && ~isempty(r_data.intensity)
                        Pr_val = str2double(r_data.intensity);
                    end
                end
            end
            
            Pg_val = NaN;
            if isfield(dados.data.osa_visivel.(tomada).(dc_campo), 'x3')
                if isfield(dados.data.osa_visivel.(tomada).(dc_campo).x3, fonte)
                    g_data = dados.data.osa_visivel.(tomada).(dc_campo).x3.(fonte);
                    if isfield(g_data, 'intensity') && ~isempty(g_data.intensity)
                        Pg_val = str2double(g_data.intensity);
                    end
                end
            end
            
            Pb_val = NaN;
            if isfield(dados.data.osa_visivel.(tomada).(dc_campo), 'x4')
                if isfield(dados.data.osa_visivel.(tomada).(dc_campo).x4, fonte)
                    b_data = dados.data.osa_visivel.(tomada).(dc_campo).x4.(fonte);
                    if isfield(b_data, 'intensity') && ~isempty(b_data.intensity)
                        Pb_val = str2double(b_data.intensity);
                    end
                end
            end
            
            % Debug: contar por que foi descartado
            if isnan(Pr_val)
                n_descartadas_pr = n_descartadas_pr + 1;
            end
            if isnan(Pg_val)
                n_descartadas_pg = n_descartadas_pg + 1;
            end
            if isnan(Pb_val)
                n_descartadas_pb = n_descartadas_pb + 1;
            end
            
            % Adicionar se todos os valores existem
            if ~isnan(Pr_val) && ~isnan(Pg_val) && ~isnan(Pb_val)
                lambda_thorlabs = [lambda_thorlabs; lambda_th];
                P_thorlabs = [P_thorlabs; P_th];
                lambda_osa = [lambda_osa; lambda_osa_val];
                Pr_osa = [Pr_osa; Pr_val];
                Pg_osa = [Pg_osa; Pg_val];
                Pb_osa = [Pb_osa; Pb_val];
                fonte_labels = [fonte_labels; fonte];
                duty_cycle = [duty_cycle; dc_valor];
                tomada_id = [tomada_id; t_idx];
            end
        end
    end
end

fprintf('  Total de amostras ThorLabs: %d\n', n_total_tentativas);
fprintf('  Amostras coletadas: %d\n', length(P_thorlabs));
fprintf('  Descartadas por falta de:\n');
fprintf('    - Lambda OSA: %d\n', n_descartadas_lambda);
fprintf('    - Canal R (Pr): %d\n', n_descartadas_pr);
fprintf('    - Canal G (Pg): %d\n', n_descartadas_pg);
fprintf('    - Canal B (Pb): %d\n', n_descartadas_pb);

% Verificar se há dados suficientes
if length(P_thorlabs) < 10
    error('Dados insuficientes! Apenas %d amostras coletadas.', length(P_thorlabs));
end

fprintf('\n  Faixa de λ (ThorLabs): [%.2f - %.2f] nm\n', min(lambda_thorlabs), max(lambda_thorlabs));
fprintf('  Faixa de λ (OSA): [%.2f - %.2f] nm\n', min(lambda_osa), max(lambda_osa));

%% Normalização
fprintf('\nNormalizando dados...\n');

lambda_min = min(lambda_thorlabs);
lambda_max = max(lambda_thorlabs);
lambda_norm = (lambda_thorlabs - lambda_min) / (lambda_max - lambda_min);

fprintf('  Intensidades ThorLabs: [%.2f - %.2f]\n', min(P_thorlabs), max(P_thorlabs));
fprintf('  Intensidades Pr: [%.2f - %.2f]\n', min(Pr_osa), max(Pr_osa));
fprintf('  Intensidades Pg: [%.2f - %.2f]\n', min(Pg_osa), max(Pg_osa));
fprintf('  Intensidades Pb: [%.2f - %.2f]\n', min(Pb_osa), max(Pb_osa));

%% Modelo Polinomial de Ordem 4
fprintf('\n=== Modelo Polinomial de Ordem 4 ===\n');
fprintf('P(λ) = Σ(aᵢ·λⁱ)·Pr + Σ(bᵢ·λⁱ)·Pg + Σ(cᵢ·λⁱ)·Pb + Σ(dᵢ·λⁱ)\n');
fprintf('onde i = 0, 1, 2, 3, 4\n');

% Construir matriz de design
% Para cada canal (Pr, Pg, Pb): 5 termos (ordem 0 a 4)
% Para o offset: 5 termos (ordem 0 a 4)
% Total: 5*4 = 20 parâmetros

X = [Pr_osa, Pr_osa.*lambda_norm, Pr_osa.*(lambda_norm.^2), ...
     Pr_osa.*(lambda_norm.^3), Pr_osa.*(lambda_norm.^4), ...
     Pg_osa, Pg_osa.*lambda_norm, Pg_osa.*(lambda_norm.^2), ...
     Pg_osa.*(lambda_norm.^3), Pg_osa.*(lambda_norm.^4), ...
     Pb_osa, Pb_osa.*lambda_norm, Pb_osa.*(lambda_norm.^2), ...
     Pb_osa.*(lambda_norm.^3), Pb_osa.*(lambda_norm.^4), ...
     ones(size(Pr_osa)), lambda_norm, lambda_norm.^2, ...
     lambda_norm.^3, lambda_norm.^4];

% Resolver usando mínimos quadrados
beta = (X' * X) \ (X' * P_thorlabs);

% Predição
P_modelo = X * beta;

% Métricas
R2 = calcular_r2(P_thorlabs, P_modelo);
RMSE = sqrt(mean((P_thorlabs - P_modelo).^2));
MAE = mean(abs(P_thorlabs - P_modelo));
erro_perc = mean(abs((P_thorlabs - P_modelo) ./ P_thorlabs)) * 100;

fprintf('\nParâmetros:\n');
fprintf('  Pr: a₀=%.4f, a₁=%.4f, a₂=%.4f, a₃=%.4f, a₄=%.4f\n', ...
    beta(1), beta(2), beta(3), beta(4), beta(5));
fprintf('  Pg: b₀=%.4f, b₁=%.4f, b₂=%.4f, b₃=%.4f, b₄=%.4f\n', ...
    beta(6), beta(7), beta(8), beta(9), beta(10));
fprintf('  Pb: c₀=%.4f, c₁=%.4f, c₂=%.4f, c₃=%.4f, c₄=%.4f\n', ...
    beta(11), beta(12), beta(13), beta(14), beta(15));
fprintf('  Offset: d₀=%.4f, d₁=%.4f, d₂=%.4f, d₃=%.4f, d₄=%.4f\n', ...
    beta(16), beta(17), beta(18), beta(19), beta(20));

fprintf('\nMétricas:\n');
fprintf('  R² = %.6f\n', R2);
fprintf('  RMSE = %.2f\n', RMSE);
fprintf('  MAE = %.2f\n', MAE);
fprintf('  Erro percentual médio = %.2f%%\n', erro_perc);

%% Visualização
fprintf('\n=== Gerando gráficos ===\n');

% Figura 1: Comparação por fonte
figure('Position', [100, 100, 1400, 500]);

fontes = {'green', 'red', 'blue'};
cores_plot = [0 0.7 0; 0.8 0 0; 0 0 0.8];
titulos = {'Verde', 'Vermelho', 'Azul'};

for fonte_idx = 1:3
    fonte = fontes{fonte_idx};
    idx_fonte = strcmp(fonte_labels, fonte);
    
    subplot(1, 3, fonte_idx);
    hold on; grid on;
    
    % Scatter plot
    scatter(P_thorlabs(idx_fonte), P_modelo(idx_fonte), 60, ...
        cores_plot(fonte_idx,:), 'filled', 'MarkerFaceAlpha', 0.6);
    
    % Linha 1:1
    lim_min = min([P_thorlabs(idx_fonte); P_modelo(idx_fonte)]);
    lim_max = max([P_thorlabs(idx_fonte); P_modelo(idx_fonte)]);
    plot([lim_min, lim_max], [lim_min, lim_max], 'k--', 'LineWidth', 2);
    
    % Calcular R² para esta fonte
    R2_fonte = calcular_r2(P_thorlabs(idx_fonte), P_modelo(idx_fonte));
    RMSE_fonte = sqrt(mean((P_thorlabs(idx_fonte) - P_modelo(idx_fonte)).^2));
    
    xlabel('ThorLabs [u.a.]', 'FontSize', 11);
    ylabel('Modelo (Ordem 4) [u.a.]', 'FontSize', 11);
    title(sprintf('%s\nR² = %.4f, RMSE = %.0f', titulos{fonte_idx}, R2_fonte, RMSE_fonte), ...
        'FontSize', 12, 'FontWeight', 'bold');
    
    axis equal;
    xlim([lim_min, lim_max]);
    ylim([lim_min, lim_max]);
    set(gca, 'FontSize', 10);
end

sgtitle('Modelo Polinomial Ordem 4: ThorLabs vs OSA Visível', ...
    'FontSize', 14, 'FontWeight', 'bold');

output_file = 'Modelo_Ordem4_Comparacao.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico salvo em: %s\n', output_file);

% Figura 2: Resíduos
figure('Position', [100, 100, 1400, 500]);

residuos = P_thorlabs - P_modelo;

for fonte_idx = 1:3
    fonte = fontes{fonte_idx};
    idx_fonte = strcmp(fonte_labels, fonte);
    
    subplot(1, 3, fonte_idx);
    hold on; grid on;
    
    scatter(P_thorlabs(idx_fonte), residuos(idx_fonte), 60, ...
        cores_plot(fonte_idx,:), 'filled', 'MarkerFaceAlpha', 0.6);
    
    plot([min(P_thorlabs), max(P_thorlabs)], [0, 0], 'k--', 'LineWidth', 2);
    
    xlabel('ThorLabs [u.a.]', 'FontSize', 11);
    ylabel('Resíduo [u.a.]', 'FontSize', 11);
    title(titulos{fonte_idx}, 'FontSize', 12, 'FontWeight', 'bold');
    set(gca, 'FontSize', 10);
end

sgtitle('Análise de Resíduos - Modelo Ordem 4', 'FontSize', 14, 'FontWeight', 'bold');

output_file = 'Modelo_Ordem4_Residuos.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico salvo em: %s\n', output_file);

% Figura 3: Resposta espectral
figure('Position', [100, 100, 1400, 900]);

lambda_test_norm = linspace(0, 1, 100)';
lambda_test = lambda_test_norm * (lambda_max - lambda_min) + lambda_min;

intensidades_teste = [
    quantile(Pr_osa, 0.25), quantile(Pg_osa, 0.25), quantile(Pb_osa, 0.25);
    quantile(Pr_osa, 0.50), quantile(Pg_osa, 0.50), quantile(Pb_osa, 0.50);
    quantile(Pr_osa, 0.75), quantile(Pg_osa, 0.75), quantile(Pb_osa, 0.75)
];

niveis = {'Baixa Intensidade', 'Média Intensidade', 'Alta Intensidade'};
cores_nivel = {'b', 'g', 'r'};

for nivel_idx = 1:3
    subplot(3, 1, nivel_idx);
    hold on; grid on;
    
    Pr_test = repmat(intensidades_teste(nivel_idx, 1), length(lambda_test_norm), 1);
    Pg_test = repmat(intensidades_teste(nivel_idx, 2), length(lambda_test_norm), 1);
    Pb_test = repmat(intensidades_teste(nivel_idx, 3), length(lambda_test_norm), 1);
    
    X_test = [Pr_test, Pr_test.*lambda_test_norm, Pr_test.*(lambda_test_norm.^2), ...
              Pr_test.*(lambda_test_norm.^3), Pr_test.*(lambda_test_norm.^4), ...
              Pg_test, Pg_test.*lambda_test_norm, Pg_test.*(lambda_test_norm.^2), ...
              Pg_test.*(lambda_test_norm.^3), Pg_test.*(lambda_test_norm.^4), ...
              Pb_test, Pb_test.*lambda_test_norm, Pb_test.*(lambda_test_norm.^2), ...
              Pb_test.*(lambda_test_norm.^3), Pb_test.*(lambda_test_norm.^4), ...
              ones(size(Pr_test)), lambda_test_norm, lambda_test_norm.^2, ...
              lambda_test_norm.^3, lambda_test_norm.^4];
    
    P_test = X_test * beta;
    
    plot(lambda_test, P_test, 'LineWidth', 3, 'Color', cores_nivel{nivel_idx});
    
    xlabel('λ [nm]', 'FontSize', 11);
    ylabel('P(λ) predito [u.a.]', 'FontSize', 11);
    title(sprintf('%s (Pr=%.1f, Pg=%.1f, Pb=%.1f)', niveis{nivel_idx}, ...
        intensidades_teste(nivel_idx, 1), intensidades_teste(nivel_idx, 2), ...
        intensidades_teste(nivel_idx, 3)), 'FontSize', 11, 'FontWeight', 'bold');
    set(gca, 'FontSize', 10);
end

sgtitle('Resposta Espectral - Modelo Ordem 4', 'FontSize', 14, 'FontWeight', 'bold');

output_file = 'Modelo_Ordem4_Resposta.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico salvo em: %s\n', output_file);

%% Salvar resultados
fprintf('\n=== Salvando resultados ===\n');

resultados.beta = beta;
resultados.R2 = R2;
resultados.RMSE = RMSE;
resultados.MAE = MAE;
resultados.erro_perc = erro_perc;
resultados.P_thorlabs = P_thorlabs;
resultados.P_modelo = P_modelo;
resultados.lambda_thorlabs = lambda_thorlabs;
resultados.lambda_osa = lambda_osa;
resultados.Pr_osa = Pr_osa;
resultados.Pg_osa = Pg_osa;
resultados.Pb_osa = Pb_osa;
resultados.fonte_labels = fonte_labels;
resultados.duty_cycle = duty_cycle;
resultados.tomada_id = tomada_id;
resultados.normalizacao.lambda_min = lambda_min;
resultados.normalizacao.lambda_max = lambda_max;

save('resultados_modelo_ordem4.mat', 'resultados');
fprintf('Resultados salvos em: resultados_modelo_ordem4.mat\n');

% Salvar parâmetros em texto
fid = fopen('parametros_modelo_ordem4.txt', 'w');
fprintf(fid, 'Modelo Polinomial de Ordem 4\n');
fprintf(fid, '============================\n\n');
fprintf(fid, 'P(λ) = Σ(aᵢ·λⁱ)·Pr + Σ(bᵢ·λⁱ)·Pg + Σ(cᵢ·λⁱ)·Pb + Σ(dᵢ·λⁱ)\n');
fprintf(fid, 'onde i = 0, 1, 2, 3, 4 e λ está normalizado em [0,1]\n\n');

fprintf(fid, 'Parâmetros:\n');
fprintf(fid, '  Canal R (Pr): a₀=%.6f, a₁=%.6f, a₂=%.6f, a₃=%.6f, a₄=%.6f\n', ...
    beta(1), beta(2), beta(3), beta(4), beta(5));
fprintf(fid, '  Canal G (Pg): b₀=%.6f, b₁=%.6f, b₂=%.6f, b₃=%.6f, b₄=%.6f\n', ...
    beta(6), beta(7), beta(8), beta(9), beta(10));
fprintf(fid, '  Canal B (Pb): c₀=%.6f, c₁=%.6f, c₂=%.6f, c₃=%.6f, c₄=%.6f\n', ...
    beta(11), beta(12), beta(13), beta(14), beta(15));
fprintf(fid, '  Offset:       d₀=%.6f, d₁=%.6f, d₂=%.6f, d₃=%.6f, d₄=%.6f\n\n', ...
    beta(16), beta(17), beta(18), beta(19), beta(20));

fprintf(fid, 'Métricas:\n');
fprintf(fid, '  R² = %.6f\n', R2);
fprintf(fid, '  RMSE = %.2f\n', RMSE);
fprintf(fid, '  MAE = %.2f\n', MAE);
fprintf(fid, '  Erro percentual médio = %.2f%%\n\n', erro_perc);

fprintf(fid, 'Normalização:\n');
fprintf(fid, '  λ_norm = (λ - %.2f) / (%.2f - %.2f)\n', lambda_min, lambda_max, lambda_min);
fprintf(fid, '\nDados:\n');
fprintf(fid, '  Total de amostras: %d\n', length(P_thorlabs));
fprintf(fid, '  Faixa de λ: [%.2f - %.2f] nm\n', lambda_min, lambda_max);

fclose(fid);
fprintf('Parâmetros salvos em: parametros_modelo_ordem4.txt\n');

fprintf('\n=== Modelagem Ordem 4 concluída! ===\n');

%% Função auxiliar
function R2 = calcular_r2(y_obs, y_pred)
    SS_res = sum((y_obs - y_pred).^2);
    SS_tot = sum((y_obs - mean(y_obs)).^2);
    R2 = 1 - (SS_res / SS_tot);
end
