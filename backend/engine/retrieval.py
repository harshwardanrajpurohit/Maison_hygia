from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from backend.data.knowledge import get_all_knowledge
from backend.models import KnowledgeChunk
from backend.config import settings

_vectorstore = None

def init_vectorstore():
    global _vectorstore
    
    if _vectorstore is not None:
        return
        
    chunks = get_all_knowledge()
    
    docs = []
    for chunk in chunks:
        # Create a document where page_content is the text, and metadata has everything else
        doc = Document(
            page_content=chunk.content,
            metadata={
                "id": chunk.id,
                "category": chunk.category,
                "trust_level": chunk.trust_level,
                "tags": chunk.tags,
                "source_type": chunk.source_type,
                "source_url": chunk.source_url
            }
        )
        docs.append(doc)
        
    try:
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            
        _vectorstore = FAISS.from_documents(docs, embeddings)
        print("Vectorstore initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize vectorstore: {e}")
        _vectorstore = None

def retrieve_knowledge(query: str, top_k: int = None, category_filter: str = None) -> List[KnowledgeChunk]:
    if top_k is None:
        top_k = settings.MAX_RETRIEVAL_CHUNKS
        
    if _vectorstore is None:
        init_vectorstore()
        
    # Fallback if embeddings fail (e.g. no API key)
    if _vectorstore is None:
        print("Falling back to empty retrieval.")
        return []
        
    # Langchain FAISS supports filtering by metadata if using MMR or similarity search with filter
    filter_dict = {}
    if category_filter:
        filter_dict["category"] = category_filter
        
    # We could use MMR for diversity, but for knowledge retrieval, similarity is usually fine.
    # Let's just use similarity search
    # Note: FAISS in langchain supports basic dict filters.
    docs = _vectorstore.similarity_search(query, k=top_k, filter=filter_dict if filter_dict else None)
    
    # Sort by trust level implicitly or explicitly if needed
    # 'high' > 'medium' > 'low'
    trust_scores = {"high": 3, "medium": 2, "low": 1}
    docs.sort(key=lambda d: trust_scores.get(d.metadata.get("trust_level", "low"), 0), reverse=True)
    
    results = []
    for doc in docs:
        results.append(
            KnowledgeChunk(
                id=doc.metadata["id"],
                content=doc.page_content,
                source_url=doc.metadata.get("source_url"),
                source_type=doc.metadata["source_type"],
                trust_level=doc.metadata["trust_level"],
                tags=doc.metadata["tags"],
                category=doc.metadata["category"]
            )
        )
        
    return results
