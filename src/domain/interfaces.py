from abc import ABC, abstractmethod
from typing import Optional

from domain.models import (
    AiAnswer,
    UserQuery,
    DocumentInput,
    DocumentUploadResult,
    DocumentInfo,
    DocumentListResult,
)


class IRagService(ABC):
    @abstractmethod
    def generate_answer(self, query: UserQuery) -> AiAnswer:
        pass


class IDocumentService(ABC):
    """ドキュメント投入・管理用のサービスインターフェース"""

    @abstractmethod
    def add_documents(self, documents: list[DocumentInput]) -> DocumentUploadResult:
        """
        ドキュメントをベクトルストアに追加します

        Args:
            documents: 投入するドキュメントのリスト

        Returns:
            投入結果
        """
        pass

    @abstractmethod
    def clear_documents(self) -> DocumentUploadResult:
        """
        ベクトルストア内の全ドキュメントをクリアします

        Returns:
            クリア結果
        """
        pass

    @abstractmethod
    def list_documents(self) -> DocumentListResult:
        """
        ベクトルストア内の全ドキュメント一覧を取得します

        Returns:
            ドキュメント一覧結果
        """
        pass

    @abstractmethod
    def get_document(self, document_id: str) -> Optional[DocumentInfo]:
        """
        指定されたIDのドキュメント詳細を取得します

        Args:
            document_id: ドキュメントID

        Returns:
            ドキュメント情報、見つからない場合はNone
        """
        pass
