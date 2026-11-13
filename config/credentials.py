# config/credentials.py
import json
from pathlib import Path
from typing import List, Dict

class CredentialManager:
    """Manage LinkedIn credentials"""
    
    ACCOUNTS_FILE = Path(__file__).parent.parent / "accounts" / "multi_account.json"
    
    @classmethod
    def load_credentials(cls) -> List[Dict]:
        """Load credentials from file"""
        if not cls.ACCOUNTS_FILE.exists():
            return []
        
        with open(cls.ACCOUNTS_FILE, 'r') as f:
            data = json.load(f)
        return data.get("accounts", [])
    
    @classmethod
    def save_credentials(cls, accounts: List[Dict]):
        """Save credentials to file"""
        cls.ACCOUNTS_FILE.parent.mkdir(exist_ok=True)
        with open(cls.ACCOUNTS_FILE, 'w') as f:
            json.dump({"accounts": accounts}, f, indent=2)