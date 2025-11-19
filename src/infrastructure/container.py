"""
依存性注入（DI）コンテナの実装

このモジュールは、injectorライブラリを使用して、
アプリケーション全体の依存性を管理します。
"""

from injector import Injector, Module, provider, singleton
from pydantic import SecretStr
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma

from domain.interfaces import IRagService, IDocumentService
from infrastructure.rag_service import LangChainRagService
from infrastructure.document_service import LangChainDocumentService
from infrastructure.auth_service import AuthService
import config


class AppModule(Module):
    """アプリケーションのDIモジュール"""

    @singleton
    @provider
    def provide_llm(self) -> ChatOpenAI:
        """
        ChatOpenAIのプロバイダー

        Returns:
            シングルトンのChatOpenAIインスタンス
        """
        return ChatOpenAI(
            api_key=SecretStr(config.OPENAI_API_KEY) if config.OPENAI_API_KEY else None,
            model=config.OPENAI_MODEL,
            temperature=0.7,
        )

    @singleton
    @provider
    def provide_embeddings(self) -> OpenAIEmbeddings:
        """
        OpenAIEmbeddingsのプロバイダー

        Returns:
            シングルトンのOpenAIEmbeddingsインスタンス
        """
        return OpenAIEmbeddings(
            api_key=SecretStr(config.OPENAI_API_KEY) if config.OPENAI_API_KEY else None,
        )

    @singleton
    @provider
    def provide_vector_store(self, embeddings: OpenAIEmbeddings) -> Chroma:
        """
        Chromaベクトルストアのプロバイダー

        Args:
            embeddings: OpenAIEmbeddingsインスタンス

        Returns:
            シングルトンのChromaインスタンス
        """
        return Chroma(
            persist_directory=config.CHROMA_PERSIST_DIRECTORY,
            embedding_function=embeddings,
            collection_name=config.CHROMA_COLLECTION_NAME,
        )

    @singleton
    @provider
    def provide_rag_service(
        self, llm: ChatOpenAI, embeddings: OpenAIEmbeddings, vector_store: Chroma
    ) -> IRagService:
        """
        RAGサービスのプロバイダー

        Args:
            llm: ChatOpenAIインスタンス
            embeddings: OpenAIEmbeddingsインスタンス
            vector_store: Chromaベクトルストアインスタンス

        Returns:
            シングルトンのIRagService実装インスタンス
        """
        return LangChainRagService(llm=llm, embeddings=embeddings, vector_store=vector_store)

    @singleton
    @provider
    def provide_document_service(
        self, embeddings: OpenAIEmbeddings, vector_store: Chroma
    ) -> IDocumentService:
        """
        ドキュメントサービスのプロバイダー

        Args:
            embeddings: OpenAIEmbeddingsインスタンス
            vector_store: Chromaベクトルストアインスタンス

        Returns:
            シングルトンのIDocumentService実装インスタンス
        """
        return LangChainDocumentService(embeddings=embeddings, vector_store=vector_store)

    @singleton
    @provider
    def provide_auth_service(self) -> AuthService:
        """
        認証サービスのプロバイダー

        Returns:
            シングルトンのAuthServiceインスタンス
        """
        return AuthService()


def create_injector() -> Injector:
    """
    アプリケーションのInjectorインスタンスを作成します

    Returns:
        Injectorインスタンス
    """
    return Injector([AppModule()])
