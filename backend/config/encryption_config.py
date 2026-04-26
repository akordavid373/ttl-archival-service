import os

class EncryptionConfig:
    ENCRYPTION_ALGORITHM = "AES-256-GCM"
    KEY_ROTATION_DAYS = int(os.getenv("KEY_ROTATION_DAYS", "90"))
    PRIMARY_KEY_ID = os.getenv("PRIMARY_KEY_ID", "key-v1")
    REQUIRE_TLS = os.getenv("REQUIRE_TLS", "True").lower() == "true"
    
encryption_settings = EncryptionConfig()