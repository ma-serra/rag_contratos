"""
Sistema de Chunking para Documentos Condominiais
Divide documentos longos em pedaços gerenciáveis para RAG
"""

from typing import List, Dict
from dataclasses import dataclass
import re


@dataclass
class DocumentChunk:
    """Representa um chunk de documento"""
    content: str
    metadata: Dict
    chunk_id: int
    total_chunks: int
    doc_type: str  # 'contrato', 'norma', 'ata', 'convencao'


class DocumentChunker:
    """Divide documentos em chunks inteligentes"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        """
        Args:
            chunk_size: Tamanho máximo de cada chunk em caracteres
            chunk_overlap: Sobreposição entre chunks para manter contexto
            separators: Lista de separadores hierárquicos
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or [
            "\n\n## ",      # Títulos nível 2
            "\n\n### ",     # Títulos nível 3
            "\n\n**",       # Negrito (seções)
            "\n\n",         # Parágrafos
            "\n",           # Linhas
            ". ",           # Sentenças
            " "             # Palavras
        ]

    def chunk_document(
        self,
        text: str,
        doc_type: str,
        metadata: Dict = None
    ) -> List[DocumentChunk]:
        """
        Divide documento em chunks preservando estrutura

        Args:
            text: Texto completo do documento
            doc_type: Tipo do documento (contrato, norma, ata, convencao)
            metadata: Metadados adicionais

        Returns:
            Lista de DocumentChunk
        """
        if not text or not text.strip():
            return []

        # Limpar texto
        text = self._clean_text(text)

        # Dividir em chunks
        chunks_text = self._split_text(text)

        # Criar objetos DocumentChunk
        chunks = []
        total = len(chunks_text)

        for i, chunk_text in enumerate(chunks_text):
            chunk_metadata = {
                **(metadata or {}),
                "position": i + 1,
                "total": total,
                "char_count": len(chunk_text)
            }

            chunk = DocumentChunk(
                content=chunk_text,
                metadata=chunk_metadata,
                chunk_id=i,
                total_chunks=total,
                doc_type=doc_type
            )
            chunks.append(chunk)

        return chunks

    def _clean_text(self, text: str) -> str:
        """Limpa e normaliza texto"""
        # Remover múltiplas quebras de linha
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remover espaços múltiplos
        text = re.sub(r' {2,}', ' ', text)

        # Remover tabs
        text = text.replace('\t', ' ')

        return text.strip()

    def _split_text(self, text: str) -> List[str]:
        """Divide texto usando separadores hierárquicos"""
        chunks = [text]

        # Tentar cada separador na hierarquia
        for separator in self.separators:
            new_chunks = []

            for chunk in chunks:
                if len(chunk) <= self.chunk_size:
                    new_chunks.append(chunk)
                else:
                    new_chunks.extend(
                        self._split_by_separator(chunk, separator)
                    )

            chunks = new_chunks

            # Se todos os chunks estão no tamanho ideal, parar
            if all(len(c) <= self.chunk_size for c in chunks):
                break

        # Aplicar overlap
        chunks = self._apply_overlap(chunks)

        return [c for c in chunks if c.strip()]

    def _split_by_separator(self, text: str, separator: str) -> List[str]:
        """Divide texto por um separador específico"""
        if separator not in text:
            return [text]

        parts = text.split(separator)
        chunks = []
        current_chunk = ""

        for i, part in enumerate(parts):
            # Recompor o separador exceto na primeira parte
            if i > 0:
                part = separator + part

            # Se adicionar esta parte ultrapassar o tamanho
            if len(current_chunk) + len(part) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = part
            else:
                current_chunk += part

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """Aplica sobreposição entre chunks para manter contexto"""
        if len(chunks) <= 1 or self.chunk_overlap == 0:
            return chunks

        overlapped_chunks = []

        for i, chunk in enumerate(chunks):
            if i == 0:
                overlapped_chunks.append(chunk)
                continue

            # Pegar final do chunk anterior
            prev_chunk = chunks[i - 1]
            overlap_text = prev_chunk[-self.chunk_overlap:] if len(prev_chunk) >= self.chunk_overlap else prev_chunk

            # Adicionar ao início do chunk atual
            overlapped_chunk = overlap_text + chunk
            overlapped_chunks.append(overlapped_chunk)

        return overlapped_chunks

    def chunk_by_sections(
        self,
        text: str,
        doc_type: str,
        section_pattern: str = r"(ARTIGO|Art\.|CAPÍTULO|TÍTULO|SEÇÃO)",
        metadata: Dict = None
    ) -> List[DocumentChunk]:
        """
        Divide documento por seções jurídicas específicas

        Args:
            text: Texto do documento
            doc_type: Tipo do documento
            section_pattern: Padrão regex para identificar seções
            metadata: Metadados adicionais

        Returns:
            Lista de chunks organizados por seção
        """
        # Encontrar todas as seções
        sections = re.split(f'({section_pattern})', text, flags=re.IGNORECASE)

        chunks = []
        current_section = ""
        section_header = ""

        for i, part in enumerate(sections):
            # Se é um cabeçalho de seção
            if re.match(section_pattern, part, re.IGNORECASE):
                # Salvar seção anterior
                if current_section:
                    chunk_metadata = {
                        **(metadata or {}),
                        "section": section_header,
                        "type": "section"
                    }
                    chunks.append(DocumentChunk(
                        content=current_section.strip(),
                        metadata=chunk_metadata,
                        chunk_id=len(chunks),
                        total_chunks=-1,  # Será atualizado depois
                        doc_type=doc_type
                    ))

                section_header = part
                current_section = part
            else:
                current_section += part

        # Adicionar última seção
        if current_section:
            chunk_metadata = {
                **(metadata or {}),
                "section": section_header,
                "type": "section"
            }
            chunks.append(DocumentChunk(
                content=current_section.strip(),
                metadata=chunk_metadata,
                chunk_id=len(chunks),
                total_chunks=-1,
                doc_type=doc_type
            ))

        # Atualizar total_chunks
        total = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total

        return chunks


