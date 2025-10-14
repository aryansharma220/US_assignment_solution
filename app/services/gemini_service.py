"""
Gemini LLM Service
Handles all interactions with Google's Gemini API for generating recommendation explanations
"""
import os
import time
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from config import Config


class GeminiService:
    """
    Service for interacting with Google's Gemini API
    Generates natural language explanations for product recommendations
    """
    
    def __init__(self):
        """Initialize Gemini service with API key"""
        self.api_key = Config.GEMINI_API_KEY
        
        if not self.api_key or self.api_key == 'your_gemini_api_key_here':
            raise ValueError(
                "Gemini API key not configured! "
                "Please set GEMINI_API_KEY in your .env file. "
                "Get your key from: https://makersuite.google.com/app/apikey"
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize the model - using gemini-1.5-flash for better rate limits
        # gemini-2.5-flash has higher free tier limits than gemini-2.5-pro
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generation config
        self.generation_config = {
            'temperature': 0.7,  # Balance creativity and consistency
            'top_p': 0.8,
            'top_k': 40,
            'max_output_tokens': 500,  # Limit response length
        }
        
        # Safety settings (moderate)
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        
        # Cache for repeated requests (simple dict cache)
        self._cache = {}
        self._cache_max_size = 100
    
    def generate_content(self, prompt: str, use_cache: bool = True) -> str:
        """
        Generate content using Gemini API
        
        Args:
            prompt: The prompt to send to Gemini
            use_cache: Whether to use cached responses
            
        Returns:
            Generated text response
        """
        # Check cache
        if use_cache and prompt in self._cache:
            return self._cache[prompt]
        
        try:
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            # Extract text - handle different response formats
            result = None
            try:
                # Try simple text accessor first
                if hasattr(response, 'text') and response.text:
                    result = response.text.strip()
            except ValueError:
                # If response.text fails, use parts accessor
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        # Combine all text parts
                        result = ''.join(part.text for part in candidate.content.parts if hasattr(part, 'text')).strip()
            
            if result:
                # Cache the response
                if use_cache:
                    self._add_to_cache(prompt, result)
                return result
            else:
                return "I apologize, but I couldn't generate an explanation at this time."
                
        except Exception as e:
            error_msg = str(e)
            
            # Handle rate limit errors gracefully
            if '429' in error_msg or 'quota' in error_msg.lower():
                print(f"⚠️  Gemini rate limit exceeded - using fallback explanation")
                return None  # Signal to use fallback
            
            print(f"Error generating content: {error_msg}")
            return None  # Signal to use fallback
    
    def _add_to_cache(self, prompt: str, response: str):
        """Add response to cache with size limit"""
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entry
            self._cache.pop(next(iter(self._cache)))
        self._cache[prompt] = response
    
    def clear_cache(self):
        """Clear the response cache"""
        self._cache.clear()
    
    def explain_recommendation(
        self,
        product: Dict[str, Any],
        user_context: Dict[str, Any],
        recommendation_reason: Dict[str, Any]
    ) -> str:
        """
        Generate a natural language explanation for why a product is recommended
        
        Args:
            product: Product information dictionary
            user_context: User profile and behavior context
            recommendation_reason: Reason dictionary from recommendation engine
            
        Returns:
            Natural language explanation
        """
        prompt = self._build_recommendation_prompt(product, user_context, recommendation_reason)
        return self.generate_content(prompt)
    
    def _build_recommendation_prompt(
        self,
        product: Dict[str, Any],
        user_context: Dict[str, Any],
        recommendation_reason: Dict[str, Any]
    ) -> str:
        """
        Build a detailed prompt for recommendation explanation
        
        Args:
            product: Product details
            user_context: User information
            recommendation_reason: Recommendation reasoning
            
        Returns:
            Formatted prompt string
        """
        # Extract key information
        product_name = product.get('name', 'this product')
        product_category = product.get('category', 'Unknown')
        product_price = product.get('price', 0)
        product_brand = product.get('brand', 'Unknown')
        product_rating = product.get('average_rating', 0)
        
        user_name = user_context.get('user', {}).get('username', 'there')
        user_preferences = user_context.get('content_context', {})
        similar_users = user_context.get('collaborative_context', {})
        
        reason_type = recommendation_reason.get('type', 'hybrid')
        
        # Build contextual prompt
        prompt = f"""You are a helpful e-commerce recommendation assistant. Generate a friendly, personalized explanation for why we're recommending a product to a user.

Product Details:
- Name: {product_name}
- Category: {product_category}
- Brand: {product_brand}
- Price: ${product_price:.2f}
- Rating: {product_rating:.1f}/5.0

User Information:
- Username: {user_name}
"""
        
        # Add user preferences if available
        if user_preferences:
            top_categories = user_preferences.get('top_categories', [])
            top_brands = user_preferences.get('top_brands', [])
            if top_categories:
                prompt += f"- Favorite Categories: {', '.join(top_categories[:3])}\n"
            if top_brands:
                prompt += f"- Favorite Brands: {', '.join(top_brands[:3])}\n"
        
        # Add similar users context
        if similar_users:
            similar_count = similar_users.get('similar_users_count', 0)
            if similar_count > 0:
                prompt += f"- Similar Users: {similar_count} users with similar taste\n"
        
        # Add recommendation reasoning
        prompt += f"\nRecommendation Method: {reason_type}\n"
        
        if reason_type == 'collaborative':
            recommenders = recommendation_reason.get('recommenders_count', 0)
            if recommenders > 0:
                prompt += f"- {recommenders} users with similar taste also liked this product\n"
        elif reason_type == 'content_based':
            matched_category = recommendation_reason.get('matched_category', False)
            matched_brand = recommendation_reason.get('matched_brand', False)
            if matched_category:
                prompt += f"- Matches your interest in {product_category}\n"
            if matched_brand:
                prompt += f"- From {product_brand}, a brand you like\n"
        elif reason_type == 'hybrid':
            prompt += "- Based on both similar users' preferences and your personal taste\n"
        
        prompt += """
Task: Write a brief, friendly explanation (2-3 sentences) of why this product is recommended. 

Guidelines:
1. Be conversational and warm
2. Reference specific reasons why it matches their interests
3. Keep it concise (2-3 sentences maximum)
4. Don't use phrases like "AI recommends" or "algorithm suggests"
5. Make it feel personal and natural
6. End with an encouraging note

Example format: "Based on your interest in [category], we think you'll love [product]. Users with similar taste have given it great reviews, and it's from [brand], one of your favorites. It's a perfect match for your style!"

Generate the explanation:"""
        
        return prompt
    
    def explain_multiple_recommendations(
        self,
        recommendations: List[tuple],
        user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate explanations for multiple recommendations
        
        Args:
            recommendations: List of (product, score, reason) tuples
            user_context: User context dictionary
            
        Returns:
            List of product dictionaries with explanations
        """
        results = []
        
        for product, score, reason in recommendations:
            # Convert product to dict if it's a model object
            if hasattr(product, 'to_dict'):
                product_dict = product.to_dict()
            else:
                product_dict = product
            
            # Generate explanation
            explanation = self.explain_recommendation(
                product_dict,
                user_context,
                reason
            )
            
            # Combine all information
            results.append({
                'product': product_dict,
                'score': round(score, 2),
                'reason': reason,
                'explanation': explanation
            })
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        return results
    
    def generate_product_summary(self, product: Dict[str, Any]) -> str:
        """
        Generate a concise product summary
        
        Args:
            product: Product information
            
        Returns:
            Product summary text
        """
        prompt = f"""Generate a brief, appealing 1-sentence summary for this product:

Product: {product.get('name', 'Product')}
Category: {product.get('category', 'General')}
Brand: {product.get('brand', 'Unknown')}
Price: ${product.get('price', 0):.2f}
Rating: {product.get('average_rating', 0):.1f}/5.0
Description: {product.get('description', 'No description')}

Write an engaging 1-sentence summary that highlights the key appeal:"""
        
        return self.generate_content(prompt)
    
    def test_connection(self) -> bool:
        """
        Test the Gemini API connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.generate_content(
                "Say 'API connection successful' if you can read this.",
                use_cache=False
            )
            return 'successful' in response.lower() or len(response) > 0
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False


# Singleton instance
_gemini_service = None


def get_gemini_service() -> GeminiService:
    """
    Get or create the singleton Gemini service instance
    
    Returns:
        GeminiService instance
    """
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
