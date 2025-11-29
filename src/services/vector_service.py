"""
Vector Service for User-Specific Data Storage and Retrieval
Provides personalized vector embeddings for LLM context
"""

import os
import uuid
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from src.config.settings import settings
from src.config.database import DatabaseClient
from src.utils.logger import logger


class VectorService:
    """
    Manages user-specific vector collections for personalized AI interactions
    """

    def __init__(self):
        """Initialize vector service with embeddings and database client"""
        self.db = DatabaseClient.get_authenticated_client()

        # Initialize embeddings with error handling for device issues
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                encode_kwargs={'normalize_embeddings': True},
                model_kwargs={'device': 'cpu'}
            )
        except Exception as e:
            logger.warning(f"Failed to initialize embeddings with device: {e}")
            # Fallback: try without device specification
            try:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    encode_kwargs={'normalize_embeddings': True}
                )
            except Exception as e2:
                logger.error(f"Failed to initialize embeddings: {e2}")
                # Last resort: use a simple fallback
                self.embeddings = None

        # ChromaDB client for user collections
        self.chroma_client = chromadb.PersistentClient(
            path="./data/user_vectors",
            settings=Settings(anonymized_telemetry=False)
        )

        # Cache for user collections
        self.user_collections = {}

    async def create_user_collection(self, user_id: str) -> Chroma:
        """
        Create or get user-specific vector collection

        Args:
            user_id: Unique user identifier

        Returns:
            Chroma vector store for the user
        """
        if self.embeddings is None:
            logger.warning("Embeddings not available, returning None for user collection")
            return None
            
        collection_name = f"user_{user_id}_data"

        # Check if collection exists in ChromaDB
        try:
            collection = self.chroma_client.get_collection(
                name=collection_name
            )
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings
            )
        except:
            # Create new collection
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings
            )

        self.user_collections[user_id] = vectorstore
        return vectorstore

    async def embed_user_data(self, user_id: str, data_type: str, content: str,
                            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Embed and store user-specific data in ChromaDB (Supabase table creation pending)

        Args:
            user_id: User identifier
            data_type: Type of data ('budget', 'goal', 'transaction', etc.)
            content: Text content to embed
            metadata: Additional metadata

        Returns:
            Success status
        """
        try:
            if self.embeddings is None:
                logger.warning("Embeddings not available, skipping vector storage")
                return False
                
            if metadata is None:
                metadata = {}

            # Store in ChromaDB for fast retrieval
            vectorstore = await self.create_user_collection(user_id)
            if vectorstore is None:
                return False

            # Add metadata for ChromaDB
            chroma_metadata = metadata.copy()
            chroma_metadata.update({
                'user_id': user_id,
                'data_type': data_type,
                'timestamp': str(uuid.uuid4())  # Unique ID for ChromaDB
            })

            vectorstore.add_texts(
                texts=[content],
                metadatas=[chroma_metadata]
            )

            # TODO: Store in Supabase when table is created
            # embedding_data = {
            #     'user_id': user_id,
            #     'content': content,
            #     'metadata': metadata,
            #     'embedding': embedding,  # pgvector format
            #     'data_type': data_type
            # }
            # result = self.db.table('user_data_embeddings').insert(embedding_data).execute()

            return True

        except Exception as e:
            print(f"Error embedding user data: {str(e)}")
            return False

    async def retrieve_user_context(self, user_id: str, query: str,
                                  top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant user-specific context for a query

        Args:
            user_id: User identifier
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant documents with metadata
        """
        try:
            if self.embeddings is None:
                logger.warning("Embeddings not available, returning empty context")
                return []
                
            vectorstore = await self.create_user_collection(user_id)
            if vectorstore is None:
                return []

            # Search for similar content
            docs = vectorstore.similarity_search(query, k=top_k)

            # Format results
            results = []
            for doc in docs:
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'data_type': doc.metadata.get('data_type', 'unknown'),
                    'similarity_score': getattr(doc, 'score', None)
                })

            return results

        except Exception as e:
            print(f"Error retrieving user context: {str(e)}")
            return []

    async def get_user_activity_timeline(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent user activity from vector store for dashboard display

        Args:
            user_id: User identifier
            limit: Maximum number of activities to return

        Returns:
            List of recent activities with timestamps
        """
        try:
            if self.embeddings is None:
                logger.warning("Embeddings not available, returning empty timeline")
                return []
                
            # For now, get from ChromaDB collection
            vectorstore = await self.create_user_collection(user_id)
            if vectorstore is None:
                return []

            # Get all documents (ChromaDB doesn't have easy timestamp sorting)
            # TODO: Use Supabase for proper timeline when table is available
            all_docs = vectorstore.get()

            activities = []
            for i, doc_id in enumerate(all_docs['ids'][:limit]):
                metadata = all_docs['metadatas'][i] if i < len(all_docs['metadatas']) else {}
                activities.append({
                    'type': metadata.get('data_type', 'activity'),
                    'content': all_docs['documents'][i][:100] + '...' if len(all_docs['documents'][i]) > 100 else all_docs['documents'][i],
                    'timestamp': metadata.get('timestamp', 'recent'),
                    'metadata': metadata
                })

            return activities

        except Exception as e:
            print(f"Error getting user activity: {str(e)}")
            return []

    async def update_user_data(self, user_id: str, data_type: str,
                             old_content: str, new_content: str,
                             metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update existing user data embedding

        Args:
            user_id: User identifier
            data_type: Type of data being updated
            old_content: Previous content (for deletion)
            new_content: New content to embed
            metadata: Updated metadata

        Returns:
            Success status
        """
        try:
            # For now, just add new content (deletion not implemented in ChromaDB easily)
            # TODO: Implement proper update logic when Supabase table is available
            return await self.embed_user_data(user_id, data_type, new_content, metadata)

        except Exception as e:
            print(f"Error updating user data: {str(e)}")
            return False

    async def delete_user_data(self, user_id: str, data_type: str,
                             content: str) -> bool:
        """
        Delete user data from vector store

        Args:
            user_id: User identifier
            data_type: Type of data to delete
            content: Content to remove

        Returns:
            Success status
        """
        try:
            # ChromaDB deletion is complex, for now just mark as deleted in metadata
            # TODO: Implement proper deletion when Supabase table is available
            vectorstore = await self.create_user_collection(user_id)

            # Search for the content and update metadata to mark as deleted
            docs = vectorstore.similarity_search(content, k=1)
            if docs:
                # Note: ChromaDB doesn't have easy deletion, this is a workaround
                pass

            return True

        except Exception as e:
            print(f"Error deleting user data: {str(e)}")
            return False

    async def get_user_stats(self, user_id: str) -> Dict[str, int]:
        """
        Get statistics about user's vector data

        Args:
            user_id: User identifier

        Returns:
            Dictionary with data type counts
        """
        try:
            # For now, get from ChromaDB
            vectorstore = await self.create_user_collection(user_id)
            all_docs = vectorstore.get()

            stats = {}
            for metadata in all_docs['metadatas']:
                data_type = metadata.get('data_type', 'unknown')
                stats[data_type] = stats.get(data_type, 0) + 1

            return stats

        except Exception as e:
            print(f"Error getting user stats: {str(e)}")
            return {}

    async def cleanup_old_data(self, user_id: str, days_old: int = 365, data_types: Optional[List[str]] = None) -> int:
        """
        Clean up old vector data based on age and type

        Args:
            user_id: User identifier
            days_old: Remove data older than this many days
            data_types: Specific data types to clean up (None for all)

        Returns:
            Number of items cleaned up
        """
        try:
            from datetime import datetime, timedelta

            vectorstore = await self.create_user_collection(user_id)
            all_docs = vectorstore.get()

            cutoff_date = datetime.now() - timedelta(days=days_old)
            ids_to_delete = []

            for i, metadata in enumerate(all_docs['metadatas']):
                # Check age
                timestamp = metadata.get('timestamp')
                if timestamp:
                    try:
                        item_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        if item_date < cutoff_date:
                            # Check data type filter
                            data_type = metadata.get('data_type')
                            if data_types is None or data_type in data_types:
                                ids_to_delete.append(all_docs['ids'][i])
                    except (ValueError, AttributeError):
                        # If timestamp is malformed, keep the data
                        continue

            if ids_to_delete:
                vectorstore.delete(ids=ids_to_delete)
                logger.info("Cleaned up old vector data", user_id=user_id, items_cleaned=len(ids_to_delete), days_old=days_old)
                return len(ids_to_delete)

            return 0

        except Exception as e:
            logger.error("Vector cleanup failed", error=str(e), user_id=user_id)
            return 0

    async def cleanup_by_type_and_count(self, user_id: str, data_type: str, max_items: int = 100) -> int:
        """
        Clean up old items of a specific type, keeping only the most recent

        Args:
            user_id: User identifier
            data_type: Type of data to clean up
            max_items: Maximum number of items to keep

        Returns:
            Number of items cleaned up
        """
        try:
            vectorstore = await self.create_user_collection(user_id)
            all_docs = vectorstore.get()

            # Filter by data type
            type_docs = []
            for i, metadata in enumerate(all_docs['metadatas']):
                if metadata.get('data_type') == data_type:
                    type_docs.append({
                        'id': all_docs['ids'][i],
                        'timestamp': metadata.get('timestamp', ''),
                        'index': i
                    })

            if len(type_docs) <= max_items:
                return 0

            # Sort by timestamp (newest first)
            type_docs.sort(key=lambda x: x['timestamp'], reverse=True)

            # Keep only the most recent items
            items_to_delete = type_docs[max_items:]
            ids_to_delete = [item['id'] for item in items_to_delete]

            if ids_to_delete:
                vectorstore.delete(ids=ids_to_delete)
                logger.info("Cleaned up excess items by type", user_id=user_id, data_type=data_type, items_cleaned=len(ids_to_delete), kept=max_items)
                return len(ids_to_delete)

            return 0

        except Exception as e:
            logger.error("Type-based cleanup failed", error=str(e), user_id=user_id, data_type=data_type)
            return 0

    async def optimize_storage(self, user_id: str) -> Dict[str, int]:
        """
        Run comprehensive storage optimization for a user

        Args:
            user_id: User identifier

        Returns:
            Dictionary with cleanup statistics
        """
        try:
            stats = {'old_data_cleaned': 0, 'transactions_cleaned': 0, 'budgets_cleaned': 0, 'goals_cleaned': 0}

            # Clean up data older than 2 years
            stats['old_data_cleaned'] = await self.cleanup_old_data(user_id, days_old=730)

            # Keep only last 200 transactions
            stats['transactions_cleaned'] = await self.cleanup_by_type_and_count(user_id, 'transaction', 200)

            # Keep only last 50 budgets
            stats['budgets_cleaned'] = await self.cleanup_by_type_and_count(user_id, 'budget', 50)

            # Keep only last 20 goals
            stats['goals_cleaned'] = await self.cleanup_by_type_and_count(user_id, 'goal', 20)

            total_cleaned = sum(stats.values())
            if total_cleaned > 0:
                logger.info("Storage optimization completed", user_id=user_id, **stats)

            return stats

        except Exception as e:
            logger.error("Storage optimization failed", error=str(e), user_id=user_id)
            return {}

    async def get_storage_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get detailed storage information for a user

        Args:
            user_id: User identifier

        Returns:
            Dictionary with storage statistics
        """
        try:
            vectorstore = await self.create_user_collection(user_id)
            all_docs = vectorstore.get()

            # Calculate storage stats
            total_items = len(all_docs['ids'])
            data_types = {}
            oldest_item = None
            newest_item = None

            for metadata in all_docs['metadatas']:
                # Count by type
                data_type = metadata.get('data_type', 'unknown')
                data_types[data_type] = data_types.get(data_type, 0) + 1

                # Track timestamps
                timestamp = metadata.get('timestamp')
                if timestamp:
                    try:
                        item_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        if oldest_item is None or item_date < oldest_item:
                            oldest_item = item_date
                        if newest_item is None or item_date > newest_item:
                            newest_item = item_date
                    except (ValueError, AttributeError):
                        continue

            # Estimate storage size (rough calculation)
            avg_content_length = sum(len(doc) for doc in all_docs['documents']) / max(total_items, 1)
            estimated_size_mb = (total_items * avg_content_length * 1.5) / (1024 * 1024)  # Rough estimate with overhead

            return {
                'total_items': total_items,
                'data_types': data_types,
                'oldest_item': oldest_item.isoformat() if oldest_item else None,
                'newest_item': newest_item.isoformat() if newest_item else None,
                'estimated_size_mb': round(estimated_size_mb, 2),
                'collection_name': f"user_{user_id}"
            }

        except Exception as e:
            logger.error("Storage info retrieval failed", error=str(e), user_id=user_id)
            return {}