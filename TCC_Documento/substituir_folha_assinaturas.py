#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para substituir a página 4 (folha de aprovação) do modelo.pdf
pela folha de assinaturas assinada.

Uso: python substituir_folha_assinaturas.py
Requer: pip install pypdf
"""

from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Erro: instale o pypdf com: pip install pypdf")
    exit(1)

# Caminhos
SCRIPT_DIR = Path(__file__).parent
MODELO_PDF = SCRIPT_DIR / "modelo.pdf"
FOLHA_ASSINATURAS = Path(r"C:\Users\DELL\Desktop\TCC\folha_de_assinaturas_Jakson.pdf")
OUTPUT_PDF = SCRIPT_DIR / "modelo_oficial.pdf"


def main():
    if not MODELO_PDF.exists():
        print(f"[ERRO] Arquivo não encontrado: {MODELO_PDF}")
        return 1

    if not FOLHA_ASSINATURAS.exists():
        print(f"[ERRO] Arquivo não encontrado: {FOLHA_ASSINATURAS}")
        return 1

    print("Carregando PDFs...")
    modelo = PdfReader(MODELO_PDF)
    assinaturas = PdfReader(FOLHA_ASSINATURAS)

    total_paginas = len(modelo.pages)
    if total_paginas < 4:
        print(f"[ERRO] O modelo.pdf tem apenas {total_paginas} página(s).")
        return 1

    print(f"Modelo: {total_paginas} páginas")
    print("Substituindo página 4 pela folha de assinaturas...")

    writer = PdfWriter()

    # Páginas 1–3 do modelo
    for i in range(3):
        writer.add_page(modelo.pages[i])

    # Folha de assinaturas (substitui página 4)
    writer.add_page(assinaturas.pages[0])

    # Páginas 5 em diante do modelo
    for i in range(4, total_paginas):
        writer.add_page(modelo.pages[i])

    writer.write(OUTPUT_PDF)
    print(f"\n[OK] PDF gerado: {OUTPUT_PDF}")
    return 0


if __name__ == "__main__":
    exit(main())
