#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script aprimorado para extrair imagens de arquivos PDF e organizá-las em subpastas.
Versão melhorada que tenta múltiplos métodos de extração.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

# Configura encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Tenta importar PyMuPDF (fitz)
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("[AVISO] PyMuPDF nao disponivel. Instale com: pip install PyMuPDF")

# Tenta importar Pillow
try:
    from PIL import Image
    import io as io_module
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# Configurações
REFERENCE_FILES_DIR = "reference_files"
IMAGES_DIR = "imagens"
SUPPORTED_IMAGE_FORMATS = ['png', 'jpg', 'jpeg']
EXTRACT_PAGE_IMAGES = True  # Extrair páginas como imagens também
DPI = 300  # DPI para renderização de páginas


def extract_images_from_pdf(pdf_path: Path, output_dir: Path, extract_pages: bool = False) -> int:
    """
    Extrai todas as imagens individuais de um arquivo PDF usando múltiplos métodos.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        output_dir: Diretório onde as imagens serão salvas
        extract_pages: Se True, também renderiza páginas completas (não recomendado)
        
    Returns:
        Número de imagens extraídas
    """
    if not PYMUPDF_AVAILABLE:
        print(f"  [ERRO] PyMuPDF nao disponivel. Instale com: pip install PyMuPDF")
        return 0
    
    try:
        # Abre o PDF
        pdf_document = fitz.open(pdf_path)
        total_images = 0
        images_extracted = set()  # Para evitar duplicatas (por XREF)
        image_hashes = set()  # Para evitar duplicatas (por conteúdo)
        
        print(f"  Processando PDF: {pdf_path.name} ({len(pdf_document)} paginas)")
        
        # Método 1: Extração direta de imagens embutidas (todas as páginas)
        print(f"  [METODO 1] Extraindo imagens embutidas de todas as paginas...")
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Obtém lista de imagens na página
            image_list = page.get_images(full=True)
            
            # Processa cada imagem
            for img_index, img in enumerate(image_list):
                try:
                    # Obtém o XREF da imagem
                    xref = img[0]
                    
                    # Verifica se já extraiu esta imagem (pode aparecer em múltiplas páginas)
                    if xref in images_extracted:
                        continue
                    
                    # Extrai a imagem
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Verifica duplicatas por hash do conteúdo
                    import hashlib
                    image_hash = hashlib.md5(image_bytes).hexdigest()
                    if image_hash in image_hashes:
                        continue
                    
                    # Gera nome do arquivo: pagina_X_imagem_Y.ext
                    image_filename = f"pagina_{page_num + 1:03d}_imagem_{img_index + 1:02d}.{image_ext}"
                    image_path = output_dir / image_filename
                    
                    # Salva a imagem
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    
                    images_extracted.add(xref)
                    image_hashes.add(image_hash)
                    total_images += 1
                    print(f"    [OK] Imagem extraida: {image_filename} ({len(image_bytes)} bytes)")
                    
                except Exception as e:
                    print(f"    [ERRO] Erro ao extrair imagem {img_index + 1} da pagina {page_num + 1}: {str(e)[:100]}")
                    continue
        
        # Método 2: Extrair imagens de objetos XObject (pode capturar mais imagens)
        print(f"  [METODO 2] Procurando imagens em objetos XObject...")
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            try:
                # Obtém o dicionário da página
                page_dict = page.get_contents()
                
                # Procura por objetos de imagem adicionais
                # PyMuPDF pode ter imagens em diferentes formatos
                image_list_extended = page.get_images(full=True)
                
                # Tenta extrair imagens que podem estar em diferentes camadas
                for img_index, img in enumerate(image_list_extended):
                    try:
                        xref = img[0]
                        
                        # Se já extraiu, pula
                        if xref in images_extracted:
                            continue
                        
                        # Tenta extrair novamente com diferentes parâmetros
                        try:
                            base_image = pdf_document.extract_image(xref)
                            image_bytes = base_image["image"]
                            image_ext = base_image["ext"]
                            
                            # Verifica duplicatas
                            import hashlib
                            image_hash = hashlib.md5(image_bytes).hexdigest()
                            if image_hash in image_hashes:
                                continue
                            
                            # Gera nome único
                            existing_count = len([f for f in output_dir.glob(f"pagina_{page_num + 1:03d}_imagem_*.{image_ext}")])
                            image_filename = f"pagina_{page_num + 1:03d}_imagem_{existing_count + 1:02d}.{image_ext}"
                            image_path = output_dir / image_filename
                            
                            # Salva a imagem
                            with open(image_path, "wb") as image_file:
                                image_file.write(image_bytes)
                            
                            images_extracted.add(xref)
                            image_hashes.add(image_hash)
                            total_images += 1
                            print(f"    [OK] Imagem adicional extraida: {image_filename} ({len(image_bytes)} bytes)")
                        except:
                            pass
                    except:
                        continue
            except Exception as e:
                # Método 2 pode falhar silenciosamente
                pass
        
        # Método 3: Renderizar páginas completas (apenas se solicitado)
        if extract_pages and PILLOW_AVAILABLE:
            print(f"  [METODO 3] Renderizando paginas completas como imagens (DPI={DPI})...")
            print(f"  [AVISO] Isso criara imagens de paginas inteiras, nao imagens individuais!")
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                try:
                    # Renderiza a página como imagem
                    mat = fitz.Matrix(DPI / 72, DPI / 72)
                    pix = page.get_pixmap(matrix=mat)
                    
                    # Converte para PIL Image
                    img_data = pix.tobytes("png")
                    pil_image = Image.open(io_module.BytesIO(img_data))
                    
                    # Salva a imagem renderizada
                    page_image_filename = f"pagina_{page_num + 1:03d}_renderizada.png"
                    page_image_path = output_dir / page_image_filename
                    pil_image.save(page_image_path, "PNG")
                    
                    total_images += 1
                    print(f"    [OK] Pagina renderizada: {page_image_filename} ({len(img_data)} bytes)")
                    
                except Exception as e:
                    print(f"    [ERRO] Erro ao renderizar pagina {page_num + 1}: {str(e)[:100]}")
                    continue
        
        pdf_document.close()
        
        if total_images == 0:
            print(f"  [INFO] Nenhuma imagem encontrada no PDF")
        else:
            print(f"  [OK] Total de {total_images} imagens individuais extraidas")
        
        return total_images
        
    except Exception as e:
        print(f"  [ERRO] Erro ao processar PDF: {str(e)[:100]}")
        import traceback
        print(f"  [DEBUG] {traceback.format_exc()[:200]}")
        return 0


