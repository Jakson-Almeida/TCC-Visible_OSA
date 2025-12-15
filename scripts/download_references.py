#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair referências do arquivo LaTeX e baixar PDFs disponíveis.
"""

import re
import os
import sys
import requests
from urllib.parse import urlparse, unquote, urljoin
from pathlib import Path
import time
from typing import List, Dict, Optional

# Configura encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configurações
LATEX_FILE = "TCC_Documento/modelo.tex"
OUTPUT_DIR = "reference_files"
TIMEOUT = 30
DELAY_BETWEEN_REQUESTS = 1  # Delay em segundos entre requisições

# Headers para simular um navegador
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/pdf,application/octet-stream,*/*',
    'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
}

# Headers alternativos para sites que bloqueiam
HEADERS_ALT = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.google.com/',
}


def extract_bibliography_entries(latex_file: str) -> List[Dict[str, str]]:
    """Extrai todas as entradas bibliográficas do arquivo LaTeX."""
    with open(latex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontra a seção de bibliografia
    bib_start = content.find(r'\begin{thebibliography}')
    bib_end = content.find(r'\end{thebibliography}')
    
    if bib_start == -1 or bib_end == -1:
        print("Erro: Seção de bibliografia não encontrada!")
        return []
    
    bib_content = content[bib_start:bib_end]
    
    # Regex para encontrar \bibitem{key} ... até o próximo \bibitem ou fim
    bib_pattern = r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem|$)'
    matches = re.finditer(bib_pattern, bib_content, re.DOTALL)
    
    entries = []
    for match in matches:
        key = match.group(1)
        entry_text = match.group(2)
        
        # Extrai URLs
        url_pattern = r'https?://[^\s}]+|http://[^\s}]+'
        urls = re.findall(url_pattern, entry_text)
        
        # Extrai DOIs - múltiplos padrões
        dois = []
        # Padrão 1: DOI: 10.xxx/...
        doi_pattern1 = r'DOI:\s*10\.\d+/[^\s,}]+'
        for doi_match in re.finditer(doi_pattern1, entry_text, re.IGNORECASE):
            doi = doi_match.group(0).replace('DOI:', '').replace('DOI:', '').strip()
            # Remove escapes LaTeX do DOI
            doi = doi.replace('\\_', '_').replace('\\%', '%').replace('\\&', '&')
            doi = doi.rstrip('.,;)}')
            dois.append(doi)
        
        # Padrão 2: doi.org/10.xxx/...
        doi_pattern2 = r'doi\.org/(10\.\d+/[^\s,}]+)'
        for doi_match in re.finditer(doi_pattern2, entry_text, re.IGNORECASE):
            doi = doi_match.group(1)
            doi = doi.replace('\\_', '_').replace('\\%', '%').replace('\\&', '&')
            doi = doi.rstrip('.,;)}')
            dois.append(doi)
        
        # Remove duplicatas mantendo ordem
        dois = list(dict.fromkeys(dois))
        
        # Limpa URLs (remove caracteres LaTeX)
        cleaned_urls = []
        for url in urls:
            # Remove escapes LaTeX comuns (importante fazer antes de outras operações)
            # Primeiro remove escapes de underscore que podem estar no meio da URL
            url = url.replace('\\_', '_').replace('\\%', '%').replace('\\&', '&')
            # Remove caracteres de formatação LaTeX no final
            url = url.rstrip('.,;)}')
            # Remove espaços e quebras de linha
            url = url.strip().replace('\n', '').replace('\r', '')
            # Remove ponto final se houver (comum em LaTeX)
            if url.endswith('.'):
                url = url[:-1]
            # Decodifica URLs codificadas
            try:
                url = unquote(url)
            except:
                pass
            if url:
                cleaned_urls.append(url)
        
        if cleaned_urls or dois:
            entries.append({
                'key': key,
                'text': entry_text.strip(),
                'urls': cleaned_urls,
                'dois': dois
            })
    
    return entries


def sanitize_filename(filename: str) -> str:
    """Sanitiza o nome do arquivo para ser válido no sistema de arquivos."""
    # Remove caracteres inválidos
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove espaços múltiplos
    filename = re.sub(r'\s+', '_', filename)
    # Limita tamanho
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def is_pdf_url(url: str) -> bool:
    """Verifica se a URL aponta diretamente para um PDF."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    return path.endswith('.pdf') or 'pdf' in parsed.query.lower()


