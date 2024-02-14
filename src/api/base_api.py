"""Base API module."""

import pyrootutils

ROOT = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git"],
    pythonpath=True,
    dotenv=True,
)

import secrets
import asyncio
import re

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from omegaconf import DictConfig

import src.utils.exceptions as exceptions
import src.utils.timer as t
from src.schema.auth.auth_schema import CurrentUser, Token
from src.database.mongodb_base import MongodbBase
from src.schema.user.user_schema import User, UserRegister, UserRegisterResponse
from src.utils.auth import Authentication
from src.utils.logger import get_logger

app = FastAPI()
basic_auth = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

log = get_logger()


class BaseAPI:
    """Base API module."""

    def __init__(self, cfg: DictConfig, mongodb: MongodbBase) -> None:
        """Initialize base api module."""
        self.cfg = cfg
        self.app = app
        self.router = APIRouter()
        self.auth = Authentication(**self.cfg.api.auth.bearer)

        # database
        self.mongodb: MongodbBase = mongodb
        # setup routes
        self.setup()

    def setup(self) -> None:
        """Setup routes."""

        @self.router.post(
            "/api/user/login",
            tags=["User"],
            description="Login user",
            responses={
                200: {"description": "Login successful"},
                401: {"description": "Invalid username or password"},
            },
            response_model=Token,
        )
        async def login(
            request: Request, creds: OAuth2PasswordRequestForm = Depends()
        ) -> Token:
            """
            Login user.

            Args:
                request (Request): Request object.
                creds (OAuth2PasswordRequestForm): Credentials form.

            Returns:
                Token: Token object.
            """
            log.log(25, f"Login request from: {creds.username} - {request.client.host}")
            user = await self.authenticate_user(
                username=creds.username,
                password=creds.password,
            )
            access_token = await self.auth.create_access_token(
                data={"sub": user.username}
            )
            log.log(25, f"Login successful for: {creds.username}")
            return Token(access_token=access_token, token_type="bearer")

        @self.router.post(
            "/api/user/register",
            tags=["User"],
            description="Register a new user",
            responses={
                200: {"description": "User registered successfully"},
                400: {"description": "User already exists"},
            },
            response_model=UserRegisterResponse,
        )
        async def register(
            request: Request, user: UserRegister
        ) -> UserRegisterResponse:
            """
            Register a new user.

            Args:
                user (UserRegister): UserRegister schema object.

            Returns:
                UserRegisterResponse: UserRegisterResponse schema object.
            """
            log.log(
                21, f"Register request from: {user.username} - {request.client.host}"
            )
            req_start = t.now()

            # check username
            pattern = re.compile(r'^[a-zA-Z0-9_.]+$')
            if not pattern.match(user.username):
                raise exceptions.BadRequest("Invalid username format, the only allowed symbol is underscore (_).")
            user.username = user.username.lower()
            
            # hashing password
            user.password = await self.auth.get_password_hash(user.password)

            # check if user already exists
            user_exists = await User.find_one(User.username == user.username)
            if user_exists:
                raise exceptions.BadRequest("Username already exists")

            # insert user
            user: User = user.to_user_schema()
            await user.insert()
            log.log(25, f"User registered: {user.username} - {t.elapsed(req_start)}")

            return UserRegisterResponse(
                status="success",
                message="User registered successfully",
                data=user.to_out(),
                elapsed=t.elapsed(req_start),
            )

        self.app.include_router(self.router)

    async def authenticate_user(self, username: str, password: str) -> User:
        """
        Authenticate user.

        Args:
            username (str): username
            password (str): password

        Returns:
            User: user schema object

        Raises:
            exceptions.Unauthorized: if user is not found
        """
        user = await User.find_one(User.username == username)
        if user is None:
            raise exceptions.Unauthorized("Invalid username or password")
        log.debug(f"Authenticating user: {user.username}")
        if not await self.auth.verify_password(password, user.password):
            raise exceptions.Unauthorized("Invalid username or password")

        return user

    async def basic_auth(
        self, credentials: HTTPBasicCredentials = Depends(basic_auth)
    ) -> User:
        """
        Basic auth.

        Args:
            credentials (HTTPBasicCredentials): credentials

        Returns:
            User: user schema object

        Raises:
            exceptions.Unauthorized: if user is not found
        """
        correct_username = secrets.compare_digest(
            credentials.username, self.cfg.api.auth.basic.username
        )
        correct_password = secrets.compare_digest(
            credentials.password, self.cfg.api.auth.basic.password
        )
        if not (correct_username and correct_password):
            raise exceptions.Unauthorized("Invalid username or password")

    async def bearer_auth(self, token: str = Depends(oauth2_scheme)) -> CurrentUser:
        """
        Bearer auth.

        Args:
            token (str): token

        Returns:
            CurrentUser: current user schema object

        Raises:
            exceptions.Unauthorized: if token is invalid
        """
        try:
            return await self.auth.decode_access_token(token)
        except Exception as e:
            exceptions.Unauthorized("Invalid token")