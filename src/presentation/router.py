from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel

from domain.models import UserQuery, DocumentInput
from domain.interfaces import IRagService, IDocumentService


def get_router(rag_service: IRagService, document_service: IDocumentService) -> APIRouter:
    """
    DIコンテナからサービスを受け取り、ルーターを作成します

    Args:
        rag_service: 依存性注入されたRAGサービス
        document_service: 依存性注入されたドキュメントサービス

    Returns:
        ルーター
    """
    router = APIRouter()

    # Request/Response モデル
    class ChatRequest(BaseModel):
        question: str

    class ChatResponse(BaseModel):
        answer: str

    class DocumentUploadRequest(BaseModel):
        content: str
        metadata: dict[str, Any] | None = None

    class DocumentUploadResponse(BaseModel):
        success: bool
        message: str
        documents_count: int | None = None

    class ClearDocumentsResponse(BaseModel):
        success: bool
        message: str

    class DocumentInfoResponse(BaseModel):
        id: str
        content: str
        metadata: dict[str, Any] | None = None
        created_at: str | None = None

    class DocumentListItemResponse(BaseModel):
        id: str
        content: str
        metadata: dict[str, Any] | None = None
        created_at: str | None = None

    class DocumentListResponseData(BaseModel):
        success: bool
        message: str
        documents: list[DocumentListItemResponse]
        total_count: int

    # Chat エンドポイント
    @router.post("/chat", response_model=ChatResponse, tags=["Chat"])
    async def chat(request: ChatRequest) -> ChatResponse:
        """
        ユーザーの質問に対してRAGを使用して回答を生成します

        Args:
            request: ユーザーの質問を含むリクエスト

        Returns:
            AI生成の回答を含むレスポンス
        """
        # ドメインモデルに変換
        query = UserQuery(content=request.question)

        # RAGサービスで回答を生成
        answer = rag_service.generate_answer(query)

        return ChatResponse(answer=answer.content)

    # ドキュメント投入エンドポイント
    @router.post("/documents", response_model=DocumentUploadResponse, tags=["Documents"])
    async def upload_documents(request: DocumentUploadRequest) -> DocumentUploadResponse:
        """
        ドキュメントをベクトルストアに投入します

        Args:
            request: 投入するドキュメント

        Returns:
            投入結果
        """
        # ドメインモデルに変換
        doc_input = DocumentInput(
            content=request.content,
            metadata=request.metadata,
        )

        # ドキュメントサービスで投入
        result = document_service.add_documents([doc_input])

        return DocumentUploadResponse(
            success=result.success,
            message=result.message,
            documents_count=result.documents_count,
        )

    # ドキュメント一覧エンドポイント
    @router.get("/documents", response_model=DocumentListResponseData, tags=["Documents"])
    async def list_documents() -> DocumentListResponseData:
        """
        ベクトルストア内の全ドキュメント一覧を取得します

        Returns:
            ドキュメント一覧
        """
        result = document_service.list_documents()

        return DocumentListResponseData(
            success=result.success,
            message=result.message,
            documents=[
                DocumentListItemResponse(
                    id=doc.id,
                    content=doc.content,
                    metadata=doc.metadata,
                    created_at=doc.created_at,
                )
                for doc in result.documents
            ],
            total_count=result.total_count,
        )

    # ドキュメント詳細エンドポイント
    @router.get("/documents/{document_id}", response_model=DocumentInfoResponse, tags=["Documents"])
    async def get_document(document_id: str) -> DocumentInfoResponse:
        """
        指定されたIDのドキュメント詳細を取得します

        Args:
            document_id: ドキュメントID

        Returns:
            ドキュメント詳細情報
        """
        doc = document_service.get_document(document_id)

        if doc is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Document not found")

        return DocumentInfoResponse(
            id=doc.id,
            content=doc.content,
            metadata=doc.metadata,
            created_at=doc.created_at,
        )

    # ドキュメントクリアエンドポイント
    @router.delete("/documents", response_model=ClearDocumentsResponse, tags=["Documents"])
    async def clear_documents() -> ClearDocumentsResponse:
        """
        ベクトルストア内の全ドキュメントをクリアします

        Returns:
            クリア結果
        """
        result = document_service.clear_documents()

        return ClearDocumentsResponse(
            success=result.success,
            message=result.message,
        )

    return router
