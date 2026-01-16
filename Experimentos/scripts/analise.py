#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para análise de espectros do OSA Visível.
Detecta e analisa picos em espectros experimentais.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.cluster.hierarchy import linkage, fcluster
from pathlib import Path
import os
from collections import defaultdict
import pandas as pd


def carregar_espectro(arquivo_spectrum):
    """
    Carrega dados de espectro do arquivo .txt.
    
    Args:
        arquivo_spectrum: Caminho para o arquivo spectrum*.txt
        
    Returns:
        wl: Array de comprimentos de onda em nanômetros
        intensity: Array de intensidades
    """
    # Lê o arquivo
    dados = np.loadtxt(arquivo_spectrum, delimiter=';')
    
    # Primeira coluna: comprimento de onda em metros (notação científica)
    # Segunda coluna: intensidade
    wl_metros = dados[:, 0]
    intensity = dados[:, 1]
    
    # Converte de metros para nanômetros
    wl = wl_metros * 1e9  # 1 metro = 1e9 nanômetros
    
    return wl, intensity


def detectar_picos(wl, intensity, prominence=5, distance=None, height=None):
    """
    Detecta picos no espectro usando scipy.signal.find_peaks.
    
    Args:
        wl: Array de comprimentos de onda
        intensity: Array de intensidades
        prominence: Prominência mínima dos picos (padrão: 5)
        distance: Distância mínima entre picos (opcional)
        height: Altura mínima dos picos (opcional)
        
    Returns:
        peaks: Índices dos picos encontrados
        peak_wl: Comprimentos de onda dos picos (nm)
        peak_intensity: Intensidades dos picos
        info: Informações adicionais sobre os picos
    """
    # Parâmetros para find_peaks
    params = {'prominence': prominence}
    
    if distance is not None:
        params['distance'] = distance
    if height is not None:
        params['height'] = height
    
    # Detecta picos
    peaks, info = find_peaks(intensity, **params)
    
    # Extrai informações dos picos
    peak_wl = wl[peaks]
    peak_intensity = intensity[peaks]
    
    return peaks, peak_wl, peak_intensity, info


def analisar_amostra_livre(pasta_amostra_livre=None):
    """
    Analisa o espectro da amostra livre do OSA Visível.
    
    Args:
        pasta_amostra_livre: Caminho para a pasta AmostraLivre (opcional)
    """
    # Define caminho padrão
    if pasta_amostra_livre is None:
        # Caminho relativo ao script
        script_dir = Path(__file__).parent
        pasta_amostra_livre = script_dir.parent / "Visible_OSA" / "AmostraLivre"
    
    pasta_amostra_livre = Path(pasta_amostra_livre)
    
    # Procura arquivo spectrum*.txt
    arquivos_spectrum = list(pasta_amostra_livre.glob("spectrum*.txt"))
    
    if not arquivos_spectrum:
        print(f"[ERRO] Nenhum arquivo spectrum*.txt encontrado em {pasta_amostra_livre}")
        return None
    
    # Usa o primeiro arquivo encontrado (ou pode processar todos)
    arquivo_spectrum = arquivos_spectrum[0]
    print(f"[INFO] Carregando espectro: {arquivo_spectrum.name}")
    
    # Carrega dados
    wl, intensity = carregar_espectro(arquivo_spectrum)
    
    print(f"[INFO] Espectro carregado: {len(wl)} pontos")
    print(f"[INFO] Faixa espectral: {wl.min():.2f} - {wl.max():.2f} nm")
    print(f"[INFO] Intensidade: min={intensity.min():.2f}, max={intensity.max():.2f}")
    
    # Detecta picos
    print(f"\n[ANALISE] Detectando picos...")
    peaks, peak_wl, peak_intensity, info = detectar_picos(wl, intensity, prominence=5)
    
    print(f"[OK] {len(peaks)} picos encontrados\n")
    
    # Exibe informações dos picos
    print("=" * 70)
    print(f"{'Pico':<6} {'Comprimento de Onda (nm)':<25} {'Intensidade':<15} {'Prominência':<15}")
    print("=" * 70)
    
    for idx, (wl_pico, int_pico) in enumerate(zip(peak_wl, peak_intensity)):
        # Obtém a prominência do pico
        prominence_val = info.get('prominences', [0] * len(peaks))[idx] if 'prominences' in info else 0
        print(f"{idx + 1:<6} {wl_pico:<25.2f} {int_pico:<15.2f} {prominence_val:<15.2f}")
    
    print("=" * 70)
    
    # Plota o espectro com picos marcados
    plt.figure(figsize=(12, 6))
    plt.plot(wl, intensity, 'b-', linewidth=1.5, label='Espectro')
    plt.plot(peak_wl, peak_intensity, 'ro', markersize=8, label=f'Picos ({len(peaks)})')
    
    # Adiciona anotações nos picos principais
    for idx, (wl_pico, int_pico) in enumerate(zip(peak_wl, peak_intensity)):
        plt.annotate(f'{wl_pico:.1f} nm', 
                    xy=(wl_pico, int_pico), 
                    xytext=(5, 5), 
                    textcoords='offset points',
                    fontsize=8,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))
    
    plt.xlabel('Comprimento de Onda (nm)', fontsize=12)
    plt.ylabel('Intensidade', fontsize=12)
    plt.title('Espectro - Amostra Livre (OSA Visível) com Picos Detectados', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # Salva o gráfico
    output_dir = pasta_amostra_livre
    output_file = output_dir / "espectro_com_picos.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n[OK] Gráfico salvo em: {output_file}")
    
    # Mostra o gráfico
    plt.show()
    
    return {
        'wl': wl,
        'intensity': intensity,
        'peaks': peaks,
        'peak_wl': peak_wl,
        'peak_intensity': peak_intensity,
        'info': info
    }


