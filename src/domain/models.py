from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class UserQuery:
    content: str


@dataclass
class AiAnswer:
    content: str


@dataclass
class DocumentInput:
    """ドキュメント投入用のモデル"""
    content: str
    metadata: Optional[dict[str, Any]] = None


@dataclass
class DocumentUploadResult:
    """ドキュメント投入結果のモデル"""
    success: bool
    message: str
    documents_count: Optional[int] = None


@dataclass
class DocumentInfo:
    """ドキュメント情報のモデル"""
    id: str
    content: str
    metadata: Optional[dict[str, Any]] = None
    created_at: Optional[str] = None


@dataclass
class DocumentListResult:
    """ドキュメント一覧結果のモデル"""
    success: bool
    message: str
    documents: list[DocumentInfo]
    total_count: int
