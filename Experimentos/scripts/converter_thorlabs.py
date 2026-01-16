#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para converter espectros ThorLabs (CSV/SPF2) para formato TXT padronizado (Visible_OSA).
Também seleciona 100 amostras espaçadas ~10 segundos da pasta Temporal.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import struct
import os


def ler_csv_thorlabs(arquivo_csv):
    """
    Lê arquivo CSV da ThorLabs e retorna comprimento de onda e intensidade.
    
    Args:
        arquivo_csv: Caminho para o arquivo CSV
        
    Returns:
        wl_nm: Array de comprimentos de onda em nanômetros
        intensity: Array de intensidades
    """
    # Lê o arquivo procurando pela seção [Data]
    with open(arquivo_csv, 'r', encoding='utf-8', errors='ignore') as f:
        linhas = f.readlines()
    
    # Encontra onde começa a seção [Data]
    inicio_dados = None
    for idx, linha in enumerate(linhas):
        if '[Data]' in linha:
            inicio_dados = idx + 1
            break
    
    if inicio_dados is None:
        raise ValueError(f"Seção [Data] não encontrada em {arquivo_csv}")
    
    # Lê os dados (formato: comprimento_onda_nm;intensidade)
    dados = []
    for linha in linhas[inicio_dados:]:
        linha = linha.strip()
        if linha and not linha.startswith('#'):
            partes = linha.split(';')
            if len(partes) >= 2:
                try:
                    wl = float(partes[0])
                    intensity = float(partes[1])
                    dados.append([wl, intensity])
                except ValueError:
                    continue
    
    if len(dados) == 0:
        raise ValueError(f"Nenhum dado encontrado em {arquivo_csv}")
    
    dados_array = np.array(dados)
    wl_nm = dados_array[:, 0]
    intensity = dados_array[:, 1]
    
    return wl_nm, intensity


def ler_spf2_thorlabs(arquivo_spf2):
    """
    Tenta ler arquivo SPF2 da ThorLabs.
    SPF2 é um formato binário proprietário. Esta função tenta uma leitura básica.
    
    Args:
        arquivo_spf2: Caminho para o arquivo SPF2
        
    Returns:
        wl_nm: Array de comprimentos de onda em nanômetros
        intensity: Array de intensidades
    """
    # Primeiro, tenta verificar se o arquivo tem alguma parte legível como texto
    try:
        with open(arquivo_spf2, 'rb') as f:
            # Lê os primeiros bytes para verificar o formato
            header = f.read(100)
            
            # Se contém texto legível, pode ser um formato híbrido
            if b'[Data]' in header or b'Thorlabs' in header:
                # Tenta ler como texto
                f.seek(0)
                return ler_spf2_como_texto(f)
            else:
                # Formato binário puro - precisa de parser mais complexo
                # Por enquanto, vamos tentar uma abordagem simples
                return ler_spf2_binario(arquivo_spf2)
    except Exception as e:
        raise ValueError(f"Erro ao ler SPF2: {str(e)}")


def ler_spf2_como_texto(file_handle):
    """Tenta ler SPF2 como arquivo de texto."""
    file_handle.seek(0)
    linhas = file_handle.read().decode('utf-8', errors='ignore').split('\n')
    
    # Procura por [Data] ou dados numéricos
    inicio_dados = None
    for idx, linha in enumerate(linhas):
        if '[Data]' in linha or (linha.strip() and not linha.startswith('#') and ';' in linha):
            if '[Data]' in linha:
                inicio_dados = idx + 1
            else:
                inicio_dados = idx
            break
    
    if inicio_dados is None:
        raise ValueError("Não foi possível encontrar dados no arquivo SPF2")
    
    dados = []
    for linha in linhas[inicio_dados:]:
        linha = linha.strip()
        if linha and not linha.startswith('#'):
            partes = linha.split(';')
            if len(partes) >= 2:
                try:
                    wl = float(partes[0])
                    intensity = float(partes[1])
                    dados.append([wl, intensity])
                except ValueError:
                    continue
    
    if len(dados) == 0:
        raise ValueError("Nenhum dado numérico encontrado no SPF2")
    
    dados_array = np.array(dados)
    wl_nm = dados_array[:, 0]
    intensity = dados_array[:, 1]
    
    return wl_nm, intensity