def processar_todos_espectros_temporais(pasta_temporal=None):
    """
    Processa todos os espectros temporais e detecta picos em cada um.
    
    Args:
        pasta_temporal: Caminho para a pasta Temporal (opcional)
        
    Returns:
        Lista de dicionários com resultados de cada espectro
    """
    # Define caminho padrão
    if pasta_temporal is None:
        script_dir = Path(__file__).parent
        pasta_temporal = script_dir.parent / "Visible_OSA" / "Temporal"
    
    pasta_temporal = Path(pasta_temporal)
    
    # Procura todos os arquivos spectrum*.txt
    arquivos_spectrum = sorted(pasta_temporal.glob("spectrum*.txt"))
    
    if not arquivos_spectrum:
        print(f"[ERRO] Nenhum arquivo spectrum*.txt encontrado em {pasta_temporal}")
        return None
    
    print(f"[INFO] Encontrados {len(arquivos_spectrum)} arquivos de espectro")
    print(f"[INFO] Processando todos os espectros...\n")
    
    resultados_todos = []
    
    for idx, arquivo in enumerate(arquivos_spectrum):
        if (idx + 1) % 10 == 0:
            print(f"  Processando {idx + 1}/{len(arquivos_spectrum)}...")
        
        try:
            # Carrega dados
            wl, intensity = carregar_espectro(arquivo)
            
            # Detecta picos
            peaks, peak_wl, peak_intensity, info = detectar_picos(wl, intensity, prominence=5)
            
            resultados_todos.append({
                'arquivo': arquivo.name,
                'indice': idx,
                'wl': wl,
                'intensity': intensity,
                'peaks': peaks,
                'peak_wl': peak_wl,
                'peak_intensity': peak_intensity,
                'info': info
            })
        except Exception as e:
            print(f"  [ERRO] Erro ao processar {arquivo.name}: {str(e)[:100]}")
            continue
    
    print(f"\n[OK] {len(resultados_todos)} espectros processados com sucesso")
    return resultados_todos


def identificar_cor_pico(wl_medio):
    """
    Identifica a cor RGB aproximada baseada no comprimento de onda.
    
    Args:
        wl_medio: Comprimento de onda médio em nm
        
    Returns:
        Tupla (nome_cor, cor_rgb)
    """
    if wl_medio < 500:
        return ("Azul", "blue")
    elif wl_medio < 580:
        return ("Verde", "green")
    else:
        return ("Vermelho", "red")


