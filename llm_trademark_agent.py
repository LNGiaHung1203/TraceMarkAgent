import json
import requests
from typing import Dict, List, Optional, Any
from openai import OpenAI
from config import get_config
from rag_system import TrademarkRAGSystem
import re

class LLMTrademarkAgent:
    """
    AI Agent that uses LLM to:
    1. Extract trademark keywords from user questions
    2. Search USPTO database
    3. Analyze results with LLM intelligence using RAG (legal context)
    4. Provide professional recommendations
    """
    
    def __init__(self, openai_api_key: str = None, rapidapi_key: str = None):
        """Initialize the LLM Trademark Agent"""
        self.config = get_config()
        
        # Override config with provided keys if available
        if openai_api_key:
            self.config.OPENAI_API_KEY = openai_api_key
        if rapidapi_key:
            self.config.RAPIDAPI_KEY = rapidapi_key
            
        # Validate configuration
        if not self.config.validate_config():
            raise ValueError("Missing required API keys. Check your .env file or provide keys directly.")
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        
        # Initialize proper RAG system with ChromaDB
        if self.config.RAG_ENABLED:
            self.rag_system = TrademarkRAGSystem()
            self.rag_system.initialize_knowledge_base()
            print("📚 Proper RAG System: Initialized with ChromaDB")
        else:
            self.rag_system = None
            print("📚 RAG System: Disabled")
        
        print(f"🤖 LLM Trademark Agent initialized with {self.config.LLM_MODEL}")
        self.config.print_config_summary()
        if self.config.RAG_ENABLED:
            print("📚 RAG System: Enhanced with ChromaDB vector database")
    
    def _get_rag_context_for_analysis(self, keywords: List[str], search_results: Dict) -> str:
        """Get relevant RAG context using proper vector database search"""
        if not self.config.RAG_ENABLED or not self.rag_system:
            return ""
        
        try:
            # Use the proper RAG system to get relevant legal context
            legal_context = self.rag_system.get_legal_context_for_analysis(keywords, search_results)
            return legal_context
        except Exception as e:
            print(f"❌ Error getting RAG context: {e}")
            return self._get_fallback_legal_context()
    
    def _get_fallback_legal_context(self) -> str:
        """Fallback legal context when RAG system fails"""
        return """
        **BASIC TRADEMARK LAW PRINCIPLES:**
        
        **Trademark Distinctiveness**: Marks must be distinctive to be protectable. Fanciful and arbitrary marks receive the strongest protection.
        
        **Likelihood of Confusion**: The primary test for trademark conflicts considers similarity of marks, goods/services, and trade channels.
        
        **DuPont Factors**: Framework for analyzing trademark conflicts including mark similarity, goods similarity, and market overlap.
        
        **Trademark Strength**: Varies from generic (no protection) to fanciful (strongest protection).
        
        **Registration Requirements**: Must be distinctive, not primarily descriptive, and not conflict with existing marks.
        """
    

    
    def extract_keywords(self, question: str) -> List[str]:
        """Use LLM to extract trademark-related keywords from user question"""
        # Try available models in order of preference
        models_to_try = self.config.AVAILABLE_MODELS
        
        for model in models_to_try:
            try:
                prompt = self.config.KEYWORD_EXTRACTION_PROMPT.format(question=question)
                
                # Use max_completion_tokens for newer models, max_tokens for older ones
                if 'gpt-4o' in model or 'gpt-4-turbo' in model:
                    response = self.openai_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a trademark expert. Extract only relevant keywords."},
                            {"role": "user", "content": prompt}
                        ],
                        max_completion_tokens=100,
                        temperature=0.1
                    )
                else:
                    response = self.openai_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a trademark expert. Extract only relevant keywords."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=100,
                        temperature=0.1
                    )
                
                keywords_text = response.choices[0].message.content.strip()
                
                if keywords_text == "NO_KEYWORDS":
                    return []
                
                # Parse keywords from LLM response
                keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
                
                # Clean up any "Keywords:" prefix that the LLM might add
                cleaned_keywords = []
                for kw in keywords:
                    if kw.startswith('Keywords:'):
                        kw = kw.replace('Keywords:', '').strip()
                    if kw:
                        cleaned_keywords.append(kw)
                
                print(f"🔍 Extracted keywords: {cleaned_keywords}")
                return cleaned_keywords
                
            except Exception as e:
                print(f"❌ Error with model {model}: {e}")
                if model == models_to_try[-1]:  # Last model failed
                    print("🔄 All models failed, using fallback keyword extraction")
                    return self._fallback_keyword_extraction(question)
                continue
        
        return []
    
    def _fallback_keyword_extraction(self, question: str) -> List[str]:
        """Enhanced fallback keyword extraction when LLM fails"""
        keywords = []
        
        # Extract potential brand names (words in quotes or capitalized)
        
        # First priority: Extract quoted names (e.g., 'TechFlow', "DataFlow")
        quoted_names = re.findall(r'[\'"]([^\'"]*)[\'"]', question)
        keywords.extend(quoted_names)
        
        # Second priority: Extract capitalized compound words that look like brand names
        # Look for patterns like TechFlow, DataFlow, CloudSync, etc.
        compound_brands = re.findall(r'\b[A-Z][a-z]+[A-Z][a-z]*\b', question)
        keywords.extend(compound_brands)
        
        # Third priority: Extract single capitalized words that might be brands
        words = question.split()
        for word in words:
            # Skip common words and focus on potential brand names
            if (word[0].isupper() and len(word) > 2 and 
                word not in ['I', 'The', 'Can', 'What', 'How', 'Compare', 'For', 'With', 'About', 'From', 'Is', 'My', 'App', 'Company', 'Business']):
                keywords.append(word)
        
        # Fourth priority: Look for distinctive phrases (2-3 word combinations)
        # Find patterns like "Tech Flow", "Data Flow", "Cloud Sync"
        for i in range(len(words) - 1):
            if (words[i][0].isupper() and words[i+1][0].isupper() and 
                len(words[i]) > 2 and len(words[i+1]) > 2):
                phrase = f"{words[i]} {words[i+1]}"
                if phrase not in keywords:
                    keywords.append(phrase)
        
        # Fifth priority: Look for industry-specific terms that might be part of brand names
        industry_terms = ['tech', 'data', 'cloud', 'digital', 'smart', 'pro', 'plus', 'max', 'ultra', 'premium']
        for word in words:
            if (word.lower() in industry_terms and word not in keywords and 
                len(word) > 2):
                keywords.append(word)
        
        # Remove duplicates and clean
        keywords = list(set([kw.strip() for kw in keywords if kw.strip()]))
        
        # If still no keywords, try to extract meaningful terms
        if not keywords:
            # Look for any word that might be a brand (longer than 3 chars, alphabetic)
            potential_brands = [word for word in words if len(word) > 3 and word.isalpha() and word.islower()]
            keywords = potential_brands[:2]  # Limit to 2 keywords
        
        # Filter out very generic terms
        generic_terms = ['app', 'software', 'company', 'business', 'service', 'product', 'brand', 'name']
        keywords = [kw for kw in keywords if kw.lower() not in generic_terms]
        
        print(f"🔍 Enhanced fallback extracted keywords: {keywords}")
        return keywords
    
    def search_uspto(self, keywords: List[str]) -> Dict[str, Any]:
        """Search USPTO database using extracted keywords with enhanced detail gathering"""
        if not keywords:
            return {"error": "No keywords to search"}
        
        all_results = {}
        
        for keyword in keywords:
            try:
                print(f"🔎 Searching USPTO for: {keyword}")
                
                # Use the correct API endpoint structure: /v1/trademarkSearch/{keyword}/all
                url = f"{self.config.BASE_URL}/v1/trademarkSearch/{keyword}/all"
                headers = self.config.get_api_headers()
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    results = response.json()
                    
                    # Enhance results with additional analysis data
                    if 'items' in results and results['items']:
                        enhanced_items = []
                        for item in results['items']:
                            enhanced_item = self._enhance_trademark_data(item)
                            enhanced_items.append(enhanced_item)
                        results['items'] = enhanced_items
                    
                    # Limit results to avoid context length issues
                    max_results = self.config.MAX_LLM_RESULTS
                    if 'items' in results and len(results['items']) > max_results:
                        original_count = len(results['items'])
                        print(f"📊 Limiting results from {original_count} to top {max_results} for LLM analysis")
                        results['items'] = results['items'][:max_results]
                        results['limited'] = True
                        results['original_count'] = original_count
                    
                    all_results[keyword] = results
                    # The API returns 'items' instead of 'results'
                    items_count = len(results.get('items', []))
                    print(f"✅ Found {items_count} results for '{keyword}' (sending to LLM)")
                else:
                    print(f"❌ USPTO API error for '{keyword}': {response.status_code}")
                    # Provide fallback data structure for analysis
                    all_results[keyword] = {
                        "results": [],
                        "error": f"API error: {response.status_code}",
                        "fallback": True
                    }
                    
            except Exception as e:
                print(f"❌ Error searching USPTO for '{keyword}': {e}")
                all_results[keyword] = {"error": str(e)}
        
        return all_results
    
    def _enhance_trademark_data(self, item: Dict) -> Dict:
        """Enhance trademark data with additional analysis fields"""
        enhanced = item.copy()
        
        # Add risk assessment based on various factors
        enhanced['risk_analysis'] = self._assess_trademark_risk(item)
        
        # Add similarity score to search keyword
        enhanced['similarity_score'] = self._calculate_similarity_score(item)
        
        # Add market relevance assessment
        enhanced['market_relevance'] = self._assess_market_relevance(item)
        
        # Add blocking potential assessment
        enhanced['blocking_potential'] = self._assess_blocking_potential(item)
        
        return enhanced
    
    def _validate_and_refine_keywords(self, keywords: List[str], original_question: str) -> List[str]:
        """Validate and refine extracted keywords to ensure they're meaningful for trademark searching"""
        refined_keywords = []
        
        # Common generic terms that should be filtered out
        generic_terms = {
            'app', 'software', 'company', 'business', 'service', 'product', 'brand', 'name',
            'the', 'and', 'or', 'for', 'with', 'my', 'can', 'is', 'are', 'will', 'would',
            'should', 'could', 'may', 'might', 'available', 'trademark', 'register', 'use'
        }
        
        # Industry-specific generic terms
        tech_generic = {'tech', 'digital', 'online', 'web', 'mobile', 'cloud', 'data', 'smart'}
        business_generic = {'solutions', 'systems', 'group', 'inc', 'llc', 'corp', 'ltd'}
        
        for keyword in keywords:
            # Clean the keyword
            clean_keyword = keyword.strip()
            if not clean_keyword:
                continue
            
            # Skip if it's too short (less than 2 characters)
            if len(clean_keyword) < 2:
                continue
            
            # Skip if it's entirely generic
            if clean_keyword.lower() in generic_terms:
                continue
            
            # Skip if it's just a single generic tech/business term
            if (clean_keyword.lower() in tech_generic or 
                clean_keyword.lower() in business_generic) and len(clean_keyword) <= 5:
                continue
            
            # Check if it contains meaningful content (not just generic words)
            words = clean_keyword.split()
            if len(words) == 1:
                # Single word - must be distinctive
                if len(clean_keyword) >= 3 and not clean_keyword.lower() in generic_terms:
                    refined_keywords.append(clean_keyword)
            else:
                # Multi-word phrase - check if it has distinctive elements
                distinctive_words = [w for w in words if w.lower() not in generic_terms and len(w) >= 2]
                if len(distinctive_words) >= 1:
                    refined_keywords.append(clean_keyword)
        
        # If we still have too many keywords, prioritize the most distinctive ones
        if len(refined_keywords) > 3:
            # Sort by distinctiveness (longer, more unique keywords first)
            refined_keywords.sort(key=lambda x: (len(x), -x.count(' ')), reverse=True)
            refined_keywords = refined_keywords[:3]
        
        # If no keywords remain, try to extract something meaningful from the question
        if not refined_keywords:
            # Look for any capitalized words that might be brand names
            potential_brands = re.findall(r'\b[A-Z][a-z]{2,}\b', original_question)
            refined_keywords = [brand for brand in potential_brands if brand.lower() not in generic_terms][:2]
        
        print(f"🔍 Refined keywords for searching: {refined_keywords}")
        return refined_keywords
    
    def _assess_trademark_risk(self, item: Dict) -> Dict:
        """Assess the risk level of a trademark conflict"""
        risk_factors = {
            'name_similarity': 'low',
            'goods_similarity': 'low',
            'market_overlap': 'low',
            'overall_risk': 'low'
        }
        
        # Analyze name similarity
        mark_name = item.get('keyword', '')
        if mark_name and isinstance(mark_name, str):
            mark_name = mark_name.lower()
            # Simple similarity scoring (can be enhanced with more sophisticated algorithms)
            if len(mark_name) <= 3:
                risk_factors['name_similarity'] = 'medium'
            elif len(mark_name) <= 5:
                risk_factors['name_similarity'] = 'medium'
            else:
                risk_factors['name_similarity'] = 'high'
        
        # Analyze goods/services similarity (if available)
        goods = item.get('goods_services', '')
        if goods and isinstance(goods, str):
            # Check for software/tech related terms
            tech_terms = ['software', 'app', 'computer', 'digital', 'online', 'web', 'mobile']
            if any(term in goods.lower() for term in tech_terms):
                risk_factors['goods_similarity'] = 'high'
                risk_factors['market_overlap'] = 'high'
        
        # Overall risk assessment
        high_risk_count = sum(1 for factor in risk_factors.values() if factor == 'high')
        if high_risk_count >= 2:
            risk_factors['overall_risk'] = 'high'
        elif high_risk_count >= 1:
            risk_factors['overall_risk'] = 'medium'
        
        return risk_factors
    
    def _calculate_similarity_score(self, item: Dict) -> float:
        """Calculate a simple similarity score (0-1) for the trademark"""
        mark_name = item.get('keyword', '')
        if not mark_name or not isinstance(mark_name, str):
            return 0.0
        
        # Simple scoring based on length and common patterns
        score = 0.5  # Base score
        
        # Adjust based on length (shorter names are more distinctive)
        if len(mark_name) <= 3:
            score += 0.3
        elif len(mark_name) <= 5:
            score += 0.2
        elif len(mark_name) <= 7:
            score += 0.1
        
        # Adjust based on descriptiveness
        descriptive_terms = ['tech', 'app', 'soft', 'data', 'cloud', 'web', 'mobile']
        if any(term in mark_name.lower() for term in descriptive_terms):
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _assess_market_relevance(self, item: Dict) -> str:
        """Assess how relevant the trademark is to the user's market"""
        goods = item.get('goods_services', '')
        if not goods or not isinstance(goods, str):
            return 'unknown'
        
        # Check for software/tech market relevance
        tech_indicators = ['software', 'app', 'computer', 'digital', 'online', 'web', 'mobile', 'technology']
        if any(indicator in goods.lower() for indicator in tech_indicators):
            return 'high'
        
        # Check for general business relevance
        business_indicators = ['business', 'service', 'consulting', 'management']
        if any(indicator in goods.lower() for indicator in business_indicators):
            return 'medium'
        
        return 'low'
    
    def _assess_blocking_potential(self, item: Dict) -> str:
        """Assess whether this trademark could block the user's registration"""
        status = item.get('status_label', '')
        if not status or not isinstance(status, str):
            return 'unknown'
            
        status = status.lower()
        filing_date = item.get('filing_date', '')
        
        # Dead or abandoned marks don't block
        if 'dead' in status or 'abandoned' in status or 'cancelled' in status:
            return 'none'
        
        # Live marks have blocking potential
        if 'live' in status or 'registered' in status:
            return 'high'
        
        # Pending applications have medium blocking potential
        if 'pending' in status or 'published' in status:
            return 'medium'
        
        return 'unknown'
    
    def analyze_with_llm(self, original_question: str, keywords: List[str], search_results: Dict) -> str:
        """Use LLM to analyze USPTO search results with RAG-enhanced chain-of-thought reasoning"""
        # Try available models in order of preference
        models_to_try = self.config.AVAILABLE_MODELS
        
        for model in models_to_try:
            try:
                # Create a RAG-enhanced analysis prompt with chain-of-thought
                if self.config.RAG_ENABLED:
                    rag_prompt = self._create_rag_enhanced_prompt(
                        original_question, keywords, search_results
                    )
                else:
                    rag_prompt = self._create_chain_of_thought_prompt(
                        original_question, keywords, search_results
                    )
                
                # Use max_completion_tokens for newer models, max_tokens for older ones
                if 'gpt-4o' in model or 'gpt-4-turbo' in model:
                    response = self.openai_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a trademark attorney and brand strategy expert with access to USPTO trademark law. Use chain-of-thought reasoning and legal principles to show your analysis step by step."},
                            {"role": "user", "content": rag_prompt}
                        ],
                        max_completion_tokens=2500,  # Increased for RAG-enhanced reasoning
                        temperature=0.2  # Lower temperature for more consistent reasoning
                    )
                else:
                    response = self.openai_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a trademark attorney and brand strategy expert with access to USPTO trademark law. Use chain-of-thought reasoning and legal principles to show your analysis step by step."},
                            {"role": "user", "content": rag_prompt}
                        ],
                        max_tokens=2500,  # Increased for RAG-enhanced reasoning
                        temperature=0.2  # Lower temperature for more consistent reasoning
                    )
                
                analysis = response.choices[0].message.content.strip()
                return analysis
                
            except Exception as e:
                print(f"❌ Error with model {model}: {e}")
                if model == models_to_try[-1]:  # Last model failed
                    print("🔄 All models failed, using fallback analysis")
                    return self._fallback_analysis(original_question, keywords, search_results)
                continue
        
        return "Error during LLM analysis: All models failed"
    
    def _create_rag_enhanced_prompt(self, question: str, keywords: List[str], search_results: Dict) -> str:
        """Create a RAG-enhanced analysis prompt with legal context"""
        
        # Build a summary of the enhanced data for the LLM
        analysis_summary = self._build_analysis_summary(search_results)
        
        # Get RAG context for the analysis
        rag_context = self._get_rag_context_for_analysis(keywords, search_results)
        
        prompt = f"""
        **TRADEMARK ANALYSIS TASK WITH LEGAL FRAMEWORK**
        
        User Question: {question}
        Keywords to Analyze: {', '.join(keywords)}
        
        **AVAILABLE DATA FOR ANALYSIS:**
        {analysis_summary}
        
        **LEGAL FRAMEWORK FROM USPTO TRADEMARK LAW:**
        {rag_context}
        
        **RAG-ENHANCED CHAIN-OF-THOUGHT ANALYSIS REQUIRED:**
        
        Please follow this exact format for your response, applying legal principles:
        
        **🧠 STEP-BY-STEP LEGAL REASONING:**
        [Show your legal analysis process step by step, examining each conflict using trademark law principles]
        
        **📊 DETAILED CONFLICT ANALYSIS WITH LEGAL BASIS:**
        [For each keyword, analyze each conflict with specific legal reasoning using DuPont factors and distinctiveness analysis]
        
        **⚖️ LEGAL ASSESSMENT:**
        [Provide legal assessment of trademark availability based on USPTO standards]
        
        **🎯 FINAL ASSESSMENT WITH LEGAL REASONING:**
        [Provide your final conclusion with clear legal reasoning]
        
        **⚠️ RISK ANALYSIS USING LEGAL PRINCIPLES:**
        [Detail specific risks with legal explanations using trademark law concepts]
        
        **💡 LEGALLY SOUND RECOMMENDATIONS:**
        [Provide actionable advice with legal reasoning]
        
        **🔍 ALTERNATIVE SUGGESTIONS WITH LEGAL BASIS:**
        [Suggest modifications with explanation of why they might work legally]
        
        **IMPORTANT**: 
        1. Use the legal framework provided to inform your analysis
        2. Apply trademark law principles (DuPont factors, distinctiveness, etc.)
        3. Show your legal reasoning for each conclusion
        4. Explain WHY each conflict is or isn't a problem using legal standards
        5. Provide legally accurate assessments and recommendations
        """
        
        return prompt
    
    def _create_chain_of_thought_prompt(self, question: str, keywords: List[str], search_results: Dict) -> str:
        """Create a structured chain-of-thought prompt for trademark analysis"""
        
        # Build a summary of the enhanced data for the LLM
        analysis_summary = self._build_analysis_summary(search_results)
        
        # Get RAG context for the analysis
        rag_context = self._get_rag_context_for_analysis(keywords, search_results)
        
        prompt = f"""
        **TRADEMARK ANALYSIS TASK**
        
        User Question: {question}
        Keywords to Analyze: {', '.join(keywords)}
        
        **AVAILABLE DATA FOR ANALYSIS:**
        {analysis_summary}
        
        **RAG LEGAL CONTEXT:**
        {rag_context}
        
        **CHAIN-OF-THOUGHT ANALYSIS REQUIRED:**
        
        Please follow this exact format for your response:
        
        **🧠 STEP-BY-STEP REASONING:**
        [Show your analysis process step by step, examining each conflict individually]
        
        **📊 DETAILED CONFLICT ANALYSIS:**
        [For each keyword, analyze each conflict with specific reasoning]
        
        **🎯 FINAL ASSESSMENT:**
        [Provide your final conclusion with clear reasoning]
        
        **⚠️ RISK ANALYSIS:**
        [Detail specific risks with explanations]
        
        **💡 RECOMMENDATIONS:**
        [Provide actionable advice with reasoning]
        
        **🔍 ALTERNATIVE SUGGESTIONS:**
        [Suggest modifications with explanation of why they might work]
        
        **IMPORTANT**: 
        1. Use the enhanced data provided (risk_analysis, similarity_score, market_relevance, blocking_potential)
        2. Show your reasoning for each conclusion
        3. Explain WHY each conflict is or isn't a problem
        4. Provide specific, actionable advice
        """
        
        return prompt
    
    def _build_analysis_summary(self, search_results: Dict) -> str:
        """Build a structured summary of the enhanced search results for LLM analysis"""
        summary_parts = []
        
        for keyword, results in search_results.items():
            if 'error' in results:
                summary_parts.append(f"❌ {keyword}: {results['error']}")
                continue
                
            items = results.get('items', [])
            if not items:
                summary_parts.append(f"✅ {keyword}: No conflicts found")
                continue
            
            summary_parts.append(f"\n🔍 {keyword.upper()} ANALYSIS:")
            summary_parts.append(f"   Total conflicts found: {len(items)}")
            if results.get('limited'):
                summary_parts.append(f"   Note: Limited to top {self.config.MAX_LLM_RESULTS} of {results.get('original_count', 0)} total results")
            
            # Show enhanced analysis for each conflict
            for i, item in enumerate(items[:5], 1):  # Show top 5 conflicts
                mark_name = item.get('keyword', 'Unknown')
                status = item.get('status_label', 'Unknown')
                goods = item.get('goods_services', 'N/A')
                owner = item.get('owners', [{}])[0].get('name', 'Unknown') if item.get('owners') else 'Unknown'
                
                # Enhanced analysis data
                risk_analysis = item.get('risk_analysis', {})
                similarity_score = item.get('similarity_score', 0.0)
                market_relevance = item.get('market_relevance', 'unknown')
                blocking_potential = item.get('blocking_potential', 'unknown')
                
                summary_parts.append(f"\n   {i}. {mark_name}")
                summary_parts.append(f"      Status: {status}")
                summary_parts.append(f"      Owner: {owner}")
                summary_parts.append(f"      Goods/Services: {goods[:100]}{'...' if len(goods) > 100 else ''}")
                summary_parts.append(f"      Risk Level: {risk_analysis.get('overall_risk', 'unknown')}")
                summary_parts.append(f"      Similarity Score: {similarity_score:.2f}")
                summary_parts.append(f"      Market Relevance: {market_relevance}")
                summary_parts.append(f"      Blocking Potential: {blocking_potential}")
        
        return "\n".join(summary_parts)
    
    def _fallback_analysis(self, question: str, keywords: List[str], search_results: Dict) -> str:
        """Fallback analysis when LLM fails"""
        analysis_parts = []
        
        # Overall assessment - handle both 'results' and 'items' from different API responses
        total_conflicts = 0
        total_original = 0
        for results in search_results.values():
            if 'results' in results:
                total_conflicts += len(results.get('results', []))
            elif 'items' in results:
                total_conflicts += len(results.get('items', []))
                # Track original count if results were limited
                if results.get('limited'):
                    total_original += results.get('original_count', 0)
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
        
        # Add note about limited results if applicable
        if total_original > 0:
            analysis_parts.append(f"\n📊 **Note**: Results were limited to top {self.config.MAX_LLM_RESULTS} for analysis. Total available: {total_original} conflicts.")
        
        # Detailed analysis for each keyword
        analysis_parts.append("\n**Detailed Analysis by Keyword:**")
        
        for keyword, results in search_results.items():
            # Handle both 'results' and 'items' from different API responses
            conflicts = results.get('results', []) or results.get('items', [])
            
            if not conflicts:
                analysis_parts.append(f"\n✅ **{keyword}**: No conflicts found. This appears to be available for trademark registration.")
            else:
                # Show if results were limited
                limit_note = ""
                if results.get('limited'):
                    limit_note = f" (limited to top {self.config.MAX_LLM_RESULTS} of {results.get('original_count', 0)} total)"
                
                analysis_parts.append(f"\n⚠️ **{keyword}**: {len(conflicts)} potential conflict(s) found{limit_note}:")
                for conflict in conflicts[:3]:  # Show first 3 conflicts
                    # Handle different field names from different API responses
                    mark = conflict.get('mark') or conflict.get('keyword', 'Unknown')
                    status = conflict.get('status') or conflict.get('status_label', 'Unknown')
                    owner = conflict.get('owner') or conflict.get('owners', [{}])[0].get('name', 'Unknown') if conflict.get('owners') else 'Unknown'
                    
                    # Enhanced analysis data
                    risk_analysis = conflict.get('risk_analysis', {})
                    similarity_score = conflict.get('similarity_score', 0.0)
                    market_relevance = conflict.get('market_relevance', 'unknown')
                    blocking_potential = conflict.get('blocking_potential', 'unknown')
                    
                    status_emoji = "🟢" if status in ['LIVE', 'active'] else "🟡"
                    risk_emoji = "🔴" if risk_analysis.get('overall_risk') == 'high' else "🟡" if risk_analysis.get('overall_risk') == 'medium' else "🟢"
                    
                    analysis_parts.append(f"   {status_emoji} {mark} - {status} - {owner}")
                    analysis_parts.append(f"      {risk_emoji} Risk: {risk_analysis.get('overall_risk', 'unknown')} | Similarity: {similarity_score:.2f} | Market: {market_relevance} | Blocking: {blocking_potential}")
        
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
        
        analysis_parts.append("\n**Note**: This is a fallback analysis due to LLM unavailability. For more detailed insights, please try again later.")
        
        # Add reasoning summary
        analysis_parts.append("\n**🧠 REASONING SUMMARY:**")
        if total_conflicts == 0:
            analysis_parts.append("• No conflicts found in USPTO database")
            analysis_parts.append("• Keywords appear to be available for trademark registration")
        elif total_conflicts <= 2:
            analysis_parts.append("• Limited conflicts detected - moderate risk")
            analysis_parts.append("• Conflicts may be in different markets or industries")
        else:
            analysis_parts.append("• Multiple conflicts detected - high risk")
            analysis_parts.append("• Professional legal review recommended")
            analysis_parts.append("• Consider alternative brand names")
        
        # Add legal context summary if RAG is enabled
        if self.config.RAG_ENABLED:
            analysis_parts.append("\n**⚖️ LEGAL CONTEXT SUMMARY:**")
            analysis_parts.append("• Analysis based on USPTO trademark law principles")
            analysis_parts.append("• Consider trademark distinctiveness and likelihood of confusion")
            analysis_parts.append("• Evaluate using DuPont factors for comprehensive assessment")
            analysis_parts.append("• Consult with trademark attorney for final legal opinion")
        
        return "\n".join(analysis_parts)
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """
        Main method to process a user question:
        1. Extract keywords with LLM
        2. Search USPTO database
        3. Analyze results with LLM
        4. Return comprehensive response
        """
        print(f"\n🤔 Processing question: {question}")
        print("=" * 50)
        
        # Step 1: Extract keywords using LLM
        keywords = self.extract_keywords(question)
        if not keywords:
            return {
                "error": "No trademark-related keywords found in your question. Please ask about specific brand names, products, or services."
            }
        
        # Step 1.5: Validate and refine keywords
        keywords = self._validate_and_refine_keywords(keywords, question)
        if not keywords:
            return {
                "error": "No valid trademark-related keywords found after validation. Please provide more specific brand names or product names."
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
    
    def get_rag_status(self) -> Dict[str, Any]:
        """Get status of the RAG system"""
        if not self.config.RAG_ENABLED or not self.rag_system:
            return {'status': 'disabled'}
        
        return self.rag_system.get_system_status()
    
    def get_legal_education(self, topic: str = None) -> str:
        """Provide legal education on trademark topics using RAG context"""
        if not self.config.RAG_ENABLED:
            return "RAG system is not enabled. Cannot provide legal education."
        
        if topic:
            # Provide specific topic education
            if 'distinctiveness' in topic.lower():
                return """
                **TRADEMARK DISTINCTIVENESS - Legal Framework:**
                
                **Fanciful/Arbitrary Marks (Strongest Protection):**
                - Examples: "Kodak" for cameras, "Apple" for computers
                - These marks have no meaning related to the goods/services
                - Receive the strongest trademark protection
                - Easier to register and enforce
                
                **Suggestive Marks (Strong Protection):**
                - Examples: "Coppertone" for suntan lotion, "Playboy" for men's magazines
                - Require imagination to connect mark to goods/services
                - Strong protection but may require more evidence of distinctiveness
                
                **Descriptive Marks (Weak Protection):**
                - Examples: "Holiday Inn" for hotels, "Vision Center" for optical services
                - Directly describe the goods/services
                - Require "secondary meaning" (consumer recognition) for protection
                - Higher risk of conflicts and challenges
                
                **Generic Terms (No Protection):**
                - Examples: "Computer" for computers, "Software" for software
                - Cannot be trademarked under any circumstances
                - These terms belong to the public domain
                """
            elif 'confusion' in topic.lower():
                return """
                **LIKELIHOOD OF CONFUSION - DuPont Factors:**
                
                **Primary Factors:**
                1. **Similarity of Marks**: Appearance, sound, meaning
                2. **Similarity of Goods/Services**: Relatedness and overlap
                3. **Trade Channels**: How and where goods/services are sold
                4. **Purchaser Sophistication**: Level of care in purchasing decisions
                
                **Secondary Factors:**
                5. **Strength of Prior Mark**: How distinctive and well-known
                6. **Number of Similar Marks**: Market saturation
                7. **Actual Confusion Evidence**: Real-world confusion examples
                8. **Intent to Deceive**: Bad faith considerations
                
                **Legal Standard**: "Likelihood of confusion" means more than mere possibility
                """
            else:
                return f"Legal education on '{topic}' not available. Available topics: distinctiveness, confusion, registration, infringement"
        else:
            # Provide general legal overview
            return """
            **USPTO TRADEMARK LAW OVERVIEW:**
            
            **Key Legal Concepts:**
            • **Trademark Distinctiveness**: Marks must be distinctive to be protectable
            • **Likelihood of Confusion**: Primary test for trademark conflicts
            • **DuPont Factors**: Framework for analyzing trademark conflicts
            • **Trademark Strength**: Varies from generic (no protection) to fanciful (strongest)
            
            **Registration Requirements:**
            • Must be distinctive
            • Cannot be primarily descriptive
            • Cannot be generic for the goods/services
            • Must not conflict with existing marks
            
            **Legal Analysis Process:**
            1. Assess mark distinctiveness
            2. Identify potential conflicts
            3. Apply DuPont factors
            4. Evaluate likelihood of confusion
            5. Provide legal recommendations
            
            For specific legal advice, consult with a qualified trademark attorney.
            """
    
    def interactive_mode(self):
        """Run the agent in interactive mode with RAG capabilities"""
        print("\n🚀 LLM Trademark AI Agent - Interactive Mode")
        print("Ask questions about trademarks and get intelligent analysis!")
        if self.config.RAG_ENABLED:
            print("📚 RAG System: Enhanced with ChromaDB vector database")
            print("💡 Type 'legal help' for trademark law education")
            print("💡 Type 'rag status' to check RAG system status")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                question = input("🤔 Ask about a trademark: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if question.lower() == 'legal help':
                    print("\n📚 TRADEMARK LAW EDUCATION:")
                    print("=" * 50)
                    print(self.get_legal_education())
                    print("=" * 50)
                    continue
                
                if question.lower().startswith('legal help '):
                    topic = question.lower().replace('legal help ', '').strip()
                    print(f"\n📚 TRADEMARK LAW EDUCATION - {topic.upper()}:")
                    print("=" * 50)
                    print(self.get_legal_education(topic))
                    print("=" * 50)
                    continue
                
                if question.lower() == 'rag status':
                    print("\n📊 RAG SYSTEM STATUS:")
                    print("=" * 50)
                    status = self.get_rag_status()
                    for key, value in status.items():
                        print(f"   {key}: {value}")
                    print("=" * 50)
                    continue
                
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
    """Main entry point"""
    try:
        # Initialize agent
        agent = LLMTrademarkAgent()
        
        # Run interactive mode
        agent.interactive_mode()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n📝 Please check your .env file or provide API keys directly:")
        print("   agent = LLMTrademarkAgent(openai_api_key='your_key', rapidapi_key='your_key')")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
