"""
認証サービスの実装

ユーザーの登録、ログイン、トークン生成・検証を管理します。
"""

import hashlib
import hmac
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional

from domain.user_models import (
    User,
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)
import config


class AuthService:
    """認証サービス"""

    def __init__(self):
        """サービスを初期化します"""
        # メモリ内ユーザーストア（本番環境ではDBを使用）
        self._users: dict[str, User] = {}
        # トークンストア（本番環境ではRedis等を使用）
        self._tokens: dict[str, dict] = {}
        # テストユーザーを作成
        self._create_test_user()

    def _create_test_user(self) -> None:
        """テストユーザーを作成"""
        test_user = User(
            id="test-user-1",
            username="testuser",
            password_hash=self._hash_password("password123"),
            created_at=datetime.now().isoformat(),
        )
        self._users[test_user.id] = test_user

    def _hash_password(self, password: str) -> str:
        """パスワードをハッシュ化します"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _generate_token(self, user_id: str) -> str:
        """JWTライクなトークンを生成します"""
        # 簡易的なトークン実装
        header = {"typ": "JWT", "alg": "HS256"}
        payload = {
            "user_id": user_id,
            "exp": (
                datetime.now() + timedelta(hours=24)
            ).timestamp(),  # 24時間有効
            "iat": datetime.now().timestamp(),
        }

        # シンプルなBase64エンコーディング（本番環境ではPyJWTを使用）
        import base64

        header_encoded = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).rstrip(b"=")
        payload_encoded = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).rstrip(b"=")

        message = header_encoded + b"." + payload_encoded
        signature = hmac.new(
            config.OPENAI_API_KEY.encode() if config.OPENAI_API_KEY else b"secret",
            message,
            hashlib.sha256,
        ).digest()
        signature_encoded = base64.urlsafe_b64encode(signature).rstrip(b"=")

        token = message + b"." + signature_encoded
        return token.decode()

    def _verify_token(self, token: str) -> Optional[str]:
        """トークンを検証してuser_idを返します"""
        try:
            import base64

            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_encoded, payload_encoded, signature_encoded = parts

            # パディングを追加
            def add_padding(s: str) -> str:
                return s + "=" * (4 - len(s) % 4)

            payload_json = base64.urlsafe_b64decode(add_padding(payload_encoded))
            payload = json.loads(payload_json)

            # 有効期限を確認
            if payload.get("exp", 0) < datetime.now().timestamp():
                return None

            return payload.get("user_id")

        except Exception as e:
            print(f"Token verification error: {e}")
            return None

    def register(self, request: UserRegisterRequest) -> UserRegisterResponse:
        """ユーザーを登録します"""
        # ユーザー名が既に使用されているか確認
        for user in self._users.values():
            if user.username == request.username:
                return UserRegisterResponse(
                    success=False,
                    message="このユーザー名は既に使用されています",
                )

        # 新しいユーザーを作成
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            username=request.username,
            password_hash=self._hash_password(request.password),
            created_at=datetime.now().isoformat(),
        )

        self._users[user_id] = user

        return UserRegisterResponse(
            success=True,
            message="ユーザーを登録しました",
            user_id=user_id,
        )

    def login(self, request: UserLoginRequest) -> UserLoginResponse:
        """ユーザーをログインさせます"""
        # ユーザー名でユーザーを検索
        user = None
        for u in self._users.values():
            if u.username == request.username:
                user = u
                break

        if not user:
            return UserLoginResponse(
                success=False,
                message="ユーザー名またはパスワードが間違っています",
            )

        # パスワードを検証
        if user.password_hash != self._hash_password(request.password):
            return UserLoginResponse(
                success=False,
                message="ユーザー名またはパスワードが間違っています",
            )

        # トークンを生成
        token = self._generate_token(user.id)

        return UserLoginResponse(
            success=True,
            message="ログインに成功しました",
            access_token=token,
            user_id=user.id,
            username=user.username,
        )

    def logout(self, token: str) -> None:
        """ユーザーをログアウトさせます"""
        # トークンを無効化（トークンストアから削除）
        if token in self._tokens:
            del self._tokens[token]

    def verify_token(self, token: str) -> Optional[str]:
        """トークンを検証してuser_idを返します"""
        return self._verify_token(token)

    def get_user(self, user_id: str) -> Optional[User]:
        """ユーザーIDでユーザーを取得します"""
        return self._users.get(user_id)
