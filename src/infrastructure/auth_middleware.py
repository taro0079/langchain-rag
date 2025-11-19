"""
認証ミドルウェア
"""

from fastapi import Header, HTTPException, status
from typing import Optional

from infrastructure.auth_service import AuthService


def get_auth_service() -> AuthService:
    """認証サービスを取得します（シングルトン）"""
    if not hasattr(get_auth_service, "_instance"):
        get_auth_service._instance = AuthService()
    return get_auth_service._instance


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> dict:
    """
    認証トークンから現在のユーザーを取得します

    Args:
        authorization: Authorizationヘッダー（"Bearer <token>"形式）

    Returns:
        user_id: ユーザーID

    Raises:
        HTTPException: トークンが無効または存在しない場合
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証トークンが必要です",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効な認証形式です",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # トークンを検証
    auth_service = get_auth_service()
    user_id = auth_service.verify_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"user_id": user_id}
