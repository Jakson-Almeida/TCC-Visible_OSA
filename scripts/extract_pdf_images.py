#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair imagens de arquivos PDF e organizá-las em subpastas.
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

# Tenta importar Pillow como alternativa
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# Configurações
REFERENCE_FILES_DIR = "reference_files"
IMAGES_DIR = "imagens"
SUPPORTED_IMAGE_FORMATS = ['png', 'jpg', 'jpeg']


def extract_images_from_pdf(pdf_path: Path, output_dir: Path) -> int:
    """
    Extrai todas as imagens de um arquivo PDF e salva na pasta de saída.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        output_dir: Diretório onde as imagens serão salvas
        
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
        
        print(f"  Processando PDF: {pdf_path.name} ({len(pdf_document)} paginas)")
        
        # Itera sobre todas as páginas
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Obtém lista de imagens na página
            image_list = page.get_images(full=True)
            
            # Processa cada imagem
            for img_index, img in enumerate(image_list):
                try:
                    # Obtém o XREF da imagem
                    xref = img[0]
                    
                    # Extrai a imagem
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Gera nome do arquivo: pagina_X_imagem_Y.ext
                    image_filename = f"pagina_{page_num + 1:03d}_imagem_{img_index + 1:02d}.{image_ext}"
                    image_path = output_dir / image_filename
                    
                    # Salva a imagem
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    
                    total_images += 1
                    print(f"    [OK] Imagem extraida: {image_filename} ({len(image_bytes)} bytes)")
                    
                except Exception as e:
                    print(f"    [ERRO] Erro ao extrair imagem {img_index + 1} da pagina {page_num + 1}: {str(e)[:100]}")
                    continue
        
        pdf_document.close()
        
        if total_images == 0:
            print(f"  [INFO] Nenhuma imagem encontrada no PDF")
        else:
            print(f"  [OK] Total de {total_images} imagens extraidas")
        
        return total_images
        
    except Exception as e:
        print(f"  [ERRO] Erro ao processar PDF: {str(e)[:100]}")
        return 0


def process_all_pdfs():
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
        pdf_name = pdf_file.stem  # Nome sem extensão
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
            images_count = extract_images_from_pdf(pdf_file, subfolder)
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
    print("=" * 60)
    print("Extracao de Imagens de PDFs")
    print("=" * 60)
    
    if not PYMUPDF_AVAILABLE:
        print("\n[ERRO] PyMuPDF nao esta disponivel!")
        print("Instale com: pip install PyMuPDF")
        print("\nAlternativamente, voce pode usar pdf2image:")
        print("  pip install pdf2image")
        print("  (requer poppler instalado)")
        return
    
    process_all_pdfs()


if __name__ == "__main__":
    main()