def agrupar_picos_correspondentes(resultados_todos, tolerancia_nm=5.0):
    """
    Agrupa picos correspondentes entre diferentes amostras usando clustering.
    Identifica os 3 picos principais RGB.
    
    Args:
        resultados_todos: Lista de resultados de cada espectro
        tolerancia_nm: Tolerância em nm para considerar picos como correspondentes
        
    Returns:
        Dicionário com grupos de picos: {grupo_id: [lista de (amostra_idx, peak_wl, peak_intensity)]}
    """
    print(f"\n[ANALISE] Agrupando picos correspondentes (tolerancia: {tolerancia_nm} nm)...")
    
    # Coleta todos os picos com informações de origem
    todos_picos = []
    for resultado in resultados_todos:
        for wl_pico, int_pico in zip(resultado['peak_wl'], resultado['peak_intensity']):
            todos_picos.append({
                'amostra_idx': resultado['indice'],
                'arquivo': resultado['arquivo'],
                'wl': wl_pico,
                'intensity': int_pico
            })
    
    if len(todos_picos) == 0:
        print("[ERRO] Nenhum pico encontrado em nenhuma amostra")
        return None
    
    # Usa clustering hierárquico para agrupar picos por comprimento de onda
    wl_array = np.array([p['wl'] for p in todos_picos])
    
    # Calcula matriz de distâncias
    from scipy.spatial.distance import pdist, squareform
    distancias = pdist(wl_array.reshape(-1, 1))
    
    # Clustering hierárquico
    linkage_matrix = linkage(distancias, method='average')
    
    # Agrupa com threshold baseado na tolerância
    grupos = fcluster(linkage_matrix, t=tolerancia_nm, criterion='distance')
    
    # Organiza picos por grupo
    grupos_picos = defaultdict(list)
    for pico, grupo_id in zip(todos_picos, grupos):
        grupos_picos[grupo_id].append(pico)
    
    print(f"[OK] {len(grupos_picos)} grupos de picos identificados")
    
    # Ordena grupos por comprimento de onda médio e identifica cores
    grupos_ordenados = {}
    for grupo_id, picos in grupos_picos.items():
        wl_medio = np.mean([p['wl'] for p in picos])
        num_amostras = len(set([p['amostra_idx'] for p in picos]))
        nome_cor, cor_rgb = identificar_cor_pico(wl_medio)
        
        grupos_ordenados[grupo_id] = {
            'picos': picos,
            'wl_medio': wl_medio,
            'num_amostras': num_amostras,
            'nome_cor': nome_cor,
            'cor_rgb': cor_rgb
        }
    
    # Ordena por comprimento de onda médio
    grupos_ordenados = dict(sorted(grupos_ordenados.items(), key=lambda x: x[1]['wl_medio']))
    
    # Identifica os 3 picos principais (maior taxa de detecção e maior intensidade média)
    num_amostras_total = len(resultados_todos)
    grupos_principais = []
    for grupo_id, grupo_data in grupos_ordenados.items():
        taxa_deteccao = (grupo_data['num_amostras'] / num_amostras_total) * 100
        int_media = np.mean([p['intensity'] for p in grupo_data['picos']])
        grupos_principais.append({
            'grupo_id': grupo_id,
            'wl_medio': grupo_data['wl_medio'],
            'taxa_deteccao': taxa_deteccao,
            'int_media': int_media,
            'nome_cor': grupo_data['nome_cor'],
            'cor_rgb': grupo_data['cor_rgb']
        })
    
    # Ordena por taxa de detecção e intensidade (prioriza picos principais)
    grupos_principais.sort(key=lambda x: (x['taxa_deteccao'], x['int_media']), reverse=True)
    
    # Identifica os 3 principais
    picos_rgb = grupos_principais[:3] if len(grupos_principais) >= 3 else grupos_principais
    
    print(f"\n[INFO] 3 Picos Principais RGB Identificados:")
    for idx, pico in enumerate(picos_rgb, 1):
        print(f"  Pico {idx} ({pico['nome_cor']}): {pico['wl_medio']:.2f} nm - "
              f"Taxa de detecção: {pico['taxa_deteccao']:.1f}% - "
              f"Intensidade média: {pico['int_media']:.2f}")
    
    # Marca os grupos principais
    for grupo_id, grupo_data in grupos_ordenados.items():
        grupo_data['eh_principal'] = grupo_id in [p['grupo_id'] for p in picos_rgb]
        if grupo_data['eh_principal']:
            # Atribui nome RGB baseado na ordem
            for idx, pico in enumerate(picos_rgb, 1):
                if pico['grupo_id'] == grupo_id:
                    grupo_data['nome_rgb'] = f"RGB-{idx} ({grupo_data['nome_cor']})"
                    break
    
    return grupos_ordenados