def ler_spf2_binario(arquivo_spf2):
    """
    Lê arquivo SPF2 binário da ThorLabs.
    Baseado na estrutura conhecida do formato SPF2 da ThorLabs.
    O arquivo SPF2 geralmente tem um cabeçalho ASCII seguido de dados binários,
    ou pode ser totalmente binário com header estruturado.
    """
    with open(arquivo_spf2, 'rb') as f:
        f.seek(0)
        data = f.read()
    
    # Primeiro, verifica se tem partes de texto ASCII no início (pode ter header ASCII)
    try:
        texto_inicio = data[:500].decode('utf-8', errors='ignore')
        # Se encontrar marcadores como "[Data]", pode ser formato híbrido
        if '[Data]' in texto_inicio or 'XAxisUnit' in texto_inicio or 'nm' in texto_inicio:
            # Tenta ler como formato híbrido texto/binário
            return ler_spf2_hibrido(arquivo_spf2, data)
    except:
        pass
    
    # Formato totalmente binário
    # Estrutura típica do SPF2: header binário + dados espectrais
    # Vamos procurar por valores razoáveis de comprimento de onda (200-1200 nm)
    
    dados_wl = []
    dados_int = []
    
    # Tenta diferentes offsets e formatos de dados
    # Primeiro tenta encontrar início dos dados procurando por padrões consistentes
    
    # Abordagem melhorada: procura por sequências consistentes de valores
    # que formam um eixo de comprimento de onda crescente
    
    # Tenta float32 (little-endian, formato mais comum no Windows)
    melhor_offset = None
    melhor_sequencia = []
    melhor_formato = None
    
    for offset in range(0, min(2000, len(data) - 16), 1):
        try:
            # Tenta float32 little-endian
            wl1 = struct.unpack('<f', data[offset:offset+4])[0]
            int1 = struct.unpack('<f', data[offset+4:offset+8])[0]
            wl2 = struct.unpack('<f', data[offset+8:offset+12])[0]
            int2 = struct.unpack('<f', data[offset+12:offset+16])[0]
            
            # Verifica se são valores razoáveis e sequenciais
            if (200 <= wl1 < 1200 and 200 <= wl2 < 1200 and 
                abs(wl2 - wl1) < 10 and  # Comprimentos de onda próximos
                wl2 > wl1 and  # Crescente
                -1000 <= int1 <= 50000 and -1000 <= int2 <= 50000):
                
                # Testa ler mais alguns pontos para confirmar
                sequencia = []
                for i in range(min(100, (len(data) - offset) // 8)):
                    try:
                        wl = struct.unpack('<f', data[offset + i*8:offset + i*8 + 4])[0]
                        int_val = struct.unpack('<f', data[offset + i*8 + 4:offset + i*8 + 8])[0]
                        
                        if 200 <= wl <= 1200 and -1000 <= int_val <= 50000:
                            sequencia.append((wl, int_val))
                        else:
                            break
                    except:
                        break
                
                if len(sequencia) > len(melhor_sequencia):
                    melhor_sequencia = sequencia
                    melhor_offset = offset
                    melhor_formato = 'float32_le'
        
        except:
            continue
    
    # Se não encontrou com float32 little-endian, tenta float32 big-endian
    if len(melhor_sequencia) < 100:
        for offset in range(0, min(2000, len(data) - 16), 1):
            try:
                wl1 = struct.unpack('>f', data[offset:offset+4])[0]
                int1 = struct.unpack('>f', data[offset+4:offset+8])[0]
                wl2 = struct.unpack('>f', data[offset+8:offset+12])[0]
                int2 = struct.unpack('>f', data[offset+12:offset+16])[0]
                
                if (200 <= wl1 < 1200 and 200 <= wl2 < 1200 and 
                    abs(wl2 - wl1) < 10 and wl2 > wl1 and
                    -1000 <= int1 <= 50000 and -1000 <= int2 <= 50000):
                    
                    sequencia = []
                    for i in range(min(100, (len(data) - offset) // 8)):
                        try:
                            wl = struct.unpack('>f', data[offset + i*8:offset + i*8 + 4])[0]
                            int_val = struct.unpack('>f', data[offset + i*8 + 4:offset + i*8 + 8])[0]
                            
                            if 200 <= wl <= 1200 and -1000 <= int_val <= 50000:
                                sequencia.append((wl, int_val))
                            else:
                                break
                        except:
                            break
                    
                    if len(sequencia) > len(melhor_sequencia):
                        melhor_sequencia = sequencia
                        melhor_offset = offset
                        melhor_formato = 'float32_be'
            
            except:
                continue
    
    # Se encontrou uma boa sequência, lê todos os dados
    if melhor_sequencia and len(melhor_sequencia) >= 50:
        # Lê todos os pontos disponíveis
        if melhor_formato == 'float32_le':
            byte_format = '<f'
        else:
            byte_format = '>f'
        
        num_points = (len(data) - melhor_offset) // 8
        for i in range(num_points):
            try:
                wl = struct.unpack(byte_format, data[melhor_offset + i*8:melhor_offset + i*8 + 4])[0]
                intensity = struct.unpack(byte_format, data[melhor_offset + i*8 + 4:melhor_offset + i*8 + 8])[0]
                
                if 200 <= wl <= 1200:  # Filtra valores razoáveis
                    dados_wl.append(wl)
                    dados_int.append(intensity)
                elif wl > 1200:  # Se ultrapassou a faixa, para
                    break
            except:
                break
        
        if len(dados_wl) > 0:
            # Remove duplicatas e ordena por comprimento de onda
            dados_array = np.array(list(zip(dados_wl, dados_int)))
            dados_array = dados_array[np.argsort(dados_array[:, 0])]  # Ordena por WL
            
            # Remove pontos muito próximos (pode ser duplicação)
            wl_unique = []
            int_unique = []
            ultimo_wl = -1
            for wl, int_val in dados_array:
                if abs(wl - ultimo_wl) > 0.01:  # Pelo menos 0.01 nm de diferença
                    wl_unique.append(wl)
                    int_unique.append(int_val)
                    ultimo_wl = wl
            
            if len(wl_unique) > 0:
                return np.array(wl_unique), np.array(int_unique)
    
    # Se chegou aqui, não conseguiu ler
    raise ValueError("Não foi possível extrair dados do arquivo SPF2 binário. "
                     "Tente exportar para CSV primeiro.")


def ler_spf2_hibrido(arquivo_spf2, data):
    """
    Lê SPF2 que tem parte ASCII (header) e parte binária (dados).
    """
    # Tenta decodificar como texto e encontrar [Data]
    try:
        texto = data.decode('utf-8', errors='ignore')
        linhas = texto.split('\n')
        
        inicio_dados = None
        for idx, linha in enumerate(linhas):
            if '[Data]' in linha:
                inicio_dados = idx + 1
                break
        
        if inicio_dados:
            dados = []
            for linha in linhas[inicio_dados:]:
                linha = linha.strip()
                if linha and not linha.startswith('#'):
                    partes = linha.split(';')
                    if len(partes) >= 2:
                        try:
                            wl = float(partes[0])
                            intensity = float(partes[1])
                            dados.append([wl, intensity])
                        except ValueError:
                            continue
            
            if len(dados) > 0:
                dados_array = np.array(dados)
                return dados_array[:, 0], dados_array[:, 1]
    except:
        pass
    
    raise ValueError("Formato híbrido não reconhecido")


def converter_para_txt_visible_osa(wl_nm, intensity, arquivo_saida):
    """
    Converte dados para formato TXT do Visible_OSA.
    Formato: comprimento_onda_metros;intensidade
    
    Args:
        wl_nm: Comprimentos de onda em nanômetros
        intensity: Intensidades
        arquivo_saida: Caminho do arquivo de saída
    """
    # Converte de nanômetros para metros
    wl_metros = wl_nm * 1e-9  # 1 nm = 1e-9 m
    
    # Salva no formato Visible_OSA
    with open(arquivo_saida, 'w') as f:
        for wl_m, int_val in zip(wl_metros, intensity):
            f.write(f"{wl_m:.15e};{int_val:.15e}\n")


def processar_arquivo_thorlabs(arquivo_entrada, arquivo_saida):
    """
    Processa um arquivo ThorLabs (CSV ou SPF2) e converte para TXT.
    
    Args:
        arquivo_entrada: Caminho do arquivo de entrada
        arquivo_saida: Caminho do arquivo de saída
    """
    arquivo_entrada = Path(arquivo_entrada)
    
    if arquivo_entrada.suffix.lower() == '.csv':
        wl_nm, intensity = ler_csv_thorlabs(arquivo_entrada)
    elif arquivo_entrada.suffix.lower() == '.spf2':
        try:
            wl_nm, intensity = ler_spf2_thorlabs(arquivo_entrada)
        except NotImplementedError:
            print(f"[AVISO] Não foi possível ler {arquivo_entrada.name} como SPF2 binário.")
            print(f"        Tente exportar para CSV primeiro ou use arquivos CSV.")
            return False
    else:
        raise ValueError(f"Formato não suportado: {arquivo_entrada.suffix}")
    
    # Converte para formato Visible_OSA
    converter_para_txt_visible_osa(wl_nm, intensity, arquivo_saida)
    return True


def selecionar_amostras_temporais(pasta_temporal, pasta_saida, num_amostras=100, prefer_csv=True):
    """
    Seleciona num_amostras espaçadas aproximadamente 10 segundos da pasta Temporal.
    
    Args:
        pasta_temporal: Pasta com arquivos temporais (SPF2)
        pasta_saida: Pasta para salvar as amostras selecionadas (TXT)
        num_amostras: Número de amostras a selecionar (padrão: 100)
    """
    pasta_temporal = Path(pasta_temporal)
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    
    # Lista arquivos - prefere CSV se disponível
    arquivos_csv = sorted(pasta_temporal.glob("*.csv"))
    arquivos_spf2 = sorted(pasta_temporal.glob("*.spf2"))
    
    if prefer_csv and len(arquivos_csv) > 0:
        arquivos = arquivos_csv
        print(f"[INFO] Usando arquivos CSV (preferido): {len(arquivos)} arquivos encontrados")
    else:
        arquivos = arquivos_spf2
        if len(arquivos_csv) > 0:
            print(f"[AVISO] Arquivos CSV encontrados mas não sendo usados.")
        print(f"[INFO] Usando arquivos SPF2: {len(arquivos)} arquivos encontrados")
        if len(arquivos_csv) == 0:
            print(f"[AVISO] Nenhum arquivo CSV encontrado. O formato SPF2 binário requer exportação via software ThorLabs.")
            print(f"[AVISO] Sugestão: Use o software ThorLabs OSA para exportar os SPF2 para CSV primeiro.")
    
    if len(arquivos) == 0:
        print(f"[ERRO] Nenhum arquivo CSV ou SPF2 encontrado em {pasta_temporal}")
        return
    
    total_arquivos = len(arquivos)
    print(f"[INFO] Total de arquivos encontrados: {total_arquivos}")
    
    # Calcula o espaçamento necessário
    # Se temos ~1000 segundos de dados e queremos 100 amostras espaçadas ~10s,
    # precisamos pegar aproximadamente 1 a cada (total_arquivos / num_amostras) arquivos
    if total_arquivos < num_amostras:
        print(f"[AVISO] Menos arquivos ({total_arquivos}) do que amostras solicitadas ({num_amostras})")
        num_amostras = total_arquivos
    
    intervalo = max(1, total_arquivos // num_amostras)
    print(f"[INFO] Selecionando 1 arquivo a cada {intervalo} arquivos")
    
    # Seleciona os arquivos
    arquivos_selecionados = arquivos[::intervalo][:num_amostras]
    
    print(f"[INFO] {len(arquivos_selecionados)} arquivos selecionados")
    print(f"[INFO] Convertendo e salvando em {pasta_saida}...")
    
    sucessos = 0
    falhas = 0
    
    for idx, arquivo in enumerate(arquivos_selecionados):
        # Nome do arquivo de saída: spectrum000.txt, spectrum001.txt, etc.
        nome_saida = f"spectrum{idx:03d}.txt"
        arquivo_saida_path = pasta_saida / nome_saida
        
        try:
            if processar_arquivo_thorlabs(arquivo, arquivo_saida_path):
                sucessos += 1
                if (idx + 1) % 10 == 0:
                    print(f"  Processado {idx + 1}/{len(arquivos_selecionados)}...")
            else:
                falhas += 1
        except Exception as e:
            print(f"  [ERRO] Erro ao processar {arquivo.name}: {str(e)[:100]}")
            falhas += 1
    
    print(f"\n[OK] Conversão concluída: {sucessos} sucessos, {falhas} falhas")
    print(f"[OK] Arquivos salvos em: {pasta_saida}")


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Converter espectros ThorLabs para formato TXT')
    parser.add_argument('--temporal', action='store_true', 
                       help='Selecionar e converter 100 amostras temporais')
    parser.add_argument('--prefer-csv', action='store_true', default=True,
                       help='Preferir arquivos CSV sobre SPF2 (padrão: True)')
    parser.add_argument('--arquivo', type=str, 
                       help='Converter um arquivo específico (CSV ou SPF2)')
    parser.add_argument('--saida', type=str, 
                       help='Arquivo ou pasta de saída')
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    
    if args.temporal:
        # Seleciona e converte amostras temporais
        pasta_temporal = base_dir / "ThorLabs" / "Temporal"
        pasta_saida = base_dir / "ThorLabs" / "Temporal_Selecionado"
        
        selecionar_amostras_temporais(pasta_temporal, pasta_saida, num_amostras=100, prefer_csv=args.prefer_csv)
    elif args.arquivo:
        # Converte um arquivo específico
        arquivo_entrada = Path(args.arquivo)
        if args.saida:
            arquivo_saida = Path(args.saida)
        else:
            arquivo_saida = arquivo_entrada.with_suffix('.txt')
        
        processar_arquivo_thorlabs(arquivo_entrada, arquivo_saida)
        print(f"[OK] Arquivo convertido: {arquivo_saida}")
    else:
        # Por padrão, processa amostra livre
        arquivo_csv = base_dir / "ThorLabs" / "AmostraLivre" / "spectrum.csv"
        arquivo_txt = base_dir / "ThorLabs" / "AmostraLivre" / "spectrum.txt"
        
        if arquivo_csv.exists():
            print(f"[INFO] Convertendo {arquivo_csv.name}...")
            processar_arquivo_thorlabs(arquivo_csv, arquivo_txt)
            print(f"[OK] Arquivo convertido: {arquivo_txt}")
        else:
            print(f"[ERRO] Arquivo não encontrado: {arquivo_csv}")


if __name__ == "__main__":
    main()
