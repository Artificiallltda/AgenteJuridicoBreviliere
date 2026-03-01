"""
Script de Seed: Popula o ChromaDB com a base de conhecimento jurídica.

Uso:
    python scripts/seed_knowledge_base.py [--reset]

    --reset  Limpa a collection antes de reindexar

Lê todos os arquivos .md em knowledge_base/ e os indexa no ChromaDB
com metadados estruturados para busca vetorial filtrada.
"""

import asyncio
import hashlib
import os
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List

# Adiciona o diretório raiz ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import get_settings
from src.rag.indexer import LegalIndexer
from src.config.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)
settings = get_settings()

# ============================================================
# Configuração de Chunking por tipo de documento
# ============================================================
CHUNK_CONFIG = {
    "faq": {"chunk_size": 512, "overlap": 50},
    "jurisprudencia": {"chunk_size": 1024, "overlap": 128},
    "institucional": {"chunk_size": 256, "overlap": 32},
    "templates_texto": {"chunk_size": 256, "overlap": 32},
}

# Mapeamento de pasta -> tipo + área jurídica
FOLDER_MAPPING = {
    "faq": "faq",
    "jurisprudencia": "jurisprudencia",
    "institucional": "institucional",
    "templates_texto": "template",
}

# Detecta área jurídica pelo nome do arquivo
AREA_MAPPING = {
    "trabalhista": "trabalhista",
    "civil": "civil",
    "familia": "familia",
    "criminal": "criminal",
    "previdenciario": "previdenciario",
    "tst": "trabalhista",
    "stj": "civil",
    "sumulas": "geral",
}


def detect_area(filename: str) -> str:
    """Detecta a área jurídica com base no nome do arquivo."""
    name_lower = filename.lower()
    for key, area in AREA_MAPPING.items():
        if key in name_lower:
            return area
    return "geral"


def extract_tags(text: str) -> List[str]:
    """Extrai tags relevantes do texto (palavras-chave jurídicas)."""
    keywords = [
        "rescisão", "fgts", "clt", "trabalhista", "férias", "salário",
        "demissão", "contrato", "dano", "moral", "indenização",
        "consumidor", "cdc", "divórcio", "guarda", "pensão", "alimentos",
        "inventário", "herança", "crime", "prisão", "flagrante", "drogas",
        "aposentadoria", "inss", "benefício", "auxílio", "previdência",
        "lgpd", "whatsapp", "honorários", "handoff", "saudação",
    ]
    text_lower = text.lower()
    return [kw for kw in keywords if kw in text_lower]


def split_by_qa(content: str) -> List[Dict]:
    """
    Divide o conteúdo markdown em chunks por pergunta/resposta.
    Cada ### é tratado como início de um novo chunk.
    """
    chunks = []
    # Divide pelo padrão ### (pergunta)
    sections = re.split(r'(?=^### )', content, flags=re.MULTILINE)

    for section in sections:
        section = section.strip()
        if not section or not section.startswith("###"):
            continue

        # Extrai título da pergunta
        lines = section.split("\n", 1)
        title = lines[0].replace("### ", "").strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        if body:
            chunks.append({
                "title": title,
                "content": f"{title}\n\n{body}",
            })

    return chunks


def split_by_section(content: str) -> List[Dict]:
    """
    Divide o conteúdo markdown em chunks por seção (##).
    Usado para documentos que não são FAQ.
    """
    chunks = []
    sections = re.split(r'(?=^## )', content, flags=re.MULTILINE)

    for section in sections:
        section = section.strip()
        if not section or not section.startswith("##"):
            continue

        lines = section.split("\n", 1)
        title = lines[0].replace("## ", "").strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        if body:
            chunks.append({
                "title": title,
                "content": f"{title}\n\n{body}",
            })

    return chunks


def generate_chunk_id(source: str, title: str) -> str:
    """Gera um ID único e determinístico para cada chunk."""
    raw = f"{source}::{title}"
    return hashlib.md5(raw.encode()).hexdigest()


