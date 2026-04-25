"""
Step 2: Connect to Database

Connects to the database client.
"""

from typing import Optional
from database import DatabaseClient
from schemas import FinalResponse


def connect_to_database(db_client: Optional[DatabaseClient] = None) -> tuple[Optional[DatabaseClient], Optional[FinalResponse]]:
    """
    Connects to the database.
    
    Returns:
        (DatabaseClient, None) on success
        (None, FinalResponse) on failure
    """
    print("\n" + "="*60)
    print("🔌 STEP 2: CONNECT TO DATABASE")
    print("="*60)
    
    if db_client is None:
        error = FinalResponse(
            success=False,
            error_message="Database client not initialized"
        )
        print("   ❌ Database client is None")
        return None, error
    
    print("   ✅ Database connection established")
    return db_client, None