import httpx
import json
from datetime import datetime
from typing import AsyncIterator

from ..config import settings


class StatisticsService:
    def __init__(self):
        self.ollama_host = settings.ollama_host
        self.model_name = settings.model_name

    async def generate_statistics(
        self, 
        query: str, 
        source: str = "AI Generated",
        chat_history: list[dict[str, str]] = None
    ) -> dict:
        """
        Generate statistics response using Ollama AI model.
        Returns a dictionary with response, source, and date.
        The response will be in the same language as the query.
        
        Args:
            query: The user's query/question
            source: Source of the statistics (default: "AI Generated")
            chat_history: Optional list of previous messages for context
        """
        # Create a prompt that instructs the AI to provide statistics with date and source
        # Make language instruction the FIRST and MOST IMPORTANT instruction
        system_prompt = """You are a helpful statistics assistant. When users ask for statistics, provide clear, well-formatted responses.

⚠️ CRITICAL LANGUAGE RULE - THIS IS THE MOST IMPORTANT INSTRUCTION:
You MUST respond in the EXACT SAME LANGUAGE as the user's question, regardless of what language it is.
- Detect the language from the user's question automatically
- Respond in that EXACT SAME LANGUAGE - do not translate or change the language
- This applies to ANY language: English, Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Arabic, Russian, Hindi, or any other language
- Match the language EXACTLY - preserve the same language throughout your entire response

FORMATTING REQUIREMENTS:
- Use clear headings and sections
- Use bullet points or numbered lists for multiple statistics
- Use line breaks between sections for readability
- Bold important numbers or key statistics
- Organize information in a logical flow
- Use proper spacing and structure

RESPONSE STRUCTURE:
1. Start with a brief introduction/overview
2. Present the main statistics clearly (use lists if multiple)
3. Include relevant dates or time periods
4. Mention the source of the data
5. Provide a brief explanation or context

Make the response easy to scan and read. Use clear formatting with proper spacing."""
        
        # Build messages list with chat history if provided
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history for context (excluding system messages)
        if chat_history:
            for msg in chat_history:
                if msg.get("role") != "system":
                    messages.append(msg)
        
        # Build user prompt with context awareness
        context_note = ""
        if chat_history:
            context_note = "\n\nNote: You have access to previous conversation context. Use it to provide relevant and contextual statistics."
        
        user_prompt = f"""User's question (respond in the SAME LANGUAGE as this question): {query}{context_note}

⚠️ CRITICAL REMINDER: 
- Detect the language of the question above automatically
- Respond in the EXACT SAME LANGUAGE as the question
- Do NOT translate or change the language
- Use the same language for your entire response

IMPORTANT FORMATTING REQUIREMENTS:
1. START your response by clearly restating the user's question in a highlighted format like this:
   "📋 **Question:** [restate the user's question here]"
   
2. Then provide your response with:
   - Clear sections with headings (use ## for main headings)
   - Bullet points or numbered lists for multiple statistics
   - Line breaks between sections for readability
   - Bold important numbers or key statistics using **text**
   - Proper spacing and structure

3. Structure your response as follows:
   - Start with: "📋 **Question:** [user's question]"
   - Then: Brief overview/introduction
   - Main statistics (use bullet points if multiple)
   - Date/relevance period
   - Source information
   - Brief explanation/context

4. Use clear formatting:
   - Use double line breaks (\\n\\n) between major sections
   - Use single line breaks (\\n) within sections
   - Use markdown-style formatting: **bold** for emphasis, ## for headings
   - Make the response easy to scan and read

Format with proper spacing and structure for maximum readability."""
        
        messages.append({"role": "user", "content": user_prompt})
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                # Use Ollama's chat API for better compatibility
                response = await client.post(
                    f"{self.ollama_host}/api/chat",
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract the response text from the message
                ai_response = data.get("message", {}).get("content", "Unable to generate statistics at this time.")
                if not ai_response:
                    # Fallback: try old format for compatibility
                    ai_response = data.get("response", "Unable to generate statistics at this time.")
                
                # Get current date for metadata
                current_date = datetime.now().strftime("%Y-%m-%d")
                
                return {
                    "response": ai_response,
                    "source": source,
                    "date": current_date,
                    "model": self.model_name,
                }
            except httpx.HTTPError as e:
                # Fallback response if Ollama is unavailable
                current_date = datetime.now().strftime("%Y-%m-%d")
                return {
                    "response": f"I apologize, but I'm unable to generate statistics at this time. Please try again later. Error: {str(e)}",
                    "source": source,
                    "date": current_date,
                    "model": "error",
                }

    async def generate_statistics_stream(
        self,
        query: str,
        source: str = "AI Generated",
        chat_history: list[dict[str, str]] = None
    ) -> AsyncIterator[str]:
        """
        Generate streaming statistics response using Ollama AI model.
        Yields response chunks as they are generated.
        
        Args:
            query: The user's query/question
            source: Source of the statistics (default: "AI Generated")
            chat_history: Optional list of previous messages for context
            
        Yields:
            Response text chunks
        """
        # Create a prompt that instructs the AI to provide statistics with date and source
        system_prompt = """You are a helpful statistics assistant. When users ask for statistics, provide clear, well-formatted responses.

⚠️ CRITICAL LANGUAGE RULE - THIS IS THE MOST IMPORTANT INSTRUCTION:
You MUST respond in the EXACT SAME LANGUAGE as the user's question, regardless of what language it is.
- Detect the language from the user's question automatically
- Respond in that EXACT SAME LANGUAGE - do not translate or change the language
- This applies to ANY language: English, Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Arabic, Russian, Hindi, or any other language
- Match the language EXACTLY - preserve the same language throughout your entire response

FORMATTING REQUIREMENTS:
- Use clear headings and sections
- Use bullet points or numbered lists for multiple statistics
- Use line breaks between sections for readability
- Bold important numbers or key statistics
- Organize information in a logical flow
- Use proper spacing and structure

RESPONSE STRUCTURE:
1. Start with a brief introduction/overview
2. Present the main statistics clearly (use lists if multiple)
3. Include relevant dates or time periods
4. Mention the source of the data
5. Provide a brief explanation or context

Make the response easy to scan and read. Use clear formatting with proper spacing."""
        
        # Build messages list with chat history if provided
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history for context (excluding system messages)
        if chat_history:
            for msg in chat_history:
                if msg.get("role") != "system":
                    messages.append(msg)
        
        # Build user prompt with context awareness
        context_note = ""
        if chat_history:
            context_note = "\n\nNote: You have access to previous conversation context. Use it to provide relevant and contextual statistics."
        
        user_prompt = f"""User's question (respond in the SAME LANGUAGE as this question): {query}{context_note}

⚠️ CRITICAL REMINDER: 
- Detect the language of the question above automatically
- Respond in the EXACT SAME LANGUAGE as the question
- Do NOT translate or change the language
- Use the same language for your entire response

IMPORTANT FORMATTING REQUIREMENTS:
1. START your response by clearly restating the user's question in a highlighted format like this:
   "📋 **Question:** [restate the user's question here]"
   
2. Then provide your response with:
   - Clear sections with headings (use ## for main headings)
   - Bullet points or numbered lists for multiple statistics
   - Line breaks between sections for readability
   - Bold important numbers or key statistics using **text**
   - Proper spacing and structure

3. Structure your response as follows:
   - Start with: "📋 **Question:** [user's question]"
   - Then: Brief overview/introduction
   - Main statistics (use bullet points if multiple)
   - Date/relevance period
   - Source information
   - Brief explanation/context

4. Use clear formatting:
   - Use double line breaks (\\n\\n) between major sections
   - Use single line breaks (\\n) within sections
   - Use markdown-style formatting: **bold** for emphasis, ## for headings
   - Make the response easy to scan and read

Format with proper spacing and structure for maximum readability."""
        
        messages.append({"role": "user", "content": user_prompt})
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                # Use Ollama's chat API with streaming
                async with client.stream(
                    "POST",
                    f"{self.ollama_host}/api/chat",
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "stream": True,
                    },
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                content = chunk.get("message", {}).get("content", "")
                                if content:
                                    yield content
                                if chunk.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
            except httpx.HTTPError as e:
                error_msg = f"I apologize, but I'm unable to generate statistics at this time. Please try again later. Error: {str(e)}"
                yield error_msg

