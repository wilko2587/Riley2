# File: tests/mocks/kdb_agent_mock.py

from riley2.core.logger_utils import logger
from tests.config import TestConfigLoader

class KnowledgeBaseAgentMock:
    """
    KnowledgeBaseAgentMock
    ---------------------
    This mock simulates the behavior of a knowledge base agent that provides
    access to personal and contextual information.
    """
    
    def __init__(self):
        """Initialize with entries from test configuration"""
        try:
            # Load knowledge base entries from configuration
            self.entries = TestConfigLoader.get_knowledge_base()
            logger.debug(f"Initialized KnowledgeBaseAgentMock with {len(self.entries)} entries from config")
        except Exception as e:
            logger.error(f"Failed to load knowledge base config: {e}")
            # Fallback to default entries if config loading fails
            logger.warning("Using fallback knowledge base data")
            self.entries = [
                {
                    "id": "kb-001",
                    "topic": "personal_preferences",
                    "data": {
                        "favorite_color": "blue"
                    }
                }
            ]
    
    def query_knowledge(self, query: str):
        """
        Query the knowledge base for information related to the query
        
        Args:
            query: String query to search for
            
        Returns:
            dict: Data related to the query or None if not found
        """
        query = query.lower()
        logger.debug(f"Mock: Querying knowledge base for: '{query}'")
        
        # First try to find an entry with a matching topic
        for entry in self.entries:
            if query in entry.get("topic", "").lower():
                logger.info(f"Mock: Found knowledge base entry with topic matching '{query}'")
                return entry.get("data", {})
        
        # Next, look for entries with matching data
        for entry in self.entries:
            data = entry.get("data", {})
            # Check if any key or value contains the query
            for key, value in data.items():
                if (query in key.lower() or 
                    (isinstance(value, str) and query in value.lower())):
                    logger.info(f"Mock: Found knowledge base entry with data matching '{query}'")
                    return data
                
                # Handle nested structures like lists and dictionaries
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and any(query in str(v).lower() for v in item.values()):
                            logger.info(f"Mock: Found matching item in list for '{query}'")
                            return item
                elif isinstance(value, dict):
                    if any(query in str(v).lower() for v in value.values()):
                        logger.info(f"Mock: Found matching item in dict for '{query}'")
                        return value
        
        logger.info(f"Mock: No knowledge base entries found for '{query}'")
        return None
    
    def add_knowledge(self, topic: str, data: dict):
        """
        Add a new entry to the knowledge base
        
        Args:
            topic: Topic category for the entry
            data: Dictionary of data to store
            
        Returns:
            str: ID of the new entry
        """
        entry_id = f"kb-{len(self.entries) + 1:03d}"
        new_entry = {
            "id": entry_id,
            "topic": topic,
            "data": data
        }
        self.entries.append(new_entry)
        logger.info(f"Mock: Added new knowledge base entry with ID {entry_id}")
        return entry_id
    
    def get_all_topics(self):
        """
        Get a list of all topics in the knowledge base
        
        Returns:
            list: List of topic strings
        """
        topics = [entry.get("topic") for entry in self.entries]
        return [t for t in topics if t]