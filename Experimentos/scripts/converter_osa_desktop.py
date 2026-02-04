#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converte CSVs do formato ThorLabs OSA IR (Desktop/OSA) para TXT Visible_OSA.
Formato de entrada: CSV com header
  Wavelength(A),Level(A),Wavelength(B),Level(B),...,Wavelength(I),Level(I).
Cada trace (A, B, C, D, E, I) gera um arquivo TXT separado.
Formato de saída: wavelength_m;intensity (um par por linha).
"""

import sys
from pathlib import Path

TRACES = ["A", "B", "C", "D", "E", "I"]


def parse_osa_wavedata_csv(path: str) -> dict[str, list[tuple[float, float]]]:
    """
    Lê CSV no formato ThorLabs WaveData (Wavelength(X),Level(X)...).
    Retorna dict {trace: [(wl_nm, intensity), ...]} para cada trace (A, B, C, D, E, I).
    """
    traces_data: dict[str, list[tuple[float, float]]] = {t: [] for t in TRACES}
    in_data = False
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if "Wavelength(A)" in line or ("Wavelength" in line and "Level" in line):
                in_data = True
                continue
            if not in_data:
                continue
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            # 6 traces × 2 colunas = 12 colunas mínimas
            if len(parts) < 12:
                continue
            for i, trace in enumerate(TRACES):
                col_wl = 2 * i
                col_lv = 2 * i + 1
                if col_lv >= len(parts):
                    break
                try:
                    w_nm = float(parts[col_wl])
                    intensity = float(parts[col_lv])
                    if 200 <= w_nm <= 2000 and abs(intensity) < 1e6:
                        traces_data[trace].append((w_nm, intensity))
                except ValueError:
                    continue
    return traces_data


def write_visible_osa_txt(path: str, data: list[tuple[float, float]]) -> None:
    """Grava TXT no formato Visible_OSA: wavelength_m;intensity."""
    with open(path, "w", encoding="utf-8") as f:
        for w_nm, intensity in data:
            w_m = w_nm * 1e-9
            f.write(f"{w_m:.14e};{intensity:.14e}\n")


def convert_one(csv_path: str, out_dir: str) -> list[str]:
    """
    Converte um CSV para múltiplos TXT (um por trace).
    Retorna lista de caminhos dos TXT gerados.
    """
    created = []
    try:
        traces_data = parse_osa_wavedata_csv(csv_path)
        base = Path(csv_path).stem
        for trace, data in traces_data.items():
            if not data:
                continue
            txt_path = Path(out_dir) / (base + "_" + trace + ".txt")
            write_visible_osa_txt(str(txt_path), data)
            created.append(str(txt_path))
        return created
    except Exception:
        return []


def main():
    if len(sys.argv) < 3:
        print("Uso: python converter_osa_desktop.py <pasta_csv> <pasta_saida>")
        print("Ex:  python converter_osa_desktop.py C:\\Users\\DELL\\Desktop\\OSA C:\\Users\\DELL\\Desktop\\OSA\\txt")
        sys.exit(1)
    pasta_csv = Path(sys.argv[1])
    pasta_saida = Path(sys.argv[2])
    pasta_saida.mkdir(parents=True, exist_ok=True)
    csvs = sorted(pasta_csv.glob("*.csv"))
    if not csvs:
        print(f"Nenhum CSV encontrado em {pasta_csv}")
        sys.exit(1)
    total_ok = 0
    for csv_path in csvs:
        results = convert_one(str(csv_path), str(pasta_saida))
        if results:
            total_ok += len(results)
            for r in results:
                print(f"OK: {csv_path.name} -> {Path(r).name}")
        else:
            print(f"FALHA: {csv_path.name}")
    print(f"\nTotal: {total_ok} arquivo(s) TXT gerados em {pasta_saida}")


if __name__ == "__main__":
    main()
