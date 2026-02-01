% modelagem_saturacao_melhorada.m
% Script melhorado para modelagem com saturação do LED vermelho
% Correções:
% - Normalização dos dados para melhor condicionamento numérico
% - Inicialização mais robusta
% - Bounds mais adequados
% - Validação da convergência
%
% Autor: Jakson Almeida
% Data: 2026-02-01

clear; close all; clc;

%% Configurações
json_file = 'dados_todos_finalmente_completo_2026-02-01T23-19-33.690Z.json';

if ~exist(json_file, 'file')
    error('Arquivo JSON não encontrado: %s', json_file);
end

%% Leitura do JSON
fprintf('=== Modelagem com Saturação Melhorada ===\n\n');
fprintf('Lendo dados de: %s\n', json_file);
json_text = fileread(json_file);
data = jsondecode(json_text);

%% Coletar dados
fprintf('\nColetando dados...\n');

cores = {'green', 'red', 'blue'};
cor_nomes = {'Verde', 'Vermelho', 'Azul'};
dados_cor = struct();

for cor_idx = 1:length(cores)
    cor = cores{cor_idx};
    
    P_thorlabs = [];
    Pr_osa = [];
    Pg_osa = [];
    Pb_osa = [];
    
    for tomada = 1:5
        tomada_str = sprintf('x%d', tomada);
        
        if ~isfield(data.data.thorlabs, tomada_str) || ...
           ~isfield(data.data.osa_visivel, tomada_str)
            continue;
        end
        
        thorlabs_tomada = data.data.thorlabs.(tomada_str);
        osa_tomada = data.data.osa_visivel.(tomada_str);
        
        for dc = 1:10
            dc_str = sprintf('x%d', dc);
            
            if ~isfield(thorlabs_tomada, dc_str)
                continue;
            end
            
            thorlabs_dc = thorlabs_tomada.(dc_str);
            p_thor = str2double(thorlabs_dc.(cor).intensity);
            
            if isfield(osa_tomada, 'x2') && isfield(osa_tomada.x2, dc_str)
                pr = str2double(osa_tomada.x2.(dc_str).(cor).intensity);
            else
                pr = NaN;
            end
            
            if isfield(osa_tomada, 'x3') && isfield(osa_tomada.x3, dc_str)
                pg = str2double(osa_tomada.x3.(dc_str).(cor).intensity);
            else
                pg = NaN;
            end
            
            if isfield(osa_tomada, 'x4') && isfield(osa_tomada.x4, dc_str)
                pb = str2double(osa_tomada.x4.(dc_str).(cor).intensity);
            else
                pb = NaN;
            end
            
            if ~isnan(p_thor) && ~isnan(pr) && ~isnan(pg) && ~isnan(pb) && ...
               ~isempty(p_thor) && ~isempty(pr) && ~isempty(pg) && ~isempty(pb)
                P_thorlabs = [P_thorlabs; p_thor];
                Pr_osa = [Pr_osa; pr];
                Pg_osa = [Pg_osa; pg];
                Pb_osa = [Pb_osa; pb];
            end
        end
    end
    
    dados_cor.(cor).P_thorlabs = P_thorlabs;
    dados_cor.(cor).Pr_osa = Pr_osa;
    dados_cor.(cor).Pg_osa = Pg_osa;
    dados_cor.(cor).Pb_osa = Pb_osa;
    dados_cor.(cor).n_amostras = length(P_thorlabs);
    
    fprintf('  %s: %d amostras coletadas\n', cor_nomes{cor_idx}, length(P_thorlabs));
end

%% Resolver modelos
fprintf('\n=== Calculando parâmetros dos modelos ===\n');

resultados = struct();

