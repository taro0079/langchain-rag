from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import PyPDF2
import io

from domain.models import UserQuery, DocumentInput
from domain.interfaces import IRagService, IDocumentService
from domain.user_models import UserLoginRequest, UserRegisterRequest
from infrastructure.auth_service import AuthService
from infrastructure.auth_middleware import get_current_user


def get_router(
    rag_service: IRagService, document_service: IDocumentService, auth_service: AuthService
) -> APIRouter:
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

    class AuthResponse(BaseModel):
        success: bool
        message: str
        access_token: Optional[str] = None
        user_id: Optional[str] = None
        username: Optional[str] = None

    # 認証エンドポイント
    @router.post("/auth/register", response_model=AuthResponse, tags=["Auth"])
    async def register(request: UserRegisterRequest) -> AuthResponse:
        """
        新規ユーザーを登録します

        Args:
            request: ユーザー名とパスワード

        Returns:
            登録結果
        """
        result = auth_service.register(request)
        return AuthResponse(
            success=result.success,
            message=result.message,
            user_id=result.user_id,
        )

    @router.post("/auth/login", response_model=AuthResponse, tags=["Auth"])
    async def login(request: UserLoginRequest) -> AuthResponse:
        """
        ユーザーをログインさせます

        Args:
            request: ユーザー名とパスワード

        Returns:
            ログイン結果（成功時はアクセストークンを含む）
        """
        result = auth_service.login(request)
        return AuthResponse(
            success=result.success,
            message=result.message,
            access_token=result.access_token,
            user_id=result.user_id,
            username=result.username,
        )

    @router.post("/auth/logout", tags=["Auth"])
    async def logout(
        current_user: dict = Depends(get_current_user),
    ) -> dict[str, str]:
        """
        ユーザーをログアウトさせます

        Args:
            current_user: 認証されたユーザー情報

        Returns:
            ログアウト完了メッセージ
        """
        return {"message": "ログアウトしました"}

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

    # ドキュメント投入エンドポイント（テキスト）
    @router.post("/documents", response_model=DocumentUploadResponse, tags=["Documents"])
    async def upload_documents(
        request: DocumentUploadRequest,
        current_user: dict = Depends(get_current_user),
    ) -> DocumentUploadResponse:
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

    # ファイルアップロードエンドポイント（Markdown/PDF）
    @router.post("/documents/upload-file", response_model=DocumentUploadResponse, tags=["Documents"])
    async def upload_file(
        file: UploadFile = File(...),
        current_user: dict = Depends(get_current_user),
    ) -> DocumentUploadResponse:
        """
        MarkdownまたはPDFファイルをアップロードして投入します

        Args:
            file: アップロードするファイル（.md, .pdf）
            current_user: 認証されたユーザー情報

        Returns:
            投入結果
        """
        if not file.filename:
            raise HTTPException(status_code=400, detail="ファイル名が必要です")

        # ファイルタイプの判定
        if file.filename.endswith(".md"):
            # Markdownファイルの処理
            content = await file.read()
            text_content = content.decode("utf-8")
        elif file.filename.endswith(".pdf"):
            # PDFファイルの処理
            content = await file.read()
            try:
                pdf_file = io.BytesIO(content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"PDFの読み込みエラー: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Markdown (.md) またはPDF (.pdf) ファイルをアップロードしてください")

        if not text_content.strip():
            raise HTTPException(status_code=400, detail="ファイルが空です")

        # ドキュメントサービスで投入
        doc_input = DocumentInput(
            content=text_content,
            metadata={"filename": file.filename, "file_type": file.content_type},
        )
        result = document_service.add_documents([doc_input])

        return DocumentUploadResponse(
            success=result.success,
            message=result.message,
            documents_count=result.documents_count,
        )

    # ドキュメント一覧エンドポイント
    @router.get("/documents", response_model=DocumentListResponseData, tags=["Documents"])
    async def list_documents(
        current_user: dict = Depends(get_current_user),
    ) -> DocumentListResponseData:
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
    async def get_document(
        document_id: str,
        current_user: dict = Depends(get_current_user),
    ) -> DocumentInfoResponse:
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
    async def clear_documents(
        current_user: dict = Depends(get_current_user),
    ) -> ClearDocumentsResponse:
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
