import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Label, Toplevel
import numpy as np
import json
import scipy.signal
from scipy.signal import find_peaks
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import cv2
from PIL import Image, ImageTk
import os
import copy
import time
from datetime import datetime
import re
import webbrowser
from matplotlib.collections import PolyCollection
# import threading

# Variáveis globais para cache
poly_collection = None
gradient_cache = None
SHOW_GRADIENT = True

# Para acesso global
glob_spec = None

# Pré-calcula as cores do gradiente uma vez (fora do loop)
def precompute_gradient(wl):
    colors = []
    for j in range(len(wl)-1):
        avg_wl = (wl[j] + wl[j+1]) / 2
        colors.append(wavelength_to_rgb(avg_wl))
    return colors

count_save_spectra = 0 # Variável global para contar o número de espectros salvos
global_frame = None    # Para se obter a qualquer momento o frame atual, caso disponível
log_element = None
buffer_msg = ""

def printf(msg="", prt=True):
    global log_element, buffer_msg
    msg = msg + buffer_msg
    if prt:
        print(msg)
    if log_element is not None:
        log_element.update(msg)
        buffer_msg = ""
    else:
        buffer_msg += msg + "\n"

def listar_webcams():
    index = 0
    webcams_disponiveis = []
    
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:  # Tenta capturar uma imagem
            break  # Sai do loop se não houver mais câmeras disponíveis
        else:
            webcams_disponiveis.append(index)
        cap.release()
        index += 1
    
    return webcams_disponiveis

# Função para carregar configurações do JSON
def carregar_configuracoes():
    with open("./interface_start.json", "r") as f:
        config = json.load(f)
    return config

# Função para salvar configurações no JSON
def salvar_configuracoes(config):
    with open("./interface_start.json", "w") as f:
        json.dump(config, f, indent=4)

# Inicialização padrão
def default_calibration(config):
    config["x_detection_start"]  = config["default"]["x_detection_start"]
    config["x_detection_end"]    = config["default"]["x_detection_end"]
    config["coeficientes"]       = config["default"]["coeficientes"]
    config["centro"]             = config["default"]["centro"]
    config["wl_fit"]             = config["default"]["wl_fit"]
    config["time_rate"]          = config["default"]["time_rate"]
    config["count_save_spectra"] = config["default"]["count_save_spectra"]
    config["WEBCAM_ON"]          = config["default"]["WEBCAM_ON"]
    config["file_dir"]           = config["default"]["file_dir"]
    config["WEBCAM_NUMBER"]      = config["default"]["WEBCAM_NUMBER"]
    config["wl_peaks"]           = config["default"]["wl_peaks"]
    config["wl_fit"]             = config["default"]["wl_fit"]
    salvar_configuracoes(config)

def start_config(config):
    global x_detection, coeficientes, coeficientes, centro, wl_fit, wl, buffer_size, buffer, count_save_spectra, WEBCAM_ON, WEBCAM_NUMBER, FRAME_WIDTH, FRAME_HEIGHT, SAVE_SPECTRA, SAVE_ONLY_ONE_SPECTRA, file_dir, start_save_time, last_save_time, COUNT_OR_TIME, DARK, SHOW_FRAME_GRAPH
    if config["WEBCAM_ON"]:
        x_detection = np.arange(config["x_detection_start"], config["x_detection_end"])
    else:
        k_ESCALAR = 3
        x_detection = np.arange(int(k_ESCALAR*config["default"]["x_detection_start"]), int(k_ESCALAR*config["default"]["x_detection_end"]))
    coeficientes = np.array(config["coeficientes"])
    centro = tuple(config["centro"])
    wl_fit = config["wl_fit"]
    wl = wl_fit[0] * x_detection + wl_fit[1]
    buffer_size = config["buffer_size"]
    buffer = np.zeros((buffer_size, len(wl)))
    count_save_spectra = config["count_save_spectra"]
    WEBCAM_ON     = config["WEBCAM_ON"]
    WEBCAM_NUMBER = config["WEBCAM_NUMBER"]
    FRAME_WIDTH   = config["FRAME_WIDTH"]
    FRAME_HEIGHT  = config["FRAME_HEIGHT"]
    SAVE_SPECTRA  = config["SAVE_SPECTRA"]
    SAVE_ONLY_ONE_SPECTRA = False
    file_dir = config["file_dir"]
    start_save_time = time.time()
    last_save_time = time.time()
    COUNT_OR_TIME = True
    SHOW_FRAME_GRAPH = False

def wavelength_to_rgb(wavelength, gamma=0.8):
    """Converte comprimento de onda para RGB com degradê suave para UV e IR"""
    wavelength = float(wavelength)
    
    # Fatores de atenuação para as bordas do espectro
    uv_attenuation = 1.0
    ir_attenuation = 1.0
    
    # Transição suave UV (380-420nm)
    if 380 <= wavelength < 420:
        return (0, 0, 0) if DARK else (1.0, 1.0, 1.0)
        # uv_attenuation = 0.2 + 0.8 * (wavelength - 380) / (420 - 380)
    elif wavelength < 380:
        return (0, 0, 0) if DARK else (1.0, 1.0, 1.0)
    
    # Transição suave IR (680-720nm)
    if 680 <= wavelength < 720:
        return (0, 0, 0) if DARK else (1.0, 1.0, 1.0)
        # ir_attenuation = 1.0 - (wavelength - 680) / (720 - 680)
    elif wavelength >= 720:
        return (0, 0, 0) if DARK else (1.0, 1.0, 1.0)
    
    # Cores do espectro visível com atenuação
    if 420 <= wavelength < 440:
        r = ((-(wavelength - 440) / (440 - 420)) * uv_attenuation) ** gamma
        g = 0.0
        b = (1.0 * uv_attenuation) ** gamma
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
    elif 645 <= wavelength < 680:
        r = 1.0 ** gamma
        g = 0.0
        b = 0.0
    elif 680 <= wavelength < 720:
        r = (1.0 * ir_attenuation) ** gamma
        g = 0.0
        b = 0.0
    else:
        r = g = b = 0.0
    
    return (max(0, r), max(0, g), max(0, b))

SPLASH_TIME = [False]

def splash_windows():
    splash = tk.Tk()
    splash.title("OSA Visível")
    splash.overrideredirect(True)
    splash.geometry("400x300")
    
    # Centralizar a janela
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width - 400) // 2
    y = (screen_height - 300) // 2
    splash.geometry(f"400x300+{x}+{y}")
    
    splash.attributes("-transparentcolor", "gray")
    splash.configure(bg="gray")

    # Logo (substitua pelo seu caminho)
    logo = tk.PhotoImage(file="data/app.png")
    tk.Label(splash, image=logo, bg="gray").pack(pady=20)

    progress = ttk.Progressbar(splash, orient=tk.HORIZONTAL, length=300, mode="determinate")
    progress.pack(pady=20)

    def update_progress():
        def simulate_initial():
            global SPLASH_TIME
            current = progress["value"]
            if current < 100:
                progress["value"] = current + 1
                splash.after(18, simulate_initial)
            else:
                # Atualiza a interface após conclusão
                splash.after(0, lambda: progress.config(value=100))
                splash.after(0, splash.destroy)
                SPLASH_TIME[-1] = True

        simulate_initial()

    # Inicia o progresso após 100ms
    splash.after(100, update_progress)
    splash.mainloop()

# # Flag para controlar a execução da thread
# stop_event = threading.Event()
# thr_splash = threading.Thread(target=splash_windows, daemon=True)
# thr_splash.start()
splash_windows()

# Carregar configurações iniciais
config = carregar_configuracoes()

# Variáveis globais e parâmetros padrão a partir do JSON
if config["WEBCAM_ON"]:
    x_detection = np.arange(config["x_detection_start"], config["x_detection_end"])
else:
    k_ESCALAR = 3
    x_detection = np.arange(int(k_ESCALAR*config["default"]["x_detection_start"]), int(k_ESCALAR*config["default"]["x_detection_end"]))
line = None
coeficientes = np.array(config["coeficientes"])
centro = tuple(config["centro"])
wl_fit = config["wl_fit"]
wl = wl_fit[0] * x_detection + wl_fit[1]
buffer_size = config["buffer_size"]
buffer = np.zeros((buffer_size, len(wl)))
i = 0
count_save_spectra = config["count_save_spectra"]
WEBCAM_ON     = config["WEBCAM_ON"]
WEBCAM_NUMBER = config["WEBCAM_NUMBER"]
FRAME_WIDTH   = config["FRAME_WIDTH"]
FRAME_HEIGHT  = config["FRAME_HEIGHT"]
SAVE_SPECTRA  = config["SAVE_SPECTRA"]
SAVE_ONLY_ONE_SPECTRA = False
file_dir = config["file_dir"]
COUNT_OR_TIME = True
DARK = False
start_save_time = time.time()
last_save_time = time.time()

# Variável para alternar entre webcam e imagem estática
IMAGE_FRAME = False  # Troque para False para usar a webcam

# Caminho da imagem estática
image_path = "data/img.png"

# Exibe as webcams disponíveis
webcams_found = listar_webcams()
printf(f"Webcams disponíveis: {webcams_found}")
if len(webcams_found) == 0:
    webcams_found.append("Vídeo")
    WEBCAM_ON = False
    printf("Nenhuma webcam encontrada, exibindo data/video.mp4")

max_cam = 0
try:
    max_cam = max(max(webcams_found), 0)
except:
    max_cam = len(webcams_found) - 1
if WEBCAM_NUMBER > max_cam:
    WEBCAM_NUMBER = config["WEBCAM_NUMBER"] = max_cam

# Texto con informações sobre a fonte de dados (webcam, vídeo ou imagem)
fonte_de_dados = "Fonte de dados: "
label_fonte_de_dados = None

def atualiza_fonte_de_dados():
    global fonte_de_dados, label_fonte_de_dados, WEBCAM_ON, IMAGE_FRAME
    fonte_de_dados = "Fonte de dados: "
    if WEBCAM_ON:
        fonte_de_dados += f"webcam [{config["WEBCAM_NUMBER"]}]."
    else:
        fonte_de_dados += f"imagem." if IMAGE_FRAME else f"vídeo."
    if label_fonte_de_dados is not None:
        label_fonte_de_dados.config(text=fonte_de_dados)