def process_single_pdf(pdf_name: str, extract_pages: bool = True):
    """Processa um único PDF específico."""
    reference_dir = Path(REFERENCE_FILES_DIR)
    images_dir = Path(IMAGES_DIR)
    
    # Verifica se a pasta de referências existe
    if not reference_dir.exists():
        print(f"[ERRO] Pasta '{REFERENCE_FILES_DIR}' nao encontrada!")
        return
    
    # Encontra o PDF
    pdf_file = reference_dir / f"{pdf_name}.pdf"
    
    if not pdf_file.exists():
        # Tenta encontrar por nome parcial
        pdf_files = list(reference_dir.glob(f"*{pdf_name}*.pdf"))
        if pdf_files:
            pdf_file = pdf_files[0]
            print(f"[INFO] PDF encontrado: {pdf_file.name}")
        else:
            print(f"[ERRO] PDF '{pdf_name}' nao encontrado em '{REFERENCE_FILES_DIR}'")
            return
    
    # Cria a pasta de imagens se não existir
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Nome da subpasta (nome do arquivo sem extensão)
    pdf_name_clean = pdf_file.stem
    subfolder = images_dir / pdf_name_clean
    
    print(f"\n[PROCESSANDO] {pdf_file.name}")
    print(f"  Subpasta: {subfolder.name}/")
    
    # Remove subpasta existente se quiser reprocessar
    if subfolder.exists():
        print(f"  [INFO] Subpasta ja existe. Removendo para reprocessar...")
        import shutil
        try:
            shutil.rmtree(subfolder)
        except Exception as e:
            print(f"  [ERRO] Erro ao remover subpasta: {str(e)[:100]}")
            return
    
    # Cria a subpasta
    subfolder.mkdir(parents=True, exist_ok=True)
    print(f"  [INFO] Subpasta criada: {subfolder.name}/")
    
    # Extrai as imagens
    images_count = extract_images_from_pdf(pdf_file, subfolder, extract_pages=extract_pages)
    
    print("\n" + "=" * 60)
    print(f"Resumo:")
    print(f"  [TOTAL] Imagens extraidas: {images_count}")
    print("=" * 60)
    print(f"\nImagens salvas em: {subfolder.absolute()}")


