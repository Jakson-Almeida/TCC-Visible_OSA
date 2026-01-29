"""
Conversor CSV (ThorLabs) para TXT (Visible_OSA).
Extrai os dados de espectro dos arquivos CSV e grava em TXT no formato
wavelength (m); intensity, um valor por linha, sem cabeçalho.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os


def parse_thorlabs_csv(path: str) -> list[tuple[float, float]]:
    """
    Lê um CSV ThorLabs e retorna lista de (wavelength_nm, intensity).
    Ignora o cabeçalho e usa apenas o bloco após [Data].
    """
    data = []
    in_data = False
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line == "[Data]":
                in_data = True
                continue
            if not in_data:
                continue
            if not line or line.startswith("#"):
                continue
            parts = line.split(";")
            if len(parts) >= 2:
                try:
                    w_nm = float(parts[0])
                    intensity = float(parts[1])
                    data.append((w_nm, intensity))
                except ValueError:
                    continue
    return data


def nm_to_m(w_nm: float) -> float:
    """Converte comprimento de onda de nm para metros."""
    return w_nm * 1e-9


def write_visible_osa_txt(path: str, data: list[tuple[float, float]]) -> None:
    """
    Grava arquivo TXT no formato Visible_OSA:
    uma linha por ponto: wavelength_m;intensity (notação científica).
    """
    with open(path, "w", encoding="utf-8") as f:
        for w_nm, intensity in data:
            w_m = nm_to_m(w_nm)
            f.write(f"{w_m:.14e};{intensity:.14e}\n")


def convert_one(csv_path: str, out_dir: str) -> str | None:
    """
    Converte um CSV para TXT na pasta out_dir.
    Retorna o caminho do TXT gerado ou None em caso de erro.
    """
    try:
        data = parse_thorlabs_csv(csv_path)
        if not data:
            return None
        base = os.path.splitext(os.path.basename(csv_path))[0]
        txt_path = os.path.join(out_dir, base + ".txt")
        write_visible_osa_txt(txt_path, data)
        return txt_path
    except Exception:
        return None


def main():
    root = tk.Tk()
    root.title("CSV ThorLabs → TXT Visible_OSA")
    root.geometry("520x280")
    root.resizable(True, True)

    selected_files: list[str] = []
    out_dir_var = tk.StringVar(value="")

    def choose_files():
        paths = filedialog.askopenfilenames(
            title="Selecionar arquivo(s) CSV",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")],
        )
        if paths:
            selected_files.clear()
            selected_files.extend(paths)
            n = len(selected_files)
            if n == 1:
                lbl_files["text"] = f"1 arquivo: {os.path.basename(selected_files[0])}"
            else:
                lbl_files["text"] = f"{n} arquivos selecionados"
            lbl_files["fg"] = "green"

    def choose_dir():
        path = filedialog.askdirectory(title="Pasta para salvar os TXT")
        if path:
            out_dir_var.set(path)
            lbl_out["fg"] = "green"

    def run_convert():
        if not selected_files:
            messagebox.showwarning("Aviso", "Selecione pelo menos um arquivo CSV.")
            return
        out = out_dir_var.get().strip()
        if not out or not os.path.isdir(out):
            messagebox.showwarning("Aviso", "Selecione a pasta de destino.")
            return
        ok = 0
        failed = []
        for csv_path in selected_files:
            result = convert_one(csv_path, out)
            if result:
                ok += 1
            else:
                failed.append(os.path.basename(csv_path))
        if failed:
            messagebox.showwarning(
                "Conversão parcial",
                f"Convertidos: {ok}. Falha em: {', '.join(failed)}",
            )
        else:
            messagebox.showinfo("Concluído", f"{ok} arquivo(s) convertido(s) com sucesso.")

    # UI
    fr = ttk.Frame(root, padding=12)
    fr.pack(fill=tk.BOTH, expand=True)

    ttk.Label(fr, text="Arquivos CSV (ThorLabs):").pack(anchor=tk.W)
    btn_open = ttk.Button(fr, text="Selecionar um ou vários CSV...", command=choose_files)
    btn_open.pack(anchor=tk.W, pady=(0, 4))
    lbl_files = tk.Label(fr, text="Nenhum arquivo selecionado", fg="gray")
    lbl_files.pack(anchor=tk.W)

    ttk.Label(fr, text="Pasta para salvar os TXT:", style="TLabel").pack(anchor=tk.W)
    btn_dir = ttk.Button(fr, text="Selecionar pasta de destino...", command=choose_dir)
    btn_dir.pack(anchor=tk.W, pady=(0, 4))
    lbl_out = tk.Label(fr, textvariable=out_dir_var, fg="gray")
    lbl_out.pack(anchor=tk.W)

    ttk.Separator(fr, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=12)

    btn_convert = ttk.Button(fr, text="Converter CSV → TXT", command=run_convert)
    btn_convert.pack(pady=4)

    root.mainloop()


if __name__ == "__main__":
    main()