def save_spectra_txt(x, y):
    global count_save_spectra, file_dir, config, COUNT_OR_TIME, last_save_time

    if (time.time() - last_save_time)*1000 < config["time_to_save_spectra"]:
        return

    now = datetime.now()
    
    # Gerar o nome do arquivo com base no contador
    filename = file_dir + (f"{config['spectrum_file_name']}{count_save_spectra:03}.txt" if COUNT_OR_TIME else (now.strftime("spectrum-%Y-%m-%d-%H-%M-%S-%f")[:-3] + ".txt"))
    
    # Incrementar o contador para o próximo arquivo
    if COUNT_OR_TIME:
        count_save_spectra += 1
    
    # Abrir o arquivo no modo de escrita
    with open(filename, 'w') as file:
        # Iterar sobre os valores de x e y e escrever no formato especificado
        n = 14
        for xi, yi in zip(x, y):
            xi = xi*1e-9
            file.write(f"{xi:.{n}e};{yi:.{n}e}\n")
    
    printf(f"Espectro salvo como '{filename}'.")
    last_save_time = time.time()

# Função para ler os dados do arquivo e retornar duas listas: frequência e ganho
def ler_dados_arquivo(caminho_arquivo):
    frequencias = []
    ganhos = []
    
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            for linha in arquivo:
                # Separar a linha pelos pontos e vírgulas
                dados = linha.strip().split(';')
                if len(dados) == 2:
                    # Converter os valores para float e adicionar às listas
                    frequencias.append(float(dados[0]))
                    ganhos.append(float(dados[1]))
    except FileNotFoundError:
        messagebox.showerror("Erro", f"O arquivo {caminho_arquivo} não foi encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao ler o arquivo: {e}")
    
    return frequencias, ganhos

# Função para plotar os dados
def plotar_espectro(frequencias, ganhos):
    plt.figure(figsize=(10, 6))
    
    # Converter frequências para a mesma escala de wl_res
    frequencias_nm = np.array(frequencias) * 1e9  # Supondo que wl_res está em nanômetros (nm)
    
    plt.plot(frequencias_nm, ganhos, label='Espectro')
    plt.xlabel('Frequência (nm)')
    plt.ylabel('Ganho')
    plt.title('Espectro de Frequência')
    plt.legend()
    plt.grid(True)
    plt.show()

# Funções auxiliares
def ajustar_reta_maior_intensidade(frame, limiar):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresholded_frame = cv2.threshold(gray_frame, limiar, 255, cv2.THRESH_BINARY)
    indices = np.where(thresholded_frame > 0)
    x, y = indices[1], indices[0]
    coeficientes = np.polyfit(x, y, 1)
    return coeficientes, (float(np.mean(x)), float(np.mean(y)))

def rotacionar_e_cortar_imagem(imagem, coeficientes, ponto_central, largura_saida, altura_saida):
    angulo_graus = np.degrees(np.arctan(coeficientes[0]))
    linhas, colunas = imagem.shape[:2]
    matriz_rotacao = cv2.getRotationMatrix2D(ponto_central, angulo_graus, 1)
    imagem_rotacionada = cv2.warpAffine(imagem, matriz_rotacao, (colunas, linhas))
    x1, y1 = int(ponto_central[0] - largura_saida / 2), int(ponto_central[1] - altura_saida / 2)
    x2, y2 = int(ponto_central[0] + largura_saida / 2), int(ponto_central[1] + altura_saida / 2)
    return imagem_rotacionada[y1:y2, x1:x2]

def obter_espectro(frame, coeficientes, x_detect=None):
    global x_detection
    if x_detect is None:
        x_detect = x_detection
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    intensidades = [gray_frame[int(np.round(coeficientes[0] * x + coeficientes[1])), x] for x in x_detect]
    return x_detect, scipy.signal.savgol_filter(intensidades, 7, 2)

def obter_espectro2(frame, coeficientes):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    intensidades = [gray_frame[int(np.round(coeficientes[0] * x + coeficientes[1])), x] for x in x_detection]
    return x_detection, scipy.signal.savgol_filter(intensidades, 7, 2)

def obter_espectro_calibracao(gray_frame, coeficientes):
    intensidades = [gray_frame[int(np.round(coeficientes[0] * x + coeficientes[1])), x] for x in x_detection]
    return x_detection, scipy.signal.savgol_filter(intensidades, 7, 2)

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def setCenter(value):
    global centro
    center_width = 300
    center_height = 40
    value[0] = constrain(value[0], center_width/2, FRAME_WIDTH-center_width/2)
    value[1] = constrain(value[1], center_height/2, FRAME_HEIGHT-center_height/2)
    centro = (value[0], value[1])

