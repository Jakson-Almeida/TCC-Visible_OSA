% modelagem_espectral.m
% Script para modelagem ESPECTRAL do OSA Visível em relação ao ThorLabs
% 
% Objetivo: Criar um modelo genérico que funcione para QUALQUER comprimento de onda,
%           não limitado apenas aos LEDs verde, vermelho e azul.
%
% Modelos testados:
%   1. Linear simples: P(λ) = a·Pr + b·Pg + c·Pb + d + e·λ
%   2. Coeficientes lineares em λ: P(λ) = (a₀+a₁·λ)·Pr + (b₀+b₁·λ)·Pg + (c₀+c₁·λ)·Pb + (d₀+d₁·λ)
%   3. Coeficientes quadráticos em λ: P(λ) = (a₀+a₁·λ+a₂·λ²)·Pr + ... (similar)
%
% Autor: Jakson Almeida
% Data: 2026-01-29

clear; clc; close all;

%% Configurações
json_file = 'dados_todos_finalmente_completo_2026-02-01T23-19-33.690Z.json';

%% Leitura do JSON
fprintf('=== Modelagem Espectral Genérica ===\n\n');
fprintf('Lendo dados de: %s\n', json_file);

% Ler arquivo JSON
json_text = fileread(json_file);
dados = jsondecode(json_text);

%% Coletar TODOS os dados (todas as cores/comprimentos de onda)
fprintf('\nColetando dados de todas as fontes e comprimentos de onda...\n');

% Arrays para armazenar todos os dados
lambda_thorlabs = [];  % Comprimento de onda ThorLabs [nm]
P_thorlabs = [];       % Intensidade ThorLabs
lambda_osa = [];       % Comprimento de onda OSA [nm]
Pr_osa = [];           % Intensidade canal R (OSA)
Pg_osa = [];           % Intensidade canal G (OSA)
Pb_osa = [];           % Intensidade canal B (OSA)
fonte_labels = {};     % Label da fonte (verde, vermelho, azul)
duty_cycle = [];       % Duty cycle [%]

% Iterar sobre os dados do ThorLabs (referência)
tomadas = fieldnames(dados.data.thorlabs);
for t_idx = 1:length(tomadas)
    tomada = tomadas{t_idx};
    
    % Iterar sobre duty cycles (1-10)
    duty_cycles_campos = fieldnames(dados.data.thorlabs.(tomada));
    for dc_idx = 1:length(duty_cycles_campos)
        dc_campo = duty_cycles_campos{dc_idx};
        dc_valor = str2double(dc_campo);
        
        % Iterar sobre as fontes (green, red, blue)
        fontes = {'green', 'red', 'blue'};
        for fonte_idx = 1:length(fontes)
            fonte = fontes{fonte_idx};
            
            % Verificar se dados existem no ThorLabs
            if ~isfield(dados.data.thorlabs.(tomada).(dc_campo), fonte)
                continue;
            end
            
            thorlabs_data = dados.data.thorlabs.(tomada).(dc_campo).(fonte);
            
            % Verificar se peak_nm e intensity existem e não são vazios
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
            
            % Buscar dados correspondentes do OSA Visível (canal RGB)
            if ~isfield(dados.data.osa_visivel, tomada)
                continue;
            end
            if ~isfield(dados.data.osa_visivel.(tomada), dc_campo)
                continue;
            end
            if ~isfield(dados.data.osa_visivel.(tomada).(dc_campo), '1')
                continue;  % Canal 1 = RGB
            end
            
            osa_data = dados.data.osa_visivel.(tomada).(dc_campo).('1');
            
            if ~isfield(osa_data, fonte)
                continue;
            end
            
            osa_fonte = osa_data.(fonte);
            
            % Verificar se todos os campos existem
            if ~isfield(osa_fonte, 'peak_nm') || ~isfield(osa_fonte, 'intensity')
                continue;
            end
            if isempty(osa_fonte.peak_nm) || isempty(osa_fonte.intensity)
                continue;
            end
            
            lambda_osa_val = str2double(osa_fonte.peak_nm);
            P_osa_val = str2double(osa_fonte.intensity);
            
            if isnan(lambda_osa_val) || isnan(P_osa_val)
                continue;
            end
            
            % Buscar intensidades dos outros canais (R, G, B separados)
            % Canal R (x2)
            Pr_val = NaN;
            if isfield(dados.data.osa_visivel.(tomada).(dc_campo), '2')
                if isfield(dados.data.osa_visivel.(tomada).(dc_campo).('2'), fonte)
                    r_data = dados.data.osa_visivel.(tomada).(dc_campo).('2').(fonte);
                    if isfield(r_data, 'intensity') && ~isempty(r_data.intensity)
                        Pr_val = str2double(r_data.intensity);
                    end
                end
            end
            
            % Canal G (x3)
            Pg_val = NaN;
            if isfield(dados.data.osa_visivel.(tomada).(dc_campo), '3')
                if isfield(dados.data.osa_visivel.(tomada).(dc_campo).('3'), fonte)
                    g_data = dados.data.osa_visivel.(tomada).(dc_campo).('3').(fonte);
                    if isfield(g_data, 'intensity') && ~isempty(g_data.intensity)
                        Pg_val = str2double(g_data.intensity);
                    end
                end
            end
            
            % Canal B (x4)
            Pb_val = NaN;
            if isfield(dados.data.osa_visivel.(tomada).(dc_campo), '4')
                if isfield(dados.data.osa_visivel.(tomada).(dc_campo).('4'), fonte)
                    b_data = dados.data.osa_visivel.(tomada).(dc_campo).('4').(fonte);
                    if isfield(b_data, 'intensity') && ~isempty(b_data.intensity)
                        Pb_val = str2double(b_data.intensity);
                    end
                end
            end
            
            % Apenas adicionar se todos os valores existem
            if ~isnan(Pr_val) && ~isnan(Pg_val) && ~isnan(Pb_val)
                lambda_thorlabs = [lambda_thorlabs; lambda_th];
                P_thorlabs = [P_thorlabs; P_th];
                lambda_osa = [lambda_osa; lambda_osa_val];
                Pr_osa = [Pr_osa; Pr_val];
                Pg_osa = [Pg_osa; Pg_val];
                Pb_osa = [Pb_osa; Pb_val];
                fonte_labels = [fonte_labels; fonte];
                duty_cycle = [duty_cycle; dc_valor];
            end
        end
    end
