from pydantic import BaseModel, Field
from datetime import datetime, UTC
from typing import Optional, List, Dict

class KnowledgeDocument(BaseModel):
    id: str
    title: str
    content: str
    category: str # faq, institucional, modelos, situacoes
    metadata: dict = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class KnowledgeDocumentCreate(BaseModel):
    title: str
    content: str
    category: str
    metadata: dict = {}

class KnowledgeDocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    metadata: Optional[dict] = None

class KnowledgeSearchResult(BaseModel):
    documents: List[KnowledgeDocument]
    total: int
    query: str

class KBStats(BaseModel):
    total_documents: int
    count_by_category: Dict[str, int]
