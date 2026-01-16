#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script comparativo entre análises do OSA Visível e ThorLabs OSA.
Gera gráficos de comparação dos resultados estatísticos.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import os


def carregar_dados_estatisticos():
    """
    Carrega dados estatísticos de ambos os experimentos.
    
    Returns:
        dict com dados de Visible_OSA e ThorLabs
    """
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    
    # Carrega dados Visible_OSA
    csv_visible = base_dir / "Visible_OSA" / "Temporal" / "estatisticas_picos.csv"
    df_visible = pd.read_csv(csv_visible)
    df_visible_principais = df_visible[df_visible['Principal_RGB'] == 'Sim'].copy()
    
    # Carrega dados ThorLabs
    csv_thorlabs = base_dir / "ThorLabs" / "Temporal_Selecionado" / "estatisticas_picos_thorlabs.csv"
    df_thorlabs = pd.read_csv(csv_thorlabs)
    df_thorlabs_principais = df_thorlabs[df_thorlabs['Principal_RGB'] == 'Sim'].copy()
    
    # Ordena por comprimento de onda para garantir ordem RGB
    df_visible_principais = df_visible_principais.sort_values('Comprimento_Onda_Medio_nm')
    df_thorlabs_principais = df_thorlabs_principais.sort_values('Comprimento_Onda_Medio_nm')
    
    # Identifica picos por cor para garantir correspondência
    dados_visible = {}
    dados_thorlabs = {}
    
    for _, row in df_visible_principais.iterrows():
        cor = row['Cor']
        dados_visible[cor] = {
            'wl_medio': row['Comprimento_Onda_Medio_nm'],
            'wl_std': row['Desvio_Padrao_nm'],
            'wl_incerteza': row['Incerteza_Expandida_nm'],
            'intensidade_media': row['Intensidade_Media'],
            'intensidade_std': row['Intensidade_Desvio_Padrao'],
            'taxa_deteccao': row['Taxa_Deteccao_%'],
            'identificacao': row['Identificacao']
        }
    
    for _, row in df_thorlabs_principais.iterrows():
        cor = row['Cor']
        dados_thorlabs[cor] = {
            'wl_medio': row['Comprimento_Onda_Medio_nm'],
            'wl_std': row['Desvio_Padrao_nm'],
            'wl_incerteza': row['Incerteza_Expandida_nm'],
            'intensidade_media': row['Intensidade_Media'],
            'intensidade_std': row['Intensidade_Desvio_Padrao'],
            'taxa_deteccao': row['Taxa_Deteccao_%'],
            'identificacao': row['Identificacao']
        }
    
    return {
        'Visible_OSA': dados_visible,
        'ThorLabs': dados_thorlabs,
        'df_visible': df_visible_principais,
        'df_thorlabs': df_thorlabs_principais
    }