end

fprintf('  Total de amostras coletadas: %d\n', length(P_thorlabs));
fprintf('  Faixa de λ (ThorLabs): [%.2f - %.2f] nm\n', min(lambda_thorlabs), max(lambda_thorlabs));
fprintf('  Faixa de λ (OSA): [%.2f - %.2f] nm\n', min(lambda_osa), max(lambda_osa));

%% Normalização dos dados para melhor condicionamento numérico
fprintf('\nNormalizando dados...\n');

% Normalizar comprimento de onda para [0, 1]
lambda_min = min(lambda_thorlabs);
lambda_max = max(lambda_thorlabs);
lambda_norm = (lambda_thorlabs - lambda_min) / (lambda_max - lambda_min);

% Estatísticas dos dados
fprintf('  Intensidades ThorLabs: [%.2f - %.2f]\n', min(P_thorlabs), max(P_thorlabs));
fprintf('  Intensidades Pr (OSA): [%.2f - %.2f]\n', min(Pr_osa), max(Pr_osa));
fprintf('  Intensidades Pg (OSA): [%.2f - %.2f]\n', min(Pg_osa), max(Pg_osa));
fprintf('  Intensidades Pb (OSA): [%.2f - %.2f]\n', min(Pb_osa), max(Pb_osa));

%% Modelo 1: Linear simples com λ
% P(λ) = a·Pr + b·Pg + c·Pb + d + e·λ
fprintf('\n=== Modelo 1: Linear Simples com λ ===\n');
fprintf('  P(λ) = a·Pr + b·Pg + c·Pb + d + e·λ\n');

X1 = [Pr_osa, Pg_osa, Pb_osa, ones(size(Pr_osa)), lambda_norm];
beta1 = (X1' * X1) \ (X1' * P_thorlabs);

P_modelo1 = X1 * beta1;
R2_1 = calcular_r2(P_thorlabs, P_modelo1);
RMSE_1 = sqrt(mean((P_thorlabs - P_modelo1).^2));
MAE_1 = mean(abs(P_thorlabs - P_modelo1));

