"""
ユーザー関連のドメインモデル
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """ユーザーモデル"""
    id: str
    username: str
    password_hash: str  # ハッシュ化されたパスワード
    created_at: Optional[str] = None


@dataclass
class UserLoginRequest:
    """ログインリクエスト"""
    username: str
    password: str


@dataclass
class UserLoginResponse:
    """ログインレスポンス"""
    success: bool
    message: str
    access_token: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None


@dataclass
class UserRegisterRequest:
    """ユーザー登録リクエスト"""
    username: str
    password: str


@dataclass
class UserRegisterResponse:
    """ユーザー登録レスポンス"""
    success: bool
    message: str
    user_id: Optional[str] = None
