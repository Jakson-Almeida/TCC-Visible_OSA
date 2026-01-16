#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para listar os 100 arquivos SPF2 selecionados para conversão manual.
"""

from pathlib import Path

# Pasta com os arquivos SPF2
pasta_temporal = Path("Experimentos/ThorLabs/Temporal")

# Lista todos os arquivos SPF2 ordenados
arquivos_spf2 = sorted(pasta_temporal.glob("*.spf2"))

total_arquivos = len(arquivos_spf2)
num_amostras = 100
intervalo = max(1, total_arquivos // num_amostras)

print(f"Total de arquivos SPF2: {total_arquivos}")
print(f"Intervalo de seleção: {intervalo} arquivos")
print(f"Número de amostras a selecionar: {num_amostras}")
print()

# Seleciona os arquivos
arquivos_selecionados = arquivos_spf2[::intervalo][:num_amostras]

print(f"=" * 60)
print(f"LISTA DOS {len(arquivos_selecionados)} ARQUIVOS SELECIONADOS")
print(f"=" * 60)
print()

for idx, arquivo in enumerate(arquivos_selecionados, 1):
    print(f"{idx:3d}. {arquivo.name}")

print()
print(f"=" * 60)
print(f"Total: {len(arquivos_selecionados)} arquivos")
print()

# Salva lista em arquivo texto
arquivo_lista = pasta_temporal / "lista_arquivos_selecionados.txt"
with open(arquivo_lista, 'w', encoding='utf-8') as f:
    f.write("Lista dos 100 arquivos SPF2 selecionados para conversão manual\n")
    f.write("Estes arquivos devem ser convertidos para CSV usando o software ThorLabs OSA\n")
    f.write("=" * 70 + "\n\n")
    for idx, arquivo in enumerate(arquivos_selecionados, 1):
        f.write(f"{idx:3d}. {arquivo.name}\n")
    
    f.write("\n" + "=" * 70 + "\n")
    f.write(f"Total: {len(arquivos_selecionados)} arquivos\n")
    f.write(f"Intervalo: {intervalo} arquivos entre cada seleção\n")
    f.write(f"Indices selecionados: {[i*intervalo for i in range(len(arquivos_selecionados))]}\n")

print(f"[OK] Lista salva em: {arquivo_lista}")
