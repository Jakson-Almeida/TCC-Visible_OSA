% modelagem_espectral_geral.m
% Modelo espectral GERAL: mapeamento direto (Pr, Pg, Pb) -> P_ThorLabs por lambda.
% Duty cycle e fontes (Verde, Vermelho, Azul) são usados apenas na CALIBRAÇÃO.
% O modelo final NÃO depende de duty cycle nem de fonte de luz.
%
% Estratégia:
% 1. Ler espectros completos (ThorLabs e Visible_OSA), média das 5 tomadas
% 2. Interpolar OSA na grade do ThorLabs (373-681 nm)
% 3. Amostrar 100 comprimentos de onda (w_n)
% 4. Para cada w_n: POOL de todos os dados (3 fontes x 10 duty = 30 pontos)
%    Ajustar regressão linear: P_ThorLabs = beta_1*Pr + beta_2*Pg + beta_3*Pb
% 5. Exportar coeficientes beta(λ) para uso com espectros quaisquer
%
% Uso do modelo: para qualquer espectro, carregue os 3 canais (Pr,Pg,Pb)
% e calcule P_ThorLabs(λ) = beta_1(λ)*Pr(λ) + beta_2(λ)*Pg(λ) + beta_3(λ)*Pb(λ)

clear; clc; close all;

fprintf('=== MODELAGEM ESPECTRAL GERAL (OSA -> ThorLabs) ===\n\n');
fprintf('Modelo final: P_ThorLabs(λ) = β₁(λ)·Pr(λ) + β₂(λ)·Pg(λ) + β₃(λ)·Pb(λ)\n');
fprintf('Independente de duty cycle e fonte de luz.\n\n');

%% PARÂMETROS
pasta_base = 'modelagem';
n_tomadas = 5;
fontes = {'Verde', 'Vermelho', 'Azul'};
duty_cycles = 1:10;
n_wavelengths = 100;

lambda_thorlabs_min = 316.5e-9;
lambda_thorlabs_max = 731.2e-9;
lambda_osa_min = 372.7e-9;
lambda_osa_max = 681.0e-9;
lambda_min = max(lambda_thorlabs_min, lambda_osa_min);
lambda_max = min(lambda_thorlabs_max, lambda_osa_max);

% Opcional: excluir pontos saturados (percentil alto)
excluir_saturacao = true;
percentil_max = 99.5;  % descartar acima deste percentil de P_thorlabs

fprintf('Faixa: %.1f - %.1f nm | %d comprimentos de onda\n\n', ...
    lambda_min*1e9, lambda_max*1e9, n_wavelengths);

%% PASSO 1: LEITURA E MÉDIA THORLABS
fprintf('PASSO 1: Lendo ThorLabs...\n');
arquivo_ref = fullfile(pasta_base, 'ThorLabs', 'peqs_1', 'Verde', '1.txt');
data_ref = readmatrix(arquivo_ref);
lambda_thorlabs_full = data_ref(:, 1);
idx_intersecao = (lambda_thorlabs_full >= lambda_min) & (lambda_thorlabs_full <= lambda_max);
lambda_grid = lambda_thorlabs_full(idx_intersecao);
n_points_grid = length(lambda_grid);

thorlabs_mean = struct();
for i_fonte = 1:length(fontes)
    fonte = fontes{i_fonte};
    thorlabs_mean.(fonte) = zeros(length(duty_cycles), n_points_grid);
    for i_duty = 1:length(duty_cycles)
        duty = duty_cycles(i_duty);
        espectros_tomadas = zeros(n_tomadas, n_points_grid);
        for tomada = 1:n_tomadas
            arquivo = fullfile(pasta_base, 'ThorLabs', sprintf('peqs_%d', tomada), fonte, sprintf('%d.txt', duty));
            if exist(arquivo, 'file')
                data = readmatrix(arquivo);
                intensidades_full = data(:, 2);
                espectros_tomadas(tomada, :) = intensidades_full(idx_intersecao);
            end
        end
        thorlabs_mean.(fonte)(i_duty, :) = mean(espectros_tomadas, 1);
    end
    fprintf('  %s OK\n', fonte);
end