def chunk_contrato(text: str, metadata: Dict = None) -> List[DocumentChunk]:
    """Helper para chunkar contratos"""
    chunker = DocumentChunker(chunk_size=1500, chunk_overlap=200)
    return chunker.chunk_by_sections(
        text,
        doc_type="contrato",
        section_pattern=r"(CLÁUSULA|Cláusula|ARTIGO|Art\.)",
        metadata=metadata
    )


def chunk_norma(text: str, metadata: Dict = None) -> List[DocumentChunk]:
    """Helper para chunkar normas/regimentos"""
    chunker = DocumentChunker(chunk_size=1200, chunk_overlap=150)
    return chunker.chunk_by_sections(
        text,
        doc_type="norma",
        section_pattern=r"(TÍTULO|CAPÍTULO|SEÇÃO|ARTIGO|Art\.)",
        metadata=metadata
    )


def chunk_ata(text: str, metadata: Dict = None) -> List[DocumentChunk]:
    """Helper para chunkar atas de assembleia"""
    chunker = DocumentChunker(chunk_size=1000, chunk_overlap=100)
    return chunker.chunk_document(
        text,
        doc_type="ata",
        metadata=metadata
    )


def chunk_convencao(text: str, metadata: Dict = None) -> List[DocumentChunk]:
    """Helper para chunkar convenções de condomínio"""
    chunker = DocumentChunker(chunk_size=1500, chunk_overlap=200)
    return chunker.chunk_by_sections(
        text,
        doc_type="convencao",
        section_pattern=r"(TÍTULO|CAPÍTULO|SEÇÃO|Art\.|ARTIGO)",
        metadata=metadata
    )