class WebcamViewer:
    def __init__(self, window=None, webcam=None, time_rate=100, deve_calibrar=False, limiar=40, show_RGB=None):
        global config
        self.time_rate = time_rate
        self.cap = webcam
        self.window = window
        self.deve_calibrar = deve_calibrar
        self.limiar = limiar
        self.frame = None
        self.show_RGB = show_RGB
        self.SHOW_LINE = False
        self.SHOW_CALIBRATION_AREA = False
        self.laser_button = None
        self.WL_CALIBRATION = False
        self.wl_count = 0
        self.max_wl_count = config["max_wl_count"]
        self.aux_list = []
        self.laser_selected = "verde"
        self.text_status = ""
        self.start_time = time.time()
        self.wl_calibration_time = time.time()
        self.pico_vermelho = None
        self.pico_verde = None
        self.calibration_polygon_points = [(0, 0), (0, 20), (x_detection[-1]-x_detection[0], 20), (x_detection[-1]-x_detection[0], 0), (x_detection[-1]-x_detection[0], -20), (0, -20)]
        
    def start(self):
        window = self.window
        window.iconbitmap('app.ico')
        window.resizable(False, False)
        
        # Configura o label para exibir os frames
        self.video_label = Label(window)
        self.video_label.pack()

        if self.deve_calibrar:
            # Botão para para iniciar calibração
            ttk.Button(window, text="Calibrar Luz Branca", command=self.make_calibration).pack(pady=10, side=tk.LEFT)
            
            # Botão para para restaurar calibração
            ttk.Button(window, text="Restaurar calibração", command=self.calibration_default).pack(pady=10, side=tk.LEFT)

            # Função para alterar o texto do botão 2
            def alterar_texto():
                match self.laser_button.cget("text"):
                    case "Calibrar Laser":
                        if self.laser_selected == "verde" and self.wl_count == 0:
                            self.laser_button.config(text="Iniciar Laser Verde")
                            self.text_status = "[PASSO 1]: Ative o laser verde. Em seguida clique em: Iniciar Laser Verde."
                        if self.laser_selected == "vermelho" and self.wl_count == 0:
                            self.laser_button.config(text="Calibrando Laser Vermelho...")
                            self.WL_CALIBRATION = True
                    case "Iniciar Laser Verde":
                        self.laser_button.config(text="Calibrando Laser Verde...")
                        self.wl_count = len(self.aux_list)
                        self.text_status = f"[PASSO 2]: Frame {self.wl_count} de {self.max_wl_count}"
                        self.WL_CALIBRATION = True
                    case "Iniciar Laser Vermelho":
                        self.laser_button.config(text="Calibrando Laser Vermelho...")
                        self.wl_count = len(self.aux_list)
                        self.text_status = f"[PASSO 3]: Frame {self.wl_count} de {self.max_wl_count}"
                        self.WL_CALIBRATION = True

            # Botão para calibrar o laser
            self.laser_button = ttk.Button(window, text="Calibrar Laser", command=alterar_texto)
            self.laser_button.pack(pady=10, side=tk.LEFT)

            # Botão para fechar a janela
            self.close_button = ttk.Button(window, text="Fechar", command=self.close)
            self.close_button.pack(pady=10, side=tk.RIGHT)
        
        else:
            # Botão para fechar a janela
            self.close_button = ttk.Button(window, text="Fechar", command=self.close)
            self.close_button.pack(pady=10)
        
        def key_pressed(event):
            self.key_event_action(event)
        
        window.bind("<Key>", key_pressed)
        
        # Atualizar os frames periodicamente
        self.update_frame()

    def key_event_action(self, event):
        key = event.keysym
        # printf(f"Tecla pressionada: {key}")
        match key:
            case 's':
                self.frame_mask_show()
            case 'w':
                self.find_wl()
            case 'l':
                self.SHOW_LINE = not self.SHOW_LINE
            case 'a':
                self.SHOW_CALIBRATION_AREA = not self.SHOW_CALIBRATION_AREA
            case '3':
                self.plot_image_as_3d_surface()

    def show_line(self, frame):
        if not self.SHOW_LINE:
            return
        # Configurações da linha
        start_point = (x_detection[0], int(x_detection[0]*coeficientes[0]+coeficientes[1]))  # Ponto inicial (x, y)
        end_point = (x_detection[-1], int(x_detection[-1]*coeficientes[0]+coeficientes[1]))  # Ponto final (x, y)
        color = (255, 255, 255)                                                              # Cor da linha (verde em BGR)
        thickness = 2                                                                        # Espessura da linha

        # Desenhar a linha no frame
        cv2.line(frame, start_point, end_point, color, thickness)

    def show_calibration_area(self, frame, polygon_points, angle=None, translation_point=None, color=(200, 200, 200)):
        """
        Desenha um polígono rotacionado e transladado em um frame.

        :param frame: Imagem/frame onde o polígono será desenhado
        :param polygon_points: Lista de tuplas (x, y) representando os vértices do polígono
        :param angle: Ângulo de rotação em graus (em relação ao ponto (0, 0))
        :param translation_point: Tupla (x, y) indicando o ponto para onde o polígono será transladado
        """
        if not self.SHOW_CALIBRATION_AREA:
            return
        if angle is None or translation_point:
            angle = np.degrees(np.arctan(coeficientes[0]))
            translation_point = (x_detection[0], int(x_detection[0]*coeficientes[0]+coeficientes[1]))
        # Converter os pontos do polígono para um array NumPy
        points = np.array(polygon_points, dtype=np.float32)

        # Converter o ângulo de graus para radianos
        angle_radians = np.radians(angle)

        # Criar a matriz de rotação 2D
        rotation_matrix = np.array([
            [np.cos(angle_radians), -np.sin(angle_radians)],
            [np.sin(angle_radians), np.cos(angle_radians)]
        ])

        # Aplicar a rotação aos pontos do polígono
        rotated_points = np.dot(points, rotation_matrix.T)

        # Aplicar a translação
        translated_points = rotated_points + np.array(translation_point, dtype=np.float32)

        # Converter os pontos para inteiros e formato compatível com OpenCV
        int_points = translated_points.astype(np.int32)

        # Desenhar o polígono no frame
        cv2.polylines(frame, [int_points], isClosed=True, color=color, thickness=3)

    
    def show_calibration_area_animated(self, frame):
        if not self.SHOW_CALIBRATION_AREA:
            return
        global config
        angle = np.arctan(config["coeficientes"][0])
        start_point = (x_detection[0], int(x_detection[0]*coeficientes[0]+coeficientes[1]))  # Ponto inicial (x, y)
        end_point = (x_detection[-1], int(x_detection[-1]*coeficientes[0]+coeficientes[1]))  # Ponto final (x, y)
        color = (100, 255, 40)                                                               # Cor da linha (verde em BGR)
        thickness = 5                                                                        # Espessura da linha

        # Desenhar a linha no frame
        cv2.line(frame, start_point, end_point, color, thickness)
    
    def plot_image_as_3d_surface(self):
        global global_frame

        frame = copy.deepcopy(global_frame)
        if frame is None:
            print("Erro: O frame global está vazio.")
            return

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img_array = np.array(gray_frame)
        
        # Criar os eixos x, y
        x = np.arange(img_array.shape[1])
        y = np.arange(img_array.shape[0])
        x, y = np.meshgrid(x, y)
        
        # Intensidade dos pixels como z
        z = img_array
        
        # Plotar o relevo
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(x, y, z, cmap='gray', edgecolor='none')
        
        # Configurações de visualização
        ax.set_title("Relevo 3D da Imagem")
        ax.set_xlabel("Largura (X)")
        ax.set_ylabel("Comprimento (Y)")
        ax.set_zlabel("Intensidade (Z)")
        
        plt.show()

    def update_frame(self):
        global global_frame
        self.frame = copy.deepcopy(global_frame)

        try:
            # Converte o frame para o formato RGB
            frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.find_wl(frame=frame)
        except Exception as e:
            printf("[ERROR] Erro ao converter frame de BGR para RGB")
            print(e)
            self.window.after(self.time_rate, self.update_frame)
            return
        
        if self.deve_calibrar:
            self.show_line(frame=frame)
            self.show_calibration_area(frame=frame, polygon_points=self.calibration_polygon_points)
            frame = self.resized_image(frame=frame, max_size=(800.0, 600.0), RESIZED=True)
            # OpenCV text
            WHITE_COLOR = True
            font      = cv2.FONT_HERSHEY_COMPLEX
            fontScale = 0.5
            fontColor     = ( 30,  30,  30)
            fontColorDark = (210, 210, 210)
            thickness = 1
            lineType  = 1
            bottomLeftCornerOfText = (int(20), int(30))
            fontColorSelected = fontColorDark if WHITE_COLOR else fontColor
            cv2.putText(frame, self.text_status, 
                bottomLeftCornerOfText, 
                font, 
                fontScale,
                fontColorSelected,
                thickness,
                lineType)
        
        # Converte o frame para uma imagem compatível com tkinter
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Atualiza o label com o novo frame
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
        
        # self.show_frame_with_resize(frame=frame, max_size=(800.0, 600.0))
    
        # Chama essa função novamente após 20 ms
        self.window.after(self.time_rate, self.update_frame)
    
    def resized_image(self, frame, max_size = (500.0, 500.0), RESIZED=False):
        # Obtém as dimensões da imagem original
        height, width, _ = frame.shape

        # Verifica se a imagem é maior do que o permitido
        if height > max_size[1] or width > max_size[0] or RESIZED:
            # Calcula a nova proporção mantendo as dimensões da imagem
            scaling_factor = min(max_size[0] / width, max_size[1] / height)
            new_width = int(width * scaling_factor)
            new_height = int(height * scaling_factor)

            # Redimensiona a imagem para caber dentro do limite
            resized_frame = cv2.resize(frame, (new_width, new_height))
        else:
            resized_frame = frame
        return resized_frame
    
    def show_frame_with_resize(self, frame, max_size=(800, 600)):
        """
        Converte um frame OpenCV para imagem PIL, redimensiona com preservação de proporções e exibe no Tkinter.

        :param frame: Frame do OpenCV (np.ndarray).
        :param max_size: Dimensões máximas para o redimensionamento (largura, altura).
        """
        # Obtém as dimensões do frame
        height, width, _ = frame.shape

        # Calcula o fator de escala preservando a proporção
        scaling_factor = min(max_size[0] / width, max_size[1] / height)
        new_width = int(width * scaling_factor)
        new_height = int(height * scaling_factor)

        # Converte o frame para formato compatível com PIL
        img = Image.fromarray(frame)  # Converte de BGR para RGB

        # Redimensiona a imagem
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)

        # Converte a imagem para formato compatível com Tkinter
        imgtk = ImageTk.PhotoImage(image=img_resized)

        # Atualiza o label com o novo frame
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

    def close(self):
        # Fecha a janela
        self.window.destroy()
    
    def frame_mask_show(self):
        if self.frame is None:
            printf("[ERROR] Can not show frame mask: frame is None")
            return
        frame = self.frame

        r, g, b = cv2.split(frame)

        # Criar máscaras binárias para segmentar as cores
        # Ajuste o valor do threshold conforme necessário
        threshold = 128

        # Máscara para o Azul
        mask_b = cv2.threshold(b, threshold, 255, cv2.THRESH_BINARY)[1]
        segmented_b = cv2.bitwise_and(frame, frame, mask=mask_b)

        # Máscara para o Verde
        mask_g = cv2.threshold(g, threshold, 255, cv2.THRESH_BINARY)[1]
        segmented_g = cv2.bitwise_and(frame, frame, mask=mask_g)

        # Máscara para o Vermelho
        mask_r = cv2.threshold(r, threshold, 255, cv2.THRESH_BINARY)[1]
        segmented_r = cv2.bitwise_and(frame, frame, mask=mask_r)

        cv2.imshow("Segmentado Vermelho",     segmented_b)
        cv2.imshow("Segmentado Verde",    segmented_g)
        cv2.imshow("Segmentado Azul", segmented_r)
    
    def make_calibration(self, frame=None):
        if frame is None:
            if self.frame is None:
                printf("[ERROR] Can not make calibration: frame is None")
                return
            frame = self.frame
        global config
        printf("[CALIBRAÇÃO] Iniciando calibração")

        try:
            config["coeficientes"], config["centro"] = ajustar_reta_maior_intensidade(frame, self.limiar)

            # Converte coeficientes para uma lista serializável
            config["coeficientes"] = config["coeficientes"].tolist()
            printf(f'"[CALIBRAÇÃO] coeficientes"{config["coeficientes"]} "centro" {config["centro"]}')
        except:
            printf("[WARNING] Erro ao ajustar a reta com maior intensidade")
            return
        try:
            salvar_configuracoes(config)
        except Exception as e:
            printf("[ERROR]: ao calibrar não foi possível salvar as configurações")
            printf("Informações sobre o erro")
            print(e)
            return
        try:
            start_config(config)
        except:
            printf("[ERROR]: ao calibrar não foi possível reiniciar as configurações")
            return
        printf("[CALIBRAÇÃO] Calibração com luz branca realizada e salva com sucesso!\n")
    
    def find_wl(self, frame=None, RGB=False):
        global config
        if time.time() - self.wl_calibration_time < config["time_calibration_frame"]/1000.0:
            return
        self.wl_calibration_time = time.time()
        if not self.WL_CALIBRATION:
            return
        if frame is None:
            if self.frame is None:
                printf("[ERROR] Can not find wl: frame is None")
                return
            frame = self.frame
        if self.show_RGB is None or RGB:
            self.show_RGB = RGB

        passo = 2 if self.laser_selected=="verde" else 3
        self.text_status = f"[PASSO {passo}]: Frame {self.wl_count+1} de {self.max_wl_count}"
        printf(f"{self.text_status}")

        # Para encontrar wl
        height, width, _ = frame.shape
        k_ESCALAR = width/float(config["default"]["FRAME_WIDTH"])
        config["x_detection_start"] = int(k_ESCALAR*config["default"]["x_detection_start"])
        config["x_detection_end"]   = int(k_ESCALAR*config["default"]["x_detection_end"])
        x_detect = np.arange(config["x_detection_start"], config["x_detection_end"])
        pix, spec = obter_espectro(frame, config["coeficientes"], x_detect=x_detect)
        self.aux_list.append(spec)

        def spec_medio():
            spec_total = None
            for aux in self.aux_list:
                if spec_total is None:
                    spec_total = aux
                else:
                    spec_total += aux
            spec_total/=self.max_wl_count
            return spec_total

        self.wl_count = self.wl_count + 1
        if self.wl_count >= self.max_wl_count:
            if self.laser_selected == "verde":
                spec_led_verde = spec_medio()
                plotar_espectro(pix, spec_led_verde)
                # print(spec_led_verde)
                success = True
                try:
                    peaks, info = find_peaks(spec_led_verde, prominence=5)
                    print(peaks)
                    self.pico_verde = pix[peaks[0]]
                    printf(f"Pico verde: {self.pico_verde}")
                except:
                    success = False
                    printf("[ERROR] Nenhum pico encontrado para o laser verde. Refaça a calibração.")
                if success:
                    wl_fit = []
                    config["wl_fit"] = list(wl_fit)
                    printf("[PASSO 3]: Agora ative o laser vermelho clicando em Iniciar Laser Vermelho")
                    self.WL_CALIBRATION = False
                    self.wl_count = 0
                    self.aux_list = []
                    self.laser_selected = "vermelho"
                    self.text_status = "[PASSO 3]: Agora ative o laser vermelho clicando em Iniciar Laser Vermelho"
                    self.laser_button.config(text="Iniciar Laser Vermelho")
                    self.WL_CALIBRATION = False
                else:
                    printf("[PASSO 3]: Pico não encontrado, refaça a calibração.")
                    self.WL_CALIBRATION = False
                    self.wl_count = 0
                    self.aux_list = []
                    self.laser_selected = "verde"
                    self.text_status = "[PASSO 3]: Pico nao encontrado, refaca a calibracao."
                    self.laser_button.config(text="Calibrar Laser")
                    self.WL_CALIBRATION = False
            elif self.laser_selected == "vermelho":
                spec_led_vermelho = spec_medio()
                plotar_espectro(pix, spec_led_vermelho)
                success = True
                try:
                    peaks, info = find_peaks(spec_led_vermelho, prominence=5)
                    printf(f"{peaks}")
                    self.pico_vermelho = pix[peaks[0]]
                    printf(f"Pico vermelho: {self.pico_vermelho}")
                    if self.pico_vermelho == self.pico_verde:
                        success = False
                except:
                    success = False
                    printf("[ERROR] Nenhum pico encontrado para o led vermelho. Refaça a calibração.")
                if success:
                    wl_fit = [(config["wl_peaks"][0]-config["wl_peaks"][1])/(self.pico_vermelho-self.pico_verde), config["wl_peaks"][0]-(config["wl_peaks"][0]-config["wl_peaks"][1])*self.pico_vermelho/(self.pico_vermelho-self.pico_verde)]
                    config["wl_fit"] = list(wl_fit)
                    salvar_configuracoes(config)
                    # start_config(config)
                    printf(f"wl_fit encontrado: {wl_fit}")
                    printf("[PASSO 4]: Calibracao terminada e salva com sucesso! Agora reinicie o programa.")
                    self.text_status = "[PASSO 4]: Calibracao terminada e salva com sucesso!"
                    if not config["WEBCAM_ON"]:
                        reiniciar()
                    # # Reiniciar todo o programa
                    # python = sys.executable              # Obtém o caminho do interpretador Python em execução
                    # os.execl(python, python, *sys.argv)  # Substitui o processo atual por um novo com os mesmos argumentos
                else:
                    self.text_status = "[PASSO 4]: Nenhum pico encontrado, refaca a caliibracao."
                self.WL_CALIBRATION = False
                self.wl_count = 0
                self.aux_list = []
                self.laser_selected = "verde"
                self.laser_button.config(text="Calibrar Laser")
                self.WL_CALIBRATION = False

        # cv2.imshow("Imagem completa", frame)

    def calibration_default(self):
        global config
        default_calibration(config)
        printf("Configurações padrão aplicadas")
        start_config(config)