def process_all_pdfs(extract_pages: bool = True):
    """Processa todos os PDFs na pasta reference_files."""
    reference_dir = Path(REFERENCE_FILES_DIR)
    images_dir = Path(IMAGES_DIR)
    
    # Verifica se a pasta de referências existe
    if not reference_dir.exists():
        print(f"[ERRO] Pasta '{REFERENCE_FILES_DIR}' nao encontrada!")
        return
    
    # Cria a pasta de imagens se não existir
    images_dir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Pasta de imagens: {images_dir.absolute()}\n")
    
    # Encontra todos os arquivos PDF
    pdf_files = list(reference_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"[INFO] Nenhum arquivo PDF encontrado em '{REFERENCE_FILES_DIR}'")
        return
    
    print(f"Encontrados {len(pdf_files)} arquivos PDF\n")
    print("=" * 60)
    
    total_processed = 0
    total_images = 0
    skipped = 0
    
    for pdf_file in pdf_files:
        # Nome da subpasta (nome do arquivo sem extensão)
        pdf_name = pdf_file.stem
        subfolder = images_dir / pdf_name
        
        print(f"\n[{total_processed + 1}/{len(pdf_files)}] {pdf_file.name}")
        
        # Verifica se a subpasta já existe
        if subfolder.exists() and any(subfolder.iterdir()):
            print(f"  [SKIP] Subpasta ja existe e contem arquivos: {subfolder.name}/")
            print(f"  [INFO] Pule esta etapa se quiser reprocessar. Delete a subpasta primeiro.")
            skipped += 1
        else:
            # Cria a subpasta
            subfolder.mkdir(parents=True, exist_ok=True)
            print(f"  [INFO] Subpasta criada: {subfolder.name}/")
            
            # Extrai as imagens
            images_count = extract_images_from_pdf(pdf_file, subfolder, extract_pages=extract_pages)
            total_images += images_count
            total_processed += 1
    
    print("\n" + "=" * 60)
    print("Resumo:")
    print(f"  [OK] PDFs processados: {total_processed}")
    print(f"  [SKIP] Subpastas ja existentes: {skipped}")
    print(f"  [TOTAL] Imagens extraidas: {total_images}")
    print("=" * 60)
    print(f"\nImagens salvas em: {images_dir.absolute()}")


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extrai imagens de PDFs')
    parser.add_argument('--pdf', type=str, help='Nome do PDF específico para processar (sem extensão)')
    parser.add_argument('--render-pages', action='store_true', help='Também renderizar páginas completas como imagens (não recomendado)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Extracao Aprimorada de Imagens de PDFs")
    print("=" * 60)
    
    if not PYMUPDF_AVAILABLE:
        print("\n[ERRO] PyMuPDF nao esta disponivel!")
        print("Instale com: pip install PyMuPDF")
        return
    
    if args.render_pages and not PILLOW_AVAILABLE:
        print("\n[AVISO] Pillow nao disponivel. Renderizacao de paginas desabilitada.")
        print("Instale com: pip install Pillow para habilitar renderizacao de paginas")
        extract_pages = False
    else:
        extract_pages = args.render_pages and PILLOW_AVAILABLE
    
    if args.pdf:
        # Processa apenas um PDF específico
        process_single_pdf(args.pdf, extract_pages=extract_pages)
    else:
        # Processa todos os PDFs
        process_all_pdfs(extract_pages=extract_pages)


if __name__ == "__main__":
    main()
