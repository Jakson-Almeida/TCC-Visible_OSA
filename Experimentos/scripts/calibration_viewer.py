"""
Visualizador de Calibração Espectral OSA Visível.
Carrega 3 arquivos de canais RGB do OSA e aplica o modelo de calibração
para gerar o espectro equivalente ThorLabs.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os


def ler_espectro(caminho):
    """
    Lê arquivo de espectro no formato: comprimento_onda;intensidade
    Retorna (wavelength_nm, intensity) ou (None, None) se falhar.
    """
    try:
        data = np.loadtxt(caminho, delimiter=';')
        wavelength_m = data[:, 0]  # Metros
        intensity = data[:, 1]
        wavelength_nm = wavelength_m * 1e9  # Converter para nm
        return wavelength_nm, intensity
    except Exception as e:
        print(f"Erro ao ler {caminho}: {e}")
        return None, None


def carregar_modelo_geral():
    """
    Carrega o modelo GERAL (independente de duty e fonte).
    Retorna DataFrame com colunas: lambda_nm, beta_1, beta_2, beta_3, R2, RMSE
    ou None se o arquivo não existir.
    """
    arquivo = "modelo_geral_parametros.csv"
    if not os.path.exists(arquivo):
        return None
    return pd.read_csv(arquivo)


def carregar_modelo(fonte):
    """
    Carrega parâmetros do modelo por fonte (depende de duty cycle).
    Retorna DataFrame com colunas: lambda_nm, a_R, b_R, c_R, ..., alpha_1, alpha_2, alpha_3
    """
    arquivo_modelo = f"modelo_{fonte.lower()}_parametros.csv"
    
    if not os.path.exists(arquivo_modelo):
        raise FileNotFoundError(f"Arquivo de modelo não encontrado: {arquivo_modelo}")
    
    df = pd.read_csv(arquivo_modelo)
    return df


def aplicar_modelo_geral(wl_nm, Pr, Pg, Pb, df_modelo):
    """
    Aplica o modelo GERAL: P_ThorLabs(λ) = β₁·Pr(λ) + β₂·Pg(λ) + β₃·Pb(λ).
    Não depende de duty cycle nem de fonte de luz.
    """
    P_calibrado = np.zeros_like(wl_nm)
    for i, lambda_i in enumerate(wl_nm):
        idx = (df_modelo['lambda_nm'] - lambda_i).abs().idxmin()
        b1 = df_modelo.loc[idx, 'beta_1']
        b2 = df_modelo.loc[idx, 'beta_2']
        b3 = df_modelo.loc[idx, 'beta_3']
        P_calibrado[i] = b1 * Pr[i] + b2 * Pg[i] + b3 * Pb[i]
    return P_calibrado


def aplicar_modelo(wl_nm, Pr, Pg, Pb, duty_cycle, df_modelo):
    """
    Aplica o modelo de calibração para cada ponto do espectro.
    
    Args:
        wl_nm: Array de comprimentos de onda (nm)
        Pr, Pg, Pb: Arrays de intensidades dos canais R, G, B
        duty_cycle: Duty cycle em % (1-10)
        df_modelo: DataFrame com parâmetros do modelo
    
    Returns:
        Array com intensidades calibradas (equivalente ThorLabs)
    """
    P_calibrado = np.zeros_like(wl_nm)
    
    for i, lambda_i in enumerate(wl_nm):
        # Encontrar parâmetros mais próximos no modelo
        idx = (df_modelo['lambda_nm'] - lambda_i).abs().idxmin()
        
        # Extrair coeficientes dos polinômios
        a_R = df_modelo.loc[idx, 'a_R']
        b_R = df_modelo.loc[idx, 'b_R']
        c_R = df_modelo.loc[idx, 'c_R']
        
        a_G = df_modelo.loc[idx, 'a_G']
        b_G = df_modelo.loc[idx, 'b_G']
        c_G = df_modelo.loc[idx, 'c_G']
        
        a_B = df_modelo.loc[idx, 'a_B']
        b_B = df_modelo.loc[idx, 'b_B']
        c_B = df_modelo.loc[idx, 'c_B']
        
        # Extrair coeficientes alpha
        alpha_1 = df_modelo.loc[idx, 'alpha_1']
        alpha_2 = df_modelo.loc[idx, 'alpha_2']
        alpha_3 = df_modelo.loc[idx, 'alpha_3']
        
        # Avaliar polinômios de 2ª ordem
        d = duty_cycle
        y_R = a_R * d**2 + b_R * d + c_R
        y_G = a_G * d**2 + b_G * d + c_G
        y_B = a_B * d**2 + b_B * d + c_B
        
        # Combinação linear (calibração)
        P_calibrado[i] = alpha_1 * y_R + alpha_2 * y_G + alpha_3 * y_B
    
    return P_calibrado


def wavelength_to_rgb(wavelength, gamma=0.8):
    """Converte comprimento de onda (nm) para RGB."""
    wavelength = float(wavelength)
    
    if wavelength < 380:
        return (0.0, 0.0, 0.0)
    if wavelength < 420:
        t = (wavelength - 380) / (420 - 380)
        return (t ** gamma, 0.0, t ** gamma)
    if wavelength >= 720:
        return (0.0, 0.0, 0.0)
    if wavelength > 680:
        t = (720 - wavelength) / (720 - 680)
        return (t ** gamma, 0.0, 0.0)
    
    if 420 <= wavelength < 440:
        r = ((-(wavelength - 440) / (440 - 420))) ** gamma
        g = 0.0
        b = 1.0 ** gamma
    elif 440 <= wavelength < 490:
        r = 0.0
        g = ((wavelength - 440) / (490 - 440)) ** gamma
        b = 1.0 ** gamma
    elif 490 <= wavelength < 510:
        r = 0.0
        g = 1.0 ** gamma
        b = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif 510 <= wavelength < 580:
        r = ((wavelength - 510) / (580 - 510)) ** gamma
        g = 1.0 ** gamma
        b = 0.0
    elif 580 <= wavelength < 645:
        r = 1.0 ** gamma
        g = (-(wavelength - 645) / (645 - 580)) ** gamma
        b = 0.0
    else:
        r = 1.0 ** gamma
        g = 0.0
        b = 0.0
    
    return (max(0, r), max(0, g), max(0, b))


def main():
    root = tk.Tk()
    root.title("Visualizador de Calibração Espectral OSA → ThorLabs")
    root.geometry("1100x700")
    
    # Variáveis de estado
    arquivos = {'R': None, 'G': None, 'B': None}
    arquivo_referencia = None
    dados = {'R': (None, None), 'G': (None, None), 'B': (None, None)}
    df_modelo = None
    fonte_atual = tk.StringVar(value="Verde")
    duty_cycle = tk.DoubleVar(value=5.0)
    mostrar_referencia = tk.BooleanVar(value=True)
    
    # Frame superior para controles
    frame_controles = ttk.Frame(root, padding=10)
    frame_controles.pack(side=tk.TOP, fill=tk.X)
    
    # Seleção de arquivos
    ttk.Label(frame_controles, text="Arquivos de Espectro:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
    
    labels_arquivo = {}
    for i, canal in enumerate(['R', 'G', 'B']):
        def criar_callback(c):
            def callback():
                arquivo = filedialog.askopenfilename(
                    title=f"Selecionar espectro Canal {c}",
                    filetypes=[("Arquivos TXT", "*.txt"), ("Todos", "*.*")]
                )
                if arquivo:
                    arquivos[c] = arquivo
                    labels_arquivo[c].config(text=os.path.basename(arquivo))
            return callback
        
        cor_canal = {'R': '#ff6666', 'G': '#66ff66', 'B': '#6666ff'}[canal]
        ttk.Button(frame_controles, text=f"Canal {canal}", command=criar_callback(canal)).grid(row=1+i, column=0, sticky=tk.W, padx=5, pady=2)
        labels_arquivo[canal] = ttk.Label(frame_controles, text="(não selecionado)", foreground="gray")
        labels_arquivo[canal].grid(row=1+i, column=1, sticky=tk.W, padx=5, pady=2)
    
    # Espectro de referência (ThorLabs ou outro)
    ttk.Label(frame_controles, text="Referência:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
    
    def selecionar_referencia():
        nonlocal arquivo_referencia
        arquivo = filedialog.askopenfilename(
            title="Selecionar espectro de referência (ex.: ThorLabs)",
            filetypes=[("Arquivos TXT", "*.txt"), ("Todos", "*.*")]
        )
        if arquivo:
            arquivo_referencia = arquivo
            label_referencia.config(text=os.path.basename(arquivo))
    
    def limpar_referencia():
        nonlocal arquivo_referencia
        arquivo_referencia = None
        label_referencia.config(text="(não selecionado)")
    
    ttk.Button(frame_controles, text="Espectro referência", command=selecionar_referencia).grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
    label_referencia = ttk.Label(frame_controles, text="(não selecionado)", foreground="gray")
    label_referencia.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)
    ttk.Button(frame_controles, text="Limpar ref.", command=limpar_referencia).grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
    ttk.Checkbutton(frame_controles, text="Mostrar referência", variable=mostrar_referencia).grid(row=6, column=1, sticky=tk.W, padx=5, pady=2)
    
    # Seleção de fonte
    ttk.Label(frame_controles, text="Fonte LED:", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky=tk.W, padx=20, pady=5)
    for i, fonte in enumerate(['Verde', 'Vermelho', 'Azul']):
        ttk.Radiobutton(frame_controles, text=fonte, variable=fonte_atual, value=fonte).grid(row=1+i, column=2, sticky=tk.W, padx=20, pady=2)
    
    # Duty cycle
    ttk.Label(frame_controles, text="Duty Cycle (%):", font=("Arial", 10, "bold")).grid(row=0, column=3, sticky=tk.W, padx=20, pady=5)
    ttk.Scale(frame_controles, from_=1, to=10, variable=duty_cycle, orient=tk.HORIZONTAL, length=150).grid(row=1, column=3, sticky=tk.W, padx=20, pady=2)
    label_duty = ttk.Label(frame_controles, text=f"{duty_cycle.get():.1f}%")
    label_duty.grid(row=2, column=3, sticky=tk.W, padx=20)
    
    def atualizar_label_duty(*args):
        label_duty.config(text=f"{duty_cycle.get():.1f}%")
    
    duty_cycle.trace('w', atualizar_label_duty)
    
    # Botão de processar
    btn_processar = ttk.Button(frame_controles, text="▶ Processar e Visualizar", command=lambda: processar())
    btn_processar.grid(row=1, column=4, rowspan=3, padx=20, pady=5, sticky=tk.NS)
    
    # Frame para gráficos
    frame_graficos = ttk.Frame(root)
    frame_graficos.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Criar figura matplotlib
    fig = Figure(figsize=(10, 6), dpi=100)
    
    # Subplot 1: Canais RGB originais
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.set_xlabel("Comprimento de onda (nm)")
    ax1.set_ylabel("Intensidade OSA (u.a.)")
    ax1.set_title("Canais RGB do OSA Visível")
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: Espectro calibrado
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.set_xlabel("Comprimento de onda (nm)")
    ax2.set_ylabel("Intensidade Calibrada (u.a.)")
    ax2.set_title("Espectro Calibrado (Equivalente ThorLabs)")
    ax2.grid(True, alpha=0.3)
    
    fig.tight_layout()
    
    # Canvas
    canvas = FigureCanvasTkAgg(fig, master=frame_graficos)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Status bar
    status_var = tk.StringVar(value="Pronto. Selecione os 3 arquivos de canais RGB.")
    status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def processar():
        """Processa os arquivos e aplica o modelo de calibração."""
        nonlocal df_modelo, dados
        
        # Verificar se todos os arquivos foram selecionados
        if None in arquivos.values():
            messagebox.showerror("Erro", "Selecione os 3 arquivos de canais RGB!")
            return
        
        # Ler espectros
        status_var.set("Lendo espectros...")
        root.update()
        
        for canal in ['R', 'G', 'B']:
            wl, intensity = ler_espectro(arquivos[canal])
            if wl is None:
                messagebox.showerror("Erro", f"Falha ao ler arquivo do canal {canal}")
                return
            dados[canal] = (wl, intensity)
        
        # Verificar se as grades de comprimento de onda são compatíveis
        wl_R, _ = dados['R']
        wl_G, _ = dados['G']
        wl_B, _ = dados['B']
        
        if not (np.allclose(wl_R, wl_G, atol=1e-6) and np.allclose(wl_R, wl_B, atol=1e-6)):
            messagebox.showerror("Erro", "Os arquivos têm grades de comprimento de onda incompatíveis!")
            return
        
        # Usar grade comum
        wl_nm = wl_R
        _, Pr = dados['R']
        _, Pg = dados['G']
        _, Pb = dados['B']
        
        # Prioridade: modelo GERAL (independente de duty e fonte)
        df_geral = carregar_modelo_geral()
        usar_modelo_geral = df_geral is not None
        
        if usar_modelo_geral:
            status_var.set("Carregando modelo geral (espectros quaisquer)...")
            root.update()
            P_calibrado = aplicar_modelo_geral(wl_nm, Pr, Pg, Pb, df_geral)
            duty = None  # não usado no modelo geral
        else:
            status_var.set(f"Carregando modelo para fonte {fonte_atual.get()}...")
            root.update()
            try:
                df_modelo = carregar_modelo(fonte_atual.get())
            except FileNotFoundError as e:
                messagebox.showerror("Erro", str(e))
                status_var.set("Erro: arquivo de modelo não encontrado.")
                return
            status_var.set("Aplicando modelo de calibração...")
            root.update()
            duty = duty_cycle.get()
            P_calibrado = aplicar_modelo(wl_nm, Pr, Pg, Pb, duty, df_modelo)
        
        # Carregar espectro de referência (se houver)
        P_referencia = None
        if arquivo_referencia and mostrar_referencia.get():
            status_var.set("Carregando espectro de referência...")
            root.update()
            wl_ref, I_ref = ler_espectro(arquivo_referencia)
            if wl_ref is not None:
                # Interpolar referência na grade do OSA para comparação
                P_referencia = np.interp(wl_nm, wl_ref, I_ref)
        
        # Plotar resultados
        status_var.set("Gerando gráficos...")
        root.update()
        
        ax1.clear()
        ax2.clear()
        
        # Plot 1: Canais RGB originais
        ax1.plot(wl_nm, Pr, 'r-', label='Canal R', linewidth=1.5, alpha=0.8)
        ax1.plot(wl_nm, Pg, 'g-', label='Canal G', linewidth=1.5, alpha=0.8)
        ax1.plot(wl_nm, Pb, 'b-', label='Canal B', linewidth=1.5, alpha=0.8)
        ax1.set_xlabel("Comprimento de onda (nm)")
        ax1.set_ylabel("Intensidade OSA (u.a.)")
        titulo1 = "Canais RGB do OSA Visível" + (f" - Duty {duty:.1f}%" if duty is not None else " (modelo geral)")
        ax1.set_title(titulo1)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(wl_nm.min(), wl_nm.max())
        
        # Plot 2: Espectro calibrado (e referência se houver)
        for j in range(len(wl_nm) - 1):
            wl_mid = (wl_nm[j] + wl_nm[j + 1]) / 2
            color = wavelength_to_rgb(wl_mid)
            ax2.fill_between([wl_nm[j], wl_nm[j + 1]], 
                            [0, 0], 
                            [P_calibrado[j], P_calibrado[j + 1]], 
                            color=color, alpha=0.6, linewidth=0)
        
        ax2.plot(wl_nm, P_calibrado, 'k-', linewidth=2, alpha=0.7, label='Calibrado (OSA→ThorLabs)')
        
        if P_referencia is not None:
            ax2.plot(wl_nm, P_referencia, '--', color='orangered', linewidth=2, alpha=0.9, label='Referência (ThorLabs)')
        
        ax2.set_xlabel("Comprimento de onda (nm)")
        ax2.set_ylabel("Intensidade (u.a.)")
        titulo2 = "Calibrado vs Referência"
        if usar_modelo_geral:
            titulo2 += " (modelo geral: espectros quaisquer)"
        else:
            titulo2 += f" - Fonte {fonte_atual.get()} - Duty {duty:.1f}%"
        ax2.set_title(titulo2)
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(wl_nm.min(), wl_nm.max())
        ax2.set_ylim(bottom=0)
        
        fig.tight_layout()
        canvas.draw()
        
        # Estatísticas
        max_calib = P_calibrado.max()
        idx_max = P_calibrado.argmax()
        lambda_max = wl_nm[idx_max]
        
        msg_status = f"✓ Processado!"
        if usar_modelo_geral:
            msg_status += " [Modelo geral]"
        msg_status += f" Pico calibrado: λ={lambda_max:.2f} nm, I={max_calib:.2f}"
        if P_referencia is not None:
            # Métricas de comparação na faixa comum
            valid = np.isfinite(P_referencia) & np.isfinite(P_calibrado) & (P_referencia > 0)
            if np.any(valid):
                rmse = np.sqrt(np.mean((P_calibrado[valid] - P_referencia[valid])**2))
                erro_rel_medio = 100 * np.mean(np.abs(P_calibrado[valid] - P_referencia[valid]) / np.maximum(P_referencia[valid], 1e-10))
                max_ref = P_referencia.max()
                msg_status += f"  |  Referência: I_max={max_ref:.2f}  |  RMSE={rmse:.2f}  Erro médio={erro_rel_medio:.1f}%"
        status_var.set(msg_status)
    
    root.mainloop()


if __name__ == "__main__":
    main()