class LogWidget:
    def __init__(self, parent, size=(50, 10), buffer=100, theme="white", element=None, start_pose=(0,0), add_str=""):
        """
        Inicializa o LogWidget.

        :param parent: Janela onde o log será exibido.
        :param size: Tupla (largura, altura) do widget de log.
        :param buffer: Número máximo de mensagens armazenadas.
        :param theme: Tema do log ("white" ou "black").
        :param element: Elemento de referência para posicionamento relativo.
        :param pose: Posição inicial.
        :param add_str: Adição inicial de texto antes da mensagem.
        """
        self.parent = parent
        self.size = size
        self.buffer = buffer
        self.logs = []  # Lista para armazenar as mensagens de log
        self.element = element
        self.start_pose = start_pose
        self.add_str = add_str

        # Configurações de tema
        bg_color = "white" if theme == "white" else "black"
        fg_color = "black" if theme == "white" else "white"

        # Criação do widget Text com Scrollbar
        self.frame = tk.Frame(self.parent)
        self.text = tk.Text(
            self.frame, width=size[0], height=size[1], bg=bg_color, fg=fg_color, state="disabled", wrap="word"
        )
        self.scrollbar = tk.Scrollbar(self.frame, command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)

        # Posiciona o Text e a Scrollbar
        self.text.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Posição padrão inicial
        self.frame.place(x=start_pose[0], y=start_pose[1])

        # Se o elemento for fornecido, vincula eventos de atualização de posição
        if self.element is not None:
            self._bind_to_element()

    def update(self, msg=""):
        """
        Adiciona uma mensagem ao log.

        :param msg: String com a mensagem a ser adicionada.
        """
        # Atualiza a lista de logs com limite de buffer
        if len(self.logs) >= self.buffer:
            self.logs.pop(0)
        msg = self.add_str + msg
        self.logs.append(msg)

        # Atualiza o widget de log
        self.text.config(state="normal")

        # Redefine o conteúdo do Text para refletir apenas os logs no buffer
        self.text.delete("1.0", "end")
        self.text.insert("1.0", "\n".join(self.logs) + "\n")

        self.text.config(state="disabled")
        self.text.see("end")  # Rola automaticamente para o final

    def set_pose(self, pose):
        """
        Define a posição do log na janela ou em relação a um elemento.

        :param pose: Tupla (x, y) com a posição.
        """
        def update_position():
            if self.element is None:
                self.frame.place(x=pose[0], y=pose[1])
            else:
                # Obtém a posição do elemento e adiciona o deslocamento relativo
                x, y = self.element.winfo_x(), self.element.winfo_y()
                self.frame.place(x=x + pose[0], y=y + pose[1] + self.element.winfo_height())

        # Verifica se a posição do elemento está pronta
        if self.element and (self.element.winfo_x() == 0 and self.element.winfo_y() == 0):
            # Adiciona um atraso para esperar as coordenadas do elemento
            self.parent.after(1, lambda: self.set_pose(pose))
        else:
            update_position()
    
    def resize(self, size):
        """
        Redimensiona o widget para o novo tamanho especificado.
        
        :param size: Tupla (largura, altura) com as novas dimensões do widget.
        """
        if len(size) != 2:
            printf("[ERROR]: param size: Tupla (largura, altura) com as novas dimensões do widget.")
            return
        if size[1] == None:
            self.text.config(width=size[0])
            return
        if size[0] == None:
            self.text.config(height=size[1])
            return
        new_width, new_height = size
        self.text.config(width=new_width, height=new_height)  # Ajusta diretamente o widget Text

    def _bind_to_element(self):
        """
        Vincula o log à posição do elemento de referência.
        """
        def update_position(event=None):
            x, y = self.element.winfo_x(), self.element.winfo_y()
            self.frame.place(x=x + self.start_pose[0], y=y + self.start_pose[1] + self.element.winfo_height())
            k = 1.0
            self.resize((None, int(self.size[1]*root.winfo_height()/400)))

        # Adiciona um atraso para garantir que as coordenadas do elemento estejam disponíveis
        self.parent.after(1, update_position)

        # Vincula eventos de movimento e redimensionamento do elemento
        self.element.bind("<Configure>", update_position)

count_error = 0

