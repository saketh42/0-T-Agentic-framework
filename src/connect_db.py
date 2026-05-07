"""
Step 2: Connect to Database

Connects to the database client.
"""

from typing import Optional, Tuple
from database import IdentityAgentDatabaseClient
from schemas import IdentityValidationResponse


def establish_identity_agent_db_connection(db_client: Optional[IdentityAgentDatabaseClient] = None) -> tuple[Optional[IdentityAgentDatabaseClient], Optional[IdentityValidationResponse]]:
    """
    Connects to the database.
    
    Returns:
        (IdentityAgentDatabaseClient, None) on success
        (None, IdentityValidationResponse) on failure
    """
    print("\n" + "="*60)
    print(" STEP 2: CONNECT TO DATABASE")
    print("="*60)
    
    if db_client is None:
        error = IdentityValidationResponse(
            is_authorized=False,
            failure_reason="Database client not initialized"
        )
        print("    Database client is None")
        return None, error
    
    print("    Database connection established")
    return db_client, None