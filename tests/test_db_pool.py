import pytest
import logging
from db import ConnectionPool

def test_pool_exhaustion(caplog):
    """
    Verify that the connection pool logs a warning when exhausted
    and successfully creates a temporary connection.
    """
    # Use a small pool size for testing
    pool = ConnectionPool(":memory:", pool_size=1)
    pool.initialize()
    
    # Take the only available connection
    conn1 = pool.get_connection(timeout=0.1)
    assert conn1 is not None
    
    # Configure logging checks
    with caplog.at_level(logging.WARNING):
        # Request a second connection (should trigger exhaustion logic)
        # Timeout is small because we expect it to fail getting from queue quickly 
        # but in our implementation queue.get(timeout) raises Empty.
        # Wait, the implementation uses timeout=POOL_TIMEOUT (30s) by default.
        # We should pass a short timeout to get_connection to make the test fast.
        
        conn2 = pool.get_connection(timeout=0.1)
        
        # Verify connection was created
        assert conn2 is not None
        assert conn2 is not conn1
        
        # Verify warning was logged
        assert "Connection pool exhausted" in caplog.text
        assert "creating temporary connection" in caplog.text

    # Clean up
    pool.return_connection(conn1)
    pool.return_connection(conn2)
    pool.close_all()