def update():
    global i, buffer, wl, wl_fit, buffer_size, line, fig, ax, canvas, config, x_detection, centro, count_error, webcam, FRAME_WIDTH, FRAME_HEIGHT, SAVE_SPECTRA, SAVE_ONLY_ONE_SPECTRA, WEBCAM_NUMBER, webcams_found, global_frame, WEBCAM_ON, IMAGE_FRAME, start_save_time

    if IMAGE_FRAME and not WEBCAM_ON:
        frame = cv2.imread(image_path)
        validacao = True
    else:
        validacao, frame = webcam.read()

    if validacao:
        global_frame = frame
        height, width, _ = frame.shape
        if FRAME_WIDTH != int(width) or FRAME_HEIGHT != int(height):
            # if width > FRAME_WIDTH:
            #     k_ESCALAR = width/float(config["default"]["FRAME_WIDTH"])
            #     x_detection = np.arange(int(k_ESCALAR*config["default"]["x_detection_start"]), int(k_ESCALAR*config["default"]["x_detection_end"]))
            if width < FRAME_WIDTH and config["x_detection_end"] != config["default"]["x_detection_end"]:
                atualiza_fonte_de_dados()
                default_calibration(config)
                salvar_configuracoes(config)
                printf("[WARNING] Atualizando o programa com as configurações padrão.")
                # print("[WARNING] Reiniciando o programa com as configurações padrão.")
                # python = sys.executable              # Obtém o caminho do interpretador Python em execução
                # os.execl(python, python, *sys.argv)  # Substitui o processo atual por um novo com os mesmos argumentos
                # start_config(config)
                reiniciar()
        rotated_frame = frame
        try:
            rotated_frame = rotacionar_e_cortar_imagem(frame, coeficientes, centro, 300, 40)
            
            # Verifique se rotated_frame não é None
            if rotated_frame is not None and rotated_frame.shape[0] == 40 and rotated_frame.shape[1] == 300:
                imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(rotated_frame, cv2.COLOR_BGR2RGB)))
                webcam_label.imgtk = imgtk
                webcam_label.configure(image=imgtk)
            else:
                # print("{}\t A imagem está vazia ou não pôde ser processada.".format(count_error))
                printf("[WARNING] Não é possível exibir espectro. Faça a calibração. O programa será reiniciado com as configurações padrão.")
                default_calibration(config)
                start_config(config)
                reiniciar()
                # # Reiniciar todo o programa
                # python = sys.executable              # Obtém o caminho do interpretador Python em execução
                # os.execl(python, python, *sys.argv)  # Substitui o processo atual por um novo com os mesmos argumentos
                count_error += 1
        except cv2.error as e:
            print("Erro ao processar a imagem:", e)
        
        try:
            _, intensidade = obter_espectro(frame, coeficientes)
        except Exception as e:
            printf("[ERROR]: Faça a calibração")
            print(e)
            _, intensidade = x_detection, np.zeros_like(x_detection)
            # Reiniciar todo o programa
            default_calibration(config)
            reiniciar()
            # python = sys.executable              # Obtém o caminho do interpretador Python em execução
            # os.execl(python, python, *sys.argv)  # Substitui o processo atual por um novo com os mesmos argumentos
        buffer[i, :] = intensidade
        i = (i + 1) % buffer_size

        if i > 0:  # Só calcula a média se i for maior que zero
            global glob_spec
            spec = glob_spec = np.mean(buffer[:i, :], axis=0) if i < buffer_size else np.mean(buffer, axis=0)
            # Modifique a seção de plotagem:
            if SHOW_GRADIENT:
                try:
                    global poly_collection, gradient_cache
                    
                    # Pré-calcula o gradiente apenas uma vez
                    if gradient_cache is None:
                        gradient_cache = precompute_gradient(wl)
                    
                    # Cria vértices para PolyCollection
                    verts = []
                    for j in range(len(wl)-1):
                        verts.append([(wl[j], 0), (wl[j], spec[j]), (wl[j+1], spec[j+1]), (wl[j+1], 0)])
                    
                    # Atualiza a coleção ao invés de recriar
                    if poly_collection is None:
                        poly_collection = PolyCollection(verts, facecolors=gradient_cache, edgecolors='none')
                        ax.add_collection(poly_collection)
                    else:
                        poly_collection.set_verts(verts)
                    
                    # Mantém a linha principal
                    if line is None:
                        line, = ax.plot(wl, spec, color='white', lw=1.5, alpha=0.8) if DARK else ax.plot(wl, spec, color='gray', lw=1.5, alpha=0.8)
                    else:
                        line.set_ydata(spec)
                        
                except Exception as e:
                    print(f"Erro na renderização: {e}")

            if line is None:
                line, = ax.plot(wl, spec, color='black', lw=1.5, alpha=0.8) if SHOW_GRADIENT else ax.plot(wl, spec, color='b')
            else:
                line.set_ydata(spec)
            
            if SAVE_SPECTRA and config["total_time_save_spectra"] != 0.0:
                SAVE_SPECTRA = time.time() - start_save_time < config["total_time_save_spectra"]
                
            if SAVE_SPECTRA or SAVE_ONLY_ONE_SPECTRA:
                save_spectra_txt(wl, spec)
                config["count_save_spectra"] = count_save_spectra
                salvar_configuracoes(config)
            SAVE_ONLY_ONE_SPECTRA = False
            canvas.draw()
    elif not WEBCAM_ON:
        webcam.set(cv2.CAP_PROP_POS_FRAMES, 0)
    else:
        webcams_found = listar_webcams()
        printf(f"Webcams disponíveis: {webcams_found}")
        if len(webcams_found) == 0:
            webcams_found.append("Vídeo")
            WEBCAM_ON = False
        try:
            max_cam = max(max(webcams_found), 0)
        except:
            max_cam = len(webcams_found) - 1
        if WEBCAM_NUMBER > max_cam:
            WEBCAM_NUMBER = config["WEBCAM_NUMBER"] = max_cam
        webcam = cv2.VideoCapture(WEBCAM_NUMBER) if WEBCAM_ON else cv2.VideoCapture("data/video.mp4")
        atualiza_fonte_de_dados()
    
    root.after(20, update)

#///////////////////////////////////////////////////////////////////////////////////////////////////////

def abrir_janela_edicao():
    global config
    janela_edicao = tk.Toplevel(root)
    janela_edicao.title("Editar Inicialização")
    janela_edicao.iconbitmap('app.ico')
    janela_edicao.resizable(False, False)

    # Usando ttk para uma aparência melhor
    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 10))
    style.configure('TLabel',  font=('Helvetica', 10))
    style.configure('TEntry',  font=('Helvetica', 10))

    # Para Luz Branca
    label_luz = ttk.Label(janela_edicao, text="Calibração com Luz Branca:", font=("Arial", 12), padding=(0,10))
    label_luz.grid(row=0, column=0, columnspan=2, sticky=tk.W)

    # Entradas manuais para coeficientes
    tk.Label(janela_edicao, text="Coeficiente 1:").grid(row=1, column=0, sticky="w")
    entrada_coef1 = tk.Entry(janela_edicao)
    entrada_coef1.insert(0, str(coeficientes[0]))
    entrada_coef1.grid(row=1, column=1)

    tk.Label(janela_edicao, text="Coeficiente 2:").grid(row=2, column=0, sticky="w")
    entrada_coef2 = tk.Entry(janela_edicao)
    entrada_coef2.insert(0, str(coeficientes[1]))
    entrada_coef2.grid(row=2, column=1)

    # Entradas e sliders para ajustar o centro
    def atualizar_centro(event):
        global centro
        setCenter([slider_centro_x.get(), slider_centro_y.get()])

    tk.Label(janela_edicao, text="Centro X:").grid(row=3, column=0, sticky="w")
    entrada_centro_x = tk.Entry(janela_edicao)
    entrada_centro_x.insert(0, str(centro[0]))
    entrada_centro_x.grid(row=3, column=1)

    tk.Label(janela_edicao, text="Centro Y:").grid(row=4, column=0, sticky="w")
    entrada_centro_y = tk.Entry(janela_edicao)
    entrada_centro_y.insert(0, str(centro[1]))
    entrada_centro_y.grid(row=4, column=1)

    def on_enter_time(event):
        global config
        config["time_rate"] = entrada_time_rate.get()
        printf(f"Time Rate: {config["time_rate"]}")

    # Entradas manuais para coeficientes
    tk.Label(janela_edicao, text="Time Rate:").grid(row=5, column=0, sticky="w")
    entrada_time_rate = tk.Entry(janela_edicao)
    entrada_time_rate.insert(0, str(config["time_rate"]))
    entrada_time_rate.grid(row=5, column=1)
    entrada_time_rate.bind('<Return>', on_enter_time)

    tk.Label(janela_edicao, text="Centro X:").grid(row=6, column=0, sticky="w")
    tk.Label(janela_edicao, text="Centro Y:").grid(row=7, column=0, sticky="w")

    slider_centro_x = tk.Scale(janela_edicao, from_=0, to=FRAME_WIDTH, orient='horizontal')
    slider_centro_x.set(centro[0])  # Define o valor inicial sem acionar o comando
    slider_centro_x.config(command=atualizar_centro)  # Vincula o comando depois
    slider_centro_x.grid(row=6, column=1, columnspan=2, sticky="ew")

    slider_centro_y = tk.Scale(janela_edicao, from_=0, to=FRAME_HEIGHT, orient='horizontal')
    slider_centro_y.set(centro[1])  # Define o valor inicial sem acionar o comando
    slider_centro_y.config(command=atualizar_centro)  # Vincula o comando depois
    slider_centro_y.grid(row=7, column=1, columnspan=2, sticky="ew")

    # Para os Lasers
    label_luz = ttk.Label(janela_edicao, text="Calibração com Lasers:", font=("Arial", 12), padding=(0,10))
    label_luz.grid(row=8, column=0, columnspan=2, sticky=tk.W)

    # Entradas manuais para coeficientes
    tk.Label(janela_edicao, text="wl_fit coef1:").grid(row=9, column=0, sticky="w")
    entrada_coef3 = tk.Entry(janela_edicao)
    entrada_coef3.insert(0, str(config["wl_fit"][0]))
    entrada_coef3.grid(row=9, column=1)

    tk.Label(janela_edicao, text="wl_fit coef2:").grid(row=10, column=0, sticky="w")
    entrada_coef4 = tk.Entry(janela_edicao)
    entrada_coef4.insert(0, str(config["wl_fit"][1]))
    entrada_coef4.grid(row=10, column=1)

    tk.Label(janela_edicao, text="Pico Vermelho:").grid(row=11, column=0, sticky="w")
    entrada_coef5 = tk.Entry(janela_edicao)
    entrada_coef5.insert(0, str(config["wl_peaks"][0]))
    entrada_coef5.grid(row=11, column=1)

    tk.Label(janela_edicao, text="Pico Verde:").grid(row=12, column=0, sticky="w")
    entrada_coef6 = tk.Entry(janela_edicao)
    entrada_coef6.insert(0, str(config["wl_peaks"][1]))
    entrada_coef6.grid(row=12, column=1)

    def aplicar():
        global coeficientes
        coeficientes = np.array([float(entrada_coef1.get()), float(entrada_coef2.get())])
        wl_fit = np.array([float(entrada_coef3.get()), float(entrada_coef4.get())])
        wl_peaks = np.array([float(entrada_coef5.get()), float(entrada_coef6.get())])
        config["time_rate"] = int(entrada_time_rate.get())
        config["coeficientes"] = coeficientes.tolist()
        config["wl_fit"] = wl_fit.tolist()
        config["wl_peaks"] = wl_peaks.tolist()
        config["centro"] = list(centro)
        salvar_configuracoes(config)
        start_config(config)
        printf("Configurações salvas e aplicadas")
        janela_edicao.destroy()
        abrir_janela_edicao()

    ttk.Button(janela_edicao, text="Aplicar configurações", command=aplicar).grid(row=18, columnspan=2)

    def fazer_calibracao():
        global global_frame
        WebcamViewer().make_calibration(global_frame)

    ttk.Button(janela_edicao, text="Calibrar com luz branca", command=fazer_calibracao).grid(row=19, columnspan=2)

    def calibracao_padrao():
        global config
        default_calibration(config)
        printf("Configurações padrão aplicadas. Reinicie para carregar as devidas configurações.")
        start_config(config)
        janela_edicao.destroy()
        abrir_janela_edicao()

    ttk.Button(janela_edicao, text="Configurações padrão", command=calibracao_padrao).grid(row=20, columnspan=2)

#///////////////////////////////////////////////////////////////////////////////////////////////////////

def abrir_janela_webcam():
    janela_configuracoes = tk.Toplevel(root)
    janela_configuracoes.title("Editar Configurações")
    janela_configuracoes.iconbitmap('app.ico')
    janela_configuracoes.geometry(f"{200}x{120}+{30}+{50}")
    janela_configuracoes.resizable(False, False)

    # Defina o BooleanVar fora da função e associe-o ao Checkbutton
    webcam_on_var = tk.BooleanVar(value=WEBCAM_ON)

    # Seletor de Webcam
    def alternar_webcam():
        global WEBCAM_ON, webcam, centro
        WEBCAM_ON = not WEBCAM_ON
        config["WEBCAM_ON"] = WEBCAM_ON
        webcam.release()
        webcam = cv2.VideoCapture(WEBCAM_NUMBER) if WEBCAM_ON else cv2.VideoCapture("data/video.mp4")
        centro = config["centro"]
        atualiza_fonte_de_dados()
        salvar_configuracoes(config)
        webcam_on_var.set(WEBCAM_ON)
        janela_configuracoes.update()
        janela_configuracoes.destroy()
        abrir_janela_webcam()

    webcam_seletor = tk.Checkbutton(janela_configuracoes, text="Ativar Webcam", variable=webcam_on_var, command=alternar_webcam)
    webcam_seletor.pack(anchor=tk.W, padx=(10, 0))

    if WEBCAM_ON:
        try:
            max_cam = max(max(webcams_found), 0)
        except:
            max_cam = len(webcams_found) - 1
        if config["WEBCAM_NUMBER"] > max_cam:
            config["WEBCAM_NUMBER"] = max_cam
            salvar_configuracoes(config)

        # Valor padrão: primeiro elemento da lista, ou 0 caso a lista esteja vazia
        selected_webcam_index = tk.StringVar(value=config["WEBCAM_NUMBER"] if webcams_found else webcams_found[-1])

        def selecionar_webcam(nada):
            global WEBCAM_ON, webcam, centro, config, IMAGE_FRAME
            try:
                if selected_webcam_index.get() == webcams_found[-1]:
                    WEBCAM_ON = False
                    webcam.release()
                    webcam = cv2.VideoCapture("data/video.mp4")
                    IMAGE_FRAME = False
                    printf("Exibição de vídeo".format(selected_webcam_index))
                elif WEBCAM_ON:
                    WEBCAM_NUMBER = config["WEBCAM_NUMBER"] = int(selected_webcam_index.get())
                    webcam.release()
                    webcam = cv2.VideoCapture(WEBCAM_NUMBER)
                    centro = config["centro"]
                    printf("A webcam {} foi selecionada".format(selected_webcam_index.get()))
                    salvar_configuracoes(config)
                else:
                    WEBCAM_ON = True
                atualiza_fonte_de_dados()
                janela_configuracoes.destroy()
                abrir_janela_webcam()
            except Exception as inst:
                printf("[WARNING] function selecionar_webcam() is not able.")
                print("ERROR: ", inst)

        # Label de título
        label_select_webcam = tk.Label(janela_configuracoes, text="Escolha a webcam:")
        label_select_webcam.pack(anchor=tk.W, padx=(10, 0))

        # Criação do OptionMenu para seleção de valores
        option_menu = tk.OptionMenu(janela_configuracoes, selected_webcam_index, *webcams_found, command=selecionar_webcam)
        option_menu.pack(side=tk.LEFT, padx=(10, 0))

        # Para abrir o Webcam Viewer
        seletor_webcam_viewer = tk.Button(janela_configuracoes, justify="left", text="Visualizar", command=open_webcam_window)
        seletor_webcam_viewer.pack(side=tk.LEFT)
    else:
        midea = ["Vídeo ", "Imagem"]
        
        # Valor padrão: primeiro elemento da lista, ou 0 caso a lista esteja vazia
        selected_midea = tk.StringVar(value=midea[0] if not IMAGE_FRAME else midea[1])

        # Seletor de Webcam
        def exibir_video_ou_imagem(nada):
            global IMAGE_FRAME, config
            IMAGE_FRAME = (selected_midea.get() == midea[1])
            atualiza_fonte_de_dados()

        # Label de título
        label_select_midea = tk.Label(janela_configuracoes, text="Escolha vídeo ou imagem:")
        label_select_midea.pack(anchor=tk.W, padx=(10, 0))

        # Criação do OptionMenu para seleção de valores
        option_menu = tk.OptionMenu(janela_configuracoes, selected_midea, *midea, command=exibir_video_ou_imagem)
        option_menu.pack(side=tk.LEFT, padx=(10, 0))

        # Para abrir o Webcam Viewer
        seletor_webcam_viewer = tk.Button(janela_configuracoes, justify="left", text="Visualizar", command=open_webcam_window)
        seletor_webcam_viewer.pack(side=tk.LEFT)


#///////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////
gerenciador_aberto = False

def abrir_janela_configuracoes():
    global gerenciador_aberto, COUNT_OR_TIME, start_save_time
    janela_configuracoes = tk.Toplevel(root)
    janela_configuracoes.title("Configurações de exportação")
    janela_configuracoes.iconbitmap('app.ico')
    janela_configuracoes.resizable(False, False)

    # Usando ttk para uma aparência melhor
    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 9))
    style.configure('TLabel',  font=('Helvetica', 9))
    style.configure('TEntry',  font=('Helvetica', 9))

    tk.Label(janela_configuracoes, text="Onde salvar", font=("Arial", 12)).pack(anchor="w", padx="10", pady=(10, 0))

    # Localização do arquivo
    label_endereco = ttk.Label(janela_configuracoes, text="Escolha a pasta onde salvar:    ")
    label_endereco.pack(anchor="w", padx="10")

    entrada_endereco = ttk.Entry(janela_configuracoes, width=40, foreground='grey')
    entrada_endereco.pack(anchor="w", padx="10")
    entrada_endereco.insert(0, file_dir)

    # Variável de controle para evitar múltiplos eventos
    gerenciador_aberto = False

    def on_focus_in(event):
        global file_dir, count_save_spectra, config, gerenciador_aberto
        # Verifica se o gerenciador já foi aberto
        if gerenciador_aberto:
            return
        gerenciador_aberto = True
        if entrada_endereco.get() == file_dir:
            printf("Escolha o diretório onde salvar os spectros.")
            entrada_endereco.delete(0, 'end')
            entrada_endereco.config(foreground='black')
            diretorio = filedialog.askdirectory(title="Selecione um diretório")
            try:
                janela_configuracoes.lift()
            except:
                print("[WARNING] Exception in janela_configuracoes.lift()")
            if diretorio and diretorio != file_dir:
                if not os.path.isdir(diretorio):
                    printf(f"O diretório '{diretorio}' não existe.")
                    return
                file_dir = diretorio + "/"
                printf(f"Diretório selecionado: {diretorio}")
                entrada_endereco.delete(0, 'end')
                entrada_endereco.insert(0, file_dir)
                # salvar_configuracoes(config)
                # count_save_spectra = config["count_save_spectra"] = 0
            else:
                printf("Nenhum diretório foi selecionado.")

    def on_focus_out(event):
        global file_dir
        if entrada_endereco.get() == file_dir + '/':
            entrada_endereco.insert(0, file_dir)
            entrada_endereco.config(foreground='grey')
        
    def on_enter(event):
        global file_dir, config
        diretorio = filedialog.askdirectory(title="Selecione um diretório") if entrada_endereco.get() == file_dir else entrada_endereco.get()
        try:
            janela_configuracoes.lift()
        except:
            printf("[WARNING] Exception in janela_configuracoes.lift()")
        if diretorio.endswith("/") or diretorio.endswith("\\"):
            diretorio = diretorio[:-1]
        if diretorio and diretorio != file_dir:
            if not os.path.isdir(diretorio):
                printf(f"O diretório '{diretorio}' não existe.")
                return
            file_dir = diretorio + "/"
            printf(f"Diretório selecionado: {diretorio}")
            entrada_endereco.delete(0, 'end')
            entrada_endereco.insert(0, file_dir)

    # Save Spectra
    save_on_var = tk.BooleanVar(value=SAVE_SPECTRA)

    # Seletor de Salvar Spectro
    def save_spectra():
        global SAVE_SPECTRA, start_save_time
        SAVE_SPECTRA = save_on_var.get()
        if SAVE_SPECTRA:
            start_save_time = time.time()
    
    def save_one_spectra():
        global SAVE_SPECTRA, SAVE_ONLY_ONE_SPECTRA, save_only_var, last_save_time
        if not SAVE_SPECTRA:
            SAVE_ONLY_ONE_SPECTRA = True
            save_only_var = tk.BooleanVar(value=False)
            last_save_time = -9999
    
    def on_enter_mouse(event):
        event.widget.config(bg="lightgreen", fg="black")  # Muda cor de fundo e texto ao entrar

    def on_leave(event):
        event.widget.config(bg="SystemButtonFace", fg="black")  # Restaura as cores originais
    
    tk.Label(janela_configuracoes, text="Opções de nome", font=("Arial", 12)).pack(anchor="w", padx="10", pady=(15, 0))

    def on_return_name(event):
        global config
        value = "spectrum"
        try:
            value = str(entrada_nome.get())
        except:
            printf("[Error]: certifique-se de que o valor é uma string.")
            return
        if config["spectrum_file_name"] == value:
            return
        config["spectrum_file_name"] = value
        salvar_configuracoes(config)
        printf(f"Nome do arquivo atualizado como \"{value}\".")

    tk.Label(janela_configuracoes, text="Nome do arquivo:").pack(anchor="w", padx="10")
    entrada_nome = tk.Entry(janela_configuracoes, width=40)
    entrada_nome.insert(0, config["spectrum_file_name"])
    entrada_nome.pack(anchor="w", padx="10")

    tk.Label(janela_configuracoes, text="Completar o nome de arquivo com:").pack(anchor="w", padx="10")
    # op_nomes = ["\"exe: /spectrum000.txt\"", "\"spectrum-2025-01-09-17-54-37-261.txt\""]
    op_nomes = ["Contador", "Data"]

    selected_name = tk.StringVar(value=op_nomes[0] if COUNT_OR_TIME else op_nomes[-1])

    def change_menu(nada):
        global COUNT_OR_TIME
        if selected_name.get() == op_nomes[0]:
            COUNT_OR_TIME = True
        elif selected_name.get() == op_nomes[-1]:
            COUNT_OR_TIME = False

    option_menu = tk.OptionMenu(janela_configuracoes, selected_name, *op_nomes, command=change_menu)
    option_menu.pack(anchor="w", padx="10")

    def on_return_counter(event):
        global config, count_save_spectra
        value = 0
        try:
            value = int(entrada_coef2.get())
        except:
            printf("[Error]: certifique-se de que o valor é um número inteiro.")
            return
        config["count_save_spectra"] = value
        count_save_spectra = value
        salvar_configuracoes(config)
        printf(f"Contador atualizado: {value}.")

    def on_focus_counter(event):
        global config
        entrada_coef2.delete(0, 'end')
        text = str(config["count_save_spectra"])
        entrada_coef2.insert(0, text)
    

    tk.Label(janela_configuracoes, text="Contador começa em (adicionado ao nome):").pack(anchor="w", padx="10")
    entrada_coef2 = tk.Entry(janela_configuracoes, width=40)
    entrada_coef2.insert(0, int(config["count_save_spectra"]))
    entrada_coef2.pack(anchor="w", padx="10")
    
    tk.Label(janela_configuracoes, text="Temporalização", font=("Arial", 12)).pack(anchor="w", padx="10", pady=(15, 0))

    tk.Label(janela_configuracoes, text="Tempo total de coleta (s):").pack(anchor="w", padx="10")
    entrada_coef0 = tk.Entry(janela_configuracoes, width=40)
    entrada_coef0.insert(0, "0 (Tempo de coleta infinito.)" if (config["total_time_save_spectra"] == 0.0) else str(config["total_time_save_spectra"]))
    entrada_coef0.pack(anchor="w", padx="10")

    def on_return_temporal(event):
        global config
        value = 0.0
        try:
            match = re.search(r'\d+\.\d+|\d+', entrada_coef0.get())
            if match:
                value = float(match.group())
        except:
            printf("[ERROR]: o valor tem de ser um número racional.")
            return
        if config["total_time_save_spectra"] == value:
            return
        config["total_time_save_spectra"] = value
        entrada_coef0.delete(0, 'end')
        entrada_coef0.insert(0, str(config["total_time_save_spectra"]))
        salvar_configuracoes(config)
        printf(f"Tempo de coleta: {entrada_coef0.get()} segundos.")
    
    def on_enter_temporal(event):
        entrada_coef0.delete(0, 'end')
        text = str(config["total_time_save_spectra"])
        entrada_coef0.insert(0, text)

    def on_leave_temporal(event):
        text = str(config["total_time_save_spectra"])
        if config["total_time_save_spectra"] == 0.0:
            text = "0 (Tempo de coleta infinito.)"
        elif entrada_coef0.get() != str(config["total_time_save_spectra"]):
            on_return_temporal(None)
            return
        entrada_coef0.delete(0, 'end')
        entrada_coef0.insert(0, text)
    
    def remove_focus(event):
        event.widget.master.focus_set()
    
    def on_return_delta(event):
        global config
        value = 0
        try:
            value = int(entrada_coef1.get())
        except:
            printf("[Error]: certifique-se de que o valor é um número inteiro.")
            return
        if config["time_to_save_spectra"] == value:
            return
        config["time_to_save_spectra"] = value
        printf(f"Período de coleta salvo como {value}ms.")
        salvar_configuracoes(config)
    
    tk.Label(janela_configuracoes, text="Período de coleta (ms):").pack(anchor="w", padx="10")
    entrada_coef1 = tk.Entry(janela_configuracoes, width=40)
    entrada_coef1.insert(0, int(config["time_to_save_spectra"]))
    entrada_coef1.pack(anchor="w", padx="10")

    save_seletor = tk.Checkbutton(janela_configuracoes, justify="left", text="Salvar sequência de espectros", variable=save_on_var, command=save_spectra)
    save_seletor.pack(anchor="w", padx="10", pady=(8, 0))

    save_only = tk.Button(janela_configuracoes, justify="left", text="Salvar um único espectro", command=save_one_spectra)
    save_only.pack(anchor="center", padx="10", pady=(10, 20))

    entrada_endereco.bind("<FocusIn>", on_focus_in)
    entrada_endereco.bind("<FocusOut>", on_focus_out)
    entrada_endereco.bind('<Return>', on_enter)
    save_only.bind("<Enter>", on_enter_mouse)
    save_only.bind("<Leave>", on_leave)
    entrada_coef0.bind("<Return>", on_return_temporal)
    entrada_coef0.bind("<Enter>", on_enter_temporal)
    entrada_coef0.bind("<Leave>", on_leave_temporal)
    entrada_coef0.bind("<Button-1>", remove_focus)
    entrada_coef1.bind("<Leave>", on_return_delta)
    entrada_coef1.bind("<Return>", on_return_delta)
    entrada_coef2.bind("<FocusIn>", on_focus_counter)
    entrada_coef2.bind("<Return>", on_return_counter)
    entrada_nome.bind("<Return>", on_return_name)
    entrada_nome.bind("<Leave>", on_return_name)