def try_download_pdf(url: str, output_path: Path, entry_key: str, use_alt_headers: bool = False) -> bool:
    """Tenta baixar um PDF da URL fornecida."""
    headers_to_use = HEADERS_ALT if use_alt_headers else HEADERS
    
    try:
        if use_alt_headers:
            print(f"  Tentando baixar (headers alternativos): {url[:80]}...")
        else:
            print(f"  Tentando baixar: {url[:80]}...")
        
        # Usa sessão para manter cookies
        session = requests.Session()
        session.headers.update(headers_to_use)
        
        response = session.get(url, timeout=TIMEOUT, stream=True, allow_redirects=True)
        
        # Se recebeu 403, tenta com headers alternativos
        if response.status_code == 403 and not use_alt_headers:
            session.close()
            print(f"  [INFO] Recebeu 403, tentando com headers alternativos...")
            return try_download_pdf(url, output_path, entry_key, use_alt_headers=True)
        
        # Se recebeu 403 mesmo com headers alternativos, pode ser bloqueio permanente
        if response.status_code == 403:
            session.close()
            print(f"  [ERRO] Bloqueado pelo servidor (403) mesmo com headers alternativos")
            return False
        
        response.raise_for_status()
        
        # Verifica Content-Type antes de baixar
        content_type = response.headers.get('Content-Type', '').lower()
        is_pdf_by_url = is_pdf_url(url) or is_pdf_url(response.url)
        
        # Se a URL termina em .pdf, tenta baixar mesmo que Content-Type não indique PDF
        # (alguns servidores retornam Content-Type incorreto)
        should_download = False
        if 'pdf' in content_type:
            should_download = True
        elif is_pdf_by_url or url.lower().endswith('.pdf'):
            should_download = True
            if 'pdf' not in content_type:
                print(f"  [INFO] URL indica PDF mas Content-Type e {content_type}, tentando baixar mesmo assim...")
        
        if not should_download:
            session.close()
            print(f"  [ERRO] URL nao retorna PDF (Content-Type: {content_type})")
            return False
        
        # Remove arquivo existente se houver
        if output_path.exists():
            try:
                output_path.unlink()
            except:
                pass
        
        # Baixa o arquivo
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        session.close()
        
        # Verifica se o arquivo baixado é realmente um PDF
        if output_path.exists() and output_path.stat().st_size > 0:
            # Aguarda um pouco para garantir que o arquivo foi escrito completamente
            time.sleep(0.1)
            
            with open(output_path, 'rb') as f:
                header = f.read(4)
                if header == b'%PDF':
                    print(f"  [OK] PDF baixado com sucesso: {output_path.name} ({output_path.stat().st_size} bytes)")
                    return True
                else:
                    # Verifica se pode ser HTML que redireciona para PDF
                    f.seek(0)
                    content_start = f.read(512).decode('utf-8', errors='ignore')
                    
                    # Tenta encontrar URL de PDF no HTML
                    pdf_url_match = re.search(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', content_start, re.IGNORECASE)
                    if pdf_url_match:
                        pdf_url = pdf_url_match.group(1)
                        # Se é URL relativa, torna absoluta
                        if not pdf_url.startswith('http'):
                            pdf_url = urljoin(url, pdf_url)
                        print(f"  [INFO] Encontrado link para PDF no HTML, tentando: {pdf_url[:80]}...")
                        # Tenta baixar o PDF encontrado
                        if try_download_pdf(pdf_url, output_path, entry_key, use_alt_headers=False):
                            return True
                    
                    print(f"  [ERRO] Arquivo baixado nao e PDF valido (header: {header[:20]})")
                    # Se a URL termina em .pdf mas retornou HTML, pode ser bloqueio
                    if is_pdf_url(url) and 'html' in response.headers.get('Content-Type', '').lower():
                        print(f"  [INFO] URL termina em .pdf mas retornou HTML - possivel bloqueio do servidor")
                    try:
                        output_path.unlink()
                    except:
                        pass
                    return False
        else:
            print(f"  [ERRO] Arquivo baixado esta vazio ou nao existe")
            if output_path.exists():
                try:
                    output_path.unlink()
                except:
                    pass
            return False
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403 and not use_alt_headers:
            # Tenta novamente com headers alternativos
            return try_download_pdf(url, output_path, entry_key, use_alt_headers=True)
        print(f"  [ERRO] HTTP {e.response.status_code}: {str(e)[:100]}")
        if output_path.exists():
            try:
                output_path.unlink()
            except:
                pass
        return False
    except requests.exceptions.RequestException as e:
        print(f"  [ERRO] Erro ao baixar: {str(e)[:100]}")
        if output_path.exists():
            try:
                output_path.unlink()
            except:
                pass
        return False
    except Exception as e:
        print(f"  [ERRO] Erro inesperado: {str(e)[:100]}")
        if output_path.exists():
            try:
                output_path.unlink()
            except:
                pass
        return False


def try_download_from_doi(doi: str, output_path: Path, entry_key: str) -> bool:
    """Tenta baixar PDF usando DOI através de serviços públicos."""
    try:
        # Limpa o DOI de caracteres extras e escapes LaTeX
        doi = doi.strip()
        doi = doi.replace('\\_', '_').replace('\\%', '%')
        
        if not doi.startswith('10.'):
            # Se não começa com 10., pode estar em formato URL
            if 'doi.org/' in doi:
                doi = doi.split('doi.org/')[-1]
            elif 'DOI:' in doi.upper():
                doi = doi.split('DOI:')[-1].strip()
        
        # Remove caracteres extras no final
        doi = doi.rstrip('.,;)}')
        
        # Tenta resolver DOI para URL
        doi_url = f"https://doi.org/{doi}"
        print(f"  Tentando resolver DOI: {doi_url}")
        
        response = requests.get(doi_url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        resolved_url = response.url
        
        print(f"  DOI resolvido para: {resolved_url[:80]}...")
        
        # Tenta algumas estratégias comuns para obter PDFs de publishers
        pdf_urls_to_try = []
        
        # Springer
        if 'springer.com' in resolved_url or 'link.springer.com' in resolved_url:
            # Tenta adicionar /pdf no final
            if '/article/' in resolved_url:
                pdf_urls_to_try.append(resolved_url.replace('/article/', '/pdf/'))
            if '/chapter/' in resolved_url:
                pdf_urls_to_try.append(resolved_url.replace('/chapter/', '/pdf/'))
            if '/book/' in resolved_url:
                pdf_urls_to_try.append(resolved_url.replace('/book/', '/pdf/'))
        
        # IEEE
        if 'ieee.org' in resolved_url:
            pdf_urls_to_try.append(resolved_url.replace('/abstract/', '/pdf/'))
            pdf_urls_to_try.append(resolved_url.replace('/document/', '/pdf/'))
        
        # MDPI
        if 'mdpi.com' in resolved_url:
            pdf_urls_to_try.append(resolved_url.replace('/html/', '/pdf/'))
        
        # SPIE (Optical Engineering)
        if 'spiedigitallibrary.org' in resolved_url:
            pdf_urls_to_try.append(resolved_url.replace('/article/', '/pdf/'))
        
        # Tenta a URL resolvida primeiro
        pdf_urls_to_try.insert(0, resolved_url)
        
        for pdf_url in pdf_urls_to_try:
            if try_download_pdf(pdf_url, output_path, entry_key):
                return True
        
        return False
        
    except Exception as e:
        print(f"  [ERRO] Erro ao processar DOI: {str(e)[:100]}")
        return False


def is_valid_pdf(file_path: Path) -> bool:
    """Verifica se um arquivo é um PDF válido."""
    if not file_path.exists():
        return False
    try:
        if file_path.stat().st_size == 0:
            return False
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except Exception:
        return False


def download_reference_pdfs(entries: List[Dict[str, str]], output_dir: Path):
    """Baixa PDFs para todas as referências que têm URLs ou DOIs."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded = 0
    failed = 0
    skipped = 0
    
    print(f"\nProcessando {len(entries)} referências...\n")
    
    # Verifica arquivos já existentes antes de começar
    existing_files = {}
    for entry in entries:
        filename = f"{entry['key']}.pdf"
        output_path = output_dir / filename
        if output_path.exists() and is_valid_pdf(output_path):
            existing_files[entry['key']] = output_path
    
    if existing_files:
        print(f"[INFO] Encontrados {len(existing_files)} PDFs validos ja existentes na pasta.\n")
    
    for i, entry in enumerate(entries, 1):
        print(f"\n[{i}/{len(entries)}] Referência: {entry['key']}")
        
        # Gera nome do arquivo baseado na chave
        filename = f"{entry['key']}.pdf"
        output_path = output_dir / filename
        
        # Verifica se já existe e é válido
        if output_path.exists() and is_valid_pdf(output_path):
            print(f"  [SKIP] Arquivo ja existe e e valido: {filename} ({output_path.stat().st_size} bytes)")
            skipped += 1
            continue
        elif output_path.exists():
            print(f"  [INFO] Arquivo existe mas nao e PDF valido, tentando baixar novamente...")
            try:
                output_path.unlink()
            except Exception as e:
                print(f"  [AVISO] Nao foi possivel remover arquivo invalido: {str(e)[:50]}")
        
        success = False
        
        # Tenta baixar de URLs diretas primeiro
        for url in entry['urls']:
            # Tenta URL direta primeiro
            if is_pdf_url(url):
                if try_download_pdf(url, output_path, entry['key']):
                    # Verifica novamente após o download
                    if is_valid_pdf(output_path):
                        success = True
                        break
                continue
            
            # Para URLs que não são PDFs diretos, tenta variantes
            parsed = urlparse(url)
            pdf_variants = []
            
            # PMC - tenta adicionar /pdf
            if 'pmc.ncbi.nlm.nih.gov' in url or 'ncbi.nlm.nih.gov/pmc' in url:
                if '/articles/' in url:
                    article_id = url.split('/articles/')[-1].rstrip('/').rstrip('PMC')
                    if article_id.startswith('PMC'):
                        article_id = article_id[3:]
                    pdf_variants.append(f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{article_id}/pdf/")
                    pdf_variants.append(f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article_id}/pdf/")
            
            # ResearchGate - tenta adicionar /pdf
            if 'researchgate.net' in url and '/publication/' in url:
                pdf_variants.append(url.rstrip('/') + '/pdf')
            
            # MDPI
            if 'mdpi.com' in url:
                pdf_variants.append(url.replace('/html/', '/pdf/'))
            
            # Tenta variantes
            for variant in pdf_variants:
                if try_download_pdf(variant, output_path, entry['key']):
                    # Verifica novamente após o download
                    if is_valid_pdf(output_path):
                        success = True
                        break
            
            if success:
                break
        
        # Se não conseguiu pelas URLs, tenta DOIs
        if not success:
            for doi in entry['dois']:
                if try_download_from_doi(doi, output_path, entry['key']):
                    # Verifica novamente após o download
                    if is_valid_pdf(output_path):
                        success = True
                        break
        
        # Conta o resultado final
        if success and is_valid_pdf(output_path):
            downloaded += 1
            print(f"  [OK] Referencia processada com sucesso")
        else:
            print(f"  [ERRO] Nao foi possivel baixar PDF para esta referencia")
            failed += 1
            # Remove arquivo inválido se existir
            if output_path.exists() and not is_valid_pdf(output_path):
                try:
                    output_path.unlink()
                except:
                    pass
        
        # Delay entre requisições para não sobrecarregar servidores
        if i < len(entries):
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Verifica quantos arquivos realmente existem na pasta
    actual_files = [f for f in output_dir.glob('*.pdf') if is_valid_pdf(f)]
    
    print(f"\n{'='*60}")
    print(f"Resumo:")
    print(f"  [OK] Baixados nesta execucao: {downloaded}")
    print(f"  [SKIP] Ja existiam: {skipped}")
    print(f"  [ERRO] Falhas: {failed}")
    print(f"  [TOTAL] Arquivos PDF validos na pasta: {len(actual_files)}")
    if len(actual_files) != (downloaded + skipped):
        print(f"  [AVISO] Discrepancia detectada! Verifique os arquivos na pasta.")
    print(f"{'='*60}\n")


def main():
    """Função principal."""
    print("="*60)
    print("Download de Referências - PDFs")
    print("="*60)
    
    # Verifica se o arquivo LaTeX existe
    latex_path = Path(LATEX_FILE)
    if not latex_path.exists():
        print(f"Erro: Arquivo não encontrado: {LATEX_FILE}")
        return
    
    # Extrai referências
    print(f"\nLendo arquivo: {LATEX_FILE}")
    entries = extract_bibliography_entries(str(latex_path))
    
    if not entries:
        print("Nenhuma referência encontrada!")
        return
    
    print(f"Encontradas {len(entries)} referências com URLs/DOIs")
    
    # Cria diretório de saída
    output_dir = Path(OUTPUT_DIR)
    
    # Baixa PDFs
    download_reference_pdfs(entries, output_dir)
    
    print(f"PDFs salvos em: {output_dir.absolute()}")


if __name__ == "__main__":
    main()

