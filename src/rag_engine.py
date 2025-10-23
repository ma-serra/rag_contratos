"""
Sistema RAG (Retrieval-Augmented Generation) para contratos
"""
import os
import chromadb
from typing import Dict, List, Optional
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter


class RAGEngine:
    """Motor RAG para indexação e busca de contratos"""

    def __init__(
        self,
        collection_name: str = "contratos",
        persist_directory: str = "./chromadb_storage",
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ):
        """
        Inicializa o motor RAG

        Args:
            collection_name: Nome da coleção no ChromaDB
            persist_directory: Diretório para persistir dados
            model_name: Modelo de embeddings (multilíngue para português)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # Criar cliente ChromaDB persistente
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Configurar função de embeddings multilíngue
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )

        # Obter ou criar coleção
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Coleção de contratos de aluguel"}
        )

        # Configurar text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def index_document(
        self,
        doc_data: Dict,
        contract_id: str,
        metadata: Optional[Dict] = None
    ):
        """
        Indexa um documento no sistema RAG

        Args:
            doc_data: Dados do documento processado pelo Docling
            contract_id: ID único do contrato
            metadata: Metadados adicionais
        """
        # Dividir texto em chunks
        full_text = doc_data.get("full_text", "")
        chunks = self.text_splitter.split_text(full_text)

        # Preparar metadados
        base_metadata = {
            "contract_id": contract_id,
            "file_name": doc_data.get("file_name", "unknown"),
            "num_pages": doc_data.get("metadata", {}).get("num_pages", 0)
        }

        if metadata:
            base_metadata.update(metadata)

        # Preparar dados para inserção
        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{contract_id}_chunk_{i}"
            ids.append(chunk_id)
            documents.append(chunk)

            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["chunk_total"] = len(chunks)

            metadatas.append(chunk_metadata)

        # Adicionar à coleção
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        print(f"Documento {contract_id} indexado com {len(chunks)} chunks")

    def index_sections(
        self,
        sections: List[Dict],
        contract_id: str,
        base_metadata: Optional[Dict] = None
    ):
        """
        Indexa seções específicas do documento

        Args:
            sections: Lista de seções extraídas
            contract_id: ID do contrato
            base_metadata: Metadados base
        """
        if not sections:
            return

        ids = []
        documents = []
        metadatas = []

        for i, section in enumerate(sections):
            section_id = f"{contract_id}_section_{i}"
            ids.append(section_id)
            documents.append(section.get("text", ""))

            metadata = base_metadata.copy() if base_metadata else {}
            metadata.update({
                "contract_id": contract_id,
                "section_type": section.get("type", "unknown"),
                "section_level": section.get("level", 0),
                "is_section": True
            })

            metadatas.append(metadata)

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        print(f"Indexadas {len(sections)} seções do contrato {contract_id}")

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Realiza busca semântica

        Args:
            query: Consulta em linguagem natural
            n_results: Número de resultados
            filter_metadata: Filtros de metadados

        Returns:
            Resultados da busca
        """
        search_params = {
            "query_texts": [query],
            "n_results": n_results
        }

        if filter_metadata:
            search_params["where"] = filter_metadata

        results = self.collection.query(**search_params)

        return {
            "documents": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0]
        }

    def search_by_contract(
        self,
        query: str,
        contract_id: str,
        n_results: int = 3
    ) -> Dict:
        """
        Busca dentro de um contrato específico

        Args:
            query: Consulta
            contract_id: ID do contrato
            n_results: Número de resultados

        Returns:
            Resultados filtrados por contrato
        """
        return self.search(
            query=query,
            n_results=n_results,
            filter_metadata={"contract_id": contract_id}
        )

    def get_all_contracts(self) -> List[str]:
        """
        Retorna lista de todos os IDs de contratos indexados

        Returns:
            Lista de IDs de contratos
        """
        all_data = self.collection.get()
        contract_ids = set()

        for metadata in all_data.get("metadatas", []):
            if "contract_id" in metadata:
                contract_ids.add(metadata["contract_id"])

        return sorted(list(contract_ids))

    def delete_contract(self, contract_id: str):
        """
        Remove um contrato da base de dados

        Args:
            contract_id: ID do contrato a remover
        """
        # Obter IDs de todos os chunks do contrato
        results = self.collection.get(
            where={"contract_id": contract_id}
        )

        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            print(f"Contrato {contract_id} removido ({len(results['ids'])} chunks)")
        else:
            print(f"Contrato {contract_id} não encontrado")

    def reset_collection(self):
        """Reseta a coleção (remove todos os dados)"""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        print("Coleção resetada")


if __name__ == "__main__":
    # Exemplo de uso
    rag = RAGEngine()
    print(f"RAG Engine inicializado. Contratos indexados: {rag.get_all_contracts()}")
