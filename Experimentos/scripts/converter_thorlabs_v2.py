#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script melhorado para converter espectros ThorLabs (CSV/SPF2) para formato TXT padronizado.
Versão com parser SPF2 melhorado baseado em estrutura conhecida.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import struct
import os


def ler_csv_thorlabs(arquivo_csv):
    """
    Lê arquivo CSV da ThorLabs e retorna comprimento de onda e intensidade.
    Os dados CSV já estão em nanômetros (nm_vac).
    
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
    Lê arquivo SPF2 binário da ThorLabs usando método melhorado.
    Estrutura típica: header binário (variável) + dados espectrais.
    """
    with open(arquivo_spf2, 'rb') as f:
        data = f.read()
    
    file_size = len(data)
    
    # Abordagem melhorada: tenta múltiplas estratégias
    
    # Estratégia 1: Procurar por padrões de floats consistentes
    # Assumindo formato: pairs de (wavelength, intensity) como float32 ou float64
    
    melhor_resultado = None
    melhor_score = 0
    
    # Tenta diferentes offsets iniciais (headers podem variar)
    for offset in range(0, min(1024, file_size - 32), 4):
        for formato in ['<ff', '<dd', '>ff', '>dd']:  # float32/float64, little/big endian
            try:
                if formato == '<ff' or formato == '>ff':
                    struct_size = 8
                else:
                    struct_size = 16
                
                if offset + struct_size > file_size:
                    continue
                
                # Testa ler alguns pontos
                pontos_teste = []
                for i in range(min(50, (file_size - offset) // struct_size)):
                    try:
                        if struct_size == 8:
                            if formato.startswith('<'):
                                wl, int_val = struct.unpack('<ff', data[offset + i*8:offset + i*8 + 8])
                            else:
                                wl, int_val = struct.unpack('>ff', data[offset + i*8:offset + i*8 + 8])
                        else:
                            if formato.startswith('<'):
                                wl, int_val = struct.unpack('<dd', data[offset + i*16:offset + i*16 + 16])
                            else:
                                wl, int_val = struct.unpack('>dd', data[offset + i*16:offset + i*16 + 16])
                        
                        # Validação: valores devem ser razoáveis para espectros ópticos
                        if 200 <= wl <= 1200 and -1000 <= int_val <= 50000:
                            # Verifica se a sequência é crescente (comprimento de onda deve aumentar)
                            if len(pontos_teste) == 0 or wl >= pontos_teste[-1][0] - 5:  # Permite pequenas variações
                                pontos_teste.append((wl, int_val))
                            elif wl < pontos_teste[-1][0] - 10:  # Se cai muito, pode ser outro bloco
                                break
                        else:
                            break
                    except (struct.error, IndexError):
                        break
                
                # Score baseado no número de pontos válidos e consistência
                if len(pontos_teste) > melhor_score:
                    # Verifica se a sequência é monotônica crescente (comprimento de onda)
                    wls = [p[0] for p in pontos_teste]
                    if len(wls) > 10:
                        # Calcula diferença média entre pontos consecutivos
                        diffs = np.diff(wls)
                        if np.all(diffs >= 0) or np.mean(diffs[diffs >= 0]) > 0.1:  # Deve ser crescente ou pelo menos não decrescente
                            melhor_resultado = (offset, formato, struct_size, pontos_teste)
                            melhor_score = len(pontos_teste)
            
            except (struct.error, ValueError):
                continue
    
    # Se encontrou uma boa sequência, lê todos os dados
    if melhor_resultado and melhor_score >= 50:
        offset, formato, struct_size, pontos_teste = melhor_resultado
        
        dados_wl = []
        dados_int = []
        
        num_points = (file_size - offset) // struct_size
        for i in range(num_points):
            try:
                if struct_size == 8:
                    if formato.startswith('<'):
                        wl, int_val = struct.unpack('<ff', data[offset + i*8:offset + i*8 + 8])
                    else:
                        wl, int_val = struct.unpack('>ff', data[offset + i*8:offset + i*8 + 8])
                else:
                    if formato.startswith('<'):
                        wl, int_val = struct.unpack('<dd', data[offset + i*16:offset + i*16 + 16])
                    else:
                        wl, int_val = struct.unpack('>dd', data[offset + i*16:offset + i*16 + 16])
                
                if 200 <= wl <= 1200 and -1000 <= int_val <= 50000:
                    dados_wl.append(wl)
                    dados_int.append(int_val)
                elif wl > 1200:  # Ultrapassou a faixa espectral
                    break
            except (struct.error, IndexError):
                break
        
        if len(dados_wl) >= 50:
            # Remove duplicatas próximas e ordena
            dados_array = np.array(list(zip(dados_wl, dados_int)))
            # Remove duplicatas baseadas em comprimento de onda
            _, indices_unicos = np.unique(np.round(dados_array[:, 0], decimals=2), return_index=True)
            dados_array = dados_array[np.sort(indices_unicos)]
            dados_array = dados_array[np.argsort(dados_array[:, 0])]
            
            return dados_array[:, 0], dados_array[:, 1]
    
    # Se não conseguiu ler, sugere exportar via software
    raise ValueError(
        f"Não foi possível ler o arquivo SPF2 binário: {arquivo_spf2.name}\n"
        "Sugestão: Use o software ThorLabs OSA para exportar os arquivos SPF2 para CSV primeiro, "
        "ou verifique se há arquivos CSV disponíveis na pasta."
    )


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
    Prefere CSV se disponível.
    """
    arquivo_entrada = Path(arquivo_entrada)
    
    if arquivo_entrada.suffix.lower() == '.csv':
        wl_nm, intensity = ler_csv_thorlabs(arquivo_entrada)
    elif arquivo_entrada.suffix.lower() == '.spf2':
        try:
            wl_nm, intensity = ler_spf2_thorlabs(arquivo_entrada)
        except ValueError as e:
            print(f"[AVISO] {str(e)}")
            return False
    else:
        raise ValueError(f"Formato não suportado: {arquivo_entrada.suffix}")
    
    # Converte para formato Visible_OSA
    converter_para_txt_visible_osa(wl_nm, intensity, arquivo_saida)
    return True


def selecionar_amostras_temporais(pasta_temporal, pasta_saida, num_amostras=100, prefer_csv=True):
    """
    Seleciona num_amostras espaçadas aproximadamente 10 segundos.
    Prefere arquivos CSV se disponíveis.
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
            print(f"[AVISO] Arquivos CSV encontrados mas não sendo usados. Use --prefer-csv=False para forçar SPF2")
        print(f"[INFO] Usando arquivos SPF2: {len(arquivos)} arquivos encontrados")
    
    if len(arquivos) == 0:
        print(f"[ERRO] Nenhum arquivo CSV ou SPF2 encontrado em {pasta_temporal}")
        return
    
    total_arquivos = len(arquivos)
    print(f"[INFO] Total de arquivos: {total_arquivos}")
    
    # Calcula o espaçamento necessário
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
        arquivo_saida = pasta_saida / nome_saida
        
        try:
            if processar_arquivo_thorlabs(arquivo, arquivo_saida):
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
        pasta_temporal = base_dir / "ThorLabs" / "Temporal"
        pasta_saida = base_dir / "ThorLabs" / "Temporal_Selecionado"
        
        selecionar_amostras_temporais(pasta_temporal, pasta_saida, num_amostras=100, 
                                     prefer_csv=args.prefer_csv)
    elif args.arquivo:
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