#///////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////

def abrir_janela_read_file_spectra():
    # Criação da interface gráfica
    window_file_spectra = tk.Toplevel(root)
    window_file_spectra.title("Visualizador de Espectro")
    window_file_spectra.iconbitmap('app.ico')
    window_file_spectra.geometry("500x250")

    # Usando ttk para uma aparência melhor
    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 12))
    style.configure('TLabel', font=('Helvetica', 12))
    style.configure('TEntry', font=('Helvetica', 12))

    # Frame para organizar os widgets
    frame = ttk.Frame(window_file_spectra, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Label e campo de entrada para o endereço do arquivo
    label_endereco = ttk.Label(frame, text="Endereço do arquivo:")
    label_endereco.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

    entrada_endereco = ttk.Entry(frame, width=40)
    entrada_endereco.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

    # Função para selecionar o arquivo e atualizar o campo de entrada
    def selecionar_arquivo():
        caminho_arquivo = filedialog.askopenfilename(title="Selecione o arquivo de espectro", filetypes=[("Text Files", "*.txt")])
        try:
            window_file_spectra.lift()
        except:
            printf("[WARNING] Exception in janela_configuracoes.lift()")
        if caminho_arquivo:
            entrada_endereco.delete(0, tk.END)
            entrada_endereco.insert(0, caminho_arquivo)
            atualizar_visualizacao()

    # Função para atualizar a visualização do espectro
    def atualizar_visualizacao():
        caminho_arquivo = entrada_endereco.get()
        frequencias, ganhos = ler_dados_arquivo(caminho_arquivo)
        if frequencias and ganhos:
            plotar_espectro(frequencias, ganhos)

    # Botão para selecionar o arquivo via gerenciador de arquivos
    botao_selecionar = ttk.Button(frame, text="Selecionar Arquivo", command=selecionar_arquivo)
    botao_selecionar.grid(row=1, column=1, padx=5, pady=5)

    # Botão para atualizar a visualização
    botao_atualizar = ttk.Button(frame, text="Atualizar Visualização", command=atualizar_visualizacao)
    botao_atualizar.grid(row=2, column=0, columnspan=2, pady=10)

    # Configuração de expansão das colunas
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=0)

#///////////////////////////////////////////////////////////////////////////////////////////////////////

# Configuração da interface principal
def open_webcam_window():
    # Open a new window
    webcam_window = Toplevel(root)
    webcam_window.title("Webcam Viewer")
    WebcamViewer(webcam_window, webcam, time_rate=config["time_rate"]).start()

def open_calibration_window():
    calibration_window = Toplevel(root)
    calibration_window.title("Advanced calibration")
    WebcamViewer(window=calibration_window, webcam=webcam, time_rate=config["time_rate"], deve_calibrar=True, limiar=40).start()

def on_closing():
    webcam.release()
    root.destroy()

def on_closing_all():
    on_closing()
    exit()