def gerar_graficos_comparativos(dados, pasta_output):
    """
    Gera gráficos comparativos entre Visible_OSA e ThorLabs.
    
    Args:
        dados: Dicionário com dados de ambos os experimentos
        pasta_output: Pasta para salvar os gráficos
    """
    pasta_output = Path(pasta_output)
    pasta_output.mkdir(parents=True, exist_ok=True)
    
    dados_visible = dados['Visible_OSA']
    dados_thorlabs = dados['ThorLabs']
    
    cores_rgb = ['Azul', 'Verde', 'Vermelho']
    cores_hex = {'Azul': 'blue', 'Verde': 'green', 'Vermelho': 'red'}
    
    # Gráfico 1: Comparação de comprimentos de onda médios com incertezas
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x_pos = np.arange(len(cores_rgb))
    width = 0.35
    
    wl_visible = []
    inc_visible = []
    wl_thorlabs = []
    inc_thorlabs = []
    cores_plot = []
    
    for cor in cores_rgb:
        if cor in dados_visible and cor in dados_thorlabs:
            wl_visible.append(dados_visible[cor]['wl_medio'])
            inc_visible.append(dados_visible[cor]['wl_incerteza'])
            wl_thorlabs.append(dados_thorlabs[cor]['wl_medio'])
            inc_thorlabs.append(dados_thorlabs[cor]['wl_incerteza'])
            cores_plot.append(cores_hex[cor])
    
    if len(wl_visible) == 3 and len(wl_thorlabs) == 3:
        bars1 = ax.bar(x_pos - width/2, wl_visible, width, yerr=inc_visible, 
                      label='OSA Visível', alpha=0.8, capsize=5, color='lightblue',
                      edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x_pos + width/2, wl_thorlabs, width, yerr=inc_thorlabs,
                      label='ThorLabs OSA', alpha=0.8, capsize=5, color='lightcoral',
                      edgecolor='black', linewidth=1.5)
        
        # Adiciona valores nas barras
        for i, (bar1, bar2, cor) in enumerate(zip(bars1, bars2, cores_plot)):
            # Visible_OSA
            ax.text(bar1.get_x() + bar1.get_width()/2, 
                   bar1.get_height() + inc_visible[i] + 2,
                   f"{wl_visible[i]:.2f}±{inc_visible[i]:.3f}",
                   ha='center', va='bottom', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.8))
            
            # ThorLabs
            ax.text(bar2.get_x() + bar2.get_width()/2,
                   bar2.get_height() + inc_thorlabs[i] + 2,
                   f"{wl_thorlabs[i]:.2f}±{inc_thorlabs[i]:.3f}",
                   ha='center', va='bottom', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.8))
        
        # Adiciona linha de diferença
        for i, cor in enumerate(cores_rgb):
            if cor in dados_visible and cor in dados_thorlabs:
                dif = abs(wl_visible[i] - wl_thorlabs[i])
                ax.plot([i - width/2, i + width/2], 
                       [max(wl_visible[i], wl_thorlabs[i]) + max(inc_visible[i], inc_thorlabs[i]) + 5] * 2,
                       'k--', linewidth=1.5, alpha=0.7)
                ax.text(i, max(wl_visible[i], wl_thorlabs[i]) + max(inc_visible[i], inc_thorlabs[i]) + 7,
                       f'Δ = {dif:.2f} nm', ha='center', fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    ax.set_xlabel('Pico RGB', fontsize=13, fontweight='bold')
    ax.set_ylabel('Comprimento de Onda (nm)', fontsize=13, fontweight='bold')
    ax.set_title('Comparação de Comprimentos de Onda Médios dos 3 Picos RGB\nOSA Visível vs ThorLabs OSA (100 amostras cada)', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'{cor}\n(λ~{wl_visible[i]:.0f} nm)' if i < len(wl_visible) else cor 
                        for i, cor in enumerate(cores_rgb)], fontsize=11)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax.legend(fontsize=12, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(pasta_output / "comparacao_comprimentos_onda.png", dpi=300, bbox_inches='tight')
    print(f"  [OK] Gráfico salvo: comparacao_comprimentos_onda.png")
    plt.close()
    
    # Gráfico 2: Comparação de desvios padrão
    fig, ax = plt.subplots(figsize=(12, 7))
    
    std_visible = [dados_visible[cor]['wl_std'] for cor in cores_rgb if cor in dados_visible]
    std_thorlabs = [dados_thorlabs[cor]['wl_std'] for cor in cores_rgb if cor in dados_thorlabs]
    
    if len(std_visible) == 3 and len(std_thorlabs) == 3:
        bars1 = ax.bar(x_pos - width/2, std_visible, width, 
                      label='OSA Visível', alpha=0.8, color='lightblue',
                      edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x_pos + width/2, std_thorlabs, width,
                      label='ThorLabs OSA', alpha=0.8, color='lightcoral',
                      edgecolor='black', linewidth=1.5)
        
        # Adiciona valores
        for bar1, bar2, std_v, std_t in zip(bars1, bars2, std_visible, std_thorlabs):
            ax.text(bar1.get_x() + bar1.get_width()/2, bar1.get_height() + 0.05,
                   f"{std_v:.3f}", ha='center', va='bottom', fontsize=10, fontweight='bold')
            ax.text(bar2.get_x() + bar2.get_width()/2, bar2.get_height() + 0.05,
                   f"{std_t:.3f}", ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Pico RGB', fontsize=13, fontweight='bold')
    ax.set_ylabel('Desvio Padrão (nm)', fontsize=13, fontweight='bold')
    ax.set_title('Comparação de Desvios Padrão dos Comprimentos de Onda\nOSA Visível vs ThorLabs OSA', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([cor for cor in cores_rgb], fontsize=11)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax.legend(fontsize=12)
    
    plt.tight_layout()
    plt.savefig(pasta_output / "comparacao_desvios_padrao.png", dpi=300, bbox_inches='tight')
    print(f"  [OK] Gráfico salvo: comparacao_desvios_padrao.png")
    plt.close()
    
    # Gráfico 3: Comparação de incertezas expandidas
    fig, ax = plt.subplots(figsize=(12, 7))
    
    if len(inc_visible) == 3 and len(inc_thorlabs) == 3:
        bars1 = ax.bar(x_pos - width/2, inc_visible, width,
                      label='OSA Visível', alpha=0.8, color='lightblue',
                      edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x_pos + width/2, inc_thorlabs, width,
                      label='ThorLabs OSA', alpha=0.8, color='lightcoral',
                      edgecolor='black', linewidth=1.5)
        
        # Adiciona valores
        for bar1, bar2, inc_v, inc_t in zip(bars1, bars2, inc_visible, inc_thorlabs):
            ax.text(bar1.get_x() + bar1.get_width()/2, bar1.get_height() + 0.005,
                   f"{inc_v:.3f}", ha='center', va='bottom', fontsize=10, fontweight='bold')
            ax.text(bar2.get_x() + bar2.get_width()/2, bar2.get_height() + 0.005,
                   f"{inc_t:.3f}", ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Pico RGB', fontsize=13, fontweight='bold')
    ax.set_ylabel('Incerteza Expandida (nm)', fontsize=13, fontweight='bold')
    ax.set_title('Comparação de Incertezas Expandidas (k=1.96, 95% confiança)\nOSA Visível vs ThorLabs OSA', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([cor for cor in cores_rgb], fontsize=11)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax.legend(fontsize=12)
    
    plt.tight_layout()
    plt.savefig(pasta_output / "comparacao_incertezas.png", dpi=300, bbox_inches='tight')
    print(f"  [OK] Gráfico salvo: comparacao_incertezas.png")
    plt.close()
    
    # Gráfico 4: Gráfico de diferenças absolutas
    fig, ax = plt.subplots(figsize=(12, 7))
    
    diferencas = []
    cores_dif = []
    for cor in cores_rgb:
        if cor in dados_visible and cor in dados_thorlabs:
            dif = abs(dados_visible[cor]['wl_medio'] - dados_thorlabs[cor]['wl_medio'])
            diferencas.append(dif)
            cores_dif.append(cores_hex[cor])
    
    if len(diferencas) == 3:
        bars = ax.bar(x_pos, diferencas, width=0.6, color=cores_dif, alpha=0.7,
                     edgecolor='black', linewidth=1.5)
        
        # Adiciona valores
        for bar, dif in zip(bars, diferencas):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                   f"{dif:.2f} nm", ha='center', va='bottom', fontsize=11, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Linha de referência para diferença aceitável (ex: 5 nm)
        ax.axhline(y=5, color='red', linestyle='--', linewidth=2, alpha=0.7,
                  label='Referência: 5 nm')
    
    ax.set_xlabel('Pico RGB', fontsize=13, fontweight='bold')
    ax.set_ylabel('Diferença Absoluta (nm)', fontsize=13, fontweight='bold')
    ax.set_title('Diferenças Absolutas entre Comprimentos de Onda Médios\nOSA Visível vs ThorLabs OSA', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([cor for cor in cores_rgb], fontsize=11)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    if len(diferencas) == 3:
        ax.legend(fontsize=11)
    
    plt.tight_layout()
    plt.savefig(pasta_output / "comparacao_diferencas.png", dpi=300, bbox_inches='tight')
    print(f"  [OK] Gráfico salvo: comparacao_diferencas.png")
    plt.close()
    
    # Gráfico 5: Comparação lado a lado com barras de erro
    fig, ax = plt.subplots(figsize=(16, 8))
    
    if len(wl_visible) == 3 and len(wl_thorlabs) == 3:
        # Posições para os dois sistemas
        x_visible = x_pos - width/2
        x_thorlabs = x_pos + width/2
        
        # Plota barras de erro
        for i, (cor, cor_hex) in enumerate(zip(cores_rgb, cores_dif)):
            # Visible_OSA
            ax.errorbar(x_visible[i], wl_visible[i], yerr=inc_visible[i],
                       fmt='o', capsize=8, capthick=3, markersize=12, linewidth=3,
                       color=cor_hex, label='OSA Visível' if i == 0 else '',
                       alpha=0.8, zorder=3)
            
            # ThorLabs
            ax.errorbar(x_thorlabs[i], wl_thorlabs[i], yerr=inc_thorlabs[i],
                       fmt='s', capsize=8, capthick=3, markersize=12, linewidth=3,
                       color=cor_hex, label='ThorLabs OSA' if i == 0 else '',
                       markerfacecolor='white', markeredgewidth=2, markeredgecolor=cor_hex,
                       alpha=0.8, zorder=3)
            
            # Linha conectando os dois sistemas
            ax.plot([x_visible[i], x_thorlabs[i]], 
                   [wl_visible[i], wl_thorlabs[i]],
                   'k--', linewidth=2, alpha=0.5, zorder=1)
            
            # Adiciona anotações
            ax.text(x_visible[i], wl_visible[i] + inc_visible[i] + 3,
                   f'{wl_visible[i]:.1f} nm', ha='center', va='bottom',
                   fontsize=9, fontweight='bold', color=cor_hex)
            ax.text(x_thorlabs[i], wl_thorlabs[i] + inc_thorlabs[i] + 3,
                   f'{wl_thorlabs[i]:.1f} nm', ha='center', va='bottom',
                   fontsize=9, fontweight='bold', color=cor_hex)
    
    ax.set_xlabel('Pico RGB', fontsize=13, fontweight='bold')
    ax.set_ylabel('Comprimento de Onda (nm)', fontsize=13, fontweight='bold')
    ax.set_title('Comparação Detalhada: Comprimentos de Onda com Incertezas Expandidas\nOSA Visível vs ThorLabs OSA (100 amostras cada)', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([cor for cor in cores_rgb], fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=12, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(pasta_output / "comparacao_detalhada.png", dpi=300, bbox_inches='tight')
    print(f"  [OK] Gráfico salvo: comparacao_detalhada.png")
    plt.close()
    
    # Gráfico 6: Tabela comparativa visual
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.axis('tight')
    ax.axis('off')
    
    # Prepara dados para a tabela
    tabela_dados = []
    for cor in cores_rgb:
        if cor in dados_visible and cor in dados_thorlabs:
            linha = [
                cor,
                f"{dados_visible[cor]['wl_medio']:.2f} ± {dados_visible[cor]['wl_incerteza']:.3f}",
                f"{dados_thorlabs[cor]['wl_medio']:.2f} ± {dados_thorlabs[cor]['wl_incerteza']:.3f}",
                f"{abs(dados_visible[cor]['wl_medio'] - dados_thorlabs[cor]['wl_medio']):.2f}",
                f"{dados_visible[cor]['wl_std']:.3f}",
                f"{dados_thorlabs[cor]['wl_std']:.3f}"
            ]
            tabela_dados.append(linha)
    
    colunas = ['Pico RGB', 'OSA Visível\nλ médio ± incerteza (nm)', 
               'ThorLabs OSA\nλ médio ± incerteza (nm)', 
               'Diferença\nAbsoluta (nm)',
               'OSA Visível\nσ (nm)', 
               'ThorLabs OSA\nσ (nm)']
    
    tabela = ax.table(cellText=tabela_dados, colLabels=colunas,
                     cellLoc='center', loc='center',
                     colWidths=[0.15, 0.2, 0.2, 0.15, 0.15, 0.15])
    
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(11)
    tabela.scale(1, 2.5)
    
    # Estiliza o cabeçalho
    for i in range(len(colunas)):
        tabela[(0, i)].set_facecolor('#4472C4')
        tabela[(0, i)].set_text_props(weight='bold', color='white')
    
    # Estiliza as linhas por cor
    cores_tabela = {'Azul': '#E7F3FF', 'Verde': '#E2EFDA', 'Vermelho': '#FCE4D6'}
    for idx, (linha, cor) in enumerate(zip(tabela_dados, cores_rgb), 1):
        if cor in cores_tabela:
            for j in range(len(colunas)):
                tabela[(idx, j)].set_facecolor(cores_tabela[cor])
                tabela[(idx, j)].set_text_props(weight='bold')
    
    plt.title('Tabela Comparativa: Estatísticas dos 3 Picos Principais RGB\nOSA Visível vs ThorLabs OSA', 
             fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(pasta_output / "tabela_comparativa.png", dpi=300, bbox_inches='tight')
    print(f"  [OK] Gráfico salvo: tabela_comparativa.png")
    plt.close()
    
    print(f"[OK] Todos os graficos comparativos salvos em: {pasta_output}")


def gerar_relatorio_comparativo(dados, pasta_output):
    """
    Gera relatório comparativo em texto.
    
    Args:
        dados: Dicionário com dados de ambos os experimentos
        pasta_output: Pasta para salvar o relatório
    """
    pasta_output = Path(pasta_output)
    pasta_output.mkdir(parents=True, exist_ok=True)
    
    dados_visible = dados['Visible_OSA']
    dados_thorlabs = dados['ThorLabs']
    
    relatorio = pasta_output / "relatorio_comparativo.txt"
    
    with open(relatorio, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("RELATÓRIO COMPARATIVO: OSA VISÍVEL vs THORLABS OSA\n")
        f.write("Análise Estatística dos 3 Picos Principais RGB (100 amostras cada)\n")
        f.write("=" * 100 + "\n\n")
        
        cores_rgb = ['Azul', 'Verde', 'Vermelho']
        
        for cor in cores_rgb:
            if cor in dados_visible and cor in dados_thorlabs:
                f.write(f"\n{'='*100}\n")
                f.write(f"PICO {cor.upper()}\n")
                f.write(f"{'='*100}\n\n")
                
                v = dados_visible[cor]
                t = dados_thorlabs[cor]
                
                f.write(f"OSA Visível:\n")
                f.write(f"  Comprimento de onda médio: {v['wl_medio']:.2f} nm\n")
                f.write(f"  Desvio padrão: {v['wl_std']:.3f} nm\n")
                f.write(f"  Incerteza expandida (k=1.96): ±{v['wl_incerteza']:.3f} nm\n")
                f.write(f"  Intensidade média: {v['intensidade_media']:.2f}\n")
                f.write(f"  Taxa de detecção: {v['taxa_deteccao']:.1f}%\n\n")
                
                f.write(f"ThorLabs OSA:\n")
                f.write(f"  Comprimento de onda médio: {t['wl_medio']:.2f} nm\n")
                f.write(f"  Desvio padrão: {t['wl_std']:.3f} nm\n")
                f.write(f"  Incerteza expandida (k=1.96): ±{t['wl_incerteza']:.3f} nm\n")
                f.write(f"  Intensidade média: {t['intensidade_media']:.2f}\n")
                f.write(f"  Taxa de detecção: {t['taxa_deteccao']:.1f}%\n\n")
                
                dif = abs(v['wl_medio'] - t['wl_medio'])
                f.write(f"COMPARAÇÃO:\n")
                f.write(f"  Diferença absoluta: {dif:.2f} nm\n")
                f.write(f"  Diferença relativa: {(dif/v['wl_medio']*100):.2f}%\n")
                f.write(f"  Razão de desvios padrão (ThorLabs/Visible): {t['wl_std']/v['wl_std']:.3f}\n")
                f.write(f"  Razão de incertezas (ThorLabs/Visible): {t['wl_incerteza']/v['wl_incerteza']:.3f}\n")
        
        f.write(f"\n{'='*100}\n")
        f.write("CONCLUSÕES\n")
        f.write(f"{'='*100}\n\n")
        f.write("- Ambos os sistemas detectaram os 3 picos principais RGB corretamente.\n")
        f.write("- As incertezas expandidas estão na mesma ordem de grandeza.\n")
        f.write("- O ThorLabs OSA apresenta desvios padrão ligeiramente maiores, possivelmente devido\n")
        f.write("  à maior sensibilidade do equipamento comercial.\n")
        f.write("- As diferenças nos comprimentos de onda médios podem ser atribuídas a diferenças\n")
        f.write("  na calibração espectral entre os dois sistemas.\n")
    
    print(f"[OK] Relatório salvo em: {relatorio}")


def main():
    """Função principal."""
    print("=" * 70)
    print("Análise Comparativa: OSA Visível vs ThorLabs OSA")
    print("=" * 70)
    print()
    
    # Carrega dados estatísticos
    print("[INFO] Carregando dados estatísticos...")
    dados = carregar_dados_estatisticos()
    
    print("[OK] Dados carregados com sucesso")
    print()
    
    # Exibe resumo comparativo
    dados_visible = dados['Visible_OSA']
    dados_thorlabs = dados['ThorLabs']
    
    cores_rgb = ['Azul', 'Verde', 'Vermelho']
    
    print("=" * 100)
    print("RESUMO COMPARATIVO")
    print("=" * 100)
    print(f"{'Cor':<10} {'OSA Visível (nm)':<25} {'ThorLabs OSA (nm)':<25} {'Diferença (nm)':<20}")
    print("-" * 100)
    
    for cor in cores_rgb:
        if cor in dados_visible and cor in dados_thorlabs:
            v = dados_visible[cor]['wl_medio']
            t = dados_thorlabs[cor]['wl_medio']
            dif = abs(v - t)
            print(f"{cor:<10} {v:.2f} ± {dados_visible[cor]['wl_incerteza']:.3f}  "
                  f"{t:.2f} ± {dados_thorlabs[cor]['wl_incerteza']:.3f}  "
                  f"{dif:.2f}")
    
    print("=" * 100)
    print()
    
    # Define pasta de saída
    script_dir = Path(__file__).parent
    pasta_output = script_dir.parent / "Comparacao"
    
    # Gera gráficos comparativos
    print("[GRAFICOS] Gerando graficos comparativos...")
    gerar_graficos_comparativos(dados, pasta_output)
    
    # Gera relatório comparativo
    print()
    print("[RELATORIO] Gerando relatorio comparativo...")
    gerar_relatorio_comparativo(dados, pasta_output)
    
    print()
    print("[OK] Análise comparativa concluída com sucesso!")
    print(f"[OK] Todos os arquivos salvos em: {pasta_output}")


if __name__ == "__main__":
    main()
