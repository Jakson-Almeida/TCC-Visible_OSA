"""
Visualizador de espectros com detecção de picos.
Permite carregar um ou vários arquivos de espectro (formato wl;intensity),
visualizar um por vez e navegar entre eles com < e > (ou setas).
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from scipy.signal import find_peaks
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os


def ler_dados_arquivo(caminho_arquivo):
    """
    Lê arquivo de espectro (uma linha por ponto: wavelength;intensity).
    Retorna (wl_metros, intensidade) ou ([], []) em caso de erro.
    """
    frequencias = []
    ganhos = []
    try:
        with open(caminho_arquivo, "r", encoding="utf-8", errors="replace") as arquivo:
            for linha in arquivo:
                dados = linha.strip().split(";")
                if len(dados) >= 2:
                    try:
                        frequencias.append(float(dados[0]))
                        ganhos.append(float(dados[1]))
                    except ValueError:
                        continue
    except FileNotFoundError:
        return [], []
    except Exception:
        return [], []
    return frequencias, ganhos


def detectar_picos(intensidade, prominence=5, valley=False):
    """Retorna índices dos picos (ou vales) e (wl_nm, intensity) nesses pontos."""
    arr = np.asarray(intensidade)
    if valley:
        peaks, _ = find_peaks(-arr, prominence=prominence)
    else:
        peaks, _ = find_peaks(arr, prominence=prominence)
    return peaks


def plotar_espectro_com_picos(ax, wl_nm, spec, prominence=5, valley=False, dark=False, show_peaks=False):
    """
    Plota espectro em ax. Se show_peaks=True, detecta picos e desenha marcadores.
    Limpa marcadores antigos em ax (ax.markers e ax.marker).
    """
    ax.clear()
    color_fg = "white" if dark else "black"
    color_bg = "black" if dark else "white"
    ax.set_facecolor(color_bg)
    ax.set_xlabel("Comprimento de onda (nm)", color=color_fg)
    ax.set_ylabel("Intensidade (u.a.)", color=color_fg)
    ax.tick_params(colors=color_fg)
    ax.grid(True)

    ax.plot(wl_nm, spec, color="gray" if dark else "steelblue", lw=1.5, alpha=0.9)

    # Remover marcadores antigos
    if hasattr(ax, "markers"):
        for m in ax.markers:
            try:
                m.remove()
            except Exception:
                pass
        ax.markers = []
    else:
        ax.markers = []
    if hasattr(ax, "marker"):
        try:
            ax.marker.remove()
        except Exception:
            pass

    if show_peaks:
        peaks = detectar_picos(spec, prominence=prominence, valley=valley)
        for idx in peaks:
            wl_p = wl_nm[idx]
            int_p = spec[idx]
            marker = ax.scatter(
                wl_p,
                int_p,
                color=color_fg,
                marker=11 if valley else 10,
                zorder=5,
                s=60,
            )
            ax.markers.append(marker)

    ax.set_xlim(wl_nm.min(), wl_nm.max())
    ymin, ymax = np.nanmin(spec), np.nanmax(spec)
    margin = (ymax - ymin) * 0.05 if ymax > ymin else 1.0
    ax.set_ylim(max(0, ymin - margin), ymax + margin)


def main():
    root = tk.Tk()
    root.title("Visualizador de Espectros e Picos")
    root.geometry("900x550")
    root.minsize(700, 450)

    # Dados: lista de (caminho, wl_nm, spec)
    spectra_data = []
    current_index = 0
    prominence = 5.0
    show_peaks = False  # Por padrão picos desabilitados
    dark_theme = False
    last_clicked_wl = None  # último pico clicado (para copiar)
    last_clicked_int = None

    # Figura matplotlib embutida
    fig = Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_xlabel("Comprimento de onda (nm)")
    ax.set_ylabel("Intensidade (u.a.)")
    ax.grid(True)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # Barra de status / título do arquivo
    status_var = tk.StringVar(value="Nenhum arquivo carregado. Use 'Carregar arquivo(s)'.")
    lbl_status = tk.Label(root, textvariable=status_var, fg="gray", font=("Segoe UI", 10))
    lbl_status.pack(anchor=tk.W, padx=8, pady=(0, 4))

    def carregar_arquivos():
        nonlocal spectra_data, current_index
        paths = filedialog.askopenfilenames(
            title="Selecionar arquivo(s) de espectro",
            filetypes=[("Texto / CSV", "*.txt *.csv"), ("Todos", "*.*")],
        )
        if not paths:
            return
        spectra_data = []
        for path in paths:
            wl_m, spec = ler_dados_arquivo(path)
            if not wl_m or not spec:
                messagebox.showwarning(
                    "Aviso",
                    f"Não foi possível ler dados de:\n{os.path.basename(path)}",
                )
                continue
            wl_nm = np.array(wl_m) * 1e9
            spec = np.array(spec)
            spectra_data.append((path, wl_nm, spec))
        if not spectra_data:
            messagebox.showwarning("Aviso", "Nenhum espectro válido carregado.")
            return
        current_index = 0
        status_var.set(f"Carregados {len(spectra_data)} arquivo(s). Navegue com < e > ou setas.")
        atualizar_grafico()

    def atualizar_grafico():
        nonlocal last_clicked_wl, last_clicked_int
        if not spectra_data:
            ax.clear()
            ax.set_xlabel("Comprimento de onda (nm)")
            ax.set_ylabel("Intensidade (u.a.)")
            ax.text(0.5, 0.5, "Carregue arquivo(s) de espectro.", ha="center", va="center", transform=ax.transAxes)
            canvas.draw_idle()
            return
        idx = max(0, min(current_index, len(spectra_data) - 1))
        path, wl_nm, spec = spectra_data[idx]
        nome = os.path.basename(path)
        status_var.set(f"Arquivo {idx + 1} / {len(spectra_data)}: {nome}")
        plotar_espectro_com_picos(
            ax, wl_nm, spec,
            prominence=prominence,
            dark=dark_theme,
            show_peaks=show_peaks,
        )
        # Se exibir picos e houver exatamente um, já mostrar suas informações
        if show_peaks:
            peaks = detectar_picos(spec, prominence=prominence)
            if len(peaks) == 1:
                wl_p = float(wl_nm[peaks[0]])
                int_p = float(spec[peaks[0]])
                last_clicked_wl = wl_p
                last_clicked_int = int_p
                status_var.set(
                    f"Pico clicado: λ = {wl_p:.2f} nm  |  Intensidade = {int_p:.2f} u.a.  (use os botões para copiar)"
                )
        else:
            last_clicked_wl = None
            last_clicked_int = None
        canvas.draw_idle()

    def anterior():
        nonlocal current_index
        if not spectra_data:
            return
        current_index = (current_index - 1) % len(spectra_data)
        atualizar_grafico()

    def proximo():
        nonlocal current_index
        if not spectra_data:
            return
        current_index = (current_index + 1) % len(spectra_data)
        atualizar_grafico()

    def on_key(event):
        key = event.keysym
        if key in ("Left", "comma", "less"):
            anterior()
        elif key in ("Right", "period", "greater"):
            proximo()

    root.bind("<KeyPress>", on_key)
    canvas.get_tk_widget().bind("<KeyPress>", on_key)

    def on_click_grafico(event):
        nonlocal last_clicked_wl, last_clicked_int
        if event.inaxes != ax or not spectra_data or not show_peaks:
            return
        idx = max(0, min(current_index, len(spectra_data) - 1))
        _, wl_nm, spec = spectra_data[idx]
        peaks = detectar_picos(spec, prominence=prominence)
        if len(peaks) == 0:
            return
        x_click, y_click = event.xdata, event.ydata
        if x_click is None or y_click is None:
            return
        wl_picos = wl_nm[peaks]
        int_picos = spec[peaks]
        distancias = (wl_picos - x_click) ** 2 + (int_picos - y_click) ** 2
        i_min = int(np.argmin(distancias))
        wl_p = float(wl_picos[i_min])
        int_p = float(int_picos[i_min])
        last_clicked_wl = wl_p
        last_clicked_int = int_p
        status_var.set(
            f"Pico clicado: λ = {wl_p:.2f} nm  |  Intensidade = {int_p:.2f} u.a.  (use os botões para copiar)"
        )

    def copiar_lambda():
        if last_clicked_wl is None:
            status_var.set("Clique em um pico antes de copiar λ.")
            return
        texto = f"{last_clicked_wl:.6g}"
        root.clipboard_clear()
        root.clipboard_append(texto)
        root.update()
        status_var.set(f"λ = {texto} nm copiado para a área de transferência.")

    def copiar_intensidade():
        if last_clicked_int is None:
            status_var.set("Clique em um pico antes de copiar intensidade.")
            return
        texto = f"{last_clicked_int:.6g}"
        root.clipboard_clear()
        root.clipboard_append(texto)
        root.update()
        status_var.set(f"Intensidade = {texto} copiada para a área de transferência.")

    canvas.mpl_connect("button_press_event", on_click_grafico)

    # Botões e controles
    fr_btn = ttk.Frame(root, padding=4)
    fr_btn.pack(fill=tk.X, padx=8, pady=4)
    ttk.Button(fr_btn, text="Carregar arquivo(s)...", command=carregar_arquivos).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Button(fr_btn, text="< Anterior", command=anterior).pack(side=tk.LEFT, padx=2)
    ttk.Button(fr_btn, text="Próximo >", command=proximo).pack(side=tk.LEFT, padx=2)
    tk.Label(fr_btn, text="Navegação: < ou > (ou setas)", fg="gray").pack(side=tk.LEFT, padx=12)

    # Exibir picos (por padrão desligado)
    def toggle_peaks():
        nonlocal show_peaks
        show_peaks = var_show_peaks.get()
        atualizar_grafico()

    var_show_peaks = tk.BooleanVar(value=False)
    chk_peaks = ttk.Checkbutton(
        fr_btn,
        text="Exibir picos",
        variable=var_show_peaks,
        command=toggle_peaks,
    )
    chk_peaks.pack(side=tk.LEFT, padx=(16, 4))

    # Sensibilidade (prominência): valor maior = menos picos (filtra ruído)
    def on_prominence_change(val=None):
        nonlocal prominence
        if val is None:
            val = prominence_var.get()
        try:
            p = float(val)
            prominence = max(0.5, min(1000.0, p))
            prominence_var.set(prominence)
        except (ValueError, tk.TclError):
            prominence = 5.0
            prominence_var.set(5.0)
        if show_peaks:
            atualizar_grafico()

    tk.Label(fr_btn, text="Prominência (↑ menos picos):", fg="gray").pack(side=tk.LEFT, padx=(8, 2))
    prominence_var = tk.DoubleVar(value=5.0)
    spin_prominence = ttk.Spinbox(
        fr_btn,
        from_=0.5,
        to=200.0,
        increment=0.5,
        textvariable=prominence_var,
        width=6,
        command=on_prominence_change,
    )
    spin_prominence.pack(side=tk.LEFT, padx=2)
    spin_prominence.bind("<Return>", lambda e: on_prominence_change())
    spin_prominence.bind("<FocusOut>", lambda e: on_prominence_change())

    # Copiar λ ou intensidade do último pico clicado
    tk.Label(fr_btn, text="Copiar pico clicado:", fg="gray").pack(side=tk.LEFT, padx=(12, 2))
    ttk.Button(fr_btn, text="Copiar λ", command=copiar_lambda).pack(side=tk.LEFT, padx=2)
    ttk.Button(fr_btn, text="Copiar I", command=copiar_intensidade).pack(side=tk.LEFT, padx=2)

    # Inicial
    atualizar_grafico()
    root.mainloop()


if __name__ == "__main__":
    main()
