#!/usr/bin/env python3
"""
Test script for the proper RAG system with ChromaDB
"""

from rag_system import TrademarkRAGSystem

def test_rag_system():
    """Test the RAG system functionality"""
    print("🧪 Testing RAG System with ChromaDB")
    print("=" * 50)
    
    # Initialize RAG system
    rag = TrademarkRAGSystem()
    
    # Initialize knowledge base
    rag.initialize_knowledge_base()
    
    # Test system status
    status = rag.get_system_status()
    print(f"📊 System Status: {status}")
    
    # Test some queries
    test_queries = [
        "short marks trademark distinctiveness",
        "software technology trademark considerations",
        "descriptive marks secondary meaning",
        "high conflict marks likelihood of confusion"
    ]
    
    print("\n🔍 Testing RAG Queries:")
    print("-" * 30)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = rag.search_relevant_context(query, n_results=2)
        
        if results:
            for i, result in enumerate(results):
                print(f"  Result {i+1}: {result['text'][:100]}...")
                print(f"    Relevance: {result['relevance_score']:.2f}")
        else:
            print("  No results found")
    
    # Test legal context generation
    print("\n⚖️ Testing Legal Context Generation:")
    print("-" * 40)
    
    keywords = ["Dino", "app"]
    search_results = {
        "Dino": {"items": [{"keyword": "DINO WATT"}, {"keyword": "DINOSKY"}]},
        "app": {"items": []}
    }
    
    legal_context = rag.get_legal_context_for_analysis(keywords, search_results)
    print(f"Generated context length: {len(legal_context)} characters")
    print(f"Context preview: {legal_context[:200]}...")
    
    print("\n✅ RAG System test completed!")

if __name__ == "__main__":
    test_rag_system()