fprintf('\nParâmetros:\n');
fprintf('  a (Pr)     = %.6f\n', beta1(1));
fprintf('  b (Pg)     = %.6f\n', beta1(2));
fprintf('  c (Pb)     = %.6f\n', beta1(3));
fprintf('  d (offset) = %.6f\n', beta1(4));
fprintf('  e (λ)      = %.6f\n', beta1(5));
fprintf('Métricas:\n');
fprintf('  R² = %.6f\n', R2_1);
fprintf('  RMSE = %.2f\n', RMSE_1);
fprintf('  MAE = %.2f\n', MAE_1);

%% Modelo 2: Coeficientes lineares em λ
% P(λ) = (a₀ + a₁·λ)·Pr + (b₀ + b₁·λ)·Pg + (c₀ + c₁·λ)·Pb + (d₀ + d₁·λ)
fprintf('\n=== Modelo 2: Coeficientes Lineares em λ ===\n');
fprintf('  P(λ) = (a₀+a₁·λ)·Pr + (b₀+b₁·λ)·Pg + (c₀+c₁·λ)·Pb + (d₀+d₁·λ)\n');

X2 = [Pr_osa, Pr_osa.*lambda_norm, ...
      Pg_osa, Pg_osa.*lambda_norm, ...
      Pb_osa, Pb_osa.*lambda_norm, ...
      ones(size(Pr_osa)), lambda_norm];
beta2 = (X2' * X2) \ (X2' * P_thorlabs);

P_modelo2 = X2 * beta2;
R2_2 = calcular_r2(P_thorlabs, P_modelo2);
RMSE_2 = sqrt(mean((P_thorlabs - P_modelo2).^2));
MAE_2 = mean(abs(P_thorlabs - P_modelo2));

fprintf('\nParâmetros:\n');
fprintf('  Pr: a₀ = %.6f, a₁ = %.6f\n', beta2(1), beta2(2));
fprintf('  Pg: b₀ = %.6f, b₁ = %.6f\n', beta2(3), beta2(4));
fprintf('  Pb: c₀ = %.6f, c₁ = %.6f\n', beta2(5), beta2(6));
fprintf('  Offset: d₀ = %.6f, d₁ = %.6f\n', beta2(7), beta2(8));
fprintf('Métricas:\n');
fprintf('  R² = %.6f\n', R2_2);
fprintf('  RMSE = %.2f\n', RMSE_2);
fprintf('  MAE = %.2f\n', MAE_2);

%% Modelo 3: Coeficientes quadráticos em λ
% P(λ) = (a₀ + a₁·λ + a₂·λ²)·Pr + (b₀ + b₁·λ + b₂·λ²)·Pg + 
%        (c₀ + c₁·λ + c₂·λ²)·Pb + (d₀ + d₁·λ + d₂·λ²)
fprintf('\n=== Modelo 3: Coeficientes Quadráticos em λ ===\n');
fprintf('  P(λ) = (a₀+a₁·λ+a₂·λ²)·Pr + ... (similar para Pg, Pb)\n');

X3 = [Pr_osa, Pr_osa.*lambda_norm, Pr_osa.*(lambda_norm.^2), ...
      Pg_osa, Pg_osa.*lambda_norm, Pg_osa.*(lambda_norm.^2), ...
      Pb_osa, Pb_osa.*lambda_norm, Pb_osa.*(lambda_norm.^2), ...
      ones(size(Pr_osa)), lambda_norm, lambda_norm.^2];
beta3 = (X3' * X3) \ (X3' * P_thorlabs);

P_modelo3 = X3 * beta3;
R2_3 = calcular_r2(P_thorlabs, P_modelo3);
RMSE_3 = sqrt(mean((P_thorlabs - P_modelo3).^2));
MAE_3 = mean(abs(P_thorlabs - P_modelo3));

fprintf('\nParâmetros:\n');
fprintf('  Pr: a₀ = %.6f, a₁ = %.6f, a₂ = %.6f\n', beta3(1), beta3(2), beta3(3));
fprintf('  Pg: b₀ = %.6f, b₁ = %.6f, b₂ = %.6f\n', beta3(4), beta3(5), beta3(6));
fprintf('  Pb: c₀ = %.6f, c₁ = %.6f, c₂ = %.6f\n', beta3(7), beta3(8), beta3(9));
fprintf('  Offset: d₀ = %.6f, d₁ = %.6f, d₂ = %.6f\n', beta3(10), beta3(11), beta3(12));
fprintf('Métricas:\n');
fprintf('  R² = %.6f\n', R2_3);
fprintf('  RMSE = %.2f\n', RMSE_3);
fprintf('  MAE = %.2f\n', MAE_3);

