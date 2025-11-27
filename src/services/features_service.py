from src.config.settings import settings
from supabase import create_client, Client
from src.utils.logger import logger
import pandas as pd

class FeaturesService:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

    # --- PORTFOLIO ---
    def get_portfolio(self, user_id: str):
        try:
            return self.supabase.table("portfolio").select("*").eq("user_id", user_id).execute().data
        except Exception as e:
            logger.error(f"Error fetching portfolio: {e}")
            return []

    def add_portfolio_transaction(self, user_id: str, data: dict):
        try:
            # Extract symbol for portfolio lookup (not stored in transactions table)
            symbol = data.get('symbol', None)
            quantity = data.get('quantity', 0)
            price = data.get('price', 0)
            notes = data.get('notes', '')
            
            # 1. Add Transaction (without symbol field - it's not in the schema)
            trans_data = {
                "user_id": user_id,
                "transaction_type": data.get("transaction_type", "buy"),
                "quantity": quantity,
                "price": price,
                "total_amount": data.get("total_amount", quantity * price),
                "transaction_date": data.get("transaction_date"),
                "notes": notes,
                "portfolio_id": None  # Will link later if needed
            }
            self.supabase.table("portfolio_transactions").insert(trans_data).execute()
            
            # 2. Update/Create Portfolio Asset (Simplified logic)
            # In a real app, you'd calculate weighted average price here
            if symbol:
                existing = self.supabase.table("portfolio").select("*").eq("user_id", user_id).eq("symbol", symbol).execute().data
                
                if existing:
                    # Update quantity
                    new_qty = float(existing[0]['quantity']) + float(quantity)
                    # Simple average price calculation could go here, but for now just updating quantity
                    self.supabase.table("portfolio").update({"quantity": new_qty}).eq("id", existing[0]['id']).execute()
                else:
                    # Create new asset
                    asset_data = {
                        "user_id": user_id,
                        "asset_type": "Stock", # Default or from input
                        "asset_name": notes if notes else "Unknown Asset",
                        "symbol": symbol,
                        "quantity": quantity,
                        "average_buy_price": price,
                        "current_price": price # Assume current = buy for now
                    }
                    self.supabase.table("portfolio").insert(asset_data).execute()
            
            return True, "Transaction added successfully"
        except Exception as e:
            logger.error(f"Error adding transaction: {str(e)}")
            return False, str(e)

    # --- GAMIFICATION ---
    def get_achievements(self, user_id: str):
        try:
            return self.supabase.table("user_achievements").select("*").eq("user_id", user_id).execute().data
        except Exception as e:
            logger.error(f"Error fetching achievements: {e}")
            return []

    def get_leaderboard(self):
        try:
            return self.supabase.table("leaderboard").select("*").order("score", desc=True).limit(10).execute().data
        except Exception as e:
            logger.error(f"Error fetching leaderboard: {e}")
            return []

    def get_active_challenges(self, user_id: str):
        try:
            return self.supabase.table("active_challenges").select("*").eq("user_id", user_id).execute().data
        except Exception as e:
            logger.error(f"Error fetching challenges: {e}")
            return []

    def get_user_stats(self, user_id: str):
        try:
            # Get user score from leaderboard
            leaderboard_data = self.supabase.table("leaderboard").select("*").eq("user_id", user_id).execute().data
            score = leaderboard_data[0]['score'] if leaderboard_data else 0

            # Get completed challenges count
            completed_challenges = len(self.supabase.table("user_achievements").select("*").eq("user_id", user_id).execute().data)

            # Get user rank
            all_scores = self.supabase.table("leaderboard").select("score").order("score", desc=True).execute().data
            rank = next((i + 1 for i, item in enumerate(all_scores) if item['score'] <= score), len(all_scores) + 1)

            return {
                'total_score': score,
                'completed_challenges': completed_challenges,
                'rank': rank
            }
        except Exception as e:
            logger.error(f"Error fetching user stats: {e}")
            return {
                'total_score': 0,
                'completed_challenges': 0,
                'rank': 'N/A'
            }

    # --- NOTIFICATIONS ---
    def get_notifications(self, user_id: str):
        try:
            return self.supabase.table("notifications").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(5).execute().data
        except Exception as e:
            # logger.error(f"Error fetching notifications: {e}") # Suppress noise if table empty/missing
            return []

    # --- NEWS ---
    def get_latest_news(self):
        try:
            return self.supabase.table("news_cache").select("*").order("published_at", desc=True).limit(10).execute().data
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