def process_file(file_path: Path, kb_root: Path) -> List[Dict]:
    """
    Processa um arquivo .md e retorna lista de documentos para indexação.
    Cada documento tem: id, content, metadata.
    """
    relative = file_path.relative_to(kb_root)
    folder = relative.parts[0] if relative.parts else "unknown"
    doc_type = FOLDER_MAPPING.get(folder, "other")
    area = detect_area(file_path.stem)

    content = file_path.read_text(encoding="utf-8")

    # Escolhe estratégia de chunking
    if doc_type == "faq":
        chunks = split_by_qa(content)
    else:
        chunks = split_by_section(content)

    # Se não conseguiu dividir, usa o documento inteiro
    if not chunks:
        chunks = [{"title": file_path.stem, "content": content}]

    documents = []
    for chunk in chunks:
        doc_id = generate_chunk_id(str(relative), chunk["title"])
        tags = extract_tags(chunk["content"])

        documents.append({
            "id": doc_id,
            "content": chunk["content"],
            "metadata": {
                "source": str(relative),
                "area_juridica": area,
                "tipo": doc_type,
                "titulo": chunk["title"],
                "tags": ", ".join(tags),  # ChromaDB não suporta listas em metadata
                "data_atualizacao": file_path.stat().st_mtime.__str__()[:10],
            },
        })

    return documents


async def seed_knowledge_base(reset: bool = False):
    """
    Função principal: lê knowledge_base/ e indexa no ChromaDB.
    """
    kb_root = Path(__file__).parent.parent / "knowledge_base"

    if not kb_root.exists():
        logger.error("diretorio_nao_encontrado", path=str(kb_root))
        print(f"❌ Diretório não encontrado: {kb_root}")
        return

    indexer = LegalIndexer()

    # Reset da collection se solicitado
    if reset:
        logger.warning("resetando_collection")
        print("🗑️  Resetando collection 'juridico_faq'...")
        indexer.chroma_client.delete_collection("juridico_faq")
        indexer.collection = indexer.chroma_client.get_or_create_collection(
            name="juridico_faq"
        )

    # Coleta todos os arquivos .md
    md_files = sorted(kb_root.rglob("*.md"))
    md_files = [f for f in md_files if f.name != "README.md"]

    if not md_files:
        logger.warning("nenhum_arquivo_encontrado")
        print("⚠️  Nenhum arquivo .md encontrado em knowledge_base/")
        return

    print(f"\n📚 Indexando {len(md_files)} arquivos da base de conhecimento...\n")

    all_documents = []
    for file_path in md_files:
        relative = file_path.relative_to(kb_root)
        docs = process_file(file_path, kb_root)
        all_documents.extend(docs)
        print(f"  ✅ {relative} → {len(docs)} chunks")

    print(f"\n📊 Total: {len(all_documents)} chunks para indexar\n")

    # Indexa em lotes de 50 (limite do ChromaDB)
    batch_size = 50
    for i in range(0, len(all_documents), batch_size):
        batch = all_documents[i : i + batch_size]
        await indexer.index_documents(batch)
        print(f"  📤 Batch {i // batch_size + 1}: {len(batch)} chunks indexados")

    print(f"\n✅ Indexação completa! {len(all_documents)} chunks no ChromaDB.")
    print(f"   Collection: juridico_faq")
    print(f"   Persist dir: {settings.chroma_persist_dir}\n")

    # Estatísticas por tipo e área
    stats_tipo = {}
    stats_area = {}
    for doc in all_documents:
        tipo = doc["metadata"]["tipo"]
        area = doc["metadata"]["area_juridica"]
        stats_tipo[tipo] = stats_tipo.get(tipo, 0) + 1
        stats_area[area] = stats_area.get(area, 0) + 1

    print("📊 Estatísticas por tipo:")
    for tipo, count in sorted(stats_tipo.items()):
        print(f"   {tipo}: {count} chunks")

    print("\n📊 Estatísticas por área jurídica:")
    for area, count in sorted(stats_area.items()):
        print(f"   {area}: {count} chunks")


def main():
    parser = argparse.ArgumentParser(
        description="Popula o ChromaDB com a base de conhecimento jurídica."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Limpa a collection antes de reindexar",
    )
    args = parser.parse_args()

    asyncio.run(seed_knowledge_base(reset=args.reset))


if __name__ == "__main__":
    main()
