% modelagem_com_saturacao.m
% Script para modelagem do OSA Visível em relação ao ThorLabs
% - Verde e Azul: Modelo linear P(λ) = a·Pr + b·Pg + c·Pb + d
% - Vermelho: Modelo com saturação (Michaelis-Menten)
%             P(λ) = A·x / (B + x), onde x = a·Pr + b·Pg + c·Pb + d
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
fprintf('=== Modelagem com Saturação para Vermelho ===\n\n');
fprintf('Lendo dados de: %s\n', json_file);
json_text = fileread(json_file);
data = jsondecode(json_text);

%% Coletar todos os dados para cada cor
fprintf('\nColetando dados...\n');

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

%% Resolver modelos
fprintf('\n=== Calculando parâmetros dos modelos ===\n');

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
    
    if strcmp(cor, 'red')
        %% Modelo com saturação para VERMELHO (Michaelis-Menten)
        % Modelo: P(λ) = A * x / (B + x)
        % onde x = a·Pr + b·Pg + c·Pb + d
        
        % Passo 1: Estimativa inicial usando modelo linear
        X_linear = [Pr, Pg, Pb, ones(size(Pr))];
        beta_init = (X_linear' * X_linear) \ (X_linear' * Y);
        x_linear = X_linear * beta_init;
        
        % Passo 2: Estimativa melhorada de A e B usando análise dos dados
        % A deve ser o platô (valor máximo esperado)
        % Estimar A a partir dos dados de maior intensidade
        [Y_sorted, idx_sorted] = sort(Y);
        top_20_percent = round(0.2 * length(Y));
        A_init = mean(Y_sorted(end-top_20_percent+1:end)) * 1.15;
        
        % B é o valor de x onde P = A/2
        % Usar transformação de Lineweaver-Burk: 1/P = B/(A*x) + 1/A
        % Mas de forma mais simples: estimar B pelo range de x
        x_min = min(x_linear);
        x_max = max(x_linear);
        x_range = x_max - x_min;
        B_init = x_range * 0.5;  % B na metade do range
        
        % Se B_init for muito pequeno, ajustar
        if B_init < x_range * 0.1
            B_init = x_range * 0.3;
        end
        
        params_init = [beta_init(1); beta_init(2); beta_init(3); beta_init(4); A_init; B_init];
        
        fprintf('  Inicialização:\n');
        fprintf('    a=%.2f, b=%.2f, c=%.2f, d=%.2f\n', beta_init(1), beta_init(2), beta_init(3), beta_init(4));
        fprintf('    A (platô estimado)=%.0f\n', A_init);
        fprintf('    B (meia-sat estimada)=%.0f\n', B_init);
        fprintf('    x_range=[%.0f, %.0f]\n', x_min, x_max);
        
        % Função objetivo (soma dos quadrados dos resíduos)
        objetivo = @(params) sum((Y - modelo_saturacao(params, Pr, Pg, Pb)).^2);
        
        % Otimização (com restrições: A > 0, B > 0)
        % Bounds mais razoáveis baseados nos dados
        lb = [beta_init(1)*0.1; beta_init(2)*0.1; beta_init(3)*0.1; -Inf; max(Y)*0.5; x_range*0.01];
        ub = [beta_init(1)*10; beta_init(2)*10; beta_init(3)*10; Inf; max(Y)*3; x_range*5];
        
        options = optimoptions('fmincon', 'Display', 'off', 'MaxIterations', 2000, ...
            'MaxFunctionEvaluations', 10000, 'OptimalityTolerance', 1e-8);
        
        try
            [params_opt, fval, exitflag, output] = fmincon(objetivo, params_init, [], [], [], [], lb, ub, [], options);
            
            a = params_opt(1);
            b = params_opt(2);
            c = params_opt(3);
            d = params_opt(4);
            A = params_opt(5);
            B = params_opt(6);
            
            fprintf('  Otimização: exitflag=%d, iterações=%d\n', exitflag, output.iterations);
            
            % Calcular P(λ) usando o modelo com saturação
            P_modelo = modelo_saturacao(params_opt, Pr, Pg, Pb);
            
            % Calcular x para análise
            x_valores = a * Pr + b * Pg + c * Pb + d;
            
            % Validar solução
            fprintf('  Validação do modelo:\n');
            fprintf('    x_min = %.2f, x_max = %.2f\n', min(x_valores), max(x_valores));
            fprintf('    A (platô) = %.2f\n', A);
            fprintf('    B (meia-saturação) = %.2f\n', B);
            fprintf('    B / x_medio = %.4f ', B / mean(x_valores));
            
            if B / mean(x_valores) > 10
                fprintf('⚠️  Modelo comporta-se como LINEAR (B >> x)\n');
            elseif B / mean(x_valores) < 0.1
                fprintf('⚠️  Saturação extrema (B << x)\n');
            else
                fprintf('✓ Faixa adequada de saturação\n');
            end
            
            % Calcular métricas de erro
            R2 = calcular_r2(Y, P_modelo);
            RMSE = sqrt(mean((Y - P_modelo).^2));
            MAE = mean(abs(Y - P_modelo));
            erro_percentual_medio = mean(abs((Y - P_modelo) ./ Y)) * 100;
            
            % Comparar com modelo linear
            P_linear = X_linear * beta_init;
            R2_linear = calcular_r2(Y, P_linear);
            RMSE_linear = sqrt(mean((Y - P_linear).^2));
            
            fprintf('  Comparação local:\n');
            fprintf('    Linear:    R²=%.6f, RMSE=%.2f\n', R2_linear, RMSE_linear);
            fprintf('    Saturação: R²=%.6f, RMSE=%.2f\n', R2, RMSE);
            
            % Decidir qual modelo usar baseado no desempenho
            if R2 > R2_linear && RMSE < RMSE_linear
                fprintf('  ✓ Modelo de saturação é melhor!\n');
                usar_saturacao = true;
            else
                fprintf('  ⚠️  Modelo linear é melhor - usando linear\n');
                usar_saturacao = false;
            end
            
            % Armazenar resultados
            if usar_saturacao
                resultados.(cor).modelo = 'saturacao';
            else
                % Usar modelo linear ao invés de saturação
                resultados.(cor).modelo = 'linear';
                a = beta_init(1);
                b = beta_init(2);
                c = beta_init(3);
                d = beta_init(4);
                P_modelo = P_linear;
                R2 = R2_linear;
                RMSE = RMSE_linear;
                MAE = mean(abs(Y - P_modelo));
                erro_percentual_medio = mean(abs((Y - P_modelo) ./ Y)) * 100;
                A = NaN;
                B = NaN;
            end
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
            
            % Exibir resultados finais
            fprintf('\nModelo Final Escolhido: %s\n', resultados.(cor).modelo);
            if usar_saturacao
                fprintf('  P(λ) = A·x / (B + x)\n');
                fprintf('  onde x = %.4f·Pr + %.4f·Pg + %.4f·Pb + %.4f\n', a, b, c, d);
                fprintf('  A = %.2f, B = %.2f\n', A, B);
            else
                fprintf('  P(λ) = %.4f·Pr + %.4f·Pg + %.4f·Pb + %.4f\n', a, b, c, d);
            end
            fprintf('Métricas:\n');
            fprintf('  R² = %.6f\n', R2);
            fprintf('  RMSE = %.2f\n', RMSE);
            fprintf('  MAE = %.2f\n', MAE);
            fprintf('  Erro percentual médio = %.2f%%\n', erro_percentual_medio);
            
        catch ME
            fprintf('  ERRO na otimização: %s\n', ME.message);
            fprintf('  Usando modelo linear como fallback.\n');
            
            % Fallback para modelo linear
            a = beta_init(1);
            b = beta_init(2);
            c = beta_init(3);
            d = beta_init(4);
            P_modelo = X_linear * beta_init;
            
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
            resultados.(cor).exitflag = -999;
            
            fprintf('\nModelo Final: Linear (fallback)\n');
            fprintf('  P(λ) = %.4f·Pr + %.4f·Pg + %.4f·Pb + %.4f\n', a, b, c, d);
            fprintf('Métricas:\n');
            fprintf('  R² = %.6f\n', R2);
            fprintf('  RMSE = %.2f\n', RMSE);
            fprintf('  MAE = %.2f\n', MAE);
            fprintf('  Erro percentual médio = %.2f%%\n', erro_percentual_medio);
        end
        
    else
        %% Modelo LINEAR para VERDE e AZUL
        % Montar matriz de design [Pr, Pg, Pb, 1]
        X = [Pr, Pg, Pb, ones(size(Pr))];
        
        % Resolver sistema usando mínimos quadrados
        beta = (X' * X) \ (X' * Y);
        
        a = beta(1);
        b = beta(2);
        c = beta(3);
        d = beta(4);
        
        % Calcular P(λ) usando o modelo linear
        P_modelo = X * beta;
        
        % Calcular métricas de erro
        R2 = calcular_r2(Y, P_modelo);
        RMSE = sqrt(mean((Y - P_modelo).^2));
        MAE = mean(abs(Y - P_modelo));
        erro_percentual_medio = mean(abs((Y - P_modelo) ./ Y)) * 100;
        
        % Armazenar resultados
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
        
        % Exibir resultados
        fprintf('Modelo: P(λ) = %.4f·Pr + %.4f·Pg + %.4f·Pb + %.4f\n', a, b, c, d);
        fprintf('Métricas:\n');
        fprintf('  R² = %.6f\n', R2);
        fprintf('  RMSE = %.2f\n', RMSE);
        fprintf('  MAE = %.2f\n', MAE);
        fprintf('  Erro percentual médio = %.2f%%\n', erro_percentual_medio);
    end
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
    
    % Título com tipo de modelo
    if strcmp(resultados.(cor).modelo, 'saturacao')
        title_str = sprintf('LED %s (Saturação)', cor_nome);
    else
        title_str = sprintf('LED %s (Linear)', cor_nome);
    end
    title(title_str, 'FontSize', 12, 'FontWeight', 'bold');
    
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

