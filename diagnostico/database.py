"""
Sistema de Gerenciamento de ChromaDB para Documentos Condominiais
Armazena e recupera chunks com embeddings
"""

import chromadb
from typing import List, Dict, Optional
from dataclasses import asdict
import os
from .chunking import DocumentChunk


class CondominioDatabase:
    """Gerencia coleções ChromaDB para documentos condominiais"""

    def __init__(self, persist_directory: str = "./chromadb_data"):
        """
        Inicializa banco de dados ChromaDB

        Args:
            persist_directory: Diretório para persistir dados
        """
        self.persist_directory = persist_directory

        # Criar diretório se não existe
        os.makedirs(persist_directory, exist_ok=True)

        # Inicializar ChromaDB (versão simples - não persistente por padrão)
        self.client = chromadb.Client()

        # Coleções por tipo de documento
        self.collections = {}
        self._init_collections()

    def _init_collections(self):
        """Inicializa ou carrega coleções existentes"""
        collection_names = [
            "contratos",
            "normas",
            "atas",
            "convencoes"
        ]

        for name in collection_names:
            try:
                self.collections[name] = self.client.get_or_create_collection(
                    name=name,
                    metadata={"description": f"Coleção de {name} condominiais"}
                )
                print(f"✓ Coleção '{name}' pronta")
            except Exception as e:
                print(f"✗ Erro ao criar coleção '{name}': {e}")

    def add_chunks(
        self,
        chunks: List[DocumentChunk],
        condominio_id: str,
        document_name: str
    ):
        """
        Adiciona chunks ao banco de dados

        Args:
            chunks: Lista de DocumentChunk
            condominio_id: ID do condomínio
            document_name: Nome do documento
        """
        if not chunks:
            print("Nenhum chunk para adicionar")
            return

        # Determinar coleção baseada no tipo do primeiro chunk
        doc_type = chunks[0].doc_type
        collection_map = {
            "contrato": "contratos",
            "norma": "normas",
            "ata": "atas",
            "convencao": "convencoes"
        }

        collection_name = collection_map.get(doc_type)
        if not collection_name:
            print(f"Tipo de documento inválido: {doc_type}")
            return

        collection = self.collections[collection_name]

        # Preparar dados para inserção
        documents = []
        metadatas = []
        ids = []

        for chunk in chunks:
            # ID único: condominio_documento_chunk
            chunk_id = f"{condominio_id}_{document_name}_{chunk.chunk_id}"

            # Metadados completos
            metadata = {
                "condominio_id": condominio_id,
                "document_name": document_name,
                "doc_type": doc_type,
                "chunk_id": chunk.chunk_id,
                "total_chunks": chunk.total_chunks,
                **chunk.metadata
            }

            documents.append(chunk.content)
            metadatas.append(metadata)
            ids.append(chunk_id)

        # Adicionar ao ChromaDB (com embeddings automáticos)
        try:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"✓ {len(chunks)} chunks adicionados à coleção '{collection_name}'")
        except Exception as e:
            print(f"✗ Erro ao adicionar chunks: {e}")

    def search(
        self,
        query: str,
        doc_types: List[str] = None,
        condominio_id: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Busca semântica em documentos

        Args:
            query: Texto de consulta
            doc_types: Lista de tipos de documentos (contratos, normas, etc)
            condominio_id: Filtrar por condomínio específico
            n_results: Número de resultados

        Returns:
            Lista de resultados com conteúdo e metadados
        """
        if doc_types is None:
            doc_types = ["contratos", "normas", "atas", "convencoes"]

        all_results = []

        for doc_type in doc_types:
            if doc_type not in self.collections:
                continue

            collection = self.collections[doc_type]

            # Construir filtro
            where = {}
            if condominio_id:
                where["condominio_id"] = condominio_id

            try:
                # Buscar com embeddings
                results = collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=where if where else None
                )

                # Processar resultados
                if results and results['documents']:
                    for i in range(len(results['documents'][0])):
                        all_results.append({
                            'content': results['documents'][0][i],
                            'metadata': results['metadatas'][0][i],
                            'distance': results['distances'][0][i] if 'distances' in results else None,
                            'doc_type': doc_type
                        })

            except Exception as e:
                print(f"Erro ao buscar em '{doc_type}': {e}")

        # Ordenar por relevância (menor distância = mais similar)
        if all_results and all_results[0].get('distance') is not None:
            all_results.sort(key=lambda x: x['distance'])

        return all_results[:n_results]

    def get_document_chunks(
        self,
        condominio_id: str,
        document_name: str,
        doc_type: str = "contratos"
    ) -> List[Dict]:
        """
        Recupera todos os chunks de um documento específico

        Args:
            condominio_id: ID do condomínio
            document_name: Nome do documento
            doc_type: Tipo do documento

        Returns:
            Lista de chunks ordenados
        """
        collection = self.collections.get(doc_type)
        if not collection:
            return []

        try:
            results = collection.get(
                where={
                    "condominio_id": condominio_id,
                    "document_name": document_name
                }
            )

            chunks = []
            if results and results['documents']:
                for i in range(len(results['documents'])):
                    chunks.append({
                        'content': results['documents'][i],
                        'metadata': results['metadatas'][i],
                        'id': results['ids'][i]
                    })

            # Ordenar por chunk_id
            chunks.sort(key=lambda x: x['metadata'].get('chunk_id', 0))
            return chunks

        except Exception as e:
            print(f"Erro ao recuperar chunks: {e}")
            return []

    def list_documents(
        self,
        condominio_id: Optional[str] = None,
        doc_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Lista documentos armazenados

        Args:
            condominio_id: Filtrar por condomínio
            doc_type: Filtrar por tipo de documento

        Returns:
            Lista de documentos únicos
        """
        doc_types = [doc_type] if doc_type else list(self.collections.keys())
        documents = set()

        for dtype in doc_types:
            collection = self.collections.get(dtype)
            if not collection:
                continue

            try:
                where = {"condominio_id": condominio_id} if condominio_id else None
                results = collection.get(where=where)

                if results and results['metadatas']:
                    for metadata in results['metadatas']:
                        doc_key = (
                            metadata.get('condominio_id'),
                            metadata.get('document_name'),
                            dtype
                        )
                        documents.add(doc_key)

            except Exception as e:
                print(f"Erro ao listar documentos de '{dtype}': {e}")

        return [
            {
                'condominio_id': cond_id,
                'document_name': doc_name,
                'doc_type': dtype
            }
            for cond_id, doc_name, dtype in sorted(documents)
        ]

    def delete_document(
        self,
        condominio_id: str,
        document_name: str,
        doc_type: str
    ):
        """
        Remove um documento completo do banco

        Args:
            condominio_id: ID do condomínio
            document_name: Nome do documento
            doc_type: Tipo do documento
        """
        collection = self.collections.get(doc_type)
        if not collection:
            print(f"Coleção '{doc_type}' não encontrada")
            return

        try:
            # Buscar IDs dos chunks
            results = collection.get(
                where={
                    "condominio_id": condominio_id,
                    "document_name": document_name
                }
            )

            if results and results['ids']:
                collection.delete(ids=results['ids'])
                print(f"✓ Documento '{document_name}' removido ({len(results['ids'])} chunks)")
            else:
                print("Documento não encontrado")

        except Exception as e:
            print(f"✗ Erro ao deletar documento: {e}")

    def get_statistics(self) -> Dict:
        """Retorna estatísticas do banco de dados"""
        stats = {}

        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats[name] = count
            except:
                stats[name] = 0

        return stats
