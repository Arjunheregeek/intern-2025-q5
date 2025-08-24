from typing import Dict, Any, Optional
import re

class PromptTemplate:
    """A reusable prompt template system for generating structured prompts with variables."""
    
    def __init__(self, template: str, required_variables: list = None):
        self.template = template
        self.required_variables = required_variables or []
        self._validate_template()
    
    def _validate_template(self):
        """Validate that the template contains required variables."""
        template_vars = self._extract_variables()
        for var in self.required_variables:
            if var not in template_vars:
                raise ValueError(f"Required variable '{var}' not found in template")
    
    def _extract_variables(self) -> set:
        """Extract variable names from template."""
        return set(re.findall(r'\{(\w+)\}', self.template))
    
    def format(self, **kwargs) -> str:
        """Format the template with provided variables."""
        missing_vars = [var for var in self.required_variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        self._validate_variables(kwargs)
        
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Template variable {e} not provided")
    
    def _validate_variables(self, variables: Dict[str, Any]):
        """Validate variable values based on specific rules."""
        pass

class TweetTemplate(PromptTemplate):
    """Specialized template for generating tweets with validation for tweet-specific parameters."""
    
    VALID_TONES = ['professional', 'humorous', 'casual', 'excited', 'informative', 'sarcastic']
    
    def __init__(self):
        template = """Generate a {tone} tweet about {topic}. 
The tweet should be engaging and appropriate for social media.
Maximum words: {max_words}
Requirements:
- Keep it concise and impactful
- Use appropriate tone throughout
- Make it shareable and relevant
- Do not include hashtags or mentions

Tweet:"""
        
        super().__init__(template, required_variables=['topic', 'tone', 'max_words'])
    
    def _validate_variables(self, variables: Dict[str, Any]):
        """Validate tweet-specific parameters."""
        tone = variables.get('tone', '').lower()
        if tone not in self.VALID_TONES:
            raise ValueError(f"Invalid tone '{tone}'. Must be one of: {', '.join(self.VALID_TONES)}")
        
        max_words = variables.get('max_words')
        if not isinstance(max_words, int) or max_words < 5 or max_words > 50:
            raise ValueError("max_words must be an integer between 5 and 50")
        
        topic = variables.get('topic', '').strip()
        if not topic or len(topic) < 2:
            raise ValueError("topic must be a non-empty string with at least 2 characters")
    
    def generate_tweet_prompt(self, topic: str, tone: str, max_words: int) -> str:
        """Convenience method to generate a tweet prompt."""
        return self.format(topic=topic, tone=tone.lower(), max_words=max_words)

def create_custom_template(template_string: str, required_vars: list = None) -> PromptTemplate:
    """Factory function to create custom prompt templates."""
    return PromptTemplate(template_string, required_vars)
