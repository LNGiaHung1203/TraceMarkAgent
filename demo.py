#!/usr/bin/env python3
"""
Demo script for the LLM Trademark AI Agent
Shows how the agent works without requiring real API keys
"""

import json
import time
from typing import Dict, List, Any

class DemoLLMTrademarkAgent:
    """
    Demo version of the LLM Trademark Agent
    Uses simulated responses to demonstrate functionality
    """
    
    def __init__(self):
        """Initialize the demo agent"""
        print("🤖 Demo LLM Trademark Agent Initialized")
        print("🔧 This is a demonstration mode - no real API calls")
        print("💡 Use this to understand how the agent works")
        print("=" * 50)
        
        # Sample USPTO search results for demonstration
        self.sample_results = {
            "TechFlow": {
                "results": [
                    {
                        "serial_number": "12345678",
                        "mark": "TechFlow",
                        "status": "LIVE",
                        "owner": "TechFlow Solutions Inc.",
                        "goods_services": "Computer software for business management",
                        "filing_date": "2023-01-15"
                    },
                    {
                        "serial_number": "87654321",
                        "mark": "TechFlow Pro",
                        "status": "LIVE",
                        "owner": "Innovation Systems LLC",
                        "goods_services": "Software development services",
                        "filing_date": "2022-08-20"
                    }
                ]
            },
            "CloudSync": {
                "results": [
                    {
                        "serial_number": "11111111",
                        "mark": "CloudSync",
                        "status": "LIVE",
                        "owner": "Cloud Technologies Corp",
                        "goods_services": "Cloud storage and synchronization services",
                        "filing_date": "2021-06-10"
                    }
                ]
            },
            "FreshStart": {
                "results": []
            }
        }
    
    def extract_keywords(self, question: str) -> List[str]:
        """Simulate LLM keyword extraction"""
        print(f"🔍 LLM analyzing question: '{question}'")
        time.sleep(1)  # Simulate processing time
        
        # Simple keyword extraction logic for demo
        keywords = []
        question_lower = question.lower()
        
        # Extract potential brand names (words in quotes or capitalized)
        import re
        quoted_names = re.findall(r'"([^"]*)"', question)
        keywords.extend(quoted_names)
        
        # Extract capitalized words that might be brand names
        words = question.split()
        for word in words:
            if word[0].isupper() and len(word) > 2 and word not in ['I', 'The', 'Can', 'What', 'How']:
                keywords.append(word)
        
        # Remove duplicates and clean
        keywords = list(set([kw.strip() for kw in keywords if kw.strip()]))
        
        if not keywords:
            # Fallback: extract any word that might be a brand
            potential_brands = [word for word in words if len(word) > 3 and word.isalpha()]
            keywords = potential_brands[:2]  # Limit to 2 keywords
        
        print(f"✅ Extracted keywords: {keywords}")
        return keywords
    
    def search_uspto(self, keywords: List[str]) -> Dict[str, Any]:
        """Simulate USPTO API search"""
        if not keywords:
            return {"error": "No keywords to search"}
        
        all_results = {}
        
        for keyword in keywords:
            print(f"🔎 Searching USPTO for: {keyword}")
            time.sleep(0.5)  # Simulate API delay
            
            if keyword in self.sample_results:
                results = self.sample_results[keyword]
                all_results[keyword] = results
                print(f"✅ Found {len(results.get('results', []))} results for '{keyword}'")
            else:
                # Generate random results for unknown keywords
                import random
                num_results = random.randint(0, 3)
                if num_results > 0:
                    results = {
                        "results": [
                            {
                                "serial_number": f"{random.randint(10000000, 99999999)}",
                                "mark": keyword,
                                "status": random.choice(["LIVE", "DEAD", "PENDING"]),
                                "owner": f"{keyword} {random.choice(['Inc', 'LLC', 'Corp'])}",
                                "goods_services": f"Various goods and services related to {keyword.lower()}",
                                "filing_date": f"202{random.randint(0,3)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
                            }
                        ]
                    }
                else:
                    results = {"results": []}
                
                all_results[keyword] = results
                print(f"✅ Found {len(results.get('results', []))} results for '{keyword}'")
        
        return all_results
    
    def analyze_with_llm(self, original_question: str, keywords: List[str], search_results: Dict) -> str:
        """Simulate LLM analysis"""
        print("🧠 LLM analyzing search results...")
        time.sleep(1.5)  # Simulate processing time
        
        # Generate intelligent analysis based on search results
        analysis = self._generate_analysis(original_question, keywords, search_results)
        return analysis
    
    def _generate_analysis(self, question: str, keywords: List[str], search_results: Dict) -> str:
        """Generate intelligent analysis based on search results"""
        analysis_parts = []
        
        # Overall assessment
        total_conflicts = sum(len(results.get('results', [])) for results in search_results.values())
        if total_conflicts == 0:
            assessment = "🟢 **Trademark Availability Assessment**: All keywords appear to be available for registration."
            risk_level = "🟢 **Risk Level**: LOW - No significant conflicts detected."
        elif total_conflicts <= 2:
            assessment = "🟡 **Trademark Availability Assessment**: Some keywords have potential conflicts that need review."
            risk_level = "🟡 **Risk Level**: MEDIUM - Some conflicts detected, careful analysis recommended."
        else:
            assessment = "🔴 **Trademark Availability Assessment**: Multiple conflicts detected across keywords."
            risk_level = "🔴 **Risk Level**: HIGH - Significant conflicts detected, professional legal review recommended."
        
        analysis_parts.append(assessment)
        analysis_parts.append(risk_level)
        
        # Detailed analysis for each keyword
        analysis_parts.append("\n**Detailed Analysis by Keyword:**")
        
        for keyword, results in search_results.items():
            conflicts = results.get('results', [])
            
            if not conflicts:
                analysis_parts.append(f"\n✅ **{keyword}**: No conflicts found. This appears to be available for trademark registration.")
            else:
                analysis_parts.append(f"\n⚠️ **{keyword}**: {len(conflicts)} potential conflict(s) found:")
                for conflict in conflicts[:3]:  # Show first 3 conflicts
                    status_emoji = "🟢" if conflict.get('status') == 'LIVE' else "🟡"
                    analysis_parts.append(f"   {status_emoji} {conflict.get('mark')} - {conflict.get('status')} - {conflict.get('owner')}")
        
        # Recommendations
        analysis_parts.append("\n**Recommendations:**")
        if total_conflicts == 0:
            analysis_parts.append("• Proceed with trademark registration for all keywords")
            analysis_parts.append("• Consider filing applications soon to secure rights")
            analysis_parts.append("• Conduct additional searches in international databases if planning global expansion")
        elif total_conflicts <= 2:
            analysis_parts.append("• Review conflicts carefully to assess similarity and risk")
            analysis_parts.append("• Consider modifying conflicting keywords or seeking legal advice")
            analysis_parts.append("• Proceed with non-conflicting keywords")
        else:
            analysis_parts.append("• Consult with a trademark attorney for comprehensive analysis")
            analysis_parts.append("• Consider alternative brand names to avoid conflicts")
            analysis_parts.append("• Conduct broader trademark searches before proceeding")
        
        # Alternative suggestions
        if total_conflicts > 0:
            analysis_parts.append("\n**Alternative Suggestions:**")
            for keyword in keywords:
                if any(len(results.get('results', [])) > 0 for results in search_results.values() if keyword in results):
                    alternatives = self._generate_alternatives(keyword)
                    analysis_parts.append(f"• For '{keyword}': Consider {', '.join(alternatives)}")
        
        return "\n".join(analysis_parts)
    
    def _generate_alternatives(self, keyword: str) -> List[str]:
        """Generate alternative brand name suggestions"""
        alternatives = []
        
        # Simple alternative generation for demo
        if "tech" in keyword.lower():
            alternatives.extend(["TechStream", "TechFlow", "TechSync", "TechLink"])
        elif "cloud" in keyword.lower():
            alternatives.extend(["CloudLink", "CloudFlow", "CloudSync", "CloudTech"])
        elif "data" in keyword.lower():
            alternatives.extend(["DataFlow", "DataSync", "DataLink", "DataTech"])
        else:
            # Generic alternatives
            alternatives.extend([f"{keyword}Pro", f"{keyword}Plus", f"{keyword}Max", f"New{keyword}"])
        
        return alternatives[:3]  # Return 3 alternatives
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """Main method to process a user question"""
        print(f"\n🤔 Processing question: {question}")
        print("=" * 50)
        
        # Step 1: Extract keywords using LLM
        keywords = self.extract_keywords(question)
        if not keywords:
            return {
                "error": "No trademark-related keywords found in your question. Please ask about specific brand names, products, or services."
            }
        
        # Step 2: Search USPTO database
        search_results = self.search_uspto(keywords)
        
        # Step 3: Analyze results with LLM
        analysis = self.analyze_with_llm(question, keywords, search_results)
        
        # Step 4: Compile response
        response = {
            "original_question": question,
            "extracted_keywords": keywords,
            "uspto_search_results": search_results,
            "llm_analysis": analysis,
            "summary": {
                "keywords_found": len(keywords),
                "searches_performed": len(keywords),
                "analysis_provided": bool(analysis)
            }
        }
        
        return response
    
    def interactive_mode(self):
        """Run the agent in interactive mode"""
        print("\n🚀 Demo LLM Trademark AI Agent - Interactive Mode")
        print("Ask questions about trademarks and see how the agent works!")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                question = input("🤔 Ask about a trademark: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not question:
                    continue
                
                # Process the question
                result = self.process_question(question)
                
                if "error" in result:
                    print(f"❌ {result['error']}")
                else:
                    print("\n📊 Analysis Results:")
                    print("=" * 50)
                    print(result['llm_analysis'])
                    print("=" * 50)
                
                print("\n" + "-" * 50 + "\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

def main():
    """Main entry point for demo"""
    print("🎭 LLM Trademark AI Agent - DEMO MODE")
    print("This demonstrates how the agent works without real API keys")
    print("=" * 60)
    
    # Initialize demo agent
    agent = DemoLLMTrademarkAgent()
    
    # Run interactive mode
    agent.interactive_mode()

if __name__ == "__main__":
    main()
