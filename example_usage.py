#!/usr/bin/env python3
"""
Example usage of the LLM Trademark AI Agent
Demonstrates programmatic usage for various trademark analysis scenarios
"""

from llm_trademark_agent import LLMTrademarkAgent
import os

def get_api_keys():
    """Get API keys from user input"""
    print("🔑 API Key Setup")
    print("=" * 40)
    
    openai_key = input("Enter your OpenAI API key: ").strip()
    if not openai_key:
        openai_key = os.getenv('OPENAI_API_KEY')
    
    rapidapi_key = input("Enter your RapidAPI key: ").strip()
    if not rapidapi_key:
        rapidapi_key = os.getenv('RAPIDAPI_KEY')
    
    if not openai_key or not rapidapi_key:
        print("❌ Both API keys are required!")
        return None, None
    
    return openai_key, rapidapi_key

def example_basic_analysis():
    """Example: Basic trademark availability analysis"""
    print("\n📋 Example 1: Basic Trademark Analysis")
    print("-" * 40)
    
    question = "Is the brand name 'TechFlow' available for a software company?"
    print(f"Question: {question}")
    
    result = agent.process_question(question)
    
    if "error" not in result:
        print(f"\n✅ Analysis completed!")
        print(f"Keywords extracted: {result['extracted_keywords']}")
        print(f"LLM Analysis:\n{result['llm_analysis']}")
    else:
        print(f"❌ Error: {result['error']}")

def example_brand_comparison():
    """Example: Compare multiple brand names"""
    print("\n📋 Example 2: Brand Name Comparison")
    print("-" * 40)
    
    brands = ["CloudSync", "DataFlow", "SmartConnect"]
    
    for brand in brands:
        question = f"Can I trademark '{brand}' for a cloud computing service?"
        print(f"\nAnalyzing: {brand}")
        
        result = agent.process_question(question)
        
        if "error" not in result:
            print(f"✅ {brand}: Analysis completed")
            # Extract key insights
            analysis = result['llm_analysis']
            if "available" in analysis.lower() or "clear" in analysis.lower():
                print(f"   🟢 {brand} appears available")
            elif "conflict" in analysis.lower() or "risk" in analysis.lower():
                print(f"   🟡 {brand} has potential conflicts")
            else:
                print(f"   🔵 {brand} needs further review")
        else:
            print(f"❌ {brand}: {result['error']}")

def example_legal_advice():
    """Example: Get legal advice on trademark strategy"""
    print("\n📋 Example 3: Legal Strategy Advice")
    print("-" * 40)
    
    question = "I want to start a coffee shop called 'Morning Brew'. What are my trademark options and risks?"
    print(f"Question: {question}")
    
    result = agent.process_question(question)
    
    if "error" not in result:
        print(f"\n✅ Legal analysis completed!")
        print(f"Keywords extracted: {result['extracted_keywords']}")
        print(f"Legal Analysis:\n{result['llm_analysis']}")
    else:
        print(f"❌ Error: {result['error']}")

def example_industry_specific():
    """Example: Industry-specific trademark analysis"""
    print("\n📋 Example 4: Industry-Specific Analysis")
    print("-" * 40)
    
    question = "I'm launching a fitness app called 'FitLife'. What trademark considerations should I be aware of in the health tech industry?"
    print(f"Question: {question}")
    
    result = agent.process_question(question)
    
    if "error" not in result:
        print(f"\n✅ Industry analysis completed!")
        print(f"Keywords extracted: {result['extracted_keywords']}")
        print(f"Industry Analysis:\n{result['llm_analysis']}")
    else:
        print(f"❌ Error: {result['error']}")

def example_batch_analysis():
    """Example: Batch analysis of multiple trademarks"""
    print("\n📋 Example 5: Batch Trademark Analysis")
    print("-" * 40)
    
    trademarks = [
        "EcoSmart",
        "QuickFix", 
        "GlobalTech",
        "FreshStart"
    ]
    
    print("Analyzing multiple trademarks...")
    results = {}
    
    for tm in trademarks:
        question = f"Is '{tm}' available for trademark registration?"
        result = agent.process_question(question)
        results[tm] = result
    
    # Summary report
    print("\n📊 Batch Analysis Summary:")
    print("=" * 40)
    
    for tm, result in results.items():
        if "error" not in result:
            analysis = result['llm_analysis']
            if "available" in analysis.lower():
                status = "🟢 Available"
            elif "conflict" in analysis.lower():
                status = "🟡 Conflicts"
            else:
                status = "🔵 Review Needed"
            print(f"{tm}: {status}")
        else:
            print(f"{tm}: ❌ Error")

def main():
    """Main function to run examples"""
    global agent
    
    print("🚀 LLM Trademark AI Agent - Example Usage")
    print("=" * 50)
    
    # Get API keys
    openai_key, rapidapi_key = get_api_keys()
    if not openai_key or not rapidapi_key:
        return
    
    try:
        # Initialize agent
        agent = LLMTrademarkAgent(openai_api_key=openai_key, rapidapi_key=rapidapi_key)
        print("✅ Agent initialized successfully!")
        
        # Run examples
        example_basic_analysis()
        example_brand_comparison()
        example_legal_advice()
        example_industry_specific()
        example_batch_analysis()
        
        print("\n🎉 All examples completed!")
        print("\n💡 You can now use the agent in your own code:")
        print("   from llm_trademark_agent import LLMTrademarkAgent")
        print("   agent = LLMTrademarkAgent(openai_api_key='your_key', rapidapi_key='your_key')")
        print("   result = agent.process_question('Your question here')")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")

if __name__ == "__main__":
    main()