%% PASSO 2: LEITURA E MÉDIA OSA VISÍVEL
fprintf('\nPASSO 2: Lendo OSA Visível...\n');
arquivo_osa_ref = fullfile(pasta_base, 'Visible_OSA', 'peqs_1', 'Verde', 'spectrum_r_001.txt');
data_osa_ref = readmatrix(arquivo_osa_ref);
lambda_osa_original = data_osa_ref(:, 1);
canais = {'r', 'g', 'b'};
osa_original = struct();
for i_fonte = 1:length(fontes)
    fonte = fontes{i_fonte};
    osa_original.(fonte) = struct();
    for i_canal = 1:length(canais)
        canal = canais{i_canal};
        osa_original.(fonte).(canal) = zeros(length(duty_cycles), length(lambda_osa_original));
        for i_duty = 1:length(duty_cycles)
            duty = duty_cycles(i_duty);
            espectros_tomadas = zeros(n_tomadas, length(lambda_osa_original));
            for tomada = 1:n_tomadas
                arquivo = fullfile(pasta_base, 'Visible_OSA', sprintf('peqs_%d', tomada), fonte, sprintf('spectrum_%s_%03d.txt', canal, duty));
                if exist(arquivo, 'file')
                    data = readmatrix(arquivo);
                    espectros_tomadas(tomada, :) = data(:, 2);
                end
            end
            osa_original.(fonte).(canal)(i_duty, :) = mean(espectros_tomadas, 1);
        end
    end
    fprintf('  %s OK\n', fonte);
end

%% PASSO 3: INTERPOLAÇÃO OSA -> GRADE THORLABS
fprintf('\nPASSO 3: Interpolando OSA para grade ThorLabs...\n');
osa_interp = struct();
for i_fonte = 1:length(fontes)
    fonte = fontes{i_fonte};
    osa_interp.(fonte) = struct();
    for i_canal = 1:length(canais)
        canal = canais{i_canal};
        osa_interp.(fonte).(canal) = zeros(length(duty_cycles), n_points_grid);
        for i_duty = 1:length(duty_cycles)
            intensidades_interp = interp1(lambda_osa_original, osa_original.(fonte).(canal)(i_duty, :), lambda_grid, 'linear', 'extrap');
            osa_interp.(fonte).(canal)(i_duty, :) = intensidades_interp;
        end
    end
end
fprintf('  %d pontos na grade comum\n', n_points_grid);

%% PASSO 4: AMOSTRAGEM 100 COMPRIMENTOS DE ONDA
indices_amostrados = round(linspace(1, n_points_grid, n_wavelengths));
lambda_sampled = lambda_grid(indices_amostrados);

%% PASSO 5: MODELO GERAL - Regressão linear (Pr,Pg,Pb) -> P_ThorLabs por lambda (dados POOL)
fprintf('\nPASSO 5: Modelo geral - regressão linear por λ (dados de todas as fontes e duty)...\n');

resultados = struct();
resultados.lambda = lambda_sampled;
resultados.beta = zeros(n_wavelengths, 3);   % [beta_1, beta_2, beta_3]
resultados.R2 = zeros(n_wavelengths, 1);
resultados.RMSE = zeros(n_wavelengths, 1);

for i_wn = 1:n_wavelengths
    idx_grid = indices_amostrados(i_wn);
    lambda_nm = lambda_sampled(i_wn) * 1e9;

    % POOL: juntar dados das 3 fontes x 10 duty = 30 pontos
    Pr_all = [];
    Pg_all = [];
    Pb_all = [];
    P_thorlabs_all = [];
    for i_fonte = 1:length(fontes)
        fonte = fontes{i_fonte};
        Pr_all = [Pr_all; osa_interp.(fonte).r(:, idx_grid)];
        Pg_all = [Pg_all; osa_interp.(fonte).g(:, idx_grid)];
        Pb_all = [Pb_all; osa_interp.(fonte).b(:, idx_grid)];
        P_thorlabs_all = [P_thorlabs_all; thorlabs_mean.(fonte)(:, idx_grid)];
    end

    % Remover NaN
    valid = ~isnan(Pr_all) & ~isnan(Pg_all) & ~isnan(Pb_all) & ~isnan(P_thorlabs_all);
    Pr_all = Pr_all(valid);
    Pg_all = Pg_all(valid);
    Pb_all = Pb_all(valid);
    P_thorlabs_all = P_thorlabs_all(valid);

    % Opcional: excluir pontos muito altos (saturação)
    if excluir_saturacao && numel(P_thorlabs_all) >= 10
        limiar = prctile(P_thorlabs_all, percentil_max);
        ok = P_thorlabs_all <= limiar;
        Pr_all = Pr_all(ok);
        Pg_all = Pg_all(ok);
        Pb_all = Pb_all(ok);
        P_thorlabs_all = P_thorlabs_all(ok);
    end

    if numel(Pr_all) < 6
        fprintf('  λ=%.1f nm: poucos pontos (%d)\n', lambda_nm, numel(Pr_all));
        continue;
    end

    % Regressão linear: P_ThorLabs = beta_1*Pr + beta_2*Pg + beta_3*Pb (sem intercepto)
    X = [Pr_all, Pg_all, Pb_all];
    beta = (X' * X) \ (X' * P_thorlabs_all);
    P_modelo = X * beta;

    SS_res = sum((P_thorlabs_all - P_modelo).^2);
    SS_tot = sum((P_thorlabs_all - mean(P_thorlabs_all)).^2);
    R2 = 1 - SS_res / max(SS_tot, 1e-20);
    RMSE = sqrt(mean((P_thorlabs_all - P_modelo).^2));

    resultados.beta(i_wn, :) = beta';
    resultados.R2(i_wn) = R2;
    resultados.RMSE(i_wn) = RMSE;

    if mod(i_wn, 25) == 0
        fprintf('  %d/%d λ (R²=%.4f)\n', i_wn, n_wavelengths, R2);
    end
