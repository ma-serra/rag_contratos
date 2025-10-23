"""
Módulo para processar documentos PDF usando Docling
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend


class DoclingProcessor:
    """Processa documentos PDF e extrai conteúdo estruturado"""

    def __init__(self):
        """Inicializa o processador Docling"""
        # Configurar opções para processamento de PDF
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False  # Desabilitar OCR por padrão (pode ser habilitado)
        pipeline_options.do_table_structure = True  # Extrair estrutura de tabelas

        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: pipeline_options,
            }
        )

    def process_pdf(self, pdf_path: str) -> Dict:
        """
        Processa um arquivo PDF e retorna o conteúdo estruturado

        Args:
            pdf_path: Caminho para o arquivo PDF

        Returns:
            Dict com o conteúdo estruturado do documento
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")

        # Converter documento
        result = self.converter.convert(pdf_path)

        # Extrair informações estruturadas
        doc_data = {
            "file_name": Path(pdf_path).name,
            "full_text": result.document.export_to_text(),
            "markdown": result.document.export_to_markdown(),
            "sections": self._extract_sections(result.document),
            "tables": self._extract_tables(result.document),
            "metadata": {
                "num_pages": len(result.document.pages) if hasattr(result.document, 'pages') else 0,
                "file_path": pdf_path
            }
        }

        return doc_data

    def _extract_sections(self, document) -> List[Dict]:
        """Extrai seções do documento"""
        sections = []

        # Iterar sobre elementos do documento
        for element in document.iterate_items():
            if hasattr(element, 'label'):
                section_data = {
                    "type": element.label if hasattr(element, 'label') else "unknown",
                    "text": element.export_to_text() if hasattr(element, 'export_to_text') else str(element),
                    "level": getattr(element, 'level', 0)
                }
                sections.append(section_data)

        return sections

    def _extract_tables(self, document) -> List[Dict]:
        """Extrai tabelas do documento"""
        tables = []

        for element in document.iterate_items():
            if hasattr(element, 'label') and 'table' in element.label.lower():
                table_data = {
                    "text": element.export_to_text() if hasattr(element, 'export_to_text') else str(element),
                    "markdown": element.export_to_markdown() if hasattr(element, 'export_to_markdown') else ""
                }
                tables.append(table_data)

        return tables

    def process_directory(self, directory_path: str) -> List[Dict]:
        """
        Processa todos os PDFs em um diretório

        Args:
            directory_path: Caminho para o diretório

        Returns:
            Lista com dados de todos os documentos processados
        """
        pdf_files = list(Path(directory_path).glob("*.pdf"))
        results = []

        for pdf_file in pdf_files:
            try:
                print(f"Processando: {pdf_file.name}")
                doc_data = self.process_pdf(str(pdf_file))
                results.append(doc_data)
            except Exception as e:
                print(f"Erro ao processar {pdf_file.name}: {e}")

        return results


def save_processed_data(doc_data: Dict, output_dir: str = "processed_data"):
    """
    Salva os dados processados em arquivos

    Args:
        doc_data: Dados do documento processado
        output_dir: Diretório de saída
    """
    os.makedirs(output_dir, exist_ok=True)

    base_name = Path(doc_data["file_name"]).stem

    # Salvar texto completo
    with open(f"{output_dir}/{base_name}_text.txt", "w", encoding="utf-8") as f:
        f.write(doc_data["full_text"])

    # Salvar markdown
    with open(f"{output_dir}/{base_name}_markdown.md", "w", encoding="utf-8") as f:
        f.write(doc_data["markdown"])

    print(f"Dados salvos em {output_dir}/")


if __name__ == "__main__":
    # Exemplo de uso
    processor = DoclingProcessor()

    # Processar um PDF (substituir pelo caminho real)
    # doc_data = processor.process_pdf("caminho/para/contrato.pdf")
    # save_processed_data(doc_data)

    print("DoclingProcessor inicializado. Use as funções para processar PDFs.")