def osa_start():
    global line, i, config, root, webcam_label, open_button_canva, fig, ax, canvas, webcam, fonte_de_dados, label_fonte_de_dados, log_element, DARK, poly_collection, gradient_cache, SHOW_FRAME_GRAPH
    line = None
    i = 0
    # count_save_spectra = 0
    # global_frame = None   
    config = carregar_configuracoes()
    fonte_de_dados = "Fonte de dados: "
    label_fonte_de_dados = None
    atualiza_fonte_de_dados()

    # Variáveis globais para cache
    poly_collection = None
    gradient_cache = None

    
    # Configuração da interface principal
    root = tk.Tk()
    root.title("Interface Osa Visível")
    root.iconbitmap('app.ico')

    # tamanho mínimo da janela
    root.minsize(1044, 400)

    # Função para abrir o website no navegador padrão
    def open_website():
        webbrowser.open("https://github.com/Jakson-Almeida")

    # Função para trocar a imagem ao passar o mouse
    def on_enter_logo(event):
        logo_label.config(image=hover_logo, cursor="hand2")

    # Função para restaurar a imagem original ao sair com o mouse
    def on_leave_logo(event):
        logo_label.config(image=logo, cursor="")

    # Carregar imagens
    logo = tk.PhotoImage(file="data/UFJF-logo.png")
    hover_logo = tk.PhotoImage(file="data/UFJF-logo-hover.png")  # Substitua pelo caminho da imagem para hover

    # Criar um widget de rótulo para exibir a imagem
    logo_label = tk.Label(root, image=logo)
    logo_label.place(x=15, y=10)  # Ajuste as coordenadas (x, y) conforme necessário

    # Vincular os eventos ao widget
    logo_label.bind("<Enter>", on_enter_logo)  # Mouse sobre a imagem
    logo_label.bind("<Leave>", on_leave_logo)  # Mouse fora da imagem
    logo_label.bind("<Button-1>", lambda e: open_website())  # Clique na imagem

    webcam_label = tk.Label(root, bg="white")
    webcam_label.pack(side=tk.LEFT, padx=(50, 0))

    # Botão para abrir a webcam
    open_button_canva = tk.Button(root, text="Calibrar", font=("Arial", 14), command=open_calibration_window)
    open_button_canva.pack(side=tk.LEFT)

    # Instância do LogWidget
    log_element = LogWidget(root, size=(46, 9), buffer=300, theme="white", element=open_button_canva, start_pose=(-300, 20), add_str=">>> ")
    printf("")

    def key_pressed(event):
        global SHOW_GRADIENT, poly_collection, gradient_cache, SHOW_FRAME_GRAPH
        key = event.keysym
        if key == 'd':
            change_theme()
        elif key == 'g':
            SHOW_GRADIENT = not SHOW_GRADIENT
            reiniciar()
        elif key == 'p':
            show_canvas_peak()
        elif key == 'v':
            show_canvas_peak(valley=True)
        elif key == 's':
            salvar_imagem()
        elif key == 'y':
            SHOW_FRAME_GRAPH = not SHOW_FRAME_GRAPH
            show_frame_graph(None) if SHOW_FRAME_GRAPH else hide_frame_graph(None)

    def change_theme(is_dark=None):
        global DARK, fig, ax, poly_collection, gradient_cache
        if is_dark is not None:
            DARK = is_dark
        else:
            DARK = not DARK
        reiniciar()
        printf("Tema alterado.")
    
    root.bind("<KeyPress>", key_pressed)

    if DARK:
        # plt.style.use('dark_background')
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_facecolor('black')
        ax.set_xlabel('Comprimento de onda (nm)', color='white')
        ax.set_ylabel('Intensidade (arb. unit)', color='white')
        ax.set_ylim(0, 270)
        ax.set_xlim(min(wl), max(wl))
        ax.grid(True)
    else:
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_xlabel('Comprimento de onda (nm)')
        ax.set_ylabel('Intensidade (arb. unit)')
        ax.set_ylim(0, 270)
        ax.set_xlim(min(wl), max(wl))
        ax.grid(True)
    
    def show_canvas_peak(valley=False):
        global glob_spec, wl

        # Encontra os picos
        peaks, _ = find_peaks(glob_spec, prominence=5) if not valley else find_peaks(-1*glob_spec, prominence=5)
        if len(peaks) == 0:
            printf(f"NOTA: Nenhum {'PICO' if not valley else 'VALE'} encontrado")

        # Remove marcadores antigos, se existirem
        if hasattr(ax, 'markers'):
            for marker in ax.markers:
                marker.remove()
            ax.markers = []  # Reseta a lista de marcadores
        else:
            ax.markers = []  # Inicializa a lista de marcadores

        # Adiciona novos marcadores e exibe informações
        for idx, peak in enumerate(peaks):
            wavelength = wl[peak]
            intensity = glob_spec[peak]

            # Exibe informações no console
            printf(f"{'PICO' if not valley else 'VALE'} {idx + 1}: Comprimento de onda: {wavelength:.2f} nm | Intensidade: {intensity:.2f}")

            # Adiciona marcador no gráfico
            color = 'white' if DARK else 'black'
            marker = ax.scatter(wavelength, intensity, color=color, marker=11 if valley else 10, zorder=5)
            ax.markers.append(marker)  # Armazena o marcador na lista

        # Atualiza o gráfico
        canvas.draw_idle()
    
    def onclick(event):
        """Função para capturar cliques no gráfico e exibir coordenadas."""
        if event.inaxes == ax:  # Verifica se o clique foi dentro dos eixos
            global glob_spec, wl
            if glob_spec is None:
                return
            # Obtém coordenadas do clique
            x_click = event.xdata
            show_graph_point(x_click=x_click)
    
    def show_graph_point(x_click):
        # Encontra o índice do comprimento de onda mais próximo
        idx = np.abs(wl - x_click).argmin()
        wavelength = wl[idx]
        intensity = glob_spec[idx] if 'glob_spec' in globals() else 0  # Usa dados atuais
        
        printf(f"PONTO: Comprimento de onda: {wavelength:.2f} nm | Intensidade: {intensity:.2f}")

        # Adiciona marcador vermelho no ponto clicado
        if hasattr(ax, 'marker'):
            try:
                ax.marker.remove()
            except:
                pass
        ax.marker = ax.scatter(wavelength, intensity, color='white', zorder=5) if DARK else ax.scatter(wavelength, intensity, color='black', zorder=5)
        canvas.draw_idle()  # Atualiza o gráfico
        return intensity

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.mpl_connect('button_press_event', onclick)  # <--- Nova linha!
    # canvas.mpl_connect('button_press_event', show_canvas_peak)  # <--- Nova linha!
    canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def salvar_imagem():
        # Abre a janela de diálogo para selecionar onde salvar
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".png",  # Extensão padrão
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
            title="Salvar imagem do gráfico"
        )
    
        # Salva a imagem se o usuário escolher um local
        if arquivo:
            fig.savefig(arquivo)
            printf(f"Imagem salva em: {arquivo}")

    def canvas_key_pressed(event):
        key = event.keysym
        if key == 'r' or key == 'Escape':
            reset_graph()

    def reset_graph():
        if hasattr(ax, 'marker'):
            try:
                ax.marker.remove()
            except:
                pass
        if hasattr(ax, 'markers'):
            for marker in ax.markers:
                marker.remove()
            ax.markers = []  # Reseta a lista de marcadores
    
    # Vincula o evento de teclado ao widget Tkinter
    canvas.get_tk_widget().bind("<KeyPress>", canvas_key_pressed)

    # Fonte de dados
    label_fonte_de_dados = tk.Label(root, text=fonte_de_dados, bg="white", font=('Helvetica', 12))
    label_fonte_de_dados.place(x=570, y=0)

    def show_frame_graph(event):
        updateY(None)
        frame_graph.place(x=923, y=49)

    def hide_frame_graph(event):
        frame_graph.place_forget()  # Esconde o Frame
    
    def key_frame_graph(event):
        value = 550
        try:
            match = re.search(r'\d+\.\d+|\d+', entrada_comprimento_onda.get())
            if match:
                value = float(match.group())
        except:
            value = 550
            entrada_comprimento_onda.delete(0, "end")
            entrada_comprimento_onda.insert(0, f"{value}")
            return
    
    def updateY(event):
        try:
            value = float(entrada_comprimento_onda.get())
        except:
            entrada_comprimento_onda.delete(0, "end")
            entrada_comprimento_onda.insert(0, "550")
            return
        y = show_graph_point(value)
        gain_output.delete(0, "end")
        gain_output.insert(0, f"{y:.2f}")
    
    SHOW_FRAME_GRAPH = False

    # Cria um Frame para organizar os widgets
    frame_graph = tk.Frame(root, padx=0, pady=0)
    frame_graph.place(x=923, y=49)

    # Label
    label_graph = tk.Label(frame_graph, text="λ:")
    label_graph.grid(row=0, column=0, sticky="w")

    # Campo de entrada para o comprimento de onda
    entrada_comprimento_onda = tk.Entry(frame_graph, width=6)
    entrada_comprimento_onda.insert(0, "550")  # Valor padrão de 550 nm
    entrada_comprimento_onda.grid(row=0, column=1, padx=10)
    entrada_comprimento_onda.bind('<Return>', updateY)

    # Label
    label_gain = tk.Label(frame_graph, text="y:")
    label_gain.grid(row=1, column=0, sticky="w")

    # Campo de entrada para o comprimento de onda
    gain_output = tk.Entry(frame_graph, width=6)
    gain_output.insert(0, "255")  # Valor padrão de 550 nm
    gain_output.grid(row=1, column=1, padx=10)

    entrada_comprimento_onda.bind("<Key>", key_frame_graph)

    # frame_graph.bind("<Enter>", show_frame)
    # frame_graph.bind("<Leave>", hide_frame_graph)
    hide_frame_graph(None)

    def on_enter(event):
        event.widget.config(bg="lightgreen", fg="black")  # Muda cor de fundo e texto ao entrar

    def on_leave(event):
        event.widget.config(bg="SystemButtonFace", fg="black")  # Restaura as cores originais

    # Criação dos botões
    btn_root_1 = tk.Button(root, text="Editar Inicialização", width=14, anchor="w", height=1, command=abrir_janela_edicao)
    btn_root_2 = tk.Button(root, text="Webcam",               width=14, anchor="w", height=1, command=abrir_janela_webcam)
    btn_root_3 = tk.Button(root, text="Salvar Espectros",     width=14, anchor="w", height=1, command=abrir_janela_configuracoes)
    btn_root_4 = tk.Button(root, text="Leitura Espectros",    width=14, anchor="w", height=1, command=abrir_janela_read_file_spectra)
    btn_root_5 = tk.Button(root, text="Reiniciar programa",   width=14, anchor="w", height=1, command=reiniciar)

    # Lista de botões para associar eventos
    buttons = [btn_root_1, btn_root_2, btn_root_3, btn_root_4, btn_root_5, open_button_canva]

    # Vincula os eventos para cada botão
    for button in buttons:
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    btn_root_1.pack()
    btn_root_2.pack()
    btn_root_3.pack()
    btn_root_4.pack()
    btn_root_5.pack()

    webcam = cv2.VideoCapture(WEBCAM_NUMBER) if WEBCAM_ON else cv2.VideoCapture("data/video.mp4")

    root.protocol("WM_DELETE_WINDOW", on_closing_all)
    update()
    root.mainloop()

def reiniciar():
    # Exibir uma mensagem de confirmação
    resposta = messagebox.askyesno("Confirmação", "Tem certeza de que deseja reiniciar o programa?")
    if resposta:
        # Lógica para reiniciar o programa
        messagebox.showinfo("Reiniciando", "O programa será reiniciado.")
        # Aqui você pode adicionar sua lógica de reinicialização
        # Por exemplo, reexecutar o arquivo atual (simulado aqui)
        root.destroy()
        start_config(config)
        osa_start()

if __name__ == '__main__':
    osa_start()