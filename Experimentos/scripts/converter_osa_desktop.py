#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converte CSVs do formato ThorLabs OSA (Desktop/OSA) para TXT Visible_OSA.
Formato de entrada: CSV com header Wavelength(A),Level(A),... e dados em vírgulas.
Formato de saída: wavelength_m;intensity (um par por linha).
"""

import sys
from pathlib import Path


def parse_osa_wavedata_csv(path: str) -> list[tuple[float, float]]:
    """
    Lê CSV no formato ThorLabs WaveData (Wavelength(A),Level(A),...).
    Usa Trace A (primeiras duas colunas) para wavelength e intensity.
    """
    data = []
    in_data = False
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            # Procura header de dados (Wavelength(A),Level(A),...)
            if "Wavelength(A)" in line or "Wavelength" in line and "Level" in line:
                in_data = True
                continue
            if not in_data:
                continue
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2:
                try:
                    w_nm = float(parts[0])
                    intensity = float(parts[1])
                    # Filtra linhas que parecem metadados
                    if 200 <= w_nm <= 2000 and abs(intensity) < 1e6:
                        data.append((w_nm, intensity))
                except ValueError:
                    continue
    return data


def write_visible_osa_txt(path: str, data: list[tuple[float, float]]) -> None:
    """Grava TXT no formato Visible_OSA: wavelength_m;intensity."""
    with open(path, "w", encoding="utf-8") as f:
        for w_nm, intensity in data:
            w_m = w_nm * 1e-9
            f.write(f"{w_m:.14e};{intensity:.14e}\n")


def convert_one(csv_path: str, out_dir: str) -> str | None:
    """Converte um CSV para TXT. Retorna caminho do TXT ou None."""
    try:
        data = parse_osa_wavedata_csv(csv_path)
        if not data:
            return None
        base = Path(csv_path).stem
        txt_path = Path(out_dir) / (base + ".txt")
        write_visible_osa_txt(str(txt_path), data)
        return str(txt_path)
    except Exception:
        return None


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
    ok = 0
    for csv_path in csvs:
        result = convert_one(str(csv_path), str(pasta_saida))
        if result:
            ok += 1
            print(f"OK: {csv_path.name} -> {Path(result).name}")
        else:
            print(f"FALHA: {csv_path.name}")
    print(f"\nTotal: {ok}/{len(csvs)} convertidos em {pasta_saida}")


if __name__ == "__main__":
    main()
