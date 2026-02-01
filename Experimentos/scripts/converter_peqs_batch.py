"""
Script para conversão em lote de espectros ThorLabs (CSV) para formato TXT (Visible_OSA).
Processa todas as pastas peqs_* mantendo a estrutura de diretórios (Azul, Verde, Vermelho).
Salva em ThorLabs/Intensidade/resultado/ para não sobreescrever arquivos existentes.
"""

from pathlib import Path
import sys


def ler_csv_thorlabs(arquivo_csv):
    """
    Lê arquivo CSV da ThorLabs e retorna comprimento de onda (nm) e intensidade.
    Os dados CSV têm wavelength em nanômetros (e.g. 3.165518799e+02 = 316.55 nm).
    """
    with open(arquivo_csv, "r", encoding="utf-8", errors="ignore") as f:
        linhas = f.readlines()
    
    # Encontra onde começa a seção [Data]
    inicio_dados = None
    for idx, linha in enumerate(linhas):
        if "[Data]" in linha:
            inicio_dados = idx + 1
            break
    
    if inicio_dados is None:
        raise ValueError(f"Seção [Data] não encontrada em {arquivo_csv}")
    
    # Lê os dados (formato: comprimento_onda_nm;intensidade)
    dados = []
    for linha in linhas[inicio_dados:]:
        linha = linha.strip()
        if linha and not linha.startswith("#"):
            partes = linha.split(";")
            if len(partes) >= 2:
                try:
                    wl_nm = float(partes[0])
                    intensity = float(partes[1])
                    dados.append((wl_nm, intensity))
                except ValueError:
                    continue
    
    if len(dados) == 0:
        raise ValueError(f"Nenhum dado encontrado em {arquivo_csv}")
    
    return dados


def converter_para_txt_visible_osa(dados_nm, arquivo_saida):
    """
    Converte dados para formato TXT do Visible_OSA.
    Formato: comprimento_onda_metros;intensidade (notação científica, 14 dígitos).
    
    Args:
        dados_nm: Lista de tuplas (wl_nm, intensity)
        arquivo_saida: Caminho do arquivo de saída
    """
    with open(arquivo_saida, "w", encoding="utf-8") as f:
        for wl_nm, intensity in dados_nm:
            wl_m = wl_nm * 1e-9  # Converte nm para metros
            f.write(f"{wl_m:.14e};{intensity:.14e}\n")


def processar_pasta_cor(pasta_cor_origem, pasta_cor_destino):
    """
    Processa todos os CSV de uma pasta de cor (Azul, Verde ou Vermelho).
    
    Args:
        pasta_cor_origem: Path da pasta com CSV (e.g. ThorLabs/Intensidade/peqs_1/Azul)
        pasta_cor_destino: Path da pasta de destino (e.g. resultado/peqs_1/Azul)
    
    Returns:
        (sucessos, falhas): Contadores de conversões bem-sucedidas e falhadas
    """
    pasta_cor_destino.mkdir(parents=True, exist_ok=True)
    
    arquivos_csv = sorted(pasta_cor_origem.glob("*.csv"))
    if not arquivos_csv:
        return 0, 0
    
    sucessos = 0
    falhas = 0
    
    for csv_file in arquivos_csv:
        # Mantém o nome base, só troca extensão para .txt
        txt_file = pasta_cor_destino / csv_file.with_suffix(".txt").name
        
        try:
            dados_nm = ler_csv_thorlabs(csv_file)
            converter_para_txt_visible_osa(dados_nm, txt_file)
            sucessos += 1
        except Exception as e:
            print(f"  [ERRO] {csv_file.name}: {str(e)[:80]}")
            falhas += 1
    
    return sucessos, falhas


def processar_pasta_peqs(pasta_peqs_origem, pasta_resultado):
    """
    Processa uma pasta peqs_x completa (Azul, Verde, Vermelho).
    
    Args:
        pasta_peqs_origem: Path da pasta peqs_x origem (e.g. ThorLabs/Intensidade/peqs_1)
        pasta_resultado: Path da pasta resultado (e.g. ThorLabs/Intensidade/resultado)
    
    Returns:
        (sucessos, falhas): Contadores totais
    """
    nome_peqs = pasta_peqs_origem.name
    pasta_peqs_destino = pasta_resultado / nome_peqs
    
    print(f"\n[INFO] Processando {nome_peqs}...")
    
    total_sucessos = 0
    total_falhas = 0
    
    cores = ["Azul", "Verde", "Vermelho"]
    for cor in cores:
        pasta_cor_origem = pasta_peqs_origem / cor
        if not pasta_cor_origem.exists() or not pasta_cor_origem.is_dir():
            print(f"  [AVISO] Pasta {cor} não encontrada em {nome_peqs}")
            continue
        
        pasta_cor_destino = pasta_peqs_destino / cor
        print(f"  Convertendo {cor}...")
        sucessos, falhas = processar_pasta_cor(pasta_cor_origem, pasta_cor_destino)
        total_sucessos += sucessos
        total_falhas += falhas
        
        if sucessos > 0:
            print(f"    ✓ {sucessos} arquivo(s) convertido(s)")
        if falhas > 0:
            print(f"    ✗ {falhas} falha(s)")
    
    return total_sucessos, total_falhas


def main():
    """Função principal: processa todas as pastas peqs_* encontradas."""
    # Caminhos base
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    pasta_thorlabs_intensidade = base_dir / "ThorLabs" / "Intensidade"
    pasta_resultado = pasta_thorlabs_intensidade / "resultado"
    
    if not pasta_thorlabs_intensidade.exists():
        print(f"[ERRO] Pasta não encontrada: {pasta_thorlabs_intensidade}")
        sys.exit(1)
    
    # Busca todas as pastas peqs_*
    pastas_peqs = sorted(pasta_thorlabs_intensidade.glob("peqs_*"))
    pastas_peqs = [p for p in pastas_peqs if p.is_dir()]
    
    if not pastas_peqs:
        print(f"[AVISO] Nenhuma pasta peqs_* encontrada em {pasta_thorlabs_intensidade}")
        print("Certifique-se de que as pastas existem (e.g. peqs_1, peqs_2, etc.)")
        sys.exit(0)
    
    print(f"[INFO] Encontradas {len(pastas_peqs)} pasta(s) peqs_*:")
    for p in pastas_peqs:
        print(f"  - {p.name}")
    
    print(f"\n[INFO] Convertendo para: {pasta_resultado}")
    
    # Processa cada pasta peqs_x
    total_sucessos_global = 0
    total_falhas_global = 0
    
    for pasta_peqs in pastas_peqs:
        sucessos, falhas = processar_pasta_peqs(pasta_peqs, pasta_resultado)
        total_sucessos_global += sucessos
        total_falhas_global += falhas
    
    # Resumo final
    print("\n" + "="*60)
    print(f"[OK] Conversão concluída!")
    print(f"  Total de arquivos convertidos: {total_sucessos_global}")
    if total_falhas_global > 0:
        print(f"  Total de falhas: {total_falhas_global}")
    print(f"  Arquivos salvos em: {pasta_resultado}")
    print("="*60)


if __name__ == "__main__":
    main()
