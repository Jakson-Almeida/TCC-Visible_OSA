#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para preparar dados ThorLabs convertidos manualmente.
Converte de nanômetros para metros e renomeia para formato padronizado.
"""

import numpy as np
from pathlib import Path
import shutil


def preparar_dados_thorlabs(pasta_entrada, pasta_saida):
    """
    Prepara dados ThorLabs convertidos manualmente.
    
    Args:
        pasta_entrada: Pasta com arquivos .txt convertidos (formato: nm;intensity)
        pasta_saida: Pasta para salvar arquivos no formato Visible_OSA (formato: meters;intensity)
    """
    pasta_entrada = Path(pasta_entrada)
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    
    # Lista todos os arquivos .txt ordenados numericamente
    arquivos_txt = sorted(pasta_entrada.glob("*.txt"), 
                         key=lambda x: int(x.stem) if x.stem.isdigit() else float('inf'))
    
    if len(arquivos_txt) == 0:
        print(f"[ERRO] Nenhum arquivo .txt encontrado em {pasta_entrada}")
        return
    
    print(f"[INFO] Encontrados {len(arquivos_txt)} arquivos .txt")
    print(f"[INFO] Convertendo para formato Visible_OSA...")
    print()
    
    sucessos = 0
    falhas = 0
    
    for idx, arquivo_entrada in enumerate(arquivos_txt):
        try:
            # Lê o arquivo (formato: nm;intensity)
            dados = np.loadtxt(arquivo_entrada, delimiter=';')
            
            # Verifica se os dados estão em nanômetros (valores > 100)
            # ou já em metros (valores < 1e-6)
            if dados[0, 0] > 100:
                # Está em nanômetros, converte para metros
                wl_nm = dados[:, 0]
                intensity = dados[:, 1]
                wl_metros = wl_nm * 1e-9  # 1 nm = 1e-9 m
            else:
                # Já está em metros
                wl_metros = dados[:, 0]
                intensity = dados[:, 1]
            
            # Nome do arquivo de saída: spectrum000.txt, spectrum001.txt, etc.
            nome_saida = f"spectrum{idx:03d}.txt"
            arquivo_saida = pasta_saida / nome_saida
            
            # Salva no formato Visible_OSA
            with open(arquivo_saida, 'w') as f:
                for wl_m, int_val in zip(wl_metros, intensity):
                    f.write(f"{wl_m:.15e};{int_val:.15e}\n")
            
            sucessos += 1
            if (idx + 1) % 10 == 0:
                print(f"  Processado {idx + 1}/{len(arquivos_txt)}...")
        
        except Exception as e:
            print(f"  [ERRO] Erro ao processar {arquivo_entrada.name}: {str(e)[:100]}")
            falhas += 1
    
    print()
    print(f"[OK] Conversão concluída: {sucessos} sucessos, {falhas} falhas")
    print(f"[OK] Arquivos salvos em: {pasta_saida}")


def main():
    """Função principal."""
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    
    pasta_entrada = base_dir / "ThorLabs" / "Temporal_ThorLabs"
    pasta_saida = base_dir / "ThorLabs" / "Temporal_Selecionado"
    
    preparar_dados_thorlabs(pasta_entrada, pasta_saida)


if __name__ == "__main__":
    main()