def calcular_estatisticas_picos(grupos_picos, num_amostras_total):
    """
    Calcula estatísticas para cada grupo de picos.
    
    Args:
        grupos_picos: Dicionário com grupos de picos
        num_amostras_total: Número total de amostras
        
    Returns:
        DataFrame com estatísticas
    """
    print(f"\n[ANALISE] Calculando estatisticas...")
    
    estatisticas = []
    
    for grupo_id, grupo_data in grupos_picos.items():
        picos = grupo_data['picos']
        wl_values = np.array([p['wl'] for p in picos])
        intensity_values = np.array([p['intensity'] for p in picos])
        
        # Estatísticas de comprimento de onda
        wl_mean = np.mean(wl_values)
        wl_std = np.std(wl_values, ddof=1)  # Desvio padrão amostral
        wl_sem = wl_std / np.sqrt(len(wl_values))  # Erro padrão da média
        wl_incerteza = 1.96 * wl_sem  # Incerteza expandida (95% de confiança, k=1.96)
        wl_min = np.min(wl_values)
        wl_max = np.max(wl_values)
        wl_range = wl_max - wl_min
        
        # Estatísticas de intensidade
        int_mean = np.mean(intensity_values)
        int_std = np.std(intensity_values, ddof=1)
        int_cv = (int_std / int_mean) * 100 if int_mean > 0 else 0  # Coeficiente de variação (%)
        int_min = np.min(intensity_values)
        int_max = np.max(intensity_values)
        
        # Taxa de detecção (quantas amostras têm este pico)
        taxa_deteccao = (len(picos) / num_amostras_total) * 100
        
        # Informações de cor e se é principal
        nome_cor = grupo_data.get('nome_cor', 'N/A')
        nome_rgb = grupo_data.get('nome_rgb', f'Grupo {grupo_id}')
        eh_principal = grupo_data.get('eh_principal', False)
        
        estatisticas.append({
            'Grupo': grupo_id,
            'Identificacao': nome_rgb,
            'Cor': nome_cor,
            'Principal_RGB': 'Sim' if eh_principal else 'Não',
            'Comprimento_Onda_Medio_nm': wl_mean,
            'Desvio_Padrao_nm': wl_std,
            'Incerteza_Expandida_nm': wl_incerteza,
            'Erro_Padrao_Media_nm': wl_sem,
            'Min_nm': wl_min,
            'Max_nm': wl_max,
            'Range_nm': wl_range,
            'Intensidade_Media': int_mean,
            'Intensidade_Desvio_Padrao': int_std,
            'Coeficiente_Variacao_Intensidade_%': int_cv,
            'Intensidade_Min': int_min,
            'Intensidade_Max': int_max,
            'Num_Detecoes': len(picos),
            'Taxa_Deteccao_%': taxa_deteccao
        })
    
    df = pd.DataFrame(estatisticas)
    
    # Ordena: principais primeiro, depois por comprimento de onda
    df['Principal_Order'] = df['Principal_RGB'].map({'Sim': 0, 'Não': 1})
    df = df.sort_values(['Principal_Order', 'Comprimento_Onda_Medio_nm']).drop('Principal_Order', axis=1)
    
    return df


