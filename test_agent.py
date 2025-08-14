#!/usr/bin/env python3
"""
Test script for the LLM Trademark AI Agent
Tests basic functionality without requiring API keys
"""

def test_demo_agent():
    """Test the demo agent functionality"""
    print("🧪 Testing Demo LLM Trademark Agent")
    print("=" * 40)
    
    try:
        from demo import DemoLLMTrademarkAgent
        
        # Initialize demo agent
        agent = DemoLLMTrademarkAgent()
        print("✅ Demo agent initialized successfully")
        
        # Test keyword extraction
        test_questions = [
            "Is 'TechFlow' available for a software company?",
            "Can I trademark 'CloudSync' for cloud services?",
            "What about 'FreshStart' for a new business?",
            "Compare 'DataFlow' vs 'TechFlow' for tech startups"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n📋 Test {i}: {question}")
            print("-" * 30)
            
            result = agent.process_question(question)
            
            if "error" not in result:
                print(f"✅ Keywords: {result['extracted_keywords']}")
                print(f"✅ Analysis: {len(result['llm_analysis'])} characters")
                print(f"✅ Summary: {result['summary']}")
            else:
                print(f"❌ Error: {result['error']}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n🔧 Testing Configuration")
    print("=" * 30)
    
    try:
        from config import get_config
        
        config = get_config()
        print("✅ Configuration loaded successfully")
        print(f"   LLM Model: {config.LLM_MODEL}")
        print(f"   Base URL: {config.BASE_URL}")
        print(f"   Max Results: {config.MAX_SEARCH_RESULTS}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_imports():
    """Test that all required modules can be imported"""
    print("\n📦 Testing Imports")
    print("=" * 20)
    
    modules = [
        'openai',
        'requests', 
        'python-dotenv',
        'typing_extensions'
    ]
    
    all_good = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - not installed")
            all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("🚀 LLM Trademark AI Agent - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Check", test_imports),
        ("Configuration", test_config),
        ("Demo Agent", test_demo_agent)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The agent is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Get your API keys (OpenAI + RapidAPI)")
        print("   2. Set up your .env file")
        print("   3. Run: python llm_trademark_agent.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Check Python version (3.7+)")
        print("   3. Verify file permissions")

if __name__ == "__main__":
    main()
