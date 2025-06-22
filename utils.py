from cryptography.fernet import Fernet, InvalidToken


def encrypt_message(message: str, key: str) -> str:
    fernet = Fernet(key.encode('utf-8'))
    return fernet.encrypt(message.encode('utf-8')).decode('utf-8')


def decrypt_message(token: str, key: str) -> str:
    fernet = Fernet(key.encode('utf-8'))
    try:
        return fernet.decrypt(token.encode('utf-8')).decode('utf-8')
    except InvalidToken as e:
        raise ValueError('Clave incorrecta') from e