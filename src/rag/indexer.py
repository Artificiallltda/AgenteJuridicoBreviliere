import chromadb
from typing import List, Dict, Optional
from config.settings import get_settings
from config.logging import get_logger
from rag.embeddings import get_embeddings

settings = get_settings()
logger = get_logger(__name__)

class LegalIndexer:
    _instance: Optional['LegalIndexer'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LegalIndexer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        self.chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.collection = self.chroma_client.get_or_create_collection(name="juridico_faq")
        self._initialized = True

    async def index_documents(self, documents: List[Dict]):
        texts = [doc['content'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        ids = [doc['id'] for doc in documents]
        embeddings = await get_embeddings(texts)
        self.collection.add(embeddings=embeddings, documents=texts, metadatas=metadatas, ids=ids)
        logger.info("documentos_indexados", count=len(ids))

    async def query(self, query_text: str, n_results: int = 3, filter: Dict = None):
        query_embeddings = await get_embeddings([query_text])
        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=filter
        )
