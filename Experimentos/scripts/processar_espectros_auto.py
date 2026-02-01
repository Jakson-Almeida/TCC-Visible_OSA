"""
Script para processamento automático de espectros com detecção de picos por ajuste lorentziano.
Gera JSON compatível com o app de entrada de dados.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import json
import numpy as np
from scipy.optimize import curve_fit
from datetime import datetime


# ========== DEFINIÇÕES DE INTERVALOS ==========

# Intervalos [nm] para cada combinação (espectro, fonte_cor, cor_procurada)
# espectro: 1=RGB, 2=R, 3=G, 4=B
# fonte_cor: "Azul", "Verde", "Vermelho"
# cor_procurada: "green", "red", "blue"

INTERVALOS_OSA = {
    # Espectro 1: Combinado RGB
    (1, "Verde", "green"): (504.3, 520.8),
    (1, "Verde", "blue"): (443.5, 461.7),
    (1, "Verde", "red"): (609.4, 625.5),
    (1, "Azul", "green"): (504.3, 520.8),
    (1, "Azul", "blue"): (443.5, 461.7),
    (1, "Azul", "red"): (609.4, 625.5),
    (1, "Vermelho", "green"): (504.3, 520.8),
    (1, "Vermelho", "blue"): (443.5, 461.7),
    (1, "Vermelho", "red"): (609.4, 625.5),
    
    # Espectro 2: Canal R
    (2, "Verde", "green"): (497.6, 516.8),
    (2, "Verde", "blue"): (441.4, 457.1),
    (2, "Verde", "red"): (609.4, 625.5),
    (2, "Azul", "green"): (497.6, 516.8),
    (2, "Azul", "blue"): (441.4, 457.1),
    (2, "Azul", "red"): (609.4, 625.5),
    (2, "Vermelho", "green"): (497.6, 516.8),
    (2, "Vermelho", "blue"): (441.4, 457.1),
    (2, "Vermelho", "red"): (609.4, 625.5),
    
    # Espectro 3: Canal G
    (3, "Verde", "green"): (504.9, 524.4),
    (3, "Verde", "blue"): (444.1, 461.3),
    (3, "Verde", "red"): (585.8, 628.0),
    (3, "Azul", "green"): (504.9, 524.4),
    (3, "Azul", "blue"): (444.1, 461.3),
    (3, "Azul", "red"): (585.8, 628.0),
    (3, "Vermelho", "green"): (504.9, 524.4),
    (3, "Vermelho", "blue"): (444.1, 461.3),
    (3, "Vermelho", "red"): (585.8, 628.0),
    
    # Espectro 4: Canal B
    (4, "Verde", "green"): (496.2, 516.4),
    (4, "Verde", "blue"): (444.1, 461.3),
    (4, "Verde", "red"): (611.9, 628.0),
    (4, "Azul", "green"): (496.2, 516.4),
    (4, "Azul", "blue"): (444.1, 461.3),
    (4, "Azul", "red"): (611.9, 628.0),
    (4, "Vermelho", "green"): (496.2, 516.4),
    (4, "Vermelho", "blue"): (444.1, 461.3),
    (4, "Vermelho", "red"): (611.9, 628.0),
}


# ========== FUNÇÕES DE LEITURA DE ESPECTROS ==========

def ler_espectro_osa_visivel(caminho):
    """Lê espectro OSA Visível (wl em metros)."""
    wl_m = []
    intensity = []
    try:
        with open(caminho, "r", encoding="utf-8", errors="replace") as f:
            for linha in f:
                partes = linha.strip().split(";")
                if len(partes) >= 2:
                    try:
                        wl_m.append(float(partes[0]))
                        intensity.append(float(partes[1]))
                    except ValueError:
                        continue
    except Exception:
        return None, None
    if not wl_m:
        return None, None
    wl_nm = np.array(wl_m) * 1e9  # Converte para nm
    return wl_nm, np.array(intensity)


def ler_espectro_thorlabs(caminho):
    """Lê espectro ThorLabs CSV (wl em nm)."""
    try:
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            linhas = f.readlines()
        inicio_dados = None
        for idx, linha in enumerate(linhas):
            if "[Data]" in linha:
                inicio_dados = idx + 1
                break
        if inicio_dados is None:
            return None, None
        wl_nm = []
        intensity = []
        for linha in linhas[inicio_dados:]:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                partes = linha.split(";")
                if len(partes) >= 2:
                    try:
                        wl_nm.append(float(partes[0]))
                        intensity.append(float(partes[1]))
                    except ValueError:
                        continue
        if not wl_nm:
            return None, None
        return np.array(wl_nm), np.array(intensity)
    except Exception:
        return None, None


# ========== AJUSTE DE CURVA ==========

def lorentzian(x, amp, center, gamma):
    """Função lorentziana."""
    return amp * gamma ** 2 / ((x - center) ** 2 + gamma ** 2)


def ajustar_pico_em_intervalo(wl_nm, spec, wl_min, wl_max):
    """
    Ajusta curva lorentziana em um intervalo específico e retorna (peak_nm, intensity).
    Retorna (None, None) em caso de falha.
    """
    mask = (wl_nm >= wl_min) & (wl_nm <= wl_max)
    if np.sum(mask) < 10:
        return None, None
    
    wl_fit = wl_nm[mask]
    spec_fit = spec[mask]
    
    try:
        amp_guess = np.max(spec_fit)
        center_guess = wl_fit[np.argmax(spec_fit)]
        gamma_guess = (wl_max - wl_min) / 10
        p0 = [amp_guess, center_guess, gamma_guess]
        
        popt, _ = curve_fit(lorentzian, wl_fit, spec_fit, p0=p0, maxfev=5000)
        amp, center, gamma = popt
        
        # Valida resultado
        if wl_min <= center <= wl_max and amp > 0:
            return float(center), float(amp)
        return None, None
    except Exception:
        return None, None


# ========== PROCESSAMENTO ==========

def processar_pasta_raiz(pasta_raiz, equipamento, log_callback):
    """
    Processa todas as pastas peqs_x e retorna os dados no formato do JSON.
    
    Args:
        pasta_raiz: Path da pasta raiz (contém peqs_1, peqs_2, etc.)
        equipamento: "osa_visivel" ou "thorlabs"
        log_callback: função para logar mensagens
    
    Returns:
        dict com a estrutura data[equipamento][tomada][espectro][duty][cor]
    """
    pasta_raiz = Path(pasta_raiz)
    pastas_peqs = sorted([p for p in pasta_raiz.glob("peqs_*") if p.is_dir()])
    
    if not pastas_peqs:
        log_callback("[ERRO] Nenhuma pasta peqs_* encontrada.")
        return None
    
    log_callback(f"[INFO] Encontradas {len(pastas_peqs)} pasta(s): {[p.name for p in pastas_peqs]}")
    
    # Estrutura de dados
    if equipamento == "osa_visivel":
        data_equipamento = {}
        for tomada_num in range(1, 6):
            data_equipamento[str(tomada_num)] = {}
            for espectro_num in range(1, 5):
                data_equipamento[str(tomada_num)][str(espectro_num)] = {}
                for duty in range(1, 11):
                    data_equipamento[str(tomada_num)][str(espectro_num)][str(duty)] = {
                        "green": {"peak_nm": "", "intensity": ""},
                        "red": {"peak_nm": "", "intensity": ""},
                        "blue": {"peak_nm": "", "intensity": ""},
                    }
    else:  # thorlabs
        data_equipamento = {}
        for tomada_num in range(1, 6):
            data_equipamento[str(tomada_num)] = {}
            for duty in range(1, 11):
                data_equipamento[str(tomada_num)][str(duty)] = {
                    "green": {"peak_nm": "", "intensity": ""},
                    "red": {"peak_nm": "", "intensity": ""},
                    "blue": {"peak_nm": "", "intensity": ""},
                }
    
    # Processa cada pasta peqs_x
    for pasta_peqs in pastas_peqs:
        # Extrai número da tomada (peqs_1 → 1)
        try:
            tomada_num = int(pasta_peqs.name.split("_")[1])
            if tomada_num < 1 or tomada_num > 5:
                continue
        except Exception:
            continue
        
        log_callback(f"\n[INFO] Processando {pasta_peqs.name}...")
        
        # Processa cada cor (Azul, Verde, Vermelho)
        for fonte_cor in ["Azul", "Verde", "Vermelho"]:
            pasta_cor = pasta_peqs / fonte_cor
            if not pasta_cor.exists():
                continue
            
            log_callback(f"  - Fonte {fonte_cor}...")
            
            # Mapeamento cor fonte → cor no JSON
            # Quando processamos fonte Azul, procuramos o pico blue no intervalo blue
            # Quando processamos fonte Verde, procuramos o pico green no intervalo green
            # Quando processamos fonte Vermelho, procuramos o pico red no intervalo red
            cor_mapa = {"Azul": "blue", "Verde": "green", "Vermelho": "red"}
            cor_procurada = cor_mapa[fonte_cor]
            
            # Processa cada tipo de arquivo
            padroes = [
                ("spectrum", 1),      # RGB
                ("spectrum_r_", 2),   # Canal R
                ("spectrum_g_", 3),   # Canal G
                ("spectrum_b_", 4),   # Canal B
            ]
            
            for padrao, espectro_num in padroes:
                for duty in range(1, 11):
                    # Nome do arquivo
                    nome_arquivo = f"{padrao}{duty:03d}.txt"
                    caminho_arquivo = pasta_cor / nome_arquivo
                    
                    if not caminho_arquivo.exists():
                        continue
                    
                    # Lê espectro
                    if equipamento == "osa_visivel":
                        wl_nm, spec = ler_espectro_osa_visivel(caminho_arquivo)
                    else:
                        wl_nm, spec = ler_espectro_thorlabs(caminho_arquivo)
                    
                    if wl_nm is None or spec is None:
                        continue
                    
                    # Obtém intervalo para buscar o pico
                    key = (espectro_num, fonte_cor, cor_procurada)
                    if key not in INTERVALOS_OSA:
                        continue
                    
                    wl_min, wl_max = INTERVALOS_OSA[key]
                    
                    # Ajusta pico
                    peak_nm, intensity = ajustar_pico_em_intervalo(wl_nm, spec, wl_min, wl_max)
                    
                    if peak_nm is not None:
                        # Salva resultado
                        if equipamento == "osa_visivel":
                            data_equipamento[str(tomada_num)][str(espectro_num)][str(duty)][cor_procurada] = {
                                "peak_nm": f"{peak_nm:.2f}",
                                "intensity": f"{intensity:.2f}",
                            }
                        else:
                            data_equipamento[str(tomada_num)][str(duty)][cor_procurada] = {
                                "peak_nm": f"{peak_nm:.2f}",
                                "intensity": f"{intensity:.2f}",
                            }
    
    log_callback("\n[OK] Processamento concluído!")
    return data_equipamento


# ========== INTERFACE TKINTER ==========

def criar_interface():
    root = tk.Tk()
    root.title("Processamento Automático de Espectros")
    root.geometry("700x550")
    root.resizable(True, True)
    
    pasta_raiz_var = tk.StringVar(value="")
    equipamento_var = tk.StringVar(value="osa_visivel")
    dados_processados = {"data": None}
    
    # Frame superior: seleções
    fr_top = ttk.Frame(root, padding=10)
    fr_top.pack(fill=tk.X)
    
    ttk.Label(fr_top, text="Equipamento:").grid(row=0, column=0, sticky="w", padx=(0, 5))
    combo_equip = ttk.Combobox(fr_top, textvariable=equipamento_var, state="readonly", width=20)
    combo_equip["values"] = ["osa_visivel", "thorlabs"]
    combo_equip.grid(row=0, column=1, sticky="w")
    
    ttk.Label(fr_top, text="Pasta raiz (contém peqs_1, peqs_2, ...):").grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 0))
    entry_pasta = ttk.Entry(fr_top, textvariable=pasta_raiz_var, width=50)
    entry_pasta.grid(row=2, column=0, columnspan=2, sticky="we")
    
    def selecionar_pasta():
        pasta = filedialog.askdirectory(title="Selecionar pasta raiz")
        if pasta:
            pasta_raiz_var.set(pasta)
    
    ttk.Button(fr_top, text="Selecionar pasta...", command=selecionar_pasta).grid(row=2, column=2, padx=(5, 0))
    
    fr_top.columnconfigure(0, weight=0)
    fr_top.columnconfigure(1, weight=1)
    
    # Frame central: log
    fr_log = ttk.Frame(root, padding=10)
    fr_log.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(fr_log, text="Log de processamento:").pack(anchor="w")
    log_text = scrolledtext.ScrolledText(fr_log, height=15, wrap=tk.WORD, state="disabled")
    log_text.pack(fill=tk.BOTH, expand=True)
    
    def log(msg):
        log_text.config(state="normal")
        log_text.insert(tk.END, msg + "\n")
        log_text.see(tk.END)
        log_text.config(state="disabled")
        root.update_idletasks()
    
    # Frame inferior: botões
    fr_bottom = ttk.Frame(root, padding=10)
    fr_bottom.pack(fill=tk.X)
    
    def processar():
        pasta = pasta_raiz_var.get().strip()
        if not pasta:
            messagebox.showwarning("Aviso", "Selecione a pasta raiz.")
            return
        if not Path(pasta).exists():
            messagebox.showerror("Erro", "Pasta não encontrada.")
            return
        
        log_text.config(state="normal")
        log_text.delete("1.0", tk.END)
        log_text.config(state="disabled")
        
        log("[INFO] Iniciando processamento...")
        equipamento = equipamento_var.get()
        
        data_equip = processar_pasta_raiz(pasta, equipamento, log)
        
        if data_equip is None:
            return
        
        # Cria estrutura completa do JSON
        json_data = {
            "version": 2,
            "updatedAt": datetime.now().isoformat(),
            "data": {
                "osa_visivel": {},
                "thorlabs": {},
            }
        }
        
        # Preenche com estrutura padrão vazia
        for t in range(1, 6):
            json_data["data"]["thorlabs"][str(t)] = {}
            for d in range(1, 11):
                json_data["data"]["thorlabs"][str(t)][str(d)] = {
                    "green": {"peak_nm": "", "intensity": ""},
                    "red": {"peak_nm": "", "intensity": ""},
                    "blue": {"peak_nm": "", "intensity": ""},
                }
            
            json_data["data"]["osa_visivel"][str(t)] = {}
            for e in range(1, 5):
                json_data["data"]["osa_visivel"][str(t)][str(e)] = {}
                for d in range(1, 11):
                    json_data["data"]["osa_visivel"][str(t)][str(e)][str(d)] = {
                        "green": {"peak_nm": "", "intensity": ""},
                        "red": {"peak_nm": "", "intensity": ""},
                        "blue": {"peak_nm": "", "intensity": ""},
                    }
        
        # Atualiza com dados processados
        json_data["data"][equipamento] = data_equip
        
        dados_processados["data"] = json_data
        btn_salvar.config(state="normal")
        log("[OK] Dados prontos para salvar!")
    
    def salvar_json():
        if dados_processados["data"] is None:
            messagebox.showwarning("Aviso", "Nenhum dado para salvar. Processe primeiro.")
            return
        
        arquivo = filedialog.asksaveasfilename(
            title="Salvar JSON",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
        )
        
        if arquivo:
            try:
                with open(arquivo, "w", encoding="utf-8") as f:
                    json.dump(dados_processados["data"], f, indent=2, ensure_ascii=False)
                log(f"[OK] JSON salvo em: {arquivo}")
                messagebox.showinfo("Sucesso", f"JSON salvo com sucesso!\n{arquivo}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar JSON:\n{str(e)}")
    
    btn_processar = ttk.Button(fr_bottom, text="Processar", command=processar)
    btn_processar.pack(side=tk.LEFT, padx=5)
    
    btn_salvar = ttk.Button(fr_bottom, text="Salvar JSON", command=salvar_json, state="disabled")
    btn_salvar.pack(side=tk.LEFT, padx=5)
    
    root.mainloop()


if __name__ == "__main__":
    criar_interface()