for cor_idx = 1:length(cores)
    cor = cores{cor_idx};
    cor_nome = cor_nomes{cor_idx};
    
    fprintf('\n--- LED %s ---\n', cor_nome);
    
    Y = dados_cor.(cor).P_thorlabs;
    Pr = dados_cor.(cor).Pr_osa;
    Pg = dados_cor.(cor).Pg_osa;
    Pb = dados_cor.(cor).Pb_osa;
    
    if strcmp(cor, 'red')
        %% Modelo com saturação MELHORADO para VERMELHO
        
        % Passo 1: Normalizar dados para melhor condicionamento
        Y_mean = mean(Y);
        Y_std = std(Y);
        Y_norm = (Y - Y_mean) / Y_std;
        
        Pr_mean = mean(Pr);
        Pr_std = std(Pr);
        Pr_norm = (Pr - Pr_mean) / Pr_std;
        
        Pg_mean = mean(Pg);
        Pg_std = std(Pg);
        Pg_norm = (Pg - Pg_mean) / Pg_std;
        
        Pb_mean = mean(Pb);
        Pb_std = std(Pb);
        Pb_norm = (Pb - Pb_mean) / Pb_std;
        
        % Passo 2: Estimativa inicial usando modelo linear nos dados normalizados
        X_linear = [Pr_norm, Pg_norm, Pb_norm, ones(size(Pr_norm))];
        beta_init = (X_linear' * X_linear) \ (X_linear' * Y_norm);
        x_linear_norm = X_linear * beta_init;
        
        % Passo 3: Inicialização robusta para modelo de saturação
        % Parâmetros: [a, b, c, d, A, B] em escala normalizada
        A_init = max(Y_norm) * 1.2;  % 20% acima do máximo
        B_init = mean(x_linear_norm);  % Ponto médio
        
        % Se B_init for negativo ou muito pequeno, ajustar
        if B_init <= 0
            B_init = std(x_linear_norm);
        end
        
        params_init = [beta_init(1); beta_init(2); beta_init(3); beta_init(4); A_init; B_init];
        
        fprintf('  Inicialização (normalizada):\n');
        fprintf('    a=%.4f, b=%.4f, c=%.4f, d=%.4f\n', beta_init(1), beta_init(2), beta_init(3), beta_init(4));
        fprintf('    A=%.4f, B=%.4f\n', A_init, B_init);
        
        % Função objetivo (soma dos quadrados dos resíduos)
        objetivo = @(params) sum((Y_norm - modelo_saturacao_norm(params, Pr_norm, Pg_norm, Pb_norm)).^2);
        
        % Bounds mais restritivos e realistas (escala normalizada)
        lb = [-10; -10; -10; -10; 0.1; 0.01];  % A > 0.1, B > 0.01
        ub = [10; 10; 10; 10; max(Y_norm)*3; 10];  % Limites razoáveis
        
        options = optimoptions('fmincon', ...
            'Display', 'iter', ...
            'MaxIterations', 2000, ...
            'MaxFunctionEvaluations', 10000, ...
            'OptimalityTolerance', 1e-8, ...
            'StepTolerance', 1e-10);
        
        fprintf('  Otimizando...\n');
        
        try
            [params_opt, fval, exitflag] = fmincon(objetivo, params_init, [], [], [], [], lb, ub, [], options);
            
            if exitflag <= 0
                warning('Otimização não convergiu adequadamente (exitflag=%d)', exitflag);
            end
            
            % Desnormalizar parâmetros
            a_norm = params_opt(1);
            b_norm = params_opt(2);
            c_norm = params_opt(3);
            d_norm = params_opt(4);
            A_norm = params_opt(5);
            B_norm = params_opt(6);
            
            % Conversão para escala original:
            % x_original = a·Pr + b·Pg + c·Pb + d
            % x_norm = a_norm·Pr_norm + b_norm·Pg_norm + c_norm·Pb_norm + d_norm
            % x_norm = a_norm·(Pr-Pr_mean)/Pr_std + ... 
            
            a = a_norm * Y_std / Pr_std;
            b = b_norm * Y_std / Pg_std;
            c = c_norm * Y_std / Pb_std;
            d = Y_mean + Y_std * (d_norm - a_norm*Pr_mean/Pr_std - b_norm*Pg_mean/Pg_std - c_norm*Pb_mean/Pb_std);
            
            % Para A e B, a transformação é mais complexa devido à não-linearidade
            % Aproximação: aplicar fator de escala
            A = A_norm * Y_std + Y_mean;
            B = B_norm * Y_std;
            
            % Calcular P(λ) usando o modelo com saturação (escala original)
            P_modelo = modelo_saturacao_original([a; b; c; d; A; B], Pr, Pg, Pb);
            
            % Calcular métricas
            R2 = calcular_r2(Y, P_modelo);
            RMSE = sqrt(mean((Y - P_modelo).^2));
            MAE = mean(abs(Y - P_modelo));
            erro_percentual_medio = mean(abs((Y - P_modelo) ./ Y)) * 100;
            
            % Verificar se o modelo faz sentido
            x_medio = a * mean(Pr) + b * mean(Pg) + c * mean(Pb) + d;
            razao_B_x = B / x_medio;
            
            fprintf('\n  Parâmetros na escala original:\n');
            fprintf('    a = %.4f\n', a);
            fprintf('    b = %.4f\n', b);
            fprintf('    c = %.4f\n', c);
            fprintf('    d = %.4f\n', d);
            fprintf('    A (platô) = %.2f\n', A);
            fprintf('    B (meia-saturação) = %.2f\n', B);
            fprintf('    Razão B/x_médio = %.4f ', razao_B_x);
            
            if razao_B_x > 10
                fprintf('⚠️  B muito grande - comportamento linear\n');
            elseif razao_B_x < 0.1
                fprintf('⚠️  B muito pequeno - saturação extrema\n');
            else
                fprintf('✓ Faixa adequada\n');
            end
            
            resultados.(cor).modelo = 'saturacao';
            resultados.(cor).a = a;
            resultados.(cor).b = b;
            resultados.(cor).c = c;
            resultados.(cor).d = d;
            resultados.(cor).A = A;
            resultados.(cor).B = B;
            resultados.(cor).R2 = R2;
            resultados.(cor).RMSE = RMSE;
            resultados.(cor).MAE = MAE;
            resultados.(cor).erro_perc = erro_percentual_medio;
            resultados.(cor).P_thorlabs = Y;
            resultados.(cor).P_modelo = P_modelo;
            resultados.(cor).exitflag = exitflag;
            
            fprintf('\nMétricas:\n');
            fprintf('  R² = %.6f\n', R2);
            fprintf('  RMSE = %.2f\n', RMSE);
            fprintf('  MAE = %.2f\n', MAE);
            fprintf('  Erro percentual médio = %.2f%%\n', erro_percentual_medio);
            
        catch ME
            fprintf('  ERRO na otimização: %s\n', ME.message);
            fprintf('  Usando modelo linear como fallback.\n');
            
            X_linear = [Pr, Pg, Pb, ones(size(Pr))];
            beta = (X_linear' * X_linear) \ (X_linear' * Y);
            P_modelo = X_linear * beta;
            
            resultados.(cor).modelo = 'linear_fallback';
            resultados.(cor).a = beta(1);
            resultados.(cor).b = beta(2);
            resultados.(cor).c = beta(3);
            resultados.(cor).d = beta(4);
            resultados.(cor).A = NaN;
            resultados.(cor).B = NaN;
            resultados.(cor).R2 = calcular_r2(Y, P_modelo);
            resultados.(cor).RMSE = sqrt(mean((Y - P_modelo).^2));
            resultados.(cor).P_thorlabs = Y;
            resultados.(cor).P_modelo = P_modelo;
            resultados.(cor).exitflag = -999;
        end
        
    else
        %% Modelo LINEAR para VERDE e AZUL
        X = [Pr, Pg, Pb, ones(size(Pr))];
        beta = (X' * X) \ (X' * Y);
        
        a = beta(1);
        b = beta(2);
        c = beta(3);
        d = beta(4);
        
        P_modelo = X * beta;
        
        R2 = calcular_r2(Y, P_modelo);
        RMSE = sqrt(mean((Y - P_modelo).^2));
        MAE = mean(abs(Y - P_modelo));
        erro_percentual_medio = mean(abs((Y - P_modelo) ./ Y)) * 100;
        
        resultados.(cor).modelo = 'linear';
        resultados.(cor).a = a;
        resultados.(cor).b = b;
        resultados.(cor).c = c;
        resultados.(cor).d = d;
        resultados.(cor).A = NaN;
        resultados.(cor).B = NaN;
        resultados.(cor).R2 = R2;
        resultados.(cor).RMSE = RMSE;
        resultados.(cor).MAE = MAE;
        resultados.(cor).erro_perc = erro_percentual_medio;
        resultados.(cor).P_thorlabs = Y;
        resultados.(cor).P_modelo = P_modelo;
        
        fprintf('Modelo: P(λ) = %.4f·Pr + %.4f·Pg + %.4f·Pb + %.4f\n', a, b, c, d);
        fprintf('Métricas:\n');
        fprintf('  R² = %.6f\n', R2);
        fprintf('  RMSE = %.2f\n', RMSE);
        fprintf('  MAE = %.2f\n', MAE);
        fprintf('  Erro percentual médio = %.2f%%\n', erro_percentual_medio);
    end