def gerar_graficos_estatisticos(grupos_picos, estatisticas_df, pasta_output):
    """
    Gera gráficos estatísticos da análise temporal.
    Foca nos 3 picos principais RGB.
    
    Args:
        grupos_picos: Dicionário com grupos de picos
        estatisticas_df: DataFrame com estatísticas
        pasta_output: Pasta para salvar os gráficos
    """
    print(f"\n[GRAFICOS] Gerando graficos estatisticos...")
    
    pasta_output = Path(pasta_output)
    pasta_output.mkdir(parents=True, exist_ok=True)
    
    # Filtra apenas picos principais
    picos_principais_df = estatisticas_df[estatisticas_df['Principal_RGB'] == 'Sim'].copy()
    grupos_principais = {gid: grupos_picos[gid] for gid in picos_principais_df['Grupo'].values 
                        if gid in grupos_picos}
    
    if len(grupos_principais) == 0:
        print("[AVISO] Nenhum pico principal identificado. Gerando gráficos de todos os picos.")
        grupos_principais = grupos_picos
    
    num_grupos = len(grupos_principais)
    
    # Gráfico 1: Evolução temporal dos comprimentos de onda dos 3 picos principais RGB
    fig, axes = plt.subplots(num_grupos, 1, figsize=(14, 5 * num_grupos))
    if num_grupos == 1:
        axes = [axes]
    
    for idx, (grupo_id, grupo_data) in enumerate(grupos_principais.items()):
        picos = grupo_data['picos']
        amostras = [p['amostra_idx'] for p in picos]
        wl_values = [p['wl'] for p in picos]
        
        ax = axes[idx]
        cor = grupo_data.get('cor_rgb', 'blue')
        nome_rgb = grupo_data.get('nome_rgb', f'Grupo {grupo_id}')
        
        ax.scatter(amostras, wl_values, alpha=0.6, s=40, color=cor, label='Medições')
        
        # Linha da média
        wl_mean = estatisticas_df[estatisticas_df['Grupo'] == grupo_id]['Comprimento_Onda_Medio_nm'].values[0]
        ax.axhline(y=wl_mean, color='r', linestyle='--', linewidth=2, label=f'Média: {wl_mean:.2f} nm')
        
        # Banda de incerteza expandida
        incerteza = estatisticas_df[estatisticas_df['Grupo'] == grupo_id]['Incerteza_Expandida_nm'].values[0]
        ax.fill_between(range(max(amostras) + 1), 
                       wl_mean - incerteza, 
                       wl_mean + incerteza, 
                       alpha=0.2, color='red', label=f'Incerteza Expandida (k=1.96): ±{incerteza:.3f} nm')
        
        # Banda de desvio padrão
        wl_std = estatisticas_df[estatisticas_df['Grupo'] == grupo_id]['Desvio_Padrao_nm'].values[0]
        ax.fill_between(range(max(amostras) + 1),
                       wl_mean - wl_std,
                       wl_mean + wl_std,
                       alpha=0.15, color='orange', label=f'±1σ: {wl_std:.2f} nm')
        
        ax.set_xlabel('Número da Amostra (coletadas a cada 10s)', fontsize=11)
        ax.set_ylabel('Comprimento de Onda (nm)', fontsize=11)
        ax.set_title(f'{nome_rgb} - Evolução Temporal (100 amostras)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=9)
        ax.set_xlim(-1, 100)
    
    plt.tight_layout()
    plt.savefig(pasta_output / "evolucao_temporal_3_picos_RGB.png", dpi=300, bbox_inches='tight')
    print(f"  [OK] Gráfico salvo: evolucao_temporal_3_picos_RGB.png")
    plt.close()
    
    # Gráfico 2: Histogramas de distribuição dos 3 picos principais RGB
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, (grupo_id, grupo_data) in enumerate(grupos_principais.items()):
        picos = grupo_data['picos']
        wl_values = [p['wl'] for p in picos]
        cor = grupo_data.get('cor_rgb', 'blue')
        nome_rgb = grupo_data.get('nome_rgb', f'Grupo {grupo_id}')
        
        ax = axes[idx]
        ax.hist(wl_values, bins=25, alpha=0.7, edgecolor='black', color=cor, label='Distribuição')
        
        wl_mean = estatisticas_df[estatisticas_df['Grupo'] == grupo_id]['Comprimento_Onda_Medio_nm'].values[0]
        wl_std = estatisticas_df[estatisticas_df['Grupo'] == grupo_id]['Desvio_Padrao_nm'].values[0]
        wl_incerteza = estatisticas_df[estatisticas_df['Grupo'] == grupo_id]['Incerteza_Expandida_nm'].values[0]
        
        ax.axvline(wl_mean, color='r', linestyle='--', linewidth=2.5, label=f'μ = {wl_mean:.2f} nm')
        ax.axvline(wl_mean + wl_std, color='orange', linestyle=':', linewidth=2, label=f'±1σ = {wl_std:.2f} nm')
        ax.axvline(wl_mean - wl_std, color='orange', linestyle=':', linewidth=2)
        ax.axvline(wl_mean + wl_incerteza, color='darkred', linestyle='-.', linewidth=1.5, 
                  label=f'Incerteza: ±{wl_incerteza:.3f} nm')
        ax.axvline(wl_mean - wl_incerteza, color='darkred', linestyle='-.', linewidth=1.5)
        
        ax.set_xlabel('Comprimento de Onda (nm)', fontsize=11)
        ax.set_ylabel('Frequência', fontsize=11)
        ax.set_title(f'{nome_rgb}\nμ = {wl_mean:.2f} nm | σ = {wl_std:.2f} nm | N = {len(wl_values)}', 
                     fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)
    
    plt.suptitle('Distribuição dos Comprimentos de Onda - 3 Picos Principais RGB (100 amostras)', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(pasta_output / "histogramas_3_picos_RGB.png", dpi=300, bbox_inches='tight')
    print(f"  [OK] Gráfico salvo: histogramas_3_picos_RGB.png")
    plt.close()
    
    # Gráfico 3: Box plots comparativos dos 3 picos principais RGB
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Box plot de comprimentos de onda
    ax1 = axes[0]
    dados_wl = []
    labels_wl = []
    cores_wl = []
    for grupo_id, grupo_data in grupos_principais.items():
        picos = grupo_data['picos']
        wl_values = [p['wl'] for p in picos]
        dados_wl.append(wl_values)
        nome_rgb = grupo_data.get('nome_rgb', f'Grupo {grupo_id}')
        wl_mean = estatisticas_df[estatisticas_df['Grupo'] == grupo_id]['Comprimento_Onda_Medio_nm'].values[0]
        labels_wl.append(f'{nome_rgb}\n({wl_mean:.1f} nm)')
        cor = grupo_data.get('cor_rgb', 'lightblue')
        cores_wl.append(cor)
    
    bp1 = ax1.boxplot(dados_wl, tick_labels=labels_wl, patch_artist=True)
    for patch, cor in zip(bp1['boxes'], cores_wl):
        patch.set_facecolor(cor)
        patch.set_alpha(0.7)
    
    ax1.set_ylabel('Comprimento de Onda (nm)', fontsize=12)
    ax1.set_title('Distribuição dos Comprimentos de Onda - 3 Picos Principais RGB', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Box plot de intensidades
    ax2 = axes[1]
    dados_int = []
    labels_int = []
    cores_int = []
    for grupo_id, grupo_data in grupos_principais.items():
        picos = grupo_data['picos']
        int_values = [p['intensity'] for p in picos]
        dados_int.append(int_values)
        nome_rgb = grupo_data.get('nome_rgb', f'Grupo {grupo_id}')
        int_mean = estatisticas_df[estatisticas_df['Grupo'] == grupo_id]['Intensidade_Media'].values[0]
        labels_int.append(f'{nome_rgb}\n(Int: {int_mean:.1f})')
        cor = grupo_data.get('cor_rgb', 'lightcoral')
        cores_int.append(cor)
    
    bp2 = ax2.boxplot(dados_int, tick_labels=labels_int, patch_artist=True)
    for patch, cor in zip(bp2['boxes'], cores_int):
        patch.set_facecolor(cor)
        patch.set_alpha(0.7)
    
    ax2.set_ylabel('Intensidade (arb. unit)', fontsize=12)
    ax2.set_title('Distribuição das Intensidades - 3 Picos Principais RGB', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Análise Estatística - 100 Amostras Temporais', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(pasta_output / "boxplots_3_picos_RGB.png", dpi=300, bbox_inches='tight')
    print(f"  [OK] Gráfico salvo: boxplots_3_picos_RGB.png")
    plt.close()
    
    # Gráfico 4: Resumo estatístico dos 3 picos principais (barra de erros)
    fig, ax = plt.subplots(figsize=(12, 7))
    
    grupos_ids = picos_principais_df['Grupo'].values
    wl_means = picos_principais_df['Comprimento_Onda_Medio_nm'].values
    wl_incertezas = picos_principais_df['Incerteza_Expandida_nm'].values
    wl_stds = picos_principais_df['Desvio_Padrao_nm'].values
    identificacoes = picos_principais_df['Identificacao'].values
    cores = [grupos_principais[gid].get('cor_rgb', 'blue') for gid in grupos_ids]
    
    x_pos = np.arange(len(grupos_ids))
    
    # Plota barras de erro com incerteza expandida
    ax.errorbar(x_pos, wl_means, yerr=wl_incertezas, fmt='o', capsize=8, capthick=3, 
                markersize=12, linewidth=3, color='red', 
                label='Incerteza Expandida (k=1.96, 95% confiança)', zorder=3)
    
    # Plota também desvio padrão
    ax.errorbar(x_pos, wl_means, yerr=wl_stds, fmt='s', capsize=5, capthick=2,
                markersize=10, linewidth=2, color='orange', alpha=0.7,
                label='Desvio Padrão (1σ)', zorder=2)
    
    # Adiciona pontos coloridos por cor RGB
    for i, (mean, cor) in enumerate(zip(wl_means, cores)):
        ax.scatter(i, mean, s=200, color=cor, zorder=4, edgecolors='black', linewidth=2)
    
    ax.set_xlabel('Pico RGB', fontsize=13, fontweight='bold')
    ax.set_ylabel('Comprimento de Onda (nm)', fontsize=13, fontweight='bold')
    ax.set_title('Comprimentos de Onda Médios dos 3 Picos Principais RGB\ncom Incertezas Expandidas (100 amostras)', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(identificacoes, fontsize=11, rotation=0, ha='center')
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax.legend(fontsize=11, loc='upper left')
    
    # Adiciona valores nas barras
    for i, (mean, inc, std) in enumerate(zip(wl_means, wl_incertezas, wl_stds)):
        ax.text(i, mean + inc + 2, f'{mean:.2f} ± {inc:.3f} nm\n(σ = {std:.2f} nm)', 
                ha='center', va='bottom', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(pasta_output / "resumo_estatistico_3_picos_RGB.png", dpi=300, bbox_inches='tight')
    print(f"  [OK] Gráfico salvo: resumo_estatistico_3_picos_RGB.png")
    plt.close()
    
    print(f"[OK] Todos os graficos salvos em: {pasta_output}")


def analise_estatistica_temporal(pasta_temporal=None, tolerancia_nm=5.0):
    """
    Realiza análise estatística completa dos dados temporais.
    
    Args:
        pasta_temporal: Caminho para a pasta Temporal (opcional)
        tolerancia_nm: Tolerância para agrupar picos correspondentes (nm)
    """
    print("=" * 70)
    print("Análise Estatística Temporal - OSA Visível")
    print("=" * 70)
    print()
    
    # Processa todos os espectros
    resultados_todos = processar_todos_espectros_temporais(pasta_temporal)
    
    if resultados_todos is None or len(resultados_todos) == 0:
        print("[ERRO] Nenhum espectro processado")
        return None
    
    num_amostras = len(resultados_todos)
    print(f"\n[INFO] Total de amostras processadas: {num_amostras}")
    
    # Agrupa picos correspondentes
    grupos_picos = agrupar_picos_correspondentes(resultados_todos, tolerancia_nm=tolerancia_nm)
    
    if grupos_picos is None:
        print("[ERRO] Falha ao agrupar picos")
        return None
    
    # Calcula estatísticas
    estatisticas_df = calcular_estatisticas_picos(grupos_picos, num_amostras)
    
    # Separa picos principais dos secundários
    picos_principais_df = estatisticas_df[estatisticas_df['Principal_RGB'] == 'Sim'].copy()
    picos_secundarios_df = estatisticas_df[estatisticas_df['Principal_RGB'] == 'Não'].copy()
    
    # Exibe tabela de estatísticas dos 3 picos principais RGB
    print("\n" + "=" * 130)
    print("ESTATÍSTICAS DOS 3 PICOS PRINCIPAIS RGB (100 AMOSTRAS)")
    print("=" * 130)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    
    if len(picos_principais_df) > 0:
        # Seleciona colunas mais relevantes para exibição
        cols_principais = ['Identificacao', 'Cor', 'Comprimento_Onda_Medio_nm', 'Desvio_Padrao_nm', 
                          'Incerteza_Expandida_nm', 'Intensidade_Media', 'Coeficiente_Variacao_Intensidade_%', 
                          'Taxa_Deteccao_%']
        print(picos_principais_df[cols_principais].to_string(index=False))
    else:
        print("Nenhum pico principal identificado.")
    
    print("=" * 130)
    
    # Exibe picos secundários se houver
    if len(picos_secundarios_df) > 0:
        print(f"\n[INFO] {len(picos_secundarios_df)} pico(s) secundário(s) também detectado(s)")
        print("(Consulte o arquivo CSV para detalhes completos)")
    
    # Resumo estatístico dos 3 picos principais
    if len(picos_principais_df) >= 3:
        print("\n" + "=" * 130)
        print("RESUMO ESTATÍSTICO - 3 PICOS PRINCIPAIS RGB")
        print("=" * 130)
        print(f"{'Pico':<20} {'Comprimento de Onda (nm)':<30} {'Incerteza (nm)':<20} {'Taxa Detecção (%)':<20}")
        print("-" * 130)
        for _, row in picos_principais_df.iterrows():
            print(f"{row['Identificacao']:<20} {row['Comprimento_Onda_Medio_nm']:.2f} ± {row['Incerteza_Expandida_nm']:.3f} "
                  f"{'':<15} {row['Taxa_Deteccao_%']:.1f}")
        print("=" * 130)
    
    # Salva estatísticas em CSV
    if pasta_temporal is None:
        script_dir = Path(__file__).parent
        pasta_temporal = script_dir.parent / "Visible_OSA" / "Temporal"
    
    pasta_temporal = Path(pasta_temporal)
    csv_file = pasta_temporal / "estatisticas_picos.csv"
    estatisticas_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"\n[OK] Estatísticas salvas em: {csv_file}")
    
    # Gera gráficos
    gerar_graficos_estatisticos(grupos_picos, estatisticas_df, pasta_temporal)
    
    return {
        'resultados_todos': resultados_todos,
        'grupos_picos': grupos_picos,
        'estatisticas': estatisticas_df
    }


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Análise de espectros do OSA Visível')
    parser.add_argument('--temporal', action='store_true', help='Análise estatística temporal')
    parser.add_argument('--amostra-livre', action='store_true', help='Análise de amostra livre')
    parser.add_argument('--tolerancia', type=float, default=5.0, help='Tolerância para agrupar picos (nm)')
    
    args = parser.parse_args()
    
    if args.temporal:
        # Análise estatística temporal
        resultados = analise_estatistica_temporal(tolerancia_nm=args.tolerancia)
    elif args.amostra_livre:
        # Análise de amostra livre
        resultados = analisar_amostra_livre()
    else:
        # Por padrão, faz análise temporal
        print("[INFO] Executando análise temporal por padrão. Use --amostra-livre para análise de amostra livre.")
        resultados = analise_estatistica_temporal(tolerancia_nm=args.tolerancia)
    
    if resultados is not None:
        print("\n[OK] Análise concluída com sucesso!")
        return resultados
    else:
        print("\n[ERRO] Falha na análise.")
        return None


if __name__ == "__main__":
    resultados = main()