end

fprintf('  Concluído. R² médio = %.4f, RMSE médio = %.2f\n', ...
    mean(resultados.R2, 'omitnan'), mean(resultados.RMSE, 'omitnan'));

%% PASSO 6: IMPRIMIR MODELO E EXPORTAR
fprintf('\n=== MODELO FINAL ===\n\n');
fprintf('P_ThorLabs(λ) = β₁(λ)·Pr(λ) + β₂(λ)·Pg(λ) + β₃(λ)·Pb(λ)\n');
fprintf('Válido para espectros quaisquer (faixa não saturada).\n\n');

% Exemplo em um lambda central
idx_meio = round(n_wavelengths/2);
lambda_ex = resultados.lambda(idx_meio)*1e9;
beta_ex = resultados.beta(idx_meio, :);
fprintf('Exemplo em λ = %.2f nm:\n', lambda_ex);
fprintf('  β₁ = %.6f, β₂ = %.6f, β₃ = %.6f\n', beta_ex(1), beta_ex(2), beta_ex(3));
fprintf('  R² = %.4f, RMSE = %.2f\n\n', resultados.R2(idx_meio), resultados.RMSE(idx_meio));

% Salvar .mat
save('modelagem_espectral_geral_resultados.mat', 'resultados', 'lambda_sampled', 'lambda_grid');
fprintf('Salvo: modelagem_espectral_geral_resultados.mat\n');

% CSV para uso externo (calibration_viewer, etc.)
fid = fopen('modelo_geral_parametros.csv', 'w');
fprintf(fid, 'lambda_nm,beta_1,beta_2,beta_3,R2,RMSE\n');
for i_wn = 1:n_wavelengths
    fprintf(fid, '%.6f,%.6e,%.6e,%.6e,%.6f,%.6f\n', ...
        resultados.lambda(i_wn)*1e9, resultados.beta(i_wn,1), resultados.beta(i_wn,2), resultados.beta(i_wn,3), ...
        resultados.R2(i_wn), resultados.RMSE(i_wn));
end
fclose(fid);
fprintf('Salvo: modelo_geral_parametros.csv\n');

% Resumo .txt
fid = fopen('modelagem_espectral_geral_resumo.txt', 'w');
fprintf(fid, '=== MODELAGEM ESPECTRAL GERAL ===\n\n');
fprintf(fid, 'Data: %s\n', datestr(now));
fprintf(fid, 'Modelo: P_ThorLabs(λ) = β₁(λ)·Pr(λ) + β₂(λ)·Pg(λ) + β₃(λ)·Pb(λ)\n');
fprintf(fid, 'Independente de duty cycle e fonte. Uso: espectros quaisquer.\n\n');
fprintf(fid, 'Faixa: %.1f - %.1f nm\n', lambda_min*1e9, lambda_max*1e9);
fprintf(fid, 'R² médio: %.4f\n', mean(resultados.R2, 'omitnan'));
fprintf(fid, 'RMSE médio: %.2f\n', mean(resultados.RMSE, 'omitnan'));
fclose(fid);
fprintf('Salvo: modelagem_espectral_geral_resumo.txt\n');

% Figura: beta e R² por lambda
figure('Position', [100, 100, 1200, 600]);
subplot(2,1,1);
plot(resultados.lambda*1e9, resultados.beta(:,1), 'r-', 'LineWidth', 1.5); hold on;
plot(resultados.lambda*1e9, resultados.beta(:,2), 'g-', 'LineWidth', 1.5);
plot(resultados.lambda*1e9, resultados.beta(:,3), 'b-', 'LineWidth', 1.5);
xlabel('Comprimento de onda (nm)'); ylabel('β');
legend('β₁ (R)', 'β₂ (G)', 'β₃ (B)'); grid on; title('Coeficientes do modelo geral');
subplot(2,1,2);
plot(resultados.lambda*1e9, resultados.R2, 'k-', 'LineWidth', 1.5);
xlabel('Comprimento de onda (nm)'); ylabel('R²'); grid on; title('Qualidade do ajuste');
print('modelagem_espectral_geral_coeficientes.png', '-dpng', '-r300');
fprintf('Figura: modelagem_espectral_geral_coeficientes.png\n');

fprintf('\n=== CONCLUÍDO ===\n');