end

%% Plotar resultados (mesmo código anterior)
fprintf('\n=== Gerando gráficos ===\n');

color_green = [0.2, 0.8, 0.2];
color_red = [0.9, 0.2, 0.2];
color_blue = [0.2, 0.4, 0.9];
cores_plot = {color_green, color_red, color_blue};

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
    
    max_val = max([Y; P_modelo]);
    min_val = min([Y; P_modelo]);
    plot([min_val, max_val], [min_val, max_val], 'k--', 'LineWidth', 1.5);
    
    scatter(Y, P_modelo, 40, cor_plot, 'filled', 'MarkerEdgeColor', 'k', ...
        'MarkerFaceAlpha', 0.6, 'LineWidth', 0.5);
    
    xlabel('ThorLabs (Referência)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('OSA Visível (Modelo)', 'FontSize', 11, 'FontWeight', 'bold');
    
    if strcmp(resultados.(cor).modelo, 'saturacao')
        title_str = sprintf('LED %s (Saturação Melhorada)', cor_nome);
    else
        title_str = sprintf('LED %s (Linear)', cor_nome);
    end
    title(title_str, 'FontSize', 12, 'FontWeight', 'bold');
    
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

sgtitle('Modelo com Saturação Melhorada', 'FontSize', 14, 'FontWeight', 'bold');
output_file = 'Modelo_Saturacao_Melhorada_Comparacao.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico salvo em: %s\n', output_file);

