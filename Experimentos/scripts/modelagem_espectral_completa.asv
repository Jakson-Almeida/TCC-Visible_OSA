% modelagem_espectral_completa.m
% Script para modelagem espectral completa do OSA Visível em relação ao ThorLabs
% usando 100 comprimentos de onda amostrados na região de interseção
%
% Estratégia:
% 1. Ler todos os espectros completos (ThorLabs e Visible_OSA)
% 2. Calcular média das 5 tomadas para cada equipamento
% 3. Interpolar na interseção espectral (373-681 nm)
% 4. Amostrar 100 comprimentos de onda (w_n)
% 5. Para cada w_n:
%    - Ajustar polinômios de 2ª ordem para canais R, G, B do OSA
%    - Fazer combinação linear: P_ThorLabs = α₁·y_R + α₂·y_G + α₃·y_B
% 6. Validar com picos conhecidos do JSON

clear; clc; close all;

fprintf('=== MODELAGEM ESPECTRAL COMPLETA ===\n\n');

%% PARÂMETROS DE CONFIGURAÇÃO
pasta_base = 'modelagem';
n_tomadas = 5;
fontes = {'Verde', 'Vermelho', 'Azul'};
duty_cycles = 1:10;  % 1% a 10%
n_wavelengths = 100;  % Número de comprimentos de onda a amostrar

% Faixas espectrais (em metros)
lambda_thorlabs_min = 316.5e-9;
lambda_thorlabs_max = 731.2e-9;
lambda_osa_min = 372.7e-9;
lambda_osa_max = 681.0e-9;

% Interseção (região útil)
lambda_min = max(lambda_thorlabs_min, lambda_osa_min);
lambda_max = min(lambda_thorlabs_max, lambda_osa_max);

fprintf('Faixa de análise: %.1f - %.1f nm\n', lambda_min*1e9, lambda_max*1e9);
fprintf('Número de comprimentos de onda: %d\n\n', n_wavelengths);

%% PASSO 1: LEITURA E MÉDIA DOS ESPECTROS DO THORLABS

fprintf('PASSO 1: Lendo espectros do ThorLabs...\n');

% Ler um espectro de referência para obter a grade de comprimentos de onda
arquivo_ref = fullfile(pasta_base, 'ThorLabs', 'peqs_1', 'Verde', '1.txt');
data_ref = readmatrix(arquivo_ref);
lambda_thorlabs_full = data_ref(:, 1);  % Comprimentos de onda em metros

% Filtrar para a região de interseção
idx_intersecao = (lambda_thorlabs_full >= lambda_min) & (lambda_thorlabs_full <= lambda_max);
lambda_grid = lambda_thorlabs_full(idx_intersecao);
n_points_grid = length(lambda_grid);

fprintf('  Grade espectral: %d pontos (%.1f - %.1f nm)\n', ...
    n_points_grid, lambda_grid(1)*1e9, lambda_grid(end)*1e9);

% Estrutura para armazenar médias dos espectros ThorLabs
% thorlabs_mean.(fonte)(duty_cycle, wavelength)
thorlabs_mean = struct();

for i_fonte = 1:length(fontes)
    fonte = fontes{i_fonte};
    thorlabs_mean.(fonte) = zeros(length(duty_cycles), n_points_grid);
    
    for i_duty = 1:length(duty_cycles)
        duty = duty_cycles(i_duty);
        
        % Ler as 5 tomadas e calcular média
        espectros_tomadas = zeros(n_tomadas, n_points_grid);
        
        for tomada = 1:n_tomadas
            arquivo = fullfile(pasta_base, 'ThorLabs', ...
                sprintf('peqs_%d', tomada), fonte, sprintf('%d.txt', duty));
            
            if exist(arquivo, 'file')
                data = readmatrix(arquivo);
                intensidades_full = data(:, 2);
                espectros_tomadas(tomada, :) = intensidades_full(idx_intersecao);
            else
                warning('Arquivo não encontrado: %s', arquivo);
            end
        end
        
        % Média das 5 tomadas
        thorlabs_mean.(fonte)(i_duty, :) = mean(espectros_tomadas, 1);
    end
    
    fprintf('  %s: OK (%d duty cycles)\n', fonte, length(duty_cycles));
end

%% PASSO 2: LEITURA E MÉDIA DOS ESPECTROS DO OSA VISÍVEL

