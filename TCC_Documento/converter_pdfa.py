#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converte PDFs para o formato PDF/A (archivable PDF), exigido para entrega do TCC.

Uso: python converter_pdfa.py

Requer: Ghostscript instalado (https://ghostscript.com/releases/gsdnld.html)
- Baixe o instalador Windows 64-bit (gs10xxw64.exe)
- Durante a instalação, marque "Add to PATH" se disponível
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# Arquivos a converter
ARQUIVOS = [
    SCRIPT_DIR / "modelo_oficial.pdf",
    SCRIPT_DIR / "doc1_assinado_260210_194403.pdf",
]


def encontrar_ghostscript() -> Path | None:
    """Encontra gswin64c.exe no sistema."""
    # Caminhos comuns no Windows
    caminhos = [
        Path(r"C:\Program Files\gs"),
        Path(r"C:\Program Files (x86)\gs"),
    ]
    for base in caminhos:
        if not base.exists():
            continue
        for sub in sorted(base.iterdir(), reverse=True):
            exe = sub / "bin" / "gswin64c.exe"
            if exe.exists():
                return exe
    # Tentar pelo PATH
    try:
        result = subprocess.run(
            ["where", "gswin64c"],
            capture_output=True, text=True, timeout=5, shell=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip().splitlines()[0].strip())
    except Exception:
        pass
    return None


def converter_para_pdfa(entrada: Path, saida: Path, gs: Path) -> bool:
    """Converte um PDF para PDF/A-2b usando Ghostscript."""
    # PDF/A-2b é amplamente aceito para arquivamento
    cmd = [
        str(gs),
        "-dPDFA=2",
        "-dBATCH",
        "-dNOPAUSE",
        "-dNOOUTERSAVE",
        "-sColorConversionStrategy=RGB",
        "-sDEVICE=pdfwrite",
        "-dPDFACompatibilityPolicy=2",
        f"-sOutputFile={saida}",
        str(entrada),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"  [AVISO] Ghostscript retornou código {result.returncode}")
            if result.stderr:
                for linha in result.stderr.strip().splitlines()[:5]:
                    print(f"    {linha}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("  [ERRO] Timeout na conversão")
        return False
    except Exception as e:
        print(f"  [ERRO] {e}")
        return False


def main() -> int:
    # UTF-8 no console (Windows)
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    gs = encontrar_ghostscript()
    if not gs:
        print("=" * 60)
        print("Ghostscript nao encontrado.")
        print()
        print("Para converter para PDF/A, instale o Ghostscript:")
        print("  1. Acesse: https://ghostscript.com/releases/gsdnld.html")
        print("  2. Baixe a versao Windows 64-bit (gs10xxw64.exe)")
        print("  3. Execute o instalador e conclua a instalacao")
        print("  4. Rode este script novamente")
        print()
        print("Alternativa: use o conversor online gratuito:")
        print("  https://tools.pdf24.org/en/pdf-to-pdfa")
        print("  Faca upload dos arquivos e baixe os PDF/A gerados.")
        print("=" * 60)
        return 1

    print(f"Ghostscript encontrado: {gs}\n")

    sucesso = 0
    for entrada in ARQUIVOS:
        if not entrada.exists():
            print(f"[PULAR] Não encontrado: {entrada.name}")
            continue

        saida = entrada.with_stem(entrada.stem + "_PDFA")
        print(f"Convertendo: {entrada.name} -> {saida.name}")

        if converter_para_pdfa(entrada, saida, gs):
            print(f"  [OK] {saida}")
            sucesso += 1
        else:
            print(f"  [FALHOU] {entrada.name}")

    if sucesso > 0:
        print(f"\n{sucesso} arquivo(s) convertido(s) para PDF/A.")
        print("Valide em: https://www.pdf24.org/pdfa-online-validator.html")
    return 0 if sucesso else 1


if __name__ == "__main__":
    sys.exit(main())
