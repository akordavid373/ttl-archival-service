from datetime import datetime, timedelta
import os
import json
import base64
from ..utils.encryption import AESEncryption
from ..config.encryption_config import encryption_settings

class KeyService:
    def __init__(self, keystore_path: str = "./keystore.json"):
        self.keystore_path = keystore_path
        self._load_keys()

    def _load_keys(self):
        if os.path.exists(self.keystore_path):
            with open(self.keystore_path, 'r') as f:
                self.keys = json.load(f)
        else:
            self.keys = {}
            self._generate_new_key(encryption_settings.PRIMARY_KEY_ID)

    def _save_keys(self):
        with open(self.keystore_path, 'w') as f:
            json.dump(self.keys, f)

    def _generate_new_key(self, key_id: str):
        raw_key = AESEncryption.generate_key()
        self.keys[key_id] = {
            "key": base64.b64encode(raw_key).decode('utf-8'),
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=encryption_settings.KEY_ROTATION_DAYS)).isoformat(),
            "active": True
        }
        self._save_keys()

    def get_current_key(self) -> bytes:
        for key_id, meta in self.keys.items():
            if meta.get("active") and datetime.fromisoformat(meta["expires_at"]) > datetime.utcnow():
                return base64.b64decode(self.keys[key_id]["key"])
        
        new_id = f"key-{int(datetime.utcnow().timestamp())}"
        self._generate_new_key(new_id)
        return base64.b64decode(self.keys[new_id]["key"])

    def rotate_keys(self) -> str:
        for meta in self.keys.values():
            meta["active"] = False
        new_id = f"key-{int(datetime.utcnow().timestamp())}"
        self._generate_new_key(new_id)
        return new_id