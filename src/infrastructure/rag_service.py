from typing import Any, List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from domain.interfaces import IRagService
from domain.models import UserQuery, AiAnswer
import config


class LangChainRagService(IRagService):
    """
    LangChainを使用したRAGサービス
    """

    def __init__(
        self,
        llm: ChatOpenAI,
        embeddings: OpenAIEmbeddings,
        vector_store: Chroma,
    ) -> None:
        """
        RAGサービスを初期化します

        Args:
            llm: ChatOpenAIのインスタンス
            embeddings: OpenAIEmbeddingsのインスタンス
            vector_store: Chromaベクトルストアのインスタンス
        """
        self.llm = llm
        self.embeddings = embeddings
        self.vector_store = vector_store

        # リトリーバーのセットアップ
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": config.TOP_K_RESULTS}
        )

        # RAGプロンプトのセットアップ
        self.prompt = PromptTemplate(
            template="""あなたは有益なアシスタントです。以下の文脈を使用して、質問に答えてください。

文脈:
{context}

質問: {question}

答え:""",
            input_variables=["context", "question"],
        )

    def generate_answer(self, query: UserQuery) -> AiAnswer:
        """
        ユーザーのクエリに対してRAGを使用して回答を生成します

        Args:
            query: ユーザーのクエリ

        Returns:
            AI生成の回答
        """
        # RAGチェーンの構築
        rag_chain = (
            {
                "context": self.retriever | self._format_docs,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        # クエリの実行
        answer = rag_chain.invoke(query.content)

        return AiAnswer(content=answer)

    def _format_docs(self, docs: List[Document]) -> str:
        """
        取得されたドキュメントをフォーマットします

        Args:
            docs: ドキュメントのリスト

        Returns:
            フォーマットされたテキスト
        """
        return "\n\n".join(doc.page_content for doc in docs)
