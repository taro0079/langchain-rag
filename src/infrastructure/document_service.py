"""
ドキュメント投入・管理用のサービス実装

このモジュールは、LangChainを使用してベクトルストアに
ドキュメントを投入・管理するサービスを提供します。
"""

import uuid
from typing import Optional
from datetime import datetime

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from domain.interfaces import IDocumentService
from domain.models import (
    DocumentInput,
    DocumentUploadResult,
    DocumentInfo,
    DocumentListResult,
)
import config


class LangChainDocumentService(IDocumentService):
    """
    LangChainを使用したドキュメント投入・管理サービス
    """

    def __init__(
        self,
        embeddings: OpenAIEmbeddings,
        vector_store: Chroma,
    ) -> None:
        """
        ドキュメントサービスを初期化します

        Args:
            embeddings: OpenAIEmbeddingsのインスタンス
            vector_store: Chromaベクトルストアのインスタンス
        """
        self.embeddings = embeddings
        self.vector_store = vector_store

        # テキストスプリッター（ドキュメント分割用）
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""],
        )

    def add_documents(self, documents: list[DocumentInput]) -> DocumentUploadResult:
        """
        ドキュメントをベクトルストアに追加します

        Args:
            documents: 投入するドキュメントのリスト

        Returns:
            投入結果
        """
        try:
            # DocumentInputをLangChainのDocumentオブジェクトに変換
            langchain_docs: list[Document] = []
            total_chunks = 0

            for doc_input in documents:
                # ドキュメントIDを生成
                doc_id = str(uuid.uuid4())
                created_at = datetime.now().isoformat()

                # テキストを分割
                chunks = self.text_splitter.split_text(doc_input.content)
                total_chunks += len(chunks)

                # チャンクごとにDocumentオブジェクトを作成
                for chunk in chunks:
                    metadata = doc_input.metadata or {}
                    # メタデータにドキュメント情報を追加
                    metadata["document_id"] = doc_id
                    metadata["created_at"] = created_at
                    # 最初のチャンクのみに完全なドキュメント内容を保存
                    if chunk == chunks[0]:
                        metadata["full_content"] = doc_input.content

                    doc = Document(
                        page_content=chunk,
                        metadata=metadata,
                    )
                    langchain_docs.append(doc)

            # ベクトルストアに追加
            if langchain_docs:
                self.vector_store.add_documents(langchain_docs)

            return DocumentUploadResult(
                success=True,
                message=f"Successfully uploaded {len(documents)} document(s) with {total_chunks} chunk(s)",
                documents_count=total_chunks,
            )

        except Exception as e:
            return DocumentUploadResult(
                success=False,
                message=f"Failed to upload documents: {str(e)}",
                documents_count=None,
            )

    def clear_documents(self) -> DocumentUploadResult:
        """
        ベクトルストア内の全ドキュメントをクリアします

        Returns:
            クリア結果
        """
        try:
            # Chromaのコレクションから全ドキュメントを削除
            # Chromaベクトルストアを再初期化することでクリアする
            from langchain_chroma import Chroma as ChromaVectorStore

            # 既存のコレクションを削除
            ChromaVectorStore(
                persist_directory=config.CHROMA_PERSIST_DIRECTORY,
                embedding_function=self.embeddings,
                collection_name=config.CHROMA_COLLECTION_NAME,
            ).delete_collection()

            # コレクションを再作成
            self.vector_store = Chroma(
                persist_directory=config.CHROMA_PERSIST_DIRECTORY,
                embedding_function=self.embeddings,
                collection_name=config.CHROMA_COLLECTION_NAME,
            )

            return DocumentUploadResult(
                success=True,
                message="Successfully cleared all documents from the vector store",
                documents_count=0,
            )

        except Exception as e:
            return DocumentUploadResult(
                success=False,
                message=f"Failed to clear documents: {str(e)}",
                documents_count=None,
            )

    def list_documents(self) -> DocumentListResult:
        """
        ベクトルストア内の全ドキュメント一覧を取得します

        Returns:
            ドキュメント一覧結果
        """
        try:
            documents: list[DocumentInfo] = []
            seen_doc_ids: set[str] = set()

            # Chromaから全ドキュメントを取得
            all_docs = self.vector_store.get(include=["metadatas"])

            if all_docs and all_docs["metadatas"]:
                for metadata in all_docs["metadatas"]:
                    doc_id = metadata.get("document_id")
                    # 同じドキュメントIDは1回だけ処理
                    if doc_id and doc_id not in seen_doc_ids:
                        seen_doc_ids.add(doc_id)

                        # 完全なコンテンツを取得
                        content = metadata.get("full_content", "")
                        # 完全なコンテンツがない場合は先頭100字で省略
                        if not content:
                            content = "Document content not available"
                        elif len(content) > 100:
                            content = content[:100] + "..."

                        doc = DocumentInfo(
                            id=doc_id,
                            content=content,
                            metadata={
                                k: v
                                for k, v in metadata.items()
                                if k not in ["document_id", "created_at", "full_content"]
                            },
                            created_at=metadata.get("created_at"),
                        )
                        documents.append(doc)

            return DocumentListResult(
                success=True,
                message=f"Retrieved {len(documents)} document(s)",
                documents=documents,
                total_count=len(documents),
            )

        except Exception as e:
            return DocumentListResult(
                success=False,
                message=f"Failed to list documents: {str(e)}",
                documents=[],
                total_count=0,
            )

    def get_document(self, document_id: str) -> Optional[DocumentInfo]:
        """
        指定されたIDのドキュメント詳細を取得します

        Args:
            document_id: ドキュメントID

        Returns:
            ドキュメント情報、見つからない場合はNone
        """
        try:
            # Chromaから全ドキュメントを取得
            all_docs = self.vector_store.get(include=["metadatas"])

            if all_docs and all_docs["metadatas"]:
                for metadata in all_docs["metadatas"]:
                    if metadata.get("document_id") == document_id:
                        # 最初にマッチしたメタデータから完全なコンテンツを取得
                        content = metadata.get("full_content", "")

                        return DocumentInfo(
                            id=document_id,
                            content=content,
                            metadata={
                                k: v
                                for k, v in metadata.items()
                                if k not in ["document_id", "created_at", "full_content"]
                            },
                            created_at=metadata.get("created_at"),
                        )

            return None

        except Exception:
            return None
