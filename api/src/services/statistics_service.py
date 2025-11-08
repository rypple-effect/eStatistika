import httpx
from datetime import datetime

from ..config import settings


class StatisticsService:
    def __init__(self):
        self.ollama_host = settings.ollama_host
        self.model_name = settings.model_name

    async def generate_statistics(self, query: str, source: str = "AI Generated") -> dict:
        """
        Generate statistics response using Ollama AI model.
        Returns a dictionary with response, source, and date.
        The response will be in the same language as the query.
        """
        # Create a prompt that instructs the AI to provide statistics with date and source
        # IMPORTANT: Respond in the same language as the user's question
        system_prompt = """You are a helpful statistics assistant. When users ask for statistics, provide clear, well-formatted responses.

CRITICAL: Always respond in the SAME LANGUAGE as the user's question. If the question is in Spanish, respond in Spanish. If it's in French, respond in French. If it's in English, respond in English. Detect the language from the user's query and match it exactly.

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
        
        user_prompt = f"""Please provide statistics for the following query: {query}

IMPORTANT: 
- Respond in the EXACT SAME LANGUAGE as the query above
- Format your response with clear sections, bullet points, and proper spacing
- Make it easy to read and scan
- Use headings, lists, and line breaks for better readability

Structure your response as follows:
1. Brief overview
2. Main statistics (use bullet points if multiple)
3. Date/relevance period
4. Source information
5. Brief explanation/context

Format with proper spacing and structure for maximum readability."""
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                # Use Ollama's chat API for better compatibility
                response = await client.post(
                    f"{self.ollama_host}/api/chat",
                    json={
                        "model": self.model_name,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
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

