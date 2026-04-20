#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise de espectros do OSA Visível — variantes de figuras para artigo.

Mesma lógica que analise.py; os gráficos estatísticos são salvos em
``resultados/paper_figures/<fonte>/`` e um resumo textual comparável vai para
``resultados/resultados_paper.txt`` (UTF-8, texto simples).

Ordem dos picos principais nas figuras e resumos do paper: Vermelho, Verde, Azul
(lambda medio decrescente).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.signal import find_peaks
from scipy.cluster.hierarchy import linkage, fcluster
from pathlib import Path
import os
from collections import defaultdict
import pandas as pd


def _matplotlib_paper_context():
    """Parâmetros rc para figuras de artigo: fontes legíveis, traços discretos."""
    return {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica", "Nimbus Sans"],
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "axes.linewidth": 0.9,
        "lines.linewidth": 1.2,
        "grid.linewidth": 0.55,
        "grid.alpha": 0.45,
        "figure.dpi": 120,
        "savefig.dpi": 300,
    }


def _spines_clean(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _config_fonte(fonte):
    """Retorna configuração por fonte de dados espectrais."""
    fonte_normalizada = str(fonte).strip().lower()
    script_dir = Path(__file__).parent
    if fonte_normalizada == "visible":
        return {
            "fonte": "visible",
            "label": "OSA Visível",
            "pasta_temporal": script_dir.parent / "Visible_OSA" / "Temporal",
            "peak_params": {"prominence": 5, "distance": None},
        }
    if fonte_normalizada == "thorlabs":
        return {
            "fonte": "thorlabs",
            "label": "ThorLabs OSA",
            "pasta_temporal": script_dir.parent / "ThorLabs" / "Temporal_Selecionado",
            # ThorLabs tem maior resolução e mais flutuações de alta frequência.
            # Prominence alto reduz detecção de ruído como "pico".
            "peak_params": {"prominence": 500, "distance": 10},
        }
    raise ValueError(f"Fonte inválida: {fonte}. Use 'visible' ou 'thorlabs'.")


def _paper_output_dir(fonte):
    """
    Diretório consolidado de figuras do paper:
    <raiz>/resultados/paper_figures/<visible|thorlabs>
    """
    fonte_normalizada = str(fonte).strip().lower()
    projeto_root = Path(__file__).resolve().parents[2]
    output_dir = projeto_root / "resultados" / "paper_figures" / fonte_normalizada
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _resultados_paper_path():
    """Caminho do arquivo de resumo para comparacao: <raiz>/resultados/resultados_paper.txt"""
    projeto_root = Path(__file__).resolve().parents[2]
    out_dir = projeto_root / "resultados"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / "resultados_paper.txt"


def _ordem_picos_paper_rvg(grupos_principais_dict, picos_principais_df):
    """
    Ordem fixa para figuras e textos do paper: Vermelho, Verde, Azul
    (comprimento de onda medio decrescente nos picos principais).

    Retorna lista [(grupo_id, grupo_data), ...] e o DataFrame de picos
    principais alinhado a essa ordem.
    """
    if len(grupos_principais_dict) == 0:
        return [], picos_principais_df

    triplas = []
    for gid, gdata in grupos_principais_dict.items():
        sub = picos_principais_df.loc[picos_principais_df["Grupo"] == gid, "Comprimento_Onda_Medio_nm"]
        if len(sub) > 0:
            wl_m = float(sub.iloc[0])
        else:
            wl_m = float(gdata.get("wl_medio", np.nan))
        triplas.append((gid, gdata, wl_m))

    triplas.sort(key=lambda t: t[2], reverse=True)
    pairs_ordered = [(t[0], t[1]) for t in triplas]
    ordem_ids = [t[0] for t in triplas]
    idx = picos_principais_df.set_index("Grupo")
    pdf = idx.loc[ordem_ids].reset_index()
    return pairs_ordered, pdf


def _formatar_bloco_resultados_paper(nome_equipamento, estatisticas_df):
    """
    Texto conciso com metricas dos picos principais RGB (sem simbolos especiais).
    """
    df = estatisticas_df[estatisticas_df["Principal_RGB"] == "Sim"].copy()
    df = df.sort_values("Comprimento_Onda_Medio_nm", ascending=False)
    linhas = []
    linhas.append(f"--- {nome_equipamento} ---")
    linhas.append(f"Numero de picos principais: {len(df)}")
    linhas.append("")
    for _, row in df.iterrows():
        ident = str(row.get("Identificacao", "")).strip()
        cor = str(row.get("Cor", "")).strip()
        linhas.append(f"Pico: {ident}  Cor: {cor}")
        linhas.append(f"  Lambda medio (nm): {row['Comprimento_Onda_Medio_nm']:.3f}")
        linhas.append(f"  Desvio padrao (nm): {row['Desvio_Padrao_nm']:.3f}")
        linhas.append(f"  Incerteza expandida k 1.96 (nm): {row['Incerteza_Expandida_nm']:.3f}")
        linhas.append(f"  Taxa deteccao (%): {row['Taxa_Deteccao_%']:.1f}")
        linhas.append(f"  Intensidade media (u.a.): {row['Intensidade_Media']:.2f}")
        linhas.append(f"  CV intensidade (%): {row['Coeficiente_Variacao_Intensidade_%']:.2f}")
        linhas.append(
            f"  Lambda min (nm): {row['Min_nm']:.2f}  Lambda max (nm): {row['Max_nm']:.2f}"
        )
        linhas.append("")
    return "\n".join(linhas).rstrip()


def _escrever_resultados_paper_texto(fonte_arg, resultados):
    """Grava resultados/resultados_paper.txt em UTF-8."""
    partes = []
    partes.append("Resumo estatistico temporal - picos principais RGB")
    partes.append("UTF-8. Texto simples para comparacao entre equipamentos.")
    partes.append("")

    if fonte_arg == "both" and isinstance(resultados, dict):
        for key in ("visible", "thorlabs"):
            r = resultados.get(key)
            if not r or "estatisticas" not in r:
                continue
            label = _config_fonte(key)["label"]
            partes.append(_formatar_bloco_resultados_paper(label, r["estatisticas"]))
            partes.append("")
    elif isinstance(resultados, dict) and "estatisticas" in resultados:
        label = _config_fonte(fonte_arg)["label"]
        partes.append(_formatar_bloco_resultados_paper(label, resultados["estatisticas"]))
    else:
        return

    texto = "\n".join(partes).rstrip() + "\n"
    path = _resultados_paper_path()
    path.write_text(texto, encoding="utf-8")
    print(f"\n[OK] Resumo para comparacao: {path.resolve()}")


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


def processar_todos_espectros_temporais(pasta_temporal=None, fonte="visible"):
    """
    Processa todos os espectros temporais e detecta picos em cada um.
    
    Args:
        pasta_temporal: Caminho para a pasta temporal (opcional)
        fonte: "visible" ou "thorlabs"
        
    Returns:
        Lista de dicionários com resultados de cada espectro
    """
    config = _config_fonte(fonte)
    # Define caminho padrão por fonte
    if pasta_temporal is None:
        pasta_temporal = config["pasta_temporal"]
    
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
            
            # Detecta picos (parâmetros variam por fonte)
            params = config["peak_params"]
            peaks, peak_wl, peak_intensity, info = detectar_picos(
                wl,
                intensity,
                prominence=params["prominence"],
                distance=params["distance"],
            )
            
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
        
        # Taxa de detecção: amostras únicas em que o grupo apareceu
        num_amostras_grupo = len(set([p["amostra_idx"] for p in picos]))
        taxa_deteccao = (num_amostras_grupo / num_amostras_total) * 100
        
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
            'Num_Detecoes': num_amostras_grupo,
            'Taxa_Deteccao_%': taxa_deteccao
        })
    
    df = pd.DataFrame(estatisticas)
    
    # Ordena: principais primeiro, depois por comprimento de onda
    df['Principal_Order'] = df['Principal_RGB'].map({'Sim': 0, 'Não': 1})
    df = df.sort_values(['Principal_Order', 'Comprimento_Onda_Medio_nm']).drop('Principal_Order', axis=1)
    
    return df


