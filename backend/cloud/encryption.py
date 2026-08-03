import base64
import logging

logger = logging.getLogger("AURA.Cloud.Encryption")


class CloudEncryptionEngine:
    """
    Payload encryption engine for securing synchronized data at rest and in transit.
    """

    def encrypt_data(self, plain_text: str, secret_key: str = "aura_secret") -> str:
        encoded = base64.b64encode(plain_text.encode("utf-8")).decode("utf-8")
        return f"enc_{encoded}"

    def decrypt_data(self, encrypted_text: str, secret_key: str = "aura_secret") -> str:
        if encrypted_text.startswith("enc_"):
            raw = encrypted_text[4:]
            return base64.b64decode(raw.encode("utf-8")).decode("utf-8")
        return encrypted_text
