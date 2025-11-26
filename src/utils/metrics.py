"""
FinCA Score calculation and financial metrics
"""
from typing import Dict, Any, Tuple
import structlog

logger = structlog.get_logger()

class MetricsCalculator:
    """Calculate FinCA Score and component metrics"""
    
    # Weights for FinCA Score components
    WEIGHTS = {
        'savings_rate': 0.30,      # 30%
        'emergency_fund': 0.25,     # 25%
        'goal_progress': 0.20,      # 20%
        'debt_health': 0.15,        # 15%
        'behavioral': 0.10          # 10%
    }
    
    @staticmethod
    def calculate_savings_rate_score(income: float, savings: float) -> int:
        """
        Calculate savings rate score (0-100)
        
        Args:
            income: Monthly income
            savings: Monthly savings
        
        Returns:
            Score out of 100
        """
        if income <= 0:
            return 0
        
        savings_rate = (savings / income) * 100
        
        # Score mapping
        if savings_rate >= 50:
            return 100
        elif savings_rate >= 40:
            return 90
        elif savings_rate >= 30:
            return 75
        elif savings_rate >= 20:
            return 60
        elif savings_rate >= 10:
            return 40
        else:
            return int(savings_rate * 2)  # 0-10% maps to 0-20 points
    
    @staticmethod
    def calculate_emergency_fund_score(
        monthly_expenses: float,
        emergency_fund: float
    ) -> int:
        """
        Calculate emergency fund score (0-100)
        
        Args:
            monthly_expenses: Average monthly expenses
            emergency_fund: Current emergency fund amount
        
        Returns:
            Score out of 100
        """
        if monthly_expenses <= 0:
            return 0
        
        months_covered = emergency_fund / monthly_expenses
        
        # Score mapping (6+ months = perfect)
        if months_covered >= 6:
            return 100
        elif months_covered >= 5:
            return 90
        elif months_covered >= 4:
            return 75
        elif months_covered >= 3:
            return 60
        elif months_covered >= 2:
            return 40
        elif months_covered >= 1:
            return 25
        else:
            return int(months_covered * 15)
    
    @staticmethod
    def calculate_goal_progress_score(goals: list) -> int:
        """
        Calculate goal progress score (0-100)
        
        Args:
            goals: List of goal dicts with target, current, target_date
        
        Returns:
            Score out of 100
        """
        if not goals:
            return 50  # Neutral score if no goals
        
        total_progress = 0
        for goal in goals:
            if goal.get('status') != 'active':
                continue
            
            target = float(goal.get('target_amount', 1))
            current = float(goal.get('current_amount', 0))
            progress = (current / target) * 100 if target > 0 else 0
            total_progress += min(progress, 100)
        
        avg_progress = total_progress / len(goals) if goals else 0
        return int(avg_progress)
    
    @staticmethod
    def calculate_debt_health_score(
        monthly_income: float,
        monthly_emi: float
    ) -> int:
        """
        Calculate debt health score (0-100)
        
        Args:
            monthly_income: Monthly income
            monthly_emi: Total monthly EMI payments
        
        Returns:
            Score out of 100
        """
        if monthly_income <= 0:
            return 0
        
        if monthly_emi <= 0:
            return 100  # No debt = perfect score
        
        debt_to_income = (monthly_emi / monthly_income) * 100
        
        # Score mapping (lower is better)
        if debt_to_income <= 10:
            return 100
        elif debt_to_income <= 20:
            return 90
        elif debt_to_income <= 30:
            return 75
        elif debt_to_income <= 40:
            return 60
        elif debt_to_income <= 50:
            return 40
        else:
            return max(0, 40 - int(debt_to_income - 50))
    
    @staticmethod
    def calculate_behavioral_score(
        days_active: int,
        budgets_logged: int,
        goals_set: int
    ) -> int:
        """
        Calculate behavioral score (0-100)
        
        Args:
            days_active: Days since registration
            budgets_logged: Number of budgets entered
            goals_set: Number of goals created
        
        Returns:
            Score out of 100
        """
        score = 0
        
        # Activity score (max 40 points)
        if days_active >= 30:
            score += 40
        else:
            score += int((days_active / 30) * 40)
        
        # Budget consistency (max 30 points)
        if budgets_logged >= 6:
            score += 30
        else:
            score += int((budgets_logged / 6) * 30)
        
        # Goal setting (max 30 points)
        if goals_set >= 3:
            score += 30
        else:
            score += int((goals_set / 3) * 30)
        
        return min(score, 100)
    
    @classmethod
    def calculate_finca_score(
        cls,
        monthly_income: float,
        monthly_expenses: float,
        monthly_savings: float,
        emergency_fund: float,
        monthly_emi: float,
        goals: list,
        days_active: int = 0,
        budgets_logged: int = 0,
        goals_set: int = 0
    ) -> Tuple[int, Dict[str, int]]:
        """
        Calculate overall FinCA Score with component breakdown
        
        Args:
            monthly_income: Monthly income
            monthly_expenses: Monthly expenses
            monthly_savings: Monthly savings
            emergency_fund: Emergency fund amount
            monthly_emi: Monthly EMI payments
            goals: List of goal dictionaries
            days_active: Days since user registration
            budgets_logged: Number of budgets logged
            goals_set: Number of goals set
        
        Returns:
            Tuple of (total_score, component_scores_dict)
        """
        # Calculate component scores
        savings_rate_score = cls.calculate_savings_rate_score(
            monthly_income, monthly_savings
        )
        emergency_fund_score = cls.calculate_emergency_fund_score(
            monthly_expenses, emergency_fund
        )
        goal_progress_score = cls.calculate_goal_progress_score(goals)
        debt_health_score = cls.calculate_debt_health_score(
            monthly_income, monthly_emi
        )
        behavioral_score = cls.calculate_behavioral_score(
            days_active, budgets_logged, goals_set
        )
        
        # Calculate weighted total
        total_score = int(
            savings_rate_score * cls.WEIGHTS['savings_rate'] +
            emergency_fund_score * cls.WEIGHTS['emergency_fund'] +
            goal_progress_score * cls.WEIGHTS['goal_progress'] +
            debt_health_score * cls.WEIGHTS['debt_health'] +
            behavioral_score * cls.WEIGHTS['behavioral']
        )
        
        # Component breakdown
        components = {
            'savings_rate_score': savings_rate_score,
            'emergency_fund_score': emergency_fund_score,
            'goal_progress_score': goal_progress_score,
            'debt_health_score': debt_health_score,
            'behavioral_score': behavioral_score
        }
        
        logger.info(
            "FinCA Score calculated",
            total_score=total_score,
            components=components
        )
        
        return total_score, components

# Convenience function
def calculate_finca_score(user_data: Dict[str, Any]) -> Tuple[int, Dict[str, int]]:
    """
    Calculate FinCA Score from user data dictionary
    
    Args:
        user_data: Dict containing financial data
    
    Returns:
        Tuple of (total_score, component_scores)
    """
    calculator = MetricsCalculator()
    return calculator.calculate_finca_score(
        monthly_income=user_data.get('monthly_income', 0),
        monthly_expenses=user_data.get('monthly_expenses', 0),
        monthly_savings=user_data.get('monthly_savings', 0),
        emergency_fund=user_data.get('emergency_fund', 0),
        monthly_emi=user_data.get('monthly_emi', 0),
        goals=user_data.get('goals', []),
        days_active=user_data.get('days_active', 0),
        budgets_logged=user_data.get('budgets_logged', 0),
        goals_set=user_data.get('goals_set', 0)
    )
