#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera espectogramas (heatmaps espectro × amostra) a partir dos conjuntos
temporais do OSA Visível e do ThorLabs.

Saída: ``resultados/paper_figures/<fonte>/espectograma.png``.

Uso típico:
    python Experimentos/scripts/espectograma.py --fonte both
"""

import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize


# ---------------------------------------------------------------------------
# Configurações
# ---------------------------------------------------------------------------

FAIXA_VISIVEL_NM = (380.0, 780.0)


def _config_fonte(fonte):
    """Retorna caminho padrão e rótulo por equipamento."""
    fonte_normalizada = str(fonte).strip().lower()
    script_dir = Path(__file__).parent
    if fonte_normalizada == "visible":
        return {
            "fonte": "visible",
            "label": "OSA Visível",
            "pasta_temporal": script_dir.parent / "Visible_OSA" / "Temporal",
        }
    if fonte_normalizada == "thorlabs":
        return {
            "fonte": "thorlabs",
            "label": "ThorLabs OSA",
            "pasta_temporal": script_dir.parent / "ThorLabs" / "Temporal_Selecionado",
        }
    raise ValueError(f"Fonte inválida: {fonte}. Use 'visible' ou 'thorlabs'.")


def _paper_output_dir(fonte):
    """Pasta consolidada de figuras do paper: resultados/paper_figures/<fonte>."""
    fonte_normalizada = str(fonte).strip().lower()
    projeto_root = Path(__file__).resolve().parents[2]
    output_dir = projeto_root / "resultados" / "paper_figures" / fonte_normalizada
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _matplotlib_paper_context():
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
        "figure.dpi": 120,
        "savefig.dpi": 300,
    }


def _spines_clean(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# ---------------------------------------------------------------------------
# Leitura dos dados
# ---------------------------------------------------------------------------

def carregar_espectro(arquivo):
    """Lê ``spectrum*.txt`` (wl em metros, intensidade) e retorna (wl_nm, I)."""
    dados = np.loadtxt(arquivo, delimiter=";")
    wl_nm = dados[:, 0] * 1e9
    intensidade = dados[:, 1]
    return wl_nm, intensidade


def carregar_matriz_temporal(pasta, faixa_nm=FAIXA_VISIVEL_NM):
    """
    Lê todos os ``spectrum*.txt`` de ``pasta`` (em ordem) e devolve:
        wl     -> array 1D de comprimento de onda (nm)
        matriz -> array 2D (n_amostras, n_pontos)
    """
    pasta = Path(pasta)
    arquivos = sorted(pasta.glob("spectrum*.txt"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum spectrum*.txt em {pasta}")

    wl_ref, _ = carregar_espectro(arquivos[0])
    if faixa_nm is not None:
        mask_ref = (wl_ref >= faixa_nm[0]) & (wl_ref <= faixa_nm[1])
        wl_ref = wl_ref[mask_ref]
    else:
        mask_ref = np.ones_like(wl_ref, dtype=bool)

    matriz = np.empty((len(arquivos), wl_ref.size), dtype=float)

    for i, arquivo in enumerate(arquivos):
        wl_i, inten_i = carregar_espectro(arquivo)
        if faixa_nm is not None:
            mask_i = (wl_i >= faixa_nm[0]) & (wl_i <= faixa_nm[1])
            inten_i = inten_i[mask_i]
            wl_i = wl_i[mask_i]

        # Alinha por interpolação caso a grade varie entre arquivos
        if inten_i.size != wl_ref.size or not np.allclose(wl_i, wl_ref):
            inten_i = np.interp(wl_ref, wl_i, inten_i)

        matriz[i] = inten_i

    return wl_ref, matriz


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

def plotar_espectograma(
    wl,
    matriz,
    titulo,
    caminho_saida,
    *,
    escala="linear",
    cmap="inferno",
):
    """Gera e salva um heatmap (wl × amostra) em ``caminho_saida``."""
    n_amostras = matriz.shape[0]
    amostras = np.arange(n_amostras)

    matriz_plot = matriz.copy()
    if escala == "log":
        positivo = matriz_plot[matriz_plot > 0]
        if positivo.size == 0:
            escala = "linear"
        else:
            vmin = max(positivo.min(), 1e-3)
            vmax = matriz_plot.max()
            matriz_plot = np.clip(matriz_plot, vmin, vmax)
            norm = LogNorm(vmin=vmin, vmax=vmax)
    if escala != "log":
        vmax = float(np.nanmax(matriz_plot))
        vmin = max(0.0, float(np.nanmin(matriz_plot)))
        norm = Normalize(vmin=vmin, vmax=vmax)

    with plt.rc_context(_matplotlib_paper_context()):
        fig, ax = plt.subplots(figsize=(7.0, 3.8), constrained_layout=True)
        mesh = ax.pcolormesh(
            wl,
            amostras,
            matriz_plot,
            cmap=cmap,
            shading="auto",
            norm=norm,
        )
        cbar = fig.colorbar(mesh, ax=ax, pad=0.015)
        cbar.set_label("Intensidade (u.a.)")
        cbar.outline.set_linewidth(0.5)

        ax.set_xlabel(r"$\lambda$ (nm)")
        ax.set_ylabel("Amostra")
        ax.set_title(titulo, loc="left", fontweight="600")
        _spines_clean(ax)
        ax.set_xlim(wl.min(), wl.max())
        ax.set_ylim(0, n_amostras - 1)

        fig.savefig(caminho_saida, dpi=300, bbox_inches="tight")
        plt.close(fig)


# ---------------------------------------------------------------------------
# Pipeline por fonte
# ---------------------------------------------------------------------------

def gerar_espectograma_fonte(fonte, faixa_nm=FAIXA_VISIVEL_NM, escala="linear"):
    config = _config_fonte(fonte)
    pasta_saida = _paper_output_dir(fonte)
    arquivo_saida = pasta_saida / "espectograma.png"

    print("=" * 70)
    print(f"Espectograma - {config['label']}")
    print("=" * 70)
    print(f"[INFO] Lendo espectros em: {config['pasta_temporal']}")

    wl, matriz = carregar_matriz_temporal(config["pasta_temporal"], faixa_nm=faixa_nm)
    print(f"[INFO] {matriz.shape[0]} amostras, {wl.size} pontos espectrais")
    print(f"[INFO] Faixa espectral: {wl.min():.2f} - {wl.max():.2f} nm")

    titulo = f"{config['label']} — 100 espectros"
    plotar_espectograma(
        wl,
        matriz,
        titulo=titulo,
        caminho_saida=arquivo_saida,
        escala=escala,
    )
    print(f"[OK] Figura salva em: {arquivo_saida.resolve()}\n")
    return arquivo_saida


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Gera espectograma (heatmap wl × amostra) para OSA Visível e/ou ThorLabs."
    )
    parser.add_argument(
        "--fonte",
        choices=["visible", "thorlabs", "both"],
        default="both",
        help="Fonte dos dados (default: both)",
    )
    parser.add_argument(
        "--wl-min",
        type=float,
        default=FAIXA_VISIVEL_NM[0],
        help="Limite inferior de comprimento de onda em nm (default: 380).",
    )
    parser.add_argument(
        "--wl-max",
        type=float,
        default=FAIXA_VISIVEL_NM[1],
        help="Limite superior de comprimento de onda em nm (default: 780).",
    )
    parser.add_argument(
        "--escala",
        choices=["linear", "log"],
        default="linear",
        help="Escala de intensidade no colorbar (default: linear).",
    )
    args = parser.parse_args()

    faixa = (float(args.wl_min), float(args.wl_max))

    fontes = ["visible", "thorlabs"] if args.fonte == "both" else [args.fonte]
    for fonte in fontes:
        gerar_espectograma_fonte(fonte, faixa_nm=faixa, escala=args.escala)

    print("[OK] Espectogramas gerados.")


if __name__ == "__main__":
    main()