% Título adaptativo baseado no modelo escolhido para vermelho
if strcmp(resultados.red.modelo, 'saturacao')
    titulo_geral = 'Modelo com Saturação (Vermelho) e Linear (Verde/Azul)';
else
    titulo_geral = 'Modelo Linear para Todas as Cores (Saturação não melhorou vermelho)';
end
sgtitle(titulo_geral, 'FontSize', 14, 'FontWeight', 'bold');

% Salvar figura
output_file = 'Modelo_Saturacao_Comparacao.png';
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
    
    % Título com tipo de modelo
    if strcmp(resultados.(cor).modelo, 'saturacao')
        title_str = sprintf('LED %s (Saturação)', cor_nome);
    else
        title_str = sprintf('LED %s (Linear)', cor_nome);
    end
    title(title_str, 'FontSize', 12, 'FontWeight', 'bold');
    
    grid on;
    set(gca, 'FontSize', 10);
    hold off;
end

% Título adaptativo para resíduos
if strcmp(resultados.red.modelo, 'saturacao')
    titulo_residuos = 'Análise de Resíduos - Modelo com Saturação (Vermelho)';
else
    titulo_residuos = 'Análise de Resíduos - Modelo Linear';
end
sgtitle(titulo_residuos, 'FontSize', 14, 'FontWeight', 'bold');

% Salvar figura
output_file = 'Modelo_Saturacao_Residuos.png';
print(output_file, '-dpng', '-r300');
fprintf('Gráfico salvo em: %s\n', output_file);

%% Comparação com modelo linear anterior (para vermelho)
fprintf('\n=== Resumo Final: LED Vermelho ===\n');

% Calcular modelo linear para vermelho
Y_red = dados_cor.red.P_thorlabs;
Pr_red = dados_cor.red.Pr_osa;
Pg_red = dados_cor.red.Pg_osa;
Pb_red = dados_cor.red.Pb_osa;

X_red = [Pr_red, Pg_red, Pb_red, ones(size(Pr_red))];
beta_red_linear = (X_red' * X_red) \ (X_red' * Y_red);
P_red_linear = X_red * beta_red_linear;
R2_red_linear = calcular_r2(Y_red, P_red_linear);
RMSE_red_linear = sqrt(mean((Y_red - P_red_linear).^2));

fprintf('Modelo Linear puro:\n');
fprintf('  R² = %.6f, RMSE = %.2f\n', R2_red_linear, RMSE_red_linear);

fprintf('\nModelo escolhido: %s\n', upper(resultados.red.modelo));
fprintf('  R² = %.6f, RMSE = %.2f\n', resultados.red.R2, resultados.red.RMSE);