%% Comparação
fprintf('\n=== Comparação: Modelo Linear vs Saturação Melhorada (Vermelho) ===\n');

Y_red = dados_cor.red.P_thorlabs;
Pr_red = dados_cor.red.Pr_osa;
Pg_red = dados_cor.red.Pg_osa;
Pb_red = dados_cor.red.Pb_osa;

X_red = [Pr_red, Pg_red, Pb_red, ones(size(Pr_red))];
beta_red_linear = (X_red' * X_red) \ (X_red' * Y_red);
P_red_linear = X_red * beta_red_linear;
R2_red_linear = calcular_r2(Y_red, P_red_linear);
RMSE_red_linear = sqrt(mean((Y_red - P_red_linear).^2));

fprintf('Modelo Linear:\n');
fprintf('  R² = %.6f\n', R2_red_linear);
fprintf('  RMSE = %.2f\n', RMSE_red_linear);

fprintf('\nModelo com Saturação Melhorada:\n');
fprintf('  R² = %.6f\n', resultados.red.R2);
fprintf('  RMSE = %.2f\n', resultados.red.RMSE);

fprintf('\nMelhoria:\n');
fprintf('  ΔR² = %.6f (%.2f%%)\n', resultados.red.R2 - R2_red_linear, ...
    (resultados.red.R2 - R2_red_linear) / R2_red_linear * 100);
fprintf('  ΔRMSE = %.2f (%.2f%% redução)\n', RMSE_red_linear - resultados.red.RMSE, ...
    (RMSE_red_linear - resultados.red.RMSE) / RMSE_red_linear * 100);

%% Salvar
save('resultados_saturacao_melhorada.mat', 'resultados', 'dados_cor');
fprintf('\nResultados salvos!\n');

%% Funções auxiliares

function P = modelo_saturacao_norm(params, Pr_norm, Pg_norm, Pb_norm)
    a = params(1);
    b = params(2);
    c = params(3);
    d = params(4);
    A = params(5);
    B = params(6);
    
    x = a * Pr_norm + b * Pg_norm + c * Pb_norm + d;
    P = A * x ./ (B + x);
end

function P = modelo_saturacao_original(params, Pr, Pg, Pb)
    a = params(1);
    b = params(2);
    c = params(3);
    d = params(4);
    A = params(5);
    B = params(6);
    
    x = a * Pr + b * Pg + c * Pb + d;
    P = A * x ./ (B + x);
end

function R2 = calcular_r2(y_obs, y_pred)
    SS_res = sum((y_obs - y_pred).^2);
    SS_tot = sum((y_obs - mean(y_obs)).^2);
    R2 = 1 - (SS_res / SS_tot);
end
