"""API Authentication utilities."""

import pyrootutils

ROOT = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git"],
    pythonpath=True,
    dotenv=True,
)

from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

import src.utils.exceptions as exceptions
from schema.auth.auth_schema import CurrentUser

class Authentication:
    """Authentication class for the API."""

    def __init__(
        self,
        secret: str,
        algorithm: str,
        expiration: int,
        encrypt_scheme: list = ["bcrypt"],
    ) -> None:
        """
        Constructor

        Args:
            secret (str): Secret key
            algorithm (str): Algorithm to use
            expiration (int): Expiration time in seconds
            encrypt_scheme (str): Encryption scheme to use. Default: bcrypt

        Examples:
            >>> auth = Authentication("secret", "HS256", 3600, "bcrypt")
        """
        self.secret = secret
        self.algorithm = algorithm
        self.expiration = expiration

        # Create password context
        self.pwd_context = CryptContext(schemes=encrypt_scheme, deprecated="auto")

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password.

        Args:
            plain_password (str): Plain password
            hashed_password (str): Hashed password

        Returns:
            bool: True if password is correct, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_access_token(self, data: dict) -> str:
        """
        Create access token.

        Args:
            data (dict): Data to encode

        Returns:
            str: Access token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(seconds=self.expiration)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
        return encoded_jwt

    async def decode_access_token(self, token: str) -> CurrentUser:
        """
        Decode access token.

        Args:
            token (str): Access token

        Returns:
            CurrentUser: Decoded access token
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise exceptions.Unauthorized("Could not validate credentials")
            return CurrentUser(username=username)
        except JWTError:
            raise exceptions.Unauthorized(f"Could not validate credentials: {JWTError}")

    async def get_password_hash(self, password: str) -> str:
        """
        Get password hash.

        Args:
            password (str): Password

        Returns:
            str: Password hash
        """
        return self.pwd_context.hash(password)