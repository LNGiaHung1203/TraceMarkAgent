import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for LLM Trademark AI Agent"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    
    # Available models (in order of preference)
    AVAILABLE_MODELS = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo-preview']
    
    # RapidAPI Configuration
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
    RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'uspto-trademark.p.rapidapi.com')
    BASE_URL = "https://uspto-trademark.p.rapidapi.com"
    
    # API Endpoints - Correct USPTO API structure
    ENDPOINTS = {
        'search': "/v1/trademarkSearch/{keyword}/{status}",
        'serial_search': "/v1/serialSearch/{serial_number}",
        'database_status': "/v1/databaseStatus"
    }
    
    # LLM Prompts
    KEYWORD_EXTRACTION_PROMPT = """
    You are a senior trademark attorney and brand strategy expert. Your task is to carefully analyze the user's question and extract the most relevant trademark-related keywords for USPTO database searching.
    
    **ANALYSIS REQUIREMENTS:**
    1. **Read the question carefully** - Understand the user's intent and context
    2. **Identify the core brand/product** - What is the user trying to name or protect?
    3. **Consider the industry/context** - What type of business, product, or service is this for?
    4. **Extract meaningful keywords** - Focus on distinctive, protectable terms, not generic words
    
    **KEYWORD EXTRACTION GUIDELINES:**
    - **Primary Keywords**: The main brand name, product name, or service name the user wants to protect
    - **Secondary Keywords**: Related terms that might be part of the brand identity
    - **Industry Context**: Terms that indicate the business category (if relevant to the search)
    - **Exclude**: Generic words like "the", "and", "for", "my", "app", "company", "business" (unless they're part of a distinctive phrase)
    
    **EXAMPLES:**
    - Question: "Can I name my app Dino?" → Keywords: Dino
    - Question: "Is 'TechFlow Solutions' available for a software company?" → Keywords: TechFlow, TechFlow Solutions
    - Question: "Can I trademark 'CloudSync Pro' for cloud storage?" → Keywords: CloudSync, CloudSync Pro
    - Question: "Is 'Green Earth Organics' available for organic food?" → Keywords: Green Earth, Green Earth Organics
    - Question: "Can I use 'DataFlow Analytics' for my data company?" → Keywords: DataFlow, DataFlow Analytics
    
    **User Question**: {question}
    
    **ANALYSIS**: Think step by step about what the user is asking and what keywords would be most effective for trademark searching.
    
    **Keywords**: (Return only the relevant keywords separated by commas. If no trademark-related keywords found, return "NO_KEYWORDS")
    """
    
    ANALYSIS_PROMPT = """
    You are a trademark attorney and brand strategy expert. Use chain-of-thought reasoning to analyze the USPTO search results step by step.
    
    **Step-by-Step Analysis Process:**
    1. **Examine each trademark conflict individually** - Look at the mark name, goods/services, owner, status, and filing dates
    2. **Assess similarity and risk factors** - Consider phonetic similarity, visual similarity, and relatedness of goods/services
    3. **Evaluate trademark strength** - Determine if existing marks are strong or weak based on descriptiveness
    4. **Analyze market overlap** - Check if goods/services are in the same or related industries
    5. **Consider timing and status** - Recent filings vs. older registrations, live vs. dead marks
    
    **Provide detailed reasoning for each conclusion:**
    - **Trademark Availability Assessment**: Explain WHY each keyword is available or not available
    - **Risk Analysis**: Detail SPECIFIC conflicts with reasoning (not just listing names)
    - **Detailed Conflict Analysis**: For each conflict, explain:
      * Why it's a conflict (similarity in name, goods, or market)
      * Risk level (high/medium/low) with specific reasons
      * Whether it's a blocking conflict or just a consideration
    - **Recommendations**: Provide specific, actionable advice with reasoning
    - **Alternative Suggestions**: Suggest modifications with explanation of why they might work
    
    User's Original Question: {original_question}
    Extracted Keywords: {keywords}
    USPTO Search Results: {search_results}
    
    **IMPORTANT**: Use chain-of-thought reasoning. Show your work step by step, then provide the final analysis.
    """
    
    # RAG Configuration
    RAG_ENABLED = True
    RAG_DOCUMENTS = {
        'uspto_trademark_law': {
            'url': 'https://www.uspto.gov/sites/default/files/documents/tmlaw.pdf',
            'description': 'Official USPTO Trademark Law Manual',
            'key_topics': [
                'trademark distinctiveness',
                'likelihood of confusion',
                'trademark examination',
                'trademark registration requirements',
                'trademark infringement',
                'descriptive marks',
                'generic terms',
                'secondary meaning',
                'trademark strength',
                'market analysis'
            ]
        }
    }
    
    # RAG Prompts
    RAG_CONTEXT_PROMPT = """
    **LEGAL CONTEXT FROM USPTO TRADEMARK LAW:**
    
    {rag_context}
    
    Use this legal framework to inform your analysis and provide legally accurate recommendations.
    """
    
    RAG_ANALYSIS_PROMPT = """
    You are a trademark attorney and brand strategy expert with access to official USPTO trademark law. Use chain-of-thought reasoning and legal principles to analyze the USPTO search results step by step.
    
    **LEGAL FRAMEWORK TO APPLY:**
    {rag_context}
    
    **Step-by-Step Analysis Process:**
    1. **Examine each trademark conflict individually** - Look at the mark name, goods/services, owner, status, and filing dates
    2. **Assess similarity and risk factors** - Consider phonetic similarity, visual similarity, and relatedness of goods/services using legal standards
    3. **Evaluate trademark strength** - Determine if existing marks are strong or weak based on descriptiveness and distinctiveness principles
    4. **Analyze market overlap** - Check if goods/services are in the same or related industries (relevant to likelihood of confusion)
    5. **Consider timing and status** - Recent filings vs. older registrations, live vs. dead marks
    6. **Apply legal principles** - Use trademark law concepts like likelihood of confusion, trademark strength, and market analysis
    
    **Provide detailed reasoning for each conclusion:**
    - **Trademark Availability Assessment**: Explain WHY each keyword is available or not available based on legal principles
    - **Risk Analysis**: Detail SPECIFIC conflicts with reasoning using trademark law concepts
    - **Detailed Conflict Analysis**: For each conflict, explain:
      * Why it's a conflict (similarity in name, goods, or market)
      * Risk level (high/medium/low) with specific legal reasoning
      * Whether it's a blocking conflict or just a consideration
      * Legal basis for your assessment
    - **Recommendations**: Provide specific, actionable advice with legal reasoning
    - **Alternative Suggestions**: Suggest modifications with explanation of why they might work legally
    
    User's Original Question: {original_question}
    Extracted Keywords: {keywords}
    USPTO Search Results: {search_results}
    
    **IMPORTANT**: 
    1. Use chain-of-thought reasoning showing your legal analysis step by step
    2. Apply trademark law principles from the provided legal context
    3. Provide legally accurate assessments and recommendations
    4. Show your work step by step, then provide the final analysis
    """
    
    # Search Parameters
    MAX_SEARCH_RESULTS = 50
    MAX_LLM_RESULTS = int(os.getenv('MAX_LLM_RESULTS', '10'))  # Maximum results to send to LLM to avoid context length issues
    SIMILARITY_THRESHOLD = 0.7
    
    # Risk Levels
    RISK_LEVELS = {
        'HIGH': 'High risk - Strong conflicts detected',
        'MEDIUM': 'Medium risk - Some conflicts detected',
        'LOW': 'Low risk - Minimal conflicts detected',
        'CLEAR': 'Clear - No significant conflicts detected'
    }
    
    @classmethod
    def get_api_headers(cls) -> Dict[str, str]:
        """Get headers for USPTO API requests"""
        return {
            'X-RapidAPI-Key': cls.RAPIDAPI_KEY,
            'X-RapidAPI-Host': cls.RAPIDAPI_HOST
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY is required")
            return False
        if not cls.RAPIDAPI_KEY:
            print("❌ RAPIDAPI_KEY is required")
            return False
        return True
    
    @classmethod
    def print_config_summary(cls):
        """Print configuration summary"""
        print("🔧 Configuration Summary:")
        print(f"   LLM Model: {cls.LLM_MODEL}")
        print(f"   OpenAI API: {'✅ Configured' if cls.OPENAI_API_KEY else '❌ Missing'}")
        print(f"   USPTO API: {'✅ Configured' if cls.RAPIDAPI_KEY else '❌ Missing'}")
        print(f"   Environment: {os.getenv('ENVIRONMENT', 'development')}")
        print(f"   Max LLM Results: {cls.MAX_LLM_RESULTS}")

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv('ENVIRONMENT', 'development')
    if env == 'production':
        return ProductionConfig()
    return DevelopmentConfig()