def gerar_graficos_estatisticos(grupos_picos, estatisticas_df, fonte="visible"):
    """
    Gera os mesmos gráficos estatísticos que analise.py, com formatação para artigo.

    Salva em ``resultados/paper_figures/<fonte>/``: legendas enxutas
    (sem repetir tabelas), tipografia legível e menos elementos redundantes.
    """
    print("\n[GRAFICOS] Gerando figuras (modo artigo)...")

    pasta_output = _paper_output_dir(fonte)

    picos_principais_df = estatisticas_df[estatisticas_df["Principal_RGB"] == "Sim"].copy()
    grupos_principais = {
        gid: grupos_picos[gid]
        for gid in picos_principais_df["Grupo"].values
        if gid in grupos_picos
    }

    if len(grupos_principais) == 0:
        print("[AVISO] Nenhum pico principal identificado. Gerando gráficos de todos os picos.")
        grupos_principais = grupos_picos
        pairs_ordered = list(grupos_principais.items())
    else:
        pairs_ordered, picos_principais_df = _ordem_picos_paper_rvg(
            grupos_principais, picos_principais_df
        )

    num_grupos = len(pairs_ordered)
    letters = "abcdefghijklmnopqrstuvwxyz"

    # --- Gráfico 1: evolução temporal (enxuto para paper) ---
    # Marcadores por painel (ordem RVG): triângulo, +, círculo; legenda com mesma cor.
    markers_temporal = ("^", "+", "o")
    largura_fig_temporal = 6.2 * 1.3
    # Eixo de amostra ~30% mais longo (centrado em 0..100)
    _cx_amostra = 49.5
    _meia_span_amostra = 0.5 * 101.0 * 1.3
    xlim_amostra = (_cx_amostra - _meia_span_amostra, _cx_amostra + _meia_span_amostra)

    with plt.rc_context(_matplotlib_paper_context()):
        fig, axes = plt.subplots(
            num_grupos,
            1,
            figsize=(largura_fig_temporal, 2.35 * num_grupos + 1.05),
            sharex=True,
            constrained_layout=True,
        )
        # Reserva faixa superior para a legenda sem sobrepor titulos dos paineis
        fig.set_constrained_layout_pads(rect=(0.02, 0.03, 0.98, 0.84))
        if num_grupos == 1:
            axes = [axes]

        for idx, (grupo_id, grupo_data) in enumerate(pairs_ordered):
            picos = grupo_data["picos"]
            amostras = [p["amostra_idx"] for p in picos]
            wl_values = [p["wl"] for p in picos]
            ax = axes[idx]
            cor = grupo_data.get("cor_rgb", "blue")
            nome_cor = grupo_data.get("nome_cor", "?")
            panel = f"({letters[idx]}) {nome_cor}"
            mk = markers_temporal[idx % len(markers_temporal)]
            pt_size = 21 if mk == "+" else 24
            if mk == "+":
                ax.scatter(
                    amostras,
                    wl_values,
                    alpha=0.72,
                    s=pt_size,
                    marker=mk,
                    color=cor,
                )
            else:
                ax.scatter(
                    amostras,
                    wl_values,
                    alpha=0.72,
                    s=pt_size,
                    marker=mk,
                    color=cor,
                    edgecolors="0.25",
                    linewidths=0.35,
                )
            wl_mean = estatisticas_df[estatisticas_df["Grupo"] == grupo_id][
                "Comprimento_Onda_Medio_nm"
            ].values[0]
            ax.axhline(y=wl_mean, color="0.2", linestyle="--", linewidth=1.35)

            ax.set_ylabel(r"$\lambda$ (nm)")
            ax.set_title(panel, loc="left", fontweight="600")
            ax.grid(True, axis="y", linestyle="-", alpha=0.45)
            _spines_clean(ax)
            ax.set_xlim(*xlim_amostra)

            # Dobrar o intervalo vertical de visualização, centrado nos dados
            wl_arr = np.asarray(wl_values, dtype=float)
            ymin_data = float(wl_arr.min())
            ymax_data = float(wl_arr.max())
            centro = 0.5 * (ymin_data + ymax_data)
            meia_largura = (ymax_data - ymin_data)  # dobro do atual
            if meia_largura <= 0:
                meia_largura = 1.0
            ax.set_ylim(centro - meia_largura, centro + meia_largura)

        axes[-1].set_xlabel("Amostra")
        handles_legenda = []
        for idx, (_, gd) in enumerate(pairs_ordered):
            mk = markers_temporal[idx % len(markers_temporal)]
            nome = str(gd.get("nome_cor", "?")).strip()
            lbl = f"Picos {nome}"
            c_cor = gd.get("cor_rgb", "blue")
            # Marcador '+' na legenda: contorno grosso (sem preenchimento), senão some no PDF.
            if mk == "+":
                handles_legenda.append(
                    Line2D(
                        [0],
                        [0],
                        marker="+",
                        linestyle="none",
                        color=c_cor,
                        markerfacecolor="none",
                        markeredgecolor=c_cor,
                        markersize=8,
                        markeredgewidth=1.4,
                        label=lbl,
                    )
                )
            else:
                ms = 7
                handles_legenda.append(
                    Line2D(
                        [0],
                        [0],
                        marker=mk,
                        linestyle="none",
                        color=c_cor,
                        markerfacecolor=c_cor,
                        markeredgecolor="0.2",
                        markersize=ms,
                        markeredgewidth=0.9,
                        label=lbl,
                    )
                )
        handles_legenda.append(
            Line2D(
                [0, 1],
                [0, 0],
                color="0.2",
                linestyle=(0, (4.0, 2.0, 4.0, 2.0)),
                linewidth=1.5,
                label="Média",
            )
        )
        fig.legend(
            handles=handles_legenda,
            loc="center",
            bbox_to_anchor=(0.5, 0.935),
            bbox_transform=fig.transFigure,
            ncol=min(4, len(handles_legenda)),
            framealpha=0.95,
            edgecolor="0.85",
            fontsize=9,
            handletextpad=0.28,
            columnspacing=0.9,
            handlelength=2.2,
            borderpad=0.35,
        )
        out1 = pasta_output / "evolucao_temporal_3_picos_RGB.png"
        fig.savefig(out1, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"  [OK] {out1.name}")

    # --- Gráfico 2: histogramas (bins = resolução amostral) ---
    BIN_WIDTH_NM = 1.5
    with plt.rc_context(_matplotlib_paper_context()):
        fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.35), constrained_layout=True)

        for idx, (grupo_id, grupo_data) in enumerate(pairs_ordered):
            picos = grupo_data["picos"]
            wl_values = np.array([p["wl"] for p in picos])
            cor = grupo_data.get("cor_rgb", "blue")
            nome_cor = grupo_data.get("nome_cor", "?")

            wl_min, wl_max = wl_values.min(), wl_values.max()
            bin_start = np.floor(wl_min / BIN_WIDTH_NM) * BIN_WIDTH_NM
            bin_end = (
                np.ceil((wl_max - bin_start) / BIN_WIDTH_NM) * BIN_WIDTH_NM
                + bin_start
                + BIN_WIDTH_NM
            )
            bins = np.arange(bin_start, bin_end, BIN_WIDTH_NM)
            ax = axes[idx]

            ax.hist(
                wl_values,
                bins=bins,
                alpha=0.82,
                edgecolor="0.25",
                linewidth=0.45,
                color=cor,
                label="Contagens",
            )

            wl_mean = estatisticas_df[estatisticas_df["Grupo"] == grupo_id][
                "Comprimento_Onda_Medio_nm"
            ].values[0]
            wl_std = estatisticas_df[estatisticas_df["Grupo"] == grupo_id][
                "Desvio_Padrao_nm"
            ].values[0]
            wl_incerteza = estatisticas_df[estatisticas_df["Grupo"] == grupo_id][
                "Incerteza_Expandida_nm"
            ].values[0]

            ax.axvline(wl_mean, color="0.2", linestyle="--", linewidth=1.5, label="Média")
            ax.axvline(wl_mean + wl_std, color="#cc6600", linestyle=":", linewidth=1.35)
            ax.axvline(wl_mean - wl_std, color="#cc6600", linestyle=":", linewidth=1.35, label=r"$\pm 1\sigma$")
            ax.axvline(wl_mean + wl_incerteza, color="#8b0000", linestyle="-.", linewidth=1.2)
            ax.axvline(
                wl_mean - wl_incerteza,
                color="#8b0000",
                linestyle="-.",
                linewidth=1.2,
                label=r"Incerteza ($k = 1{,}96$)",
            )

            ax.set_xlabel(r"$\lambda$ (nm)")
            if idx == 0:
                ax.set_ylabel("Contagem")
            ax.set_title(f"({letters[idx]}) {nome_cor}", loc="left", fontweight="600")
            ax.grid(True, axis="y", alpha=0.45)
            _spines_clean(ax)
            ax.set_ylim(0, 150)
            ax.legend(loc="upper right", framealpha=0.95, edgecolor="0.85")

        out2 = pasta_output / "histogramas_3_picos_RGB.png"
        fig.savefig(out2, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"  [OK] {out2.name}")

    # --- Gráfico 3: boxplots ---
    with plt.rc_context(_matplotlib_paper_context()):
        fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.6), constrained_layout=True)

        dados_wl, labels_wl, cores_wl = [], [], []
        dados_int, labels_int, cores_int = [], [], []
        for grupo_id, grupo_data in pairs_ordered:
            picos = grupo_data["picos"]
            nome_cor = grupo_data.get("nome_cor", "?")
            cor = grupo_data.get("cor_rgb", "lightblue")

            dados_wl.append([p["wl"] for p in picos])
            labels_wl.append(nome_cor)
            cores_wl.append(cor)

            dados_int.append([p["intensity"] for p in picos])
            labels_int.append(nome_cor)
            cores_int.append(cor)

        ax1 = axes[0]
        bp1 = ax1.boxplot(dados_wl, tick_labels=labels_wl, patch_artist=True)
        for patch, cor in zip(bp1["boxes"], cores_wl):
            patch.set_facecolor(cor)
            patch.set_alpha(0.65)
            patch.set_edgecolor("0.25")
        ax1.set_ylabel(r"$\lambda$ (nm)")
        ax1.grid(True, axis="y", alpha=0.45)
        _spines_clean(ax1)

        ax2 = axes[1]
        bp2 = ax2.boxplot(dados_int, tick_labels=labels_int, patch_artist=True)
        for patch, cor in zip(bp2["boxes"], cores_int):
            patch.set_facecolor(cor)
            patch.set_alpha(0.65)
            patch.set_edgecolor("0.25")
        ax2.set_ylabel("Intensidade (u.a.)")
        ax2.grid(True, axis="y", alpha=0.45)
        _spines_clean(ax2)

        out3 = pasta_output / "boxplots_3_picos_RGB.png"
        fig.savefig(out3, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"  [OK] {out3.name}")

    # --- Gráfico 4: médias com barras de erro ---
    with plt.rc_context(_matplotlib_paper_context()):
        fig, ax = plt.subplots(figsize=(5.2, 3.8), constrained_layout=True)

        grupos_ids = picos_principais_df["Grupo"].values
        wl_means = picos_principais_df["Comprimento_Onda_Medio_nm"].values
        wl_incertezas = picos_principais_df["Incerteza_Expandida_nm"].values
        wl_stds = picos_principais_df["Desvio_Padrao_nm"].values
        cores_rgb = [grupos_principais[gid].get("cor_rgb", "blue") for gid in grupos_ids]
        nomes_curtos = picos_principais_df["Cor"].values

        x_pos = np.arange(len(grupos_ids))
        w = 0.16
        ax.errorbar(
            x_pos - w / 2,
            wl_means,
            yerr=wl_incertezas,
            fmt="o",
            capsize=3.5,
            capthick=1.4,
            markersize=5,
            linewidth=1.35,
            color="#b22222",
            label=r"$U$ ($k = 1{,}96$)",
            zorder=3,
        )
        ax.errorbar(
            x_pos + w / 2,
            wl_means,
            yerr=wl_stds,
            fmt="s",
            capsize=3,
            capthick=1.2,
            markersize=4.5,
            linewidth=1.15,
            color="#cc7722",
            alpha=0.9,
            label=r"$\pm 1\sigma$",
            zorder=2,
        )
        for i, (mean, cor) in enumerate(zip(wl_means, cores_rgb)):
            ax.scatter(i, mean, s=55, color=cor, zorder=4, edgecolors="0.2", linewidth=0.8)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(nomes_curtos)
        ax.set_ylabel(r"$\lambda$ (nm)")
        ax.grid(True, axis="y", alpha=0.45)
        _spines_clean(ax)
        ax.legend(loc="upper left", framealpha=0.95, edgecolor="0.85")

        out4 = pasta_output / "resumo_estatistico_3_picos_RGB.png"
        fig.savefig(out4, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"  [OK] {out4.name}")

    print(f"[OK] Figuras (artigo) em: {pasta_output.resolve()}")