%% Comparação dos modelos
fprintf('\n=== Comparação dos Modelos ===\n');
fprintf('Modelo 1 (Linear simples): R² = %.6f, RMSE = %.2f\n', R2_1, RMSE_1);
fprintf('Modelo 2 (Linear em λ):    R² = %.6f, RMSE = %.2f\n', R2_2, RMSE_2);
fprintf('Modelo 3 (Quadrático em λ):R² = %.6f, RMSE = %.2f\n', R2_3, RMSE_3);

% Selecionar melhor modelo
[~, melhor_idx] = max([R2_1, R2_2, R2_3]);
modelos_nomes = {'Modelo 1 (Linear simples)', 'Modelo 2 (Linear em λ)', 'Modelo 3 (Quadrático em λ)'};
fprintf('\n✓ Melhor modelo: %s\n', modelos_nomes{melhor_idx});

%% Visualização dos resultados
fprintf('\n=== Gerando gráficos ===\n');

% Figura 1: Comparação dos modelos por fonte
figure('Position', [100, 100, 1400, 500]);

for fonte_idx = 1:3
    fonte = fontes{fonte_idx};
    idx_fonte = strcmp(fonte_labels, fonte);
    
    subplot(1, 3, fonte_idx);
    hold on; grid on;
    
    % Dados reais
    scatter(P_thorlabs(idx_fonte), P_thorlabs(idx_fonte), 30, 'k', 'filled', ...
        'DisplayName', 'Real');
    
    % Modelos
    scatter(P_thorlabs(idx_fonte), P_modelo1(idx_fonte), 20, 'r', 'o', ...
        'DisplayName', sprintf('Modelo 1 (R²=%.3f)', R2_1));
    scatter(P_thorlabs(idx_fonte), P_modelo2(idx_fonte), 20, 'g', '^', ...
        'DisplayName', sprintf('Modelo 2 (R²=%.3f)', R2_2));
    scatter(P_thorlabs(idx_fonte), P_modelo3(idx_fonte), 20, 'b', 's', ...
        'DisplayName', sprintf('Modelo 3 (R²=%.3f)', R2_3));
    
    % Linha 1:1
    plot([min(P_thorlabs), max(P_thorlabs)], [min(P_thorlabs), max(P_thorlabs)], ...
        'k--', 'LineWidth', 1.5, 'DisplayName', 'Ideal (1:1)');
    
    xlabel('ThorLabs [u.a.]', 'FontSize', 11);
    ylabel('Predição [u.a.]', 'FontSize', 11);
    title(sprintf('Fonte: %s', upper(fonte)), 'FontSize', 12, 'FontWeight', 'bold');
    legend('Location', 'northwest', 'FontSize', 8);
    axis equal;
    xlim([min(P_thorlabs), max(P_thorlabs)]);
    ylim([min(P_thorlabs), max(P_thorlabs)]);
end

sgtitle('Comparação dos Modelos Espectrais', 'FontSize', 14, 'FontWeight', 'bold');

output_file = 'Modelo_Espectral_Comparacao.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico salvo em: %s\n', output_file);

% Figura 2: Análise espectral (como o modelo varia com λ)
figure('Position', [100, 100, 1400, 900]);

% Criar grid de comprimentos de onda para visualização
lambda_test_norm = linspace(0, 1, 100)';
lambda_test = lambda_test_norm * (lambda_max - lambda_min) + lambda_min;

% Valores fixos de intensidade OSA (baixo, médio, alto)
intensidades_teste = [
    quantile(Pr_osa, 0.25), quantile(Pg_osa, 0.25), quantile(Pb_osa, 0.25);
    quantile(Pr_osa, 0.50), quantile(Pg_osa, 0.50), quantile(Pb_osa, 0.50);
    quantile(Pr_osa, 0.75), quantile(Pg_osa, 0.75), quantile(Pb_osa, 0.75)
];

