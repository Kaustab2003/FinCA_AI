"""
Test RecommendationAgent functionality
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.agents.recommendation_agent import RecommendationAgent

async def test_recommendation_agent():
    """Test the recommendation agent"""
    print("Testing RecommendationAgent...")

    agent = RecommendationAgent()

    # Test context
    test_context = {
        'user_id': 'test_user',
        'monthly_income': 50000,
        'monthly_expenses': 30000,
        'monthly_savings': 10000,
        'age': 28,
        'risk_profile': 'moderate',
        'existing_goals': [],
        'budget_data': {'income': 50000, 'expenses': 30000, 'savings': 10000}
    }

    try:
        response = await agent.process("Recommend emergency fund goals", test_context)
        print("✅ Agent Response:")
        print(f"Content: {response.content[:200]}...")
        print(f"Confidence: {response.confidence}")
        print(f"Agent Name: {response.agent_name}")
        return True
    except Exception as e:
        print(f"❌ Agent failed: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_recommendation_agent())
    print(f"Test result: {'PASSED' if result else 'FAILED'}")