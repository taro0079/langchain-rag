import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# srcディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrastructure.container import create_injector
from presentation.router import get_router


def create_app() -> FastAPI:
    """
    FastAPIアプリケーションを作成します

    Returns:
        FastAPIアプリケーションインスタンス
    """
    from domain.interfaces import IRagService, IDocumentService
    from infrastructure.auth_service import AuthService

    # DIコンテナの作成
    injector = create_injector()

    # サービスの取得
    rag_service = injector.get(IRagService)
    document_service = injector.get(IDocumentService)
    auth_service = injector.get(AuthService)

    # FastAPIアプリケーションの作成
    app = FastAPI(
        title="LangChain RAG API",
        description="LangChainを使用したRAG（検索拡張生成）API",
        version="0.1.0",
    )

    # CORS設定
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ルーターをアプリケーションに登録
    router = get_router(rag_service, document_service, auth_service)
    app.include_router(router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        """ヘルスチェックエンドポイント"""
        return {"status": "ok"}

    return app


# アプリケーションの作成
app = create_app()


def main():
    """FastAPIサーバーを起動します"""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )


if __name__ == "__main__":
    main()
