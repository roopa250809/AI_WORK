"""Claude LLM integration for health insights."""

from typing import Optional, Dict, Any
import os
import json
from anthropic import Anthropic


class HealthInsightsLLM:
    """Claude-powered health insights assistant."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM client.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=key)
        self.conversation_history = []
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for health insights."""
        return """You are a personal health analytics assistant trained to analyze WHOOP health data.

Your role is to:
1. Answer questions about sleep quality, workout performance, and recovery
2. Identify patterns and trends in the user's health data
3. Provide actionable insights based on the data provided
4. Explain correlations between sleep and workouts
5. Suggest improvements based on observed patterns

Guidelines:
- Be concise and specific (avoid long explanations)
- Use the data provided to support your answers
- If data is unavailable for a question, say so clearly
- Focus on what the data actually shows, not speculation
- Provide percentages and metrics when relevant
- Be encouraging but honest about areas for improvement

When given a metrics summary, use it as the foundation for your analysis."""
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def ask_with_context(self, question: str, metrics_context: str) -> str:
        """
        Ask a question with health metrics context.
        
        Args:
            question: User question
            metrics_context: Compact metrics summary
            
        Returns:
            Claude's response
        """
        context_prompt = f"""Here is the user's current health metrics summary:

{metrics_context}

User question: {question}

Please answer based on the provided data and metrics."""
        
        self.add_message("user", context_prompt)
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            system=self.system_prompt,
            messages=self.conversation_history
        )
        
        assistant_message = response.content[0].text
        self.add_message("assistant", assistant_message)
        
        return assistant_message
    
    def ask(self, question: str) -> str:
        """
        Ask a simple question without explicit context.
        
        Args:
            question: User question
            
        Returns:
            Claude's response
        """
        self.add_message("user", question)
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            system=self.system_prompt,
            messages=self.conversation_history
        )
        
        assistant_message = response.content[0].text
        self.add_message("assistant", assistant_message)
        
        return assistant_message
    
    def reset_conversation(self) -> None:
        """Reset conversation history."""
        self.conversation_history = []
    
    @staticmethod
    def format_metrics_for_claude(metrics: Dict[str, Any]) -> str:
        """
        Format metrics dictionary into readable text for Claude.
        
        Args:
            metrics: Dictionary of metrics
            
        Returns:
            Formatted text summary
        """
        summary = "Health Metrics Summary:\n"
        summary += f"- Average Sleep Duration: {metrics.get('avg_sleep_duration', 0):.1f} hours\n"
        summary += f"- Average Sleep Quality: {metrics.get('avg_sleep_quality', 0):.0f}/100\n"
        summary += f"- Sleep Consistency Score: {metrics.get('sleep_consistency_score', 0):.0f}/100\n"
        summary += f"- Total Workouts: {metrics.get('total_workouts', 0)}\n"
        summary += f"- Average Workout Duration: {metrics.get('avg_workout_duration', 0):.0f} min\n"
        summary += f"- Average Workout Intensity: {metrics.get('avg_workout_intensity', 0):.0f}/100\n"
        summary += f"- Workout Frequency: {metrics.get('workout_frequency', 0):.1f} per day\n"
        summary += f"- Sleep-Workout Correlation: {metrics.get('sleep_workout_correlation', 0):.2f}\n"
        
        recovery = metrics.get('time_recovery', {})
        summary += f"- Average Time to Sleep After Workout: {recovery.get('avg_hours', 0):.1f} hours\n"
        
        return summary