def analise_estatistica_temporal(pasta_temporal=None, tolerancia_nm=5.0, fonte="visible"):
    """
    Realiza análise estatística completa dos dados temporais.
    
    Args:
        pasta_temporal: Caminho para a pasta temporal (opcional)
        tolerancia_nm: Tolerância para agrupar picos correspondentes (nm)
        fonte: "visible" ou "thorlabs"
    """
    config = _config_fonte(fonte)
    print("=" * 70)
    print(f"Análise Estatística Temporal - {config['label']}")
    print("=" * 70)
    print()
    
    # Processa todos os espectros
    resultados_todos = processar_todos_espectros_temporais(pasta_temporal, fonte=fonte)
    
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
    
    # Separa picos principais dos secundários (ordem paper: Vermelho, Verde, Azul)
    picos_principais_df = estatisticas_df[estatisticas_df['Principal_RGB'] == 'Sim'].copy()
    if len(picos_principais_df) > 0:
        picos_principais_df = picos_principais_df.sort_values(
            "Comprimento_Onda_Medio_nm", ascending=False
        )
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
        pasta_temporal = config["pasta_temporal"]
    
    pasta_temporal = Path(pasta_temporal)
    csv_file = pasta_temporal / "estatisticas_picos.csv"
    estatisticas_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"\n[OK] Estatísticas salvas em: {csv_file}")
    
    # Gera gráficos
    gerar_graficos_estatisticos(grupos_picos, estatisticas_df, fonte=fonte)
    
    return {
        'resultados_todos': resultados_todos,
        'grupos_picos': grupos_picos,
        'estatisticas': estatisticas_df
    }


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Análise de espectros (Visible/ThorLabs) — figuras em resultados/paper_figures/'
    )
    parser.add_argument('--temporal', action='store_true', help='Análise estatística temporal')
    parser.add_argument('--amostra-livre', action='store_true', help='Análise de amostra livre')
    parser.add_argument(
        '--fonte',
        choices=['visible', 'thorlabs', 'both'],
        default='visible',
        help="Fonte dos dados temporais: visible, thorlabs ou both",
    )
    parser.add_argument('--tolerancia', type=float, default=5.0, help='Tolerância para agrupar picos (nm)')
    
    args = parser.parse_args()
    
    if args.temporal:
        # Análise estatística temporal
        if args.fonte == 'both':
            resultados = {
                'visible': analise_estatistica_temporal(tolerancia_nm=args.tolerancia, fonte='visible'),
                'thorlabs': analise_estatistica_temporal(tolerancia_nm=args.tolerancia, fonte='thorlabs'),
            }
        else:
            resultados = analise_estatistica_temporal(
                tolerancia_nm=args.tolerancia,
                fonte=args.fonte,
            )
    elif args.amostra_livre:
        # Análise de amostra livre
        if args.fonte == 'thorlabs':
            print("[ERRO] --amostra-livre só está disponível para OSA Visível.")
            return None
        resultados = analisar_amostra_livre()
    else:
        # Por padrão, faz análise temporal
        print(
            f"[INFO] Análise temporal (padrão, fonte={args.fonte}). "
            "Figuras em resultados/paper_figures/. Use --amostra-livre para amostra livre."
        )
        if args.fonte == 'both':
            resultados = {
                'visible': analise_estatistica_temporal(tolerancia_nm=args.tolerancia, fonte='visible'),
                'thorlabs': analise_estatistica_temporal(tolerancia_nm=args.tolerancia, fonte='thorlabs'),
            }
        else:
            resultados = analise_estatistica_temporal(
                tolerancia_nm=args.tolerancia,
                fonte=args.fonte,
            )
    
    if resultados is not None:
        if not args.amostra_livre:
            _escrever_resultados_paper_texto(args.fonte, resultados)
        print("\n[OK] Análise concluída com sucesso!")
        return resultados
    else:
        print("\n[ERRO] Falha na análise.")
        return None


if __name__ == "__main__":
    resultados = main()