niveis = {'Baixa', 'Média', 'Alta'};
cores_plot = {'b', 'g', 'r'};

for nivel_idx = 1:3
    Pr_test = repmat(intensidades_teste(nivel_idx, 1), length(lambda_test_norm), 1);
    Pg_test = repmat(intensidades_teste(nivel_idx, 2), length(lambda_test_norm), 1);
    Pb_test = repmat(intensidades_teste(nivel_idx, 3), length(lambda_test_norm), 1);
    
    % Modelo 1
    subplot(3, 3, (nivel_idx-1)*3 + 1);
    X1_test = [Pr_test, Pg_test, Pb_test, ones(size(Pr_test)), lambda_test_norm];
    P_test1 = X1_test * beta1;
    plot(lambda_test, P_test1, 'LineWidth', 2, 'Color', cores_plot{nivel_idx});
    grid on;
    xlabel('λ [nm]', 'FontSize', 10);
    ylabel('P(λ) predito', 'FontSize', 10);
    title(sprintf('Modelo 1 - %s intensidade', niveis{nivel_idx}), 'FontSize', 11);
    
    % Modelo 2
    subplot(3, 3, (nivel_idx-1)*3 + 2);
    X2_test = [Pr_test, Pr_test.*lambda_test_norm, ...
               Pg_test, Pg_test.*lambda_test_norm, ...
               Pb_test, Pb_test.*lambda_test_norm, ...
               ones(size(Pr_test)), lambda_test_norm];
    P_test2 = X2_test * beta2;
    plot(lambda_test, P_test2, 'LineWidth', 2, 'Color', cores_plot{nivel_idx});
    grid on;
    xlabel('λ [nm]', 'FontSize', 10);
    ylabel('P(λ) predito', 'FontSize', 10);
    title(sprintf('Modelo 2 - %s intensidade', niveis{nivel_idx}), 'FontSize', 11);
    
    % Modelo 3
    subplot(3, 3, (nivel_idx-1)*3 + 3);
    X3_test = [Pr_test, Pr_test.*lambda_test_norm, Pr_test.*(lambda_test_norm.^2), ...
               Pg_test, Pg_test.*lambda_test_norm, Pg_test.*(lambda_test_norm.^2), ...
               Pb_test, Pb_test.*lambda_test_norm, Pb_test.*(lambda_test_norm.^2), ...
               ones(size(Pr_test)), lambda_test_norm, lambda_test_norm.^2];
    P_test3 = X3_test * beta3;
    plot(lambda_test, P_test3, 'LineWidth', 2, 'Color', cores_plot{nivel_idx});
    grid on;
    xlabel('λ [nm]', 'FontSize', 10);
    ylabel('P(λ) predito', 'FontSize', 10);
    title(sprintf('Modelo 3 - %s intensidade', niveis{nivel_idx}), 'FontSize', 11);
end

sgtitle('Resposta Espectral dos Modelos', 'FontSize', 14, 'FontWeight', 'bold');

output_file = 'Modelo_Espectral_Resposta.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico salvo em: %s\n', output_file);

%% Salvar resultados
fprintf('\n=== Salvando resultados ===\n');

% Estrutura com todos os resultados
resultados.modelo1.beta = beta1;
resultados.modelo1.R2 = R2_1;
resultados.modelo1.RMSE = RMSE_1;
resultados.modelo1.MAE = MAE_1;
resultados.modelo1.P_pred = P_modelo1;

resultados.modelo2.beta = beta2;
resultados.modelo2.R2 = R2_2;
resultados.modelo2.RMSE = RMSE_2;
resultados.modelo2.MAE = MAE_2;
resultados.modelo2.P_pred = P_modelo2;

resultados.modelo3.beta = beta3;
resultados.modelo3.R2 = R2_3;
resultados.modelo3.RMSE = RMSE_3;
resultados.modelo3.MAE = MAE_3;
resultados.modelo3.P_pred = P_modelo3;

resultados.dados.lambda_thorlabs = lambda_thorlabs;
resultados.dados.P_thorlabs = P_thorlabs;
resultados.dados.lambda_osa = lambda_osa;
resultados.dados.Pr_osa = Pr_osa;
resultados.dados.Pg_osa = Pg_osa;
resultados.dados.Pb_osa = Pb_osa;
resultados.dados.fonte_labels = fonte_labels;
resultados.dados.duty_cycle = duty_cycle;
resultados.normalizacao.lambda_min = lambda_min;
resultados.normalizacao.lambda_max = lambda_max;

