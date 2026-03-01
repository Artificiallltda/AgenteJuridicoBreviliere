import uuid
from datetime import datetime, UTC
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from src.models.knowledge import (
    KnowledgeDocument, 
    KnowledgeDocumentCreate, 
    KnowledgeDocumentUpdate, 
    KnowledgeSearchResult,
    KBStats
)
from src.rag.indexer import LegalIndexer
from src.config.logging import get_logger

router = APIRouter(prefix="/admin/kb", tags=["admin"])
logger = get_logger(__name__)
indexer = LegalIndexer()

def _map_chroma_to_model(doc_id: str, content: str, metadata: dict) -> KnowledgeDocument:
    """Converte dados do ChromaDB para o modelo KnowledgeDocument."""
    return KnowledgeDocument(
        id=doc_id,
        title=metadata.get("title", "Sem Titulo"),
        content=content,
        category=metadata.get("category", "geral"),
        metadata=metadata,
        created_at=metadata.get("created_at", datetime.now(UTC)),
        updated_at=metadata.get("updated_at", datetime.now(UTC))
    )

@router.get("/documents", response_model=List[KnowledgeDocument])
async def list_documents(
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Lista documentos da KB com filtros opcionais."""
    where = {"category": category} if category else None
    
    # ChromaDB get() para listar
    results = indexer.collection.get(
        where=where,
        limit=limit,
        offset=offset,
        include=["documents", "metadatas"]
    )
    
    docs = []
    for i in range(len(results["ids"])):
        docs.append(_map_chroma_to_model(
            results["ids"][i],
            results["documents"][i],
            results["metadatas"][i]
        ))
    return docs

@router.get("/documents/{doc_id}", response_model=KnowledgeDocument)
async def get_document(doc_id: str):
    """Obtem um documento especifico pelo ID."""
    result = indexer.collection.get(
        ids=[doc_id],
        include=["documents", "metadatas"]
    )
    
    if not result["ids"]:
        raise HTTPException(status_code=404, detail="Documento nao encontrado")
    
    return _map_chroma_to_model(
        result["ids"][0],
        result["documents"][0],
        result["metadatas"][0]
    )

@router.post("/documents", response_model=KnowledgeDocument)
async def create_document(doc_in: KnowledgeDocumentCreate):
    """Cria e indexa um novo documento na KB."""
    doc_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()
    
    metadata = doc_in.metadata.copy()
    metadata.update({
        "title": doc_in.title,
        "category": doc_in.category,
        "created_at": now,
        "updated_at": now
    })
    
    await indexer.index_documents([{
        "id": doc_id,
        "content": doc_in.content,
        "metadata": metadata
    }])
    
    logger.info("documento_kb_criado", id=doc_id, title=doc_in.title)
    return _map_chroma_to_model(doc_id, doc_in.content, metadata)

@router.put("/documents/{doc_id}", response_model=KnowledgeDocument)
async def update_document(doc_id: str, doc_in: KnowledgeDocumentUpdate):
    """Atualiza um documento existente (re-indexacao)."""
    # 1. Busca atual
    existing = indexer.collection.get(ids=[doc_id], include=["documents", "metadatas"])
    if not existing["ids"]:
        raise HTTPException(status_code=404, detail="Documento nao encontrado")
    
    curr_content = existing["documents"][0]
    curr_meta = existing["metadatas"][0]
    
    # 2. Mescla campos
    new_content = doc_in.content or curr_content
    new_meta = curr_meta.copy()
    if doc_in.title: new_meta["title"] = doc_in.title
    if doc_in.category: new_meta["category"] = doc_in.category
    if doc_in.metadata: new_meta.update(doc_in.metadata)
    new_meta["updated_at"] = datetime.now(UTC).isoformat()
    
    # 3. Atualiza (Chroma delete + add e o mais seguro para garantir re-embedding se conteudo mudou)
    indexer.collection.delete(ids=[doc_id])
    await indexer.index_documents([{
        "id": doc_id,
        "content": new_content,
        "metadata": new_meta
    }])
    
    logger.info("documento_kb_atualizado", id=doc_id)
    return _map_chroma_to_model(doc_id, new_content, new_meta)

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Remove um documento da KB."""
    indexer.collection.delete(ids=[doc_id])
    logger.info("documento_kb_removido", id=doc_id)
    return {"status": "deleted", "id": doc_id}

@router.post("/search", response_model=KnowledgeSearchResult)
async def search_kb(
    query: str = Body(..., embed=True),
    n_results: int = Body(5, embed=True)
):
    """Realiza busca semantica na KB."""
    results = await indexer.query(query, n_results=n_results)
    
    docs = []
    if results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            docs.append(_map_chroma_to_model(
                results["ids"][0][i],
                results["documents"][0][i],
                results["metadatas"][0][i]
            ))
            
    return KnowledgeSearchResult(
        documents=docs,
        total=len(docs),
        query=query
    )

@router.get("/stats", response_model=KBStats)
async def get_stats():
    """Retorna estatisticas da Knowledge Base."""
    results = indexer.collection.get(include=["metadatas"])
    metadatas = results["metadatas"]
    
    counts = {}
    for meta in metadatas:
        cat = meta.get("category", "desconhecida")
        counts[cat] = counts.get(cat, 0) + 1
        
    return KBStats(
        total_documents=len(metadatas),
        count_by_category=counts
    )
