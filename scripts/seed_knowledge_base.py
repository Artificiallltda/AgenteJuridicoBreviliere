"""
Seed Knowledge Base - Indexa documentos do knowledge_base/ no ChromaDB.

Uso:
    python -m scripts.seed_knowledge_base
    
Ou:
    cd scripts
    python seed_knowledge_base.py
"""

import asyncio
from pathlib import Path
from typing import List, Dict
import hashlib

from rag.indexer import LegalIndexer
from config.logging import get_logger

logger = get_logger(__name__)


def generate_doc_id(content: str, source: str) -> str:
    """Gera um ID único para o documento baseado no conteúdo e origem."""
    text = f"{source}:{content[:100]}"
    return hashlib.md5(text.encode()).hexdigest()


async def load_markdown_files(directory: Path, category: str) -> List[Dict]:
    """Carrega todos os arquivos .md de um diretório."""
    documents = []
    
    for md_file in directory.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            
            # Extrai título do primeiro heading
            title = "Sem título"
            for line in content.split("\n")[:5]:
                if line.startswith("#"):
                    title = line.lstrip("#").strip()
                    break
            
            documents.append({
                "id": generate_doc_id(content, str(md_file)),
                "content": content,
                "metadata": {
                    "category": category,
                    "source": str(md_file.relative_to(Path(__file__).parent.parent)),
                    "title": title,
                    "type": "faq" if "faq" in category else "jurisprudencia"
                }
            })
            
            logger.info("arquivo_carregado", file=str(md_file), title=title)
            
        except Exception as e:
            logger.error("erro_carregar_arquivo", file=str(md_file), error=str(e))
    
    return documents


async def seed_knowledge_base():
    """Indexa toda a base de conhecimento no ChromaDB."""
    logger.info("iniciando_seed_knowledge_base")
    
    try:
        indexer = LegalIndexer()
        kb_path = Path(__file__).parent.parent / "knowledge_base"
        
        all_documents = []
        
        # Carrega FAQ por categoria
        faq_path = kb_path / "faq"
        if faq_path.exists():
            for category_dir in faq_path.iterdir():
                if category_dir.is_dir():
                    category = f"faq/{category_dir.name}"
                    docs = await load_markdown_files(category_dir, category)
                    all_documents.extend(docs)
                    logger.info("faq_categoria_indexada", category=category, count=len(docs))
        
        # Carrega Jurisprudência
        jurisprudencia_path = kb_path / "jurisprudencia"
        if jurisprudencia_path.exists():
            docs = await load_markdown_files(jurisprudencia_path, "jurisprudencia")
            all_documents.extend(docs)
            logger.info("jurisprudencia_indexada", count=len(docs))
        
        # Carrega Institucional
        institucional_path = kb_path / "institucional"
        if institucional_path.exists():
            docs = await load_markdown_files(institucional_path, "institucional")
            all_documents.extend(docs)
            logger.info("institucional_indexado", count=len(docs))
        
        # Carrega Templates de Texto
        templates_path = kb_path / "templates_texto"
        if templates_path.exists():
            docs = await load_markdown_files(templates_path, "templates")
            all_documents.extend(docs)
            logger.info("templates_indexados", count=len(docs))
        
        if not all_documents:
            logger.warning("nenhum_documento_encontrado")
            return
        
        # Indexa todos os documentos
        await indexer.index_documents(all_documents)
        
        logger.info(
            "seed_concluido_com_sucesso",
            total_documentos=len(all_documents),
            categorias=list(set(doc["metadata"]["category"] for doc in all_documents))
        )
        
        print(f"\n✅ Seed concluído com sucesso!")
        print(f"📊 Total de documentos indexados: {len(all_documents)}")
        print(f"📁 Categorias: {list(set(doc['metadata']['category'] for doc in all_documents))}")
        
    except Exception as e:
        logger.error("erro_seed_knowledge_base", error=str(e))
        print(f"\n❌ Erro durante o seed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())
