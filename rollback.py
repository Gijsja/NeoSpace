import argparse
import sys
import os
from alembic.config import Config
from alembic import command

def rollback(revisions=1):
    """Rollback the database by N revisions."""
    # Ensure usage of the correct alembic.ini
    alembic_cfg = Config("alembic.ini")
    
    # We might need to ensure the DB path is correct if it depends on env vars
    # Alembic env.py usually handles this by importing from app/config, 
    # so as long as env vars are set, it should work.
    
    try:
        command.downgrade(alembic_cfg, f"-{revisions}")
        print(f"Successfully rolled back {revisions} revision(s).")
    except Exception as e:
        print(f"Error during rollback: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rollback database migrations.")
    parser.add_argument("-n", "--num", type=int, default=1, help="Number of revisions to rollback")
    args = parser.parse_args()
    
    rollback(args.num)