fprintf('\nPASSO 2: Lendo espectros do OSA Visível...\n');

% Ler um espectro de referência para obter a grade original do OSA
arquivo_osa_ref = fullfile(pasta_base, 'Visible_OSA', 'peqs_1', 'Verde', 'spectrum_r_001.txt');
data_osa_ref = readmatrix(arquivo_osa_ref);
lambda_osa_original = data_osa_ref(:, 1);  % Comprimentos de onda em metros

fprintf('  Grade original OSA: %d pontos\n', length(lambda_osa_original));

% Estrutura para armazenar médias dos espectros OSA (antes da interpolação)
% osa_original.(fonte).(canal)(duty_cycle, wavelength_original)
osa_original = struct();
canais = {'r', 'g', 'b'};

for i_fonte = 1:length(fontes)
    fonte = fontes{i_fonte};
    osa_original.(fonte) = struct();
    
    for i_canal = 1:length(canais)
        canal = canais{i_canal};
        n_points_osa = length(lambda_osa_original);
        osa_original.(fonte).(canal) = zeros(length(duty_cycles), n_points_osa);
        
        for i_duty = 1:length(duty_cycles)
            duty = duty_cycles(i_duty);
            
            % Ler as 5 tomadas e calcular média
            espectros_tomadas = zeros(n_tomadas, n_points_osa);
            
            for tomada = 1:n_tomadas
                arquivo = fullfile(pasta_base, 'Visible_OSA', ...
                    sprintf('peqs_%d', tomada), fonte, ...
                    sprintf('spectrum_%s_%03d.txt', canal, duty));
                
                if exist(arquivo, 'file')
                    data = readmatrix(arquivo);
                    espectros_tomadas(tomada, :) = data(:, 2);
                else
                    warning('Arquivo não encontrado: %s', arquivo);
                end
            end
            
            % Média das 5 tomadas
            osa_original.(fonte).(canal)(i_duty, :) = mean(espectros_tomadas, 1);
        end
    end
    
    fprintf('  %s: OK (canais R, G, B)\n', fonte);
end

%% PASSO 3: INTERPOLAÇÃO DO OSA VISÍVEL PARA A GRADE DO THORLABS

fprintf('\nPASSO 3: Interpolando OSA Visível para a grade do ThorLabs...\n');

% Estrutura para armazenar espectros OSA interpolados
% osa_interp.(fonte).(canal)(duty_cycle, wavelength_grid)
osa_interp = struct();

for i_fonte = 1:length(fontes)
    fonte = fontes{i_fonte};
    osa_interp.(fonte) = struct();
    
    for i_canal = 1:length(canais)
        canal = canais{i_canal};
        osa_interp.(fonte).(canal) = zeros(length(duty_cycles), n_points_grid);
        
        for i_duty = 1:length(duty_cycles)
            % Interpolar usando interpolação linear
            intensidades_original = osa_original.(fonte).(canal)(i_duty, :);
            intensidades_interp = interp1(lambda_osa_original, intensidades_original, ...
                lambda_grid, 'linear', 'extrap');
            
            osa_interp.(fonte).(canal)(i_duty, :) = intensidades_interp;
        end
    end
end

fprintf('  Interpolação concluída: %d pontos na grade comum\n', n_points_grid);

%% PASSO 4: AMOSTRAGEM DOS COMPRIMENTOS DE ONDA (w_n)

fprintf('\nPASSO 4: Amostrando %d comprimentos de onda...\n', n_wavelengths);

% Amostrar uniformemente na grade
indices_amostrados = round(linspace(1, n_points_grid, n_wavelengths));
lambda_sampled = lambda_grid(indices_amostrados);

fprintf('  Comprimentos de onda amostrados:\n');
fprintf('    Primeiro: %.2f nm\n', lambda_sampled(1)*1e9);
fprintf('    Último: %.2f nm\n', lambda_sampled(end)*1e9);
fprintf('    Espaçamento médio: %.2f nm\n', ...
    mean(diff(lambda_sampled))*1e9);

%% PASSO 5: MODELAGEM PARA CADA COMPRIMENTO DE ONDA

fprintf('\nPASSO 5: Modelagem para cada comprimento de onda...\n');

% Estrutura para armazenar resultados da modelagem
% Para cada fonte e cada w_n:
%   - Coeficientes dos polinômios de 2ª ordem para R, G, B
%   - Coeficientes alpha da combinação linear
%   - Métricas de qualidade (R², RMSE)

resultados = struct();

for i_fonte = 1:length(fontes)
    fonte = fontes{i_fonte};
    fprintf('\n--- Fonte: %s ---\n', fonte);
    
    resultados.(fonte) = struct();
    resultados.(fonte).lambda = lambda_sampled;
    resultados.(fonte).poly_R = zeros(n_wavelengths, 3);  % [a, b, c] de ax²+bx+c
    resultados.(fonte).poly_G = zeros(n_wavelengths, 3);
    resultados.(fonte).poly_B = zeros(n_wavelengths, 3);
    resultados.(fonte).alpha = zeros(n_wavelengths, 3);  % [α₁, α₂, α₃]
    resultados.(fonte).R2 = zeros(n_wavelengths, 1);
    resultados.(fonte).RMSE = zeros(n_wavelengths, 1);
    
    for i_wn = 1:n_wavelengths
        idx_grid = indices_amostrados(i_wn);
        lambda_nm = lambda_sampled(i_wn) * 1e9;
        
        % Extrair intensidades neste comprimento de onda para todos os duty cycles
        Pr_osa = osa_interp.(fonte).r(:, idx_grid);  % [10x1]
        Pg_osa = osa_interp.(fonte).g(:, idx_grid);
        Pb_osa = osa_interp.(fonte).b(:, idx_grid);
        P_thorlabs = thorlabs_mean.(fonte)(:, idx_grid);
        
        % Verificar se há dados válidos
        valid_idx = ~isnan(Pr_osa) & ~isnan(Pg_osa) & ~isnan(Pb_osa) & ~isnan(P_thorlabs);
        
        if sum(valid_idx) < 5
            fprintf('  λ=%.1f nm: dados insuficientes (%d pontos)\n', ...
                lambda_nm, sum(valid_idx));
            continue;
        end
        
        % Usar apenas dados válidos
        duty_valid = duty_cycles(valid_idx)';
        Pr_osa = Pr_osa(valid_idx);
        Pg_osa = Pg_osa(valid_idx);
        Pb_osa = Pb_osa(valid_idx);
        P_thorlabs = P_thorlabs(valid_idx);
        
        % Ajustar polinômios de 2ª ordem para cada canal
        % y_R(duty) = a_R·duty² + b_R·duty + c_R
        p_R = polyfit(duty_valid, Pr_osa, 2);
        p_G = polyfit(duty_valid, Pg_osa, 2);
        p_B = polyfit(duty_valid, Pb_osa, 2);
        
        % Avaliar os polinômios
        y_R = polyval(p_R, duty_valid);
        y_G = polyval(p_G, duty_valid);
        y_B = polyval(p_B, duty_valid);
        
        % Montar matriz de design para combinação linear
        X = [y_R, y_G, y_B];
        
        % Resolver sistema de mínimos quadrados: P_thorlabs = X * alpha
        alpha = (X' * X) \ (X' * P_thorlabs);
        
        % Predição do modelo
        P_modelo = X * alpha;
        
        % Calcular métricas
        SS_res = sum((P_thorlabs - P_modelo).^2);
        SS_tot = sum((P_thorlabs - mean(P_thorlabs)).^2);
        R2 = 1 - SS_res/SS_tot;
        RMSE = sqrt(mean((P_thorlabs - P_modelo).^2));
        
        % Armazenar resultados
        resultados.(fonte).poly_R(i_wn, :) = p_R;
        resultados.(fonte).poly_G(i_wn, :) = p_G;
        resultados.(fonte).poly_B(i_wn, :) = p_B;
        resultados.(fonte).alpha(i_wn, :) = alpha;
        resultados.(fonte).R2(i_wn) = R2;
        resultados.(fonte).RMSE(i_wn) = RMSE;
        
        % Mostrar progresso (a cada 20 pontos)
        if mod(i_wn, 20) == 0
            fprintf('  Processado: %d/%d comprimentos de onda (R²=%.4f)\n', ...
                i_wn, n_wavelengths, R2);
        end
    end
    
    % Estatísticas finais
    R2_medio = mean(resultados.(fonte).R2, 'omitnan');
    RMSE_medio = mean(resultados.(fonte).RMSE, 'omitnan');
    fprintf('  Concluído: R² médio = %.4f, RMSE médio = %.2f\n', ...
        R2_medio, RMSE_medio);
end

%% PASSO 6: VALIDAÇÃO COM DADOS DO JSON

fprintf('\nPASSO 6: Validação com picos do JSON...\n');

% Ler arquivo JSON
json_file = 'dados_todos_finalmente_completo_2026-02-01T23-19-33.690Z.json';
if exist(json_file, 'file')
    json_text = fileread(json_file);
    dados_json = jsondecode(json_text);
    
    % Acessar tomada 1 do ThorLabs
    % Estrutura: dados_json.data.thorlabs.x1.x[duty].[fonte]
    % onde fonte = "green", "red", "blue"
    
    fprintf('\n--- Comparação com picos do JSON (Tomada 1 - ThorLabs) ---\n\n');
    
    % Mapear nomes
    fonte_map = containers.Map({'Verde', 'Vermelho', 'Azul'}, ...
                                {'green', 'red', 'blue'});
    
    for i_fonte = 1:length(fontes)
        fonte = fontes{i_fonte};
        fonte_json = fonte_map(fonte);
        
        fprintf('%s:\n', fonte);
        
        % Testar alguns duty cycles (1%, 5%, 10%)
        duty_test = [1, 5, 10];
        
        for duty_value = duty_test
            duty_field = sprintf('x%d', duty_value);
            
            % Tentar acessar dados do JSON
            try
                pico_json = dados_json.data.thorlabs.x1.(duty_field).(fonte_json);
                
                % Converter strings para números
                lambda_pico = str2double(pico_json.peak_nm) * 1e-9;  % nm -> metros
                intensidade_json = str2double(pico_json.intensity);
                
                % Encontrar comprimento de onda mais próximo nos resultados
                [~, idx_closest] = min(abs(resultados.(fonte).lambda - lambda_pico));
                lambda_modelo = resultados.(fonte).lambda(idx_closest);
                
                % Obter dados do OSA para este duty cycle e λ
                idx_grid = indices_amostrados(idx_closest);
                Pr_osa = osa_interp.(fonte).r(duty_value, idx_grid);
                Pg_osa = osa_interp.(fonte).g(duty_value, idx_grid);
                Pb_osa = osa_interp.(fonte).b(duty_value, idx_grid);
                
                % Calcular previsão do modelo usando os polinômios
                p_R = resultados.(fonte).poly_R(idx_closest, :);
                p_G = resultados.(fonte).poly_G(idx_closest, :);
                p_B = resultados.(fonte).poly_B(idx_closest, :);
                alpha = resultados.(fonte).alpha(idx_closest, :);
                
                % Avaliar polinômios no duty cycle atual
                y_R = polyval(p_R, duty_value);
                y_G = polyval(p_G, duty_value);
                y_B = polyval(p_B, duty_value);
                
                % Combinação linear
                intensidade_modelo = alpha(1)*y_R + alpha(2)*y_G + alpha(3)*y_B;
                
                % Calcular erro
                erro_abs = abs(intensidade_modelo - intensidade_json);
                erro_rel = 100 * erro_abs / intensidade_json;
                
                fprintf('  Duty %d%% (λ=%.2f nm ≈ %.2f nm):\n', ...
                    duty_value, lambda_pico*1e9, lambda_modelo*1e9);
                fprintf('    ThorLabs (JSON): %.2f\n', intensidade_json);
                fprintf('    Modelo previsto: %.2f\n', intensidade_modelo);
                fprintf('    Erro absoluto: %.2f (%.1f%%)\n', erro_abs, erro_rel);
                fprintf('    Dados OSA: R=%.2f, G=%.2f, B=%.2f\n', Pr_osa, Pg_osa, Pb_osa);
                fprintf('    Alpha: [%.3f, %.3f, %.3f]\n', alpha(1), alpha(2), alpha(3));
            catch ME
                fprintf('  Duty %d%%: Erro ao acessar dados - %s\n', duty_value, ME.message);
            end
        end
        fprintf('\n');
    end
else
    warning('Arquivo JSON não encontrado para validação');
end

%% PASSO 7: VISUALIZAÇÃO DOS RESULTADOS

fprintf('\nPASSO 7: Gerando visualizações...\n');

% Figura 1: R² e RMSE por comprimento de onda
figure('Position', [100, 100, 1400, 500]);
sgtitle('Qualidade do Modelo Espectral', 'FontSize', 14, 'FontWeight', 'bold');

subplot(1, 2, 1);
hold on;
for i_fonte = 1:length(fontes)
    fonte = fontes{i_fonte};
    plot(resultados.(fonte).lambda*1e9, resultados.(fonte).R2, ...
        'LineWidth', 2, 'DisplayName', fonte);
end
xlabel('Comprimento de onda (nm)');
ylabel('R²');
title('Coeficiente de Determinação');
legend('Location', 'best');
grid on;
ylim([0, 1]);

subplot(1, 2, 2);
hold on;
for i_fonte = 1:length(fontes)
    fonte = fontes{i_fonte};
    plot(resultados.(fonte).lambda*1e9, resultados.(fonte).RMSE, ...
        'LineWidth', 2, 'DisplayName', fonte);
end
xlabel('Comprimento de onda (nm)');
ylabel('RMSE');
title('Erro Quadrático Médio');
legend('Location', 'best');
grid on;

% Salvar figura
print('modelagem_espectral_completa_qualidade.png', '-dpng', '-r300');

% Figura 2: Coeficientes alpha por comprimento de onda
figure('Position', [100, 100, 1400, 900]);
sgtitle('Coeficientes da Combinação Linear (α)', 'FontSize', 14, 'FontWeight', 'bold');

for i_fonte = 1:length(fontes)
    fonte = fontes{i_fonte};
    
    subplot(3, 1, i_fonte);
    hold on;
    plot(resultados.(fonte).lambda*1e9, resultados.(fonte).alpha(:, 1), ...
        'r-', 'LineWidth', 2, 'DisplayName', 'α₁ (Canal R)');
    plot(resultados.(fonte).lambda*1e9, resultados.(fonte).alpha(:, 2), ...
        'g-', 'LineWidth', 2, 'DisplayName', 'α₂ (Canal G)');
    plot(resultados.(fonte).lambda*1e9, resultados.(fonte).alpha(:, 3), ...
        'b-', 'LineWidth', 2, 'DisplayName', 'α₃ (Canal B)');
    plot([resultados.(fonte).lambda(1), resultados.(fonte).lambda(end)]*1e9, ...
        [0, 0], 'k--', 'LineWidth', 1, 'HandleVisibility', 'off');
    
    xlabel('Comprimento de onda (nm)');
    ylabel('Coeficiente α');
    title(fonte);
    legend('Location', 'best');
    grid on;
end

% Salvar figura
print('modelagem_espectral_completa_coeficientes.png', '-dpng', '-r300');

fprintf('\n✓ Figuras salvas!\n');

%% PASSO 8: SALVAR RESULTADOS

fprintf('\nPASSO 8: Salvando resultados...\n');

% Salvar em arquivo .mat
save('modelagem_espectral_completa_resultados.mat', 'resultados', ...
    'lambda_sampled', 'lambda_grid', 'thorlabs_mean', 'osa_interp');

fprintf('✓ Resultados salvos em: modelagem_espectral_completa_resultados.mat\n');

% Criar arquivo de texto com resumo
fid = fopen('modelagem_espectral_completa_resumo.txt', 'w');
fprintf(fid, '=== MODELAGEM ESPECTRAL COMPLETA - RESUMO ===\n\n');
fprintf(fid, 'Data: %s\n', datestr(now));
fprintf(fid, 'Faixa espectral: %.1f - %.1f nm\n', lambda_min*1e9, lambda_max*1e9);
fprintf(fid, 'Comprimentos de onda amostrados: %d\n\n', n_wavelengths);

for i_fonte = 1:length(fontes)
    fonte = fontes{i_fonte};
    fprintf(fid, '\n--- %s ---\n', fonte);
    fprintf(fid, 'R² médio: %.4f\n', mean(resultados.(fonte).R2, 'omitnan'));
    fprintf(fid, 'R² mínimo: %.4f\n', min(resultados.(fonte).R2));
    fprintf(fid, 'R² máximo: %.4f\n', max(resultados.(fonte).R2));
    fprintf(fid, 'RMSE médio: %.2f\n', mean(resultados.(fonte).RMSE, 'omitnan'));
end

fclose(fid);
fprintf('✓ Resumo salvo em: modelagem_espectral_completa_resumo.txt\n');

fprintf('\n=== MODELAGEM CONCLUÍDA COM SUCESSO! ===\n');
