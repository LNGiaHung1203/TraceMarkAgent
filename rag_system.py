import os
import re
import json
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
import tempfile
import PyPDF2
import io

class TrademarkRAGSystem:
    """
    Proper RAG system for trademark analysis using ChromaDB
    Includes document chunking, embedding, and semantic search
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the RAG system with ChromaDB and embedding model"""
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize collection
        self.collection = self._get_or_create_collection()
        
        # Define the actual USPTO trademark law document source
        self.document_sources = {
            "uspto_trademark_law": {
                "url": "https://www.uspto.gov/sites/default/files/documents/tmlaw.pdf",
                "description": "USPTO Trademark Manual of Examining Procedure (TMEP) - Official trademark law and examination guidelines"
            }
        }
    
    def _get_or_create_collection(self):
        """Get or create the ChromaDB collection"""
        try:
            collection = self.client.get_collection("trademark_knowledge")
            print("📚 Using existing ChromaDB collection")
        except:
            collection = self.client.create_collection("trademark_knowledge")
            print("📚 Created new ChromaDB collection")
        return collection
    
    def _download_and_process_documents(self):
        """Download and process the actual USPTO trademark law PDF"""
        print("📥 Downloading USPTO Trademark Law PDF...")
        
        try:
            # Download the PDF from USPTO
            response = requests.get(self.document_sources["uspto_trademark_law"]["url"], timeout=30)
            response.raise_for_status()
            
            print("📄 PDF downloaded successfully, processing content...")
            
            # Process the PDF content
            pdf_content = self._extract_text_from_pdf(response.content)
            
            if not pdf_content or len(pdf_content.strip()) < 100:
                print("⚠️ Warning: PDF content seems too short, using fallback knowledge")
                return self._get_predefined_legal_knowledge()
            
            print(f"📊 Extracted {len(pdf_content)} characters from PDF")
            
            # Process and chunk the PDF content
            chunks = self._chunk_text(pdf_content)
            
            # Add chunks to ChromaDB
            self._add_chunks_to_database(chunks)
            
            print(f"✅ Added {len(chunks)} knowledge chunks to RAG system")
            return pdf_content
            
        except Exception as e:
            print(f"❌ Error downloading/processing PDF: {e}")
            print("🔄 Falling back to predefined legal knowledge")
            return self._get_predefined_legal_knowledge()
    
    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text content from PDF bytes"""
        try:
            # Create a file-like object from the PDF content
            pdf_file = io.BytesIO(pdf_content)
            
            # Read the PDF
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text_content = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
                except Exception as e:
                    print(f"⚠️ Warning: Could not extract text from page {page_num + 1}: {e}")
                    continue
            
            full_text = "\n\n".join(text_content)
            
            if not full_text.strip():
                print("⚠️ Warning: No text could be extracted from PDF")
                return ""
            
            return full_text
            
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {e}")
            return ""
    
    def _get_predefined_legal_knowledge(self) -> str:
        """Fallback legal knowledge if PDF processing fails"""
        return """
        **BASIC TRADEMARK LAW PRINCIPLES (Fallback Knowledge):**
        
        **Trademark Distinctiveness**: Marks must be distinctive to be protectable. Fanciful and arbitrary marks receive the strongest protection.
        
        **Likelihood of Confusion**: The primary test for trademark conflicts considers similarity of marks, goods/services, and trade channels.
        
        **DuPont Factors**: Framework for analyzing trademark conflicts including mark similarity, goods similarity, and market overlap.
        
        **Trademark Strength**: Varies from generic (no protection) to fanciful (strongest protection).
        
        **Registration Requirements**: Must be distinctive, not primarily descriptive, and not conflict with existing marks.
        
        Note: This is fallback knowledge. The system should be using the actual USPTO Trademark Manual of Examining Procedure (TMEP) for comprehensive legal analysis.
        """
    
    def _chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Split text into chunks for vector database"""
        # Split text into chunks
        text_chunks = self.text_splitter.split_text(text)
        
        # Create chunk metadata
        chunks = []
        for i, chunk in enumerate(text_chunks):
            chunks.append({
                'id': f"chunk_{i}",
                'text': chunk,
                'metadata': {
                    'chunk_id': i,
                    'source': 'trademark_law',
                    'type': 'legal_knowledge'
                }
            })
        
        return chunks
    
    def _add_chunks_to_database(self, chunks: List[Dict[str, Any]]):
        """Add text chunks to ChromaDB"""
        if not chunks:
            return
        
        # Prepare data for ChromaDB
        ids = [chunk['id'] for chunk in chunks]
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
    
    def search_relevant_context(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant legal context using semantic similarity"""
        try:
            # Search ChromaDB for relevant chunks
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            relevant_context = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    relevant_context.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'relevance_score': 1.0 - (i * 0.1)  # Simple relevance scoring
                    })
            
            return relevant_context
            
        except Exception as e:
            print(f"❌ Error searching RAG system: {e}")
            return []
    
    def get_legal_context_for_analysis(self, keywords: List[str], search_results: Dict) -> str:
        """Get relevant legal context for trademark analysis"""
        # Create a query based on the analysis context
        query = self._create_analysis_query(keywords, search_results)
        
        # Search for relevant legal context
        relevant_chunks = self.search_relevant_context(query, n_results=3)
        
        if not relevant_chunks:
            return self._get_fallback_legal_context()
        
        # Build context from relevant chunks
        context_parts = ["**RELEVANT LEGAL CONTEXT FROM USPTO TRADEMARK LAW:**"]
        
        for chunk in relevant_chunks:
            context_parts.append(f"\n{chunk['text']}")
        
        return "\n".join(context_parts)
    
    def _create_analysis_query(self, keywords: List[str], search_results: Dict) -> str:
        """Create a search query based on analysis context"""
        query_parts = []
        
        # Add keyword context
        if any(len(kw) <= 4 for kw in keywords):
            query_parts.append("short marks trademark distinctiveness")
        
        if any('app' in kw.lower() or 'software' in kw.lower() for kw in keywords):
            query_parts.append("software technology trademark considerations")
        
        if any('tech' in kw.lower() or 'data' in kw.lower() for kw in keywords):
            query_parts.append("descriptive marks secondary meaning")
        
        # Add search results context
        total_conflicts = sum(len(results.get('items', [])) for results in search_results.values())
        if total_conflicts > 5:
            query_parts.append("high conflict marks likelihood of confusion")
        elif total_conflicts > 0:
            query_parts.append("moderate conflict marks risk assessment")
        
        # Default query if no specific context
        if not query_parts:
            query_parts.append("trademark distinctiveness likelihood of confusion")
        
        return " ".join(query_parts)
    
    def _get_fallback_legal_context(self) -> str:
        """Get fallback legal context when RAG search fails"""
        return """
        **BASIC TRADEMARK LAW PRINCIPLES:**
        
        **Trademark Distinctiveness**: Marks must be distinctive to be protectable. Fanciful and arbitrary marks receive the strongest protection.
        
        **Likelihood of Confusion**: The primary test for trademark conflicts considers similarity of marks, goods/services, and trade channels.
        
        **DuPont Factors**: Framework for analyzing trademark conflicts including mark similarity, goods similarity, and market overlap.
        
        **Trademark Strength**: Varies from generic (no protection) to fanciful (strongest protection).
        
        **Registration Requirements**: Must be distinctive, not primarily descriptive, and not conflict with existing marks.
        """
    
    def initialize_knowledge_base(self):
        """Initialize the knowledge base with documents"""
        print("🚀 Initializing RAG knowledge base...")
        
        # Check if collection already has data
        try:
            count = self.collection.count()
            if count > 0:
                print(f"📚 Knowledge base already contains {count} chunks")
                return
        except:
            pass
        
        # Download and process documents
        self._download_and_process_documents()
        
        print("✅ RAG knowledge base initialized successfully")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of the RAG system"""
        try:
            count = self.collection.count()
            return {
                'status': 'active',
                'chunks_count': count,
                'collection_name': self.collection.name,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
