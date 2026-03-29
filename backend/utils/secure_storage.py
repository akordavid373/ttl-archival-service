import json
import os
import base64
from .encryption import AESEncryption
from ..config.encryption_config import encryption_settings

class SecureStorage:
    def __init__(self, storage_path: str = "./secure_data.enc"):
        self.storage_path = storage_path

    def save_encrypted_data(self, key: bytes, data: dict):
        json_data = json.dumps(data).encode('utf-8')
        encrypted = AESEncryption.encrypt(key, json_data)
        with open(self.storage_path, 'wb') as f:
            f.write(base64.b64encode(encrypted))

    def load_encrypted_data(self, key: bytes) -> dict:
        if not os.path.exists(self.storage_path):
            return {}
        with open(self.storage_path, 'rb') as f:
            encrypted = base64.b64decode(f.read())
            if not encrypted:
                return {}
        decrypted = AESEncryption.decrypt(key, encrypted)
        return json.loads(decrypted.decode('utf-8'))