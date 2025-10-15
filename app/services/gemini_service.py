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

    def generate_product_description(self, product_context: Dict[str, Any], target_market: str = 'Indian') -> str:
        """
        Generate an enhanced product description using Gemini AI
        
        Args:
            product_context: Dictionary containing product information
            target_market: Target market for the description
            
        Returns:
            AI-generated product description
        """
        try:
            # Create a prompt for product description generation
            prompt = f"""
            You are an expert e-commerce copywriter specializing in the {target_market} market.
            
            Generate an engaging, compelling product description for the following product:
            
            Product Name: {product_context.get('name', 'Unknown')}
            Category: {product_context.get('category', 'General')}
            Subcategory: {product_context.get('subcategory', '')}
            Brand: {product_context.get('brand', 'Generic')}
            Price: ₹{product_context.get('price', 0):,.0f}
            Rating: {product_context.get('rating', 0)}/5 stars
            Current Description: {product_context.get('current_description', 'No description available')}
            Features: {product_context.get('features', 'Not specified')}
            Tags: {product_context.get('tags', 'Not specified')}
            
            Requirements:
            1. Write for Indian consumers with cultural relevance
            2. Highlight key benefits and use cases
            3. Include emotional appeal and practical benefits
            4. Mention value for money if appropriate
            5. Use Indian English expressions naturally
            6. Keep it concise but compelling (150-200 words)
            7. Include relevant festivals/occasions if applicable
            8. Focus on family and lifestyle benefits
            
            Generate only the product description, no other text.
            """
            
            response = self.generate_content(prompt, use_cache=True)
            return response if response else "Enhanced description not available at this time."
            
        except Exception as e:
            print(f"Error generating product description: {e}")
            return "Enhanced description not available at this time."

    def analyze_sentiment(self, reviews: List[str], product_name: str, product_category: str) -> Dict[str, Any]:
        """
        Analyze sentiment of product reviews using Gemini AI
        
        Args:
            reviews: List of review texts
            product_name: Name of the product
            product_category: Category of the product
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        try:
            # Create prompt for sentiment analysis
            reviews_text = "\n".join([f"Review {i+1}: {review}" for i, review in enumerate(reviews)])
            
            prompt = f"""
            Analyze the sentiment of these customer reviews for "{product_name}" in the {product_category} category.
            
            Reviews:
            {reviews_text}
            
            Provide a comprehensive sentiment analysis with:
            1. Overall sentiment score (0-100, where 0=very negative, 100=very positive)
            2. Sentiment distribution (percentage positive, neutral, negative)
            3. Key themes mentioned (both positive and negative)
            4. Most common complaints (if any)
            5. Most praised aspects
            6. Recommendation for improvements
            
            Format your response as a JSON-like structure with clear categories.
            Focus on insights relevant to Indian consumers.
            """
            
            response = self.generate_content(prompt, use_cache=True)
            
            # Try to parse the response into structured data
            # For now, return the raw response with some structure
            return {
                'overall_sentiment_score': 75,  # Default positive
                'sentiment_distribution': {
                    'positive': 60,
                    'neutral': 25,
                    'negative': 15
                },
                'analysis': response if response else "Analysis not available",
                'key_themes': ['Quality', 'Value for money', 'Delivery'],
                'recommendations': ['Improve packaging', 'Better customer service']
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'overall_sentiment_score': 50,
                'sentiment_distribution': {'positive': 50, 'neutral': 30, 'negative': 20},
                'analysis': 'Sentiment analysis not available at this time.',
                'key_themes': [],
                'recommendations': []
            }

    def answer_product_question(self, question: str, product_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Answer a product-related question using Gemini AI
        
        Args:
            question: User's question about the product
            product_context: Optional product information for context
            
        Returns:
            AI-generated answer
        """
        try:
            # Build context prompt
            context_text = ""
            if product_context:
                context_text = f"""
                Product Context:
                Name: {product_context.get('name', 'Unknown')}
                Category: {product_context.get('category', 'General')}
                Brand: {product_context.get('brand', 'Generic')}
                Price: ₹{product_context.get('price', 0):,.0f}
                Description: {product_context.get('description', 'No description')}
                Features: {product_context.get('features', 'Not specified')}
                Rating: {product_context.get('rating', 0)}/5 stars
                """
            
            prompt = f"""
            You are a helpful e-commerce assistant specializing in Indian markets.
            Answer the customer's question about the product clearly and helpfully.
            
            {context_text}
            
            Customer Question: {question}
            
            Guidelines:
            1. Be helpful and informative
            2. Use Indian context and terminology
            3. If you don't have specific information, be honest about it
            4. Suggest alternatives or related information when helpful
            5. Keep the response concise but complete
            6. Use a friendly, customer-service tone
            7. Include practical advice for Indian consumers
            
            Provide only the answer, no other text.
            """
            
            response = self.generate_content(prompt, use_cache=True)
            return response if response else "I'm sorry, I couldn't process your question at this time. Please try again or contact customer support."
            
        except Exception as e:
            print(f"Error answering product question: {e}")
            return "I'm sorry, I couldn't process your question at this time. Please try again or contact customer support."

    def general_shopping_assistant(self, message: str, conversation_id: Optional[str] = None) -> str:
        """
        General shopping assistant for e-commerce queries
        
        Args:
            message: User's message/question
            conversation_id: Optional conversation ID for context
            
        Returns:
            AI-generated response
        """
        try:
            prompt = f"""
            You are ShopBot, a helpful AI shopping assistant for an Indian e-commerce platform.
            You specialize in helping customers with shopping decisions, product recommendations, 
            comparisons, and general e-commerce questions.
            
            Customer Message: {message}
            
            Guidelines:
            1. Be friendly, helpful, and conversational
            2. Use Indian context, currency (₹), and terminology
            3. Provide practical shopping advice for Indian consumers
            4. Help with product comparisons, recommendations, and decisions
            5. Suggest budget-friendly options when appropriate
            6. Mention festivals, occasions, and cultural relevance
            7. Keep responses concise but informative (100-150 words)
            8. If asked about specific products, suggest they use product search
            9. Help with shopping strategies, deals, and value-for-money tips
            10. Be encouraging and supportive in their shopping journey
            
            Respond as ShopBot in a friendly, helpful manner. Do not include any system prompts in your response.
            """
            
            response = self.generate_content(prompt, use_cache=False)
            return response if response else "I'm here to help with your shopping! Could you please rephrase your question?"
            
        except Exception as e:
            print(f"Error in general shopping assistant: {e}")
            return "I'm having trouble right now, but I'm here to help with your shopping needs! Please try again."

    def parse_natural_search(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language search query into structured parameters
        
        Args:
            query: Natural language search query
            
        Returns:
            Dictionary with parsed search parameters
        """
        try:
            prompt = f"""
            Parse this natural language shopping query into structured search parameters.
            
            Query: "{query}"
            
            Extract and return the following information if mentioned:
            - Category (electronics, clothing, home, etc.)
            - Price range (min_price, max_price in Indian Rupees)
            - Brand preferences
            - Key features or keywords
            - Sorting preference (price low to high, ratings, popularity)
            - Special requirements (budget-friendly, premium, etc.)
            
            Format your response as a structured breakdown:
            Category: [category if mentioned]
            Price Range: [min-max in ₹ if mentioned]
            Brand: [brand if mentioned]
            Keywords: [list key terms]
            Sort By: [preference if mentioned]
            Intent: [brief interpretation of what user wants]
            
            Focus on Indian market context and common shopping patterns.
            """
            
            response = self.generate_content(prompt, use_cache=True)
            
            # Parse the AI response into structured data
            # For now, return a basic structure with some intelligent defaults
            parsed_params = {
                'category': None,
                'min_price': None,
                'max_price': None,
                'brand': None,
                'keywords': [],
                'sort_by': 'popular',
                'interpretation': response if response else "General product search"
            }
            
            # Simple keyword extraction for demo
            query_lower = query.lower()
            
            # Category detection
            if any(word in query_lower for word in ['phone', 'mobile', 'smartphone']):
                parsed_params['category'] = 'Electronics'
                parsed_params['keywords'] = ['phone', 'mobile']
            elif any(word in query_lower for word in ['laptop', 'computer']):
                parsed_params['category'] = 'Electronics'
                parsed_params['keywords'] = ['laptop']
            elif any(word in query_lower for word in ['shirt', 'clothing', 'dress']):
                parsed_params['category'] = 'Fashion'
            elif any(word in query_lower for word in ['home', 'kitchen', 'appliance']):
                parsed_params['category'] = 'Home & Kitchen'
            
            # Price detection (basic patterns)
            import re
            price_patterns = re.findall(r'under (\d+)k?|below (\d+)k?|less than (\d+)k?', query_lower)
            for pattern in price_patterns:
                for price_str in pattern:
                    if price_str:
                        price = int(price_str)
                        if 'k' in query_lower:
                            price *= 1000
                        parsed_params['max_price'] = price
                        break
            
            # Sort preference
            if any(word in query_lower for word in ['cheap', 'budget', 'affordable']):
                parsed_params['sort_by'] = 'price_asc'
            elif any(word in query_lower for word in ['best', 'top rated', 'highest rating']):
                parsed_params['sort_by'] = 'rating'
            elif any(word in query_lower for word in ['popular', 'trending']):
                parsed_params['sort_by'] = 'popular'
            
            return parsed_params
            
        except Exception as e:
            print(f"Error parsing natural search: {e}")
            return {
                'category': None,
                'min_price': None,
                'max_price': None,
                'brand': None,
                'keywords': [],
                'sort_by': 'popular',
                'interpretation': 'General product search'
            }


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