save('resultados_modelagem_espectral.mat', 'resultados');
fprintf('Resultados salvos em: resultados_modelagem_espectral.mat\n');

% Salvar parâmetros em arquivo de texto
fid = fopen('parametros_modelo_espectral.txt', 'w');
fprintf(fid, 'Modelos Espectrais Calibrados\n');
fprintf(fid, '=============================\n\n');

fprintf(fid, '--- Modelo 1: Linear Simples ---\n');
fprintf(fid, 'P(λ) = a·Pr + b·Pg + c·Pb + d + e·λ\n');
fprintf(fid, '  a (Pr)     = %.6f\n', beta1(1));
fprintf(fid, '  b (Pg)     = %.6f\n', beta1(2));
fprintf(fid, '  c (Pb)     = %.6f\n', beta1(3));
fprintf(fid, '  d (offset) = %.6f\n', beta1(4));
fprintf(fid, '  e (λ)      = %.6f\n', beta1(5));
fprintf(fid, 'Métricas: R² = %.6f, RMSE = %.2f, MAE = %.2f\n\n', R2_1, RMSE_1, MAE_1);

fprintf(fid, '--- Modelo 2: Coeficientes Lineares em λ ---\n');
fprintf(fid, 'P(λ) = (a₀+a₁·λ)·Pr + (b₀+b₁·λ)·Pg + (c₀+c₁·λ)·Pb + (d₀+d₁·λ)\n');
fprintf(fid, '  Pr: a₀ = %.6f, a₁ = %.6f\n', beta2(1), beta2(2));
fprintf(fid, '  Pg: b₀ = %.6f, b₁ = %.6f\n', beta2(3), beta2(4));
fprintf(fid, '  Pb: c₀ = %.6f, c₁ = %.6f\n', beta2(5), beta2(6));
fprintf(fid, '  Offset: d₀ = %.6f, d₁ = %.6f\n', beta2(7), beta2(8));
fprintf(fid, 'Métricas: R² = %.6f, RMSE = %.2f, MAE = %.2f\n\n', R2_2, RMSE_2, MAE_2);

fprintf(fid, '--- Modelo 3: Coeficientes Quadráticos em λ ---\n');
fprintf(fid, 'P(λ) = (a₀+a₁·λ+a₂·λ²)·Pr + ... (similar)\n');
fprintf(fid, '  Pr: a₀ = %.6f, a₁ = %.6f, a₂ = %.6f\n', beta3(1), beta3(2), beta3(3));
fprintf(fid, '  Pg: b₀ = %.6f, b₁ = %.6f, b₂ = %.6f\n', beta3(4), beta3(5), beta3(6));
fprintf(fid, '  Pb: c₀ = %.6f, c₁ = %.6f, c₂ = %.6f\n', beta3(7), beta3(8), beta3(9));
fprintf(fid, '  Offset: d₀ = %.6f, d₁ = %.6f, d₂ = %.6f\n', beta3(10), beta3(11), beta3(12));
fprintf(fid, 'Métricas: R² = %.6f, RMSE = %.2f, MAE = %.2f\n\n', R2_3, RMSE_3, MAE_3);

fprintf(fid, '\nNormalização:\n');
fprintf(fid, '  λ normalizado = (λ - %.2f) / (%.2f - %.2f)\n', lambda_min, lambda_max, lambda_min);
fprintf(fid, '\nDados:\n');
fprintf(fid, '  Total de amostras: %d\n', length(P_thorlabs));
fprintf(fid, '  Faixa de λ: [%.2f - %.2f] nm\n', lambda_min, lambda_max);

fclose(fid);
fprintf('Parâmetros salvos em: parametros_modelo_espectral.txt\n');

fprintf('\n=== Modelagem Espectral concluída! ===\n');

%% Função auxiliar

function R2 = calcular_r2(y_obs, y_pred)
    % Calcula o coeficiente de determinação R²
    SS_res = sum((y_obs - y_pred).^2);
    SS_tot = sum((y_obs - mean(y_obs)).^2);
    R2 = 1 - (SS_res / SS_tot);
end