if strcmp(resultados.red.modelo, 'saturacao')
    fprintf('\n✓ Modelo de saturação oferece melhoria!\n');
    fprintf('  ΔR² = %.6f (%.2f%% melhor)\n', resultados.red.R2 - R2_red_linear, ...
        (resultados.red.R2 - R2_red_linear) / R2_red_linear * 100);
    fprintf('  ΔRMSE = %.2f (%.2f%% redução)\n', RMSE_red_linear - resultados.red.RMSE, ...
        (RMSE_red_linear - resultados.red.RMSE) / RMSE_red_linear * 100);
else
    fprintf('\n⚠️  Modelo linear foi mantido (saturação não melhorou)\n');
end

%% Salvar resultados
fprintf('\n=== Salvando resultados ===\n');

% Salvar em arquivo MAT
save('resultados_modelagem_saturacao.mat', 'resultados', 'dados_cor');
fprintf('Resultados salvos em: resultados_modelagem_saturacao.mat\n');

% Salvar parâmetros em arquivo de texto
fid = fopen('parametros_modelo_saturacao.txt', 'w');
fprintf(fid, 'Modelos Calibrados:\n');
fprintf(fid, '- Verde e Azul: Linear P(lambda) = a*Pr + b*Pg + c*Pb + d\n');
fprintf(fid, '- Vermelho: Saturacao P(lambda) = A*x/(B+x), x = a*Pr + b*Pg + c*Pb + d\n\n');

fprintf(fid, 'Parâmetros:\n\n');

for cor_idx = 1:length(cores)
    cor = cores{cor_idx};
    cor_nome = cor_nomes{cor_idx};
    
    fprintf(fid, '--- %s ---\n', cor_nome);
    fprintf(fid, 'Modelo: %s\n', resultados.(cor).modelo);
    fprintf(fid, '  a (ganho Pr) = %.6f\n', resultados.(cor).a);
    fprintf(fid, '  b (ganho Pg) = %.6f\n', resultados.(cor).b);
    fprintf(fid, '  c (ganho Pb) = %.6f\n', resultados.(cor).c);
    fprintf(fid, '  d (offset)   = %.6f\n', resultados.(cor).d);
    
    if strcmp(resultados.(cor).modelo, 'saturacao')
        fprintf(fid, '  A (plato)    = %.2f\n', resultados.(cor).A);
        fprintf(fid, '  B (K_m)      = %.2f\n', resultados.(cor).B);
    end
    
    fprintf(fid, 'Metricas:\n');
    fprintf(fid, '  R²   = %.6f\n', resultados.(cor).R2);
    fprintf(fid, '  RMSE = %.2f\n', resultados.(cor).RMSE);
    fprintf(fid, '  MAE  = %.2f\n', resultados.(cor).MAE);
    fprintf(fid, '  Erro = %.2f%%\n\n', resultados.(cor).erro_perc);
end

fclose(fid);
fprintf('Parâmetros salvos em: parametros_modelo_saturacao.txt\n');

fprintf('\n=== Modelagem concluída! ===\n');

%% Funções auxiliares

function P = modelo_saturacao(params, Pr, Pg, Pb)
    % Modelo de saturação: P(λ) = A * x / (B + x)
    % onde x = a·Pr + b·Pg + c·Pb + d
    
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
    % Calcula o coeficiente de determinação R²
    SS_res = sum((y_obs - y_pred).^2);
    SS_tot = sum((y_obs - mean(y_obs)).^2);
    R2 = 1 - (SS_res / SS_tot);
end
