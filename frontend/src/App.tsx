import React, { type FC, useState, useEffect } from "react";
import {
	chat,
	clearDocuments,
	type DocumentDetailResponse,
	type DocumentInfo,
	getDocument,
	listDocuments,
	uploadDocument,
	uploadDocumentFile,
} from "./api/client";
import { Login } from "./components/Login";
import { useAuth } from "./hooks/useAuth";

type TabType = "chat" | "documents";

const App: FC = () => {
	const [, setRefresh] = useState(0);
	const auth = useAuth();
	const [activeTab, setActiveTab] = useState<TabType>("chat");
	const [question, setQuestion] = useState("");
	const [answer, setAnswer] = useState("");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [documentContent, setDocumentContent] = useState("");
	const [documents, setDocuments] = useState<DocumentInfo[]>([]);
	const [selectedDocument, setSelectedDocument] =
		useState<DocumentDetailResponse | null>(null);
	const [showDocumentDetail, setShowDocumentDetail] = useState(false);
	const [selectedFile, setSelectedFile] = useState<File | null>(null);

	// ログイン成功時にコンポーネントを再マウント
	useEffect(() => {
		const checkAuth = () => {
			const token = localStorage.getItem("authToken");
			if (token && !auth.isAuthenticated) {
				setRefresh((prev) => prev + 1);
			}
		};

		const interval = setInterval(checkAuth, 100);
		return () => clearInterval(interval);
	}, [auth.isAuthenticated]);

	// ドキュメント管理タブに移動時にドキュメント一覧を取得
	useEffect(() => {
		if (activeTab === "documents" && auth.isAuthenticated) {
			handleListDocuments();
		}
	}, [activeTab, auth.isAuthenticated]);

	// チャットハンドラー
	const handleChat = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!question.trim()) return;

		setLoading(true);
		setError("");
		setAnswer("");

		try {
			const response = await chat(question);
			setAnswer(response.answer);
			setQuestion("");
		} catch (err) {
			setError(err instanceof Error ? err.message : "エラーが発生しました");
		} finally {
			setLoading(false);
		}
	};

	// ドキュメント投入ハンドラー
	const handleUploadDocument = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!documentContent.trim()) return;

		setLoading(true);
		setError("");

		try {
			const response = await uploadDocument(documentContent);
			alert(`ドキュメントを投入しました: ${response.message}`);
			setDocumentContent("");
			// ドキュメント一覧を更新
			await handleListDocuments();
		} catch (err) {
			setError(err instanceof Error ? err.message : "エラーが発生しました");
		} finally {
			setLoading(false);
		}
	};

	// ファイルアップロードハンドラー
	const handleUploadFile = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!selectedFile) return;

		setLoading(true);
		setError("");

		try {
			const response = await uploadDocumentFile(selectedFile);
			alert(`ファイルを投入しました: ${response.message}`);
			setSelectedFile(null);
			// ドキュメント一覧を更新
			await handleListDocuments();
		} catch (err) {
			setError(err instanceof Error ? err.message : "エラーが発生しました");
		} finally {
			setLoading(false);
		}
	};

	// ドキュメント一覧取得ハンドラー
	const handleListDocuments = async () => {
		setLoading(true);
		setError("");

		try {
			const response = await listDocuments();
			setDocuments(response.documents);
		} catch (err) {
			setError(err instanceof Error ? err.message : "エラーが発生しました");
		} finally {
			setLoading(false);
		}
	};

	// ドキュメント詳細取得ハンドラー
	const handleGetDocument = async (docId: string) => {
		setLoading(true);
		setError("");

		try {
			const response = await getDocument(docId);
			setSelectedDocument(response);
			setShowDocumentDetail(true);
		} catch (err) {
			setError(err instanceof Error ? err.message : "エラーが発生しました");
		} finally {
			setLoading(false);
		}
	};

	// ドキュメント全削除ハンドラー
	const handleClearDocuments = async () => {
		if (!confirm("本当に全ドキュメントを削除しますか？")) return;

		setLoading(true);
		setError("");

		try {
			const response = await clearDocuments();
			alert(response.message);
			setDocuments([]);
			setSelectedDocument(null);
			setShowDocumentDetail(false);
		} catch (err) {
			setError(err instanceof Error ? err.message : "エラーが発生しました");
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="min-h-screen bg-gray-50 flex flex-col">
			{/* ヘッダー */}
			<header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-8 px-4 shadow-lg">
				<div className="max-w-7xl mx-auto flex justify-between items-start">
					<div>
						<h1 className="text-4xl font-bold mb-2">
							LangChain RAG アプリケーション
						</h1>
						<p className="text-blue-100">
							React + TypeScript + Tailwind CSS フロントエンド
						</p>
					</div>
					<div className="text-right">
						{auth.isAuthenticated ? (
							<>
								<p className="text-blue-100 mb-2">
									User: <span className="font-semibold">{auth.user?.username}</span>
								</p>
								<button
									type="button"
									onClick={() => auth.logout()}
									className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors font-medium text-sm"
								>
									ログアウト
								</button>
							</>
						) : (
							<button
								type="button"
								onClick={() => setActiveTab("documents")}
								className="px-4 py-2 bg-blue-400 hover:bg-blue-500 text-white rounded-lg transition-colors font-medium text-sm"
							>
								ドキュメント管理にログイン
							</button>
						)}
					</div>
				</div>
			</header>

			{/* タブナビゲーション */}
			<nav className="bg-white border-b border-gray-200 sticky top-0 z-40">
				<div className="max-w-7xl mx-auto flex gap-8 px-4">
					<button
						type="button"
						onClick={() => setActiveTab("chat")}
						className={`py-4 px-2 font-medium transition-colors border-b-2 ${
							activeTab === "chat"
								? "border-blue-600 text-blue-600"
								: "border-transparent text-gray-600 hover:text-gray-900"
						}`}
					>
						💬 チャット
					</button>
					<button
						type="button"
						onClick={() => setActiveTab("documents")}
						className={`py-4 px-2 font-medium transition-colors border-b-2 ${
							activeTab === "documents"
								? "border-blue-600 text-blue-600"
								: "border-transparent text-gray-600 hover:text-gray-900"
						}`}
					>
						📄 ドキュメント管理
					</button>
				</div>
			</nav>

			{/* エラーメッセージ */}
			{error && (
				<div className="max-w-7xl mx-auto w-full px-4 mt-4">
					<div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
						<p className="text-red-700">{error}</p>
					</div>
				</div>
			)}

			{/* メインコンテンツ */}
			<main className="flex-1 max-w-7xl mx-auto w-full px-4 py-8">
				{/* チャットセクション */}
				{activeTab === "chat" && (
					<div className="space-y-6">
						<h2 className="text-3xl font-bold text-gray-900">チャット</h2>

						<form onSubmit={handleChat} className="flex gap-2">
							<input
								type="text"
								value={question}
								onChange={(e) => setQuestion(e.target.value)}
								placeholder="質問を入力してください..."
								disabled={loading}
								className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
							/>
							<button
								type="submit"
								disabled={loading}
								className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-medium"
							>
								{loading ? "処理中..." : "送信"}
							</button>
						</form>

						{answer && (
							<div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
								<h3 className="text-xl font-semibold text-gray-900 mb-4">
									回答
								</h3>
								<p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
									{answer}
								</p>
							</div>
						)}
					</div>
				)}

				{/* ドキュメント管理セクション */}
				{activeTab === "documents" && (
					<div className="space-y-6">
						<h2 className="text-3xl font-bold text-gray-900">
							ドキュメント管理
						</h2>

						{!auth.isAuthenticated ? (
							<div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded">
								<p className="text-blue-900 mb-4">
									ドキュメント管理機能を使用するにはログインが必要です。
								</p>
								<Login onLoginSuccess={() => {}} />
							</div>
						) : (
							<>
								<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
									{/* 投入パネル */}
									<div className="bg-white rounded-lg shadow p-6">
								<h3 className="text-xl font-semibold text-gray-900 mb-4">
									ドキュメント投入
								</h3>
									{/* テキスト投入フォーム */}
									<form onSubmit={handleUploadDocument} className="space-y-4">
										<div className="text-sm font-medium text-gray-600">テキスト入力</div>
										<textarea
											value={documentContent}
											onChange={(e) => setDocumentContent(e.target.value)}
											placeholder="ドキュメント内容を入力してください..."
											rows={6}
											disabled={loading}
											className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 font-mono text-sm"
										/>
										<button
											type="submit"
											disabled={loading || !documentContent.trim()}
											className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-medium"
										>
											{loading ? "投入中..." : "テキストを投入"}
										</button>
									</form>

									{/* ファイルアップロードフォーム */}
									<form onSubmit={handleUploadFile} className="space-y-4 border-t pt-4">
										<div className="text-sm font-medium text-gray-600">ファイルアップロード</div>
										<div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors">
											<label className="cursor-pointer">
												<input
													type="file"
													accept=".md,.pdf"
													onChange={(e) => {
														const file = e.target.files?.[0];
														if (file) setSelectedFile(file);
													}}
													disabled={loading}
													className="hidden"
												/>
												<div className="space-y-2">
													<p className="text-lg font-medium text-gray-700">
														{selectedFile ? selectedFile.name : "ファイルを選択"}
													</p>
													<p className="text-sm text-gray-500">
														Markdown (.md) または PDF (.pdf) ファイル
													</p>
												</div>
											</label>
										</div>
										<button
											type="submit"
											disabled={loading || !selectedFile}
											className="w-full px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors font-medium"
										>
											{loading ? "投入中..." : "ファイルを投入"}
										</button>
									</form>

									{/* 削除ボタン */}
									<div className="border-t pt-4">
										<button
											type="button"
											onClick={handleClearDocuments}
											disabled={loading || documents.length === 0}
											className="w-full px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 transition-colors font-medium"
										>
											すべてのドキュメントを削除
										</button>
									</div>
									</div>

									{/* 一覧パネル */}
									<div className="bg-white rounded-lg shadow p-6">
										<h3 className="text-xl font-semibold text-gray-900 mb-4">
											ドキュメント一覧 ({documents.length})
										</h3>
										{documents.length === 0 ? (
											<p className="text-center text-gray-500 py-8">
												ドキュメントがありません
											</p>
										) : (
											<ul className="space-y-2 max-h-96 overflow-y-auto">
												{documents.map((doc) => (
													<li
														key={doc.id}
														className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
													>
														<div className="flex-1 min-w-0 pr-2">
															<p className="text-gray-900 text-sm line-clamp-2">
																{doc.content}
															</p>
															<p className="text-gray-500 text-xs mt-1">
																{doc.created_at
																	? new Date(doc.created_at).toLocaleString()
																	: "日時不明"}
															</p>
														</div>
														<button
															type="button"
															onClick={() => handleGetDocument(doc.id)}
															disabled={loading}
															className="flex-shrink-0 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
														>
															詳細
														</button>
													</li>
												))}
											</ul>
										)}
									</div>
								</div>

								{/* ドキュメント詳細モーダル */}
								{showDocumentDetail && selectedDocument && (
									<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
										<div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-96 overflow-y-auto">
											<div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex justify-between items-center">
												<h3 className="text-xl font-semibold text-gray-900">
													ドキュメント詳細
												</h3>
												<button
													type="button"
													onClick={() => {
														setShowDocumentDetail(false);
														setSelectedDocument(null);
													}}
													className="text-gray-500 hover:text-gray-700 text-2xl"
												>
													×
												</button>
											</div>
											<div className="p-6 space-y-4">
												<div>
													<p className="text-sm text-gray-600 mb-1">ID</p>
													<p className="text-gray-900 font-mono text-sm break-all">
														{selectedDocument.id}
													</p>
												</div>
												<div>
													<p className="text-sm text-gray-600 mb-1">作成日時</p>
													<p className="text-gray-900">
														{selectedDocument.created_at
															? new Date(
																	selectedDocument.created_at,
																).toLocaleString()
															: "日時不明"}
													</p>
												</div>
												<div>
													<p className="text-sm text-gray-600 mb-2">内容</p>
													<div className="bg-gray-50 rounded p-4 text-gray-900 whitespace-pre-wrap break-words max-h-48 overflow-y-auto font-mono text-sm">
														{selectedDocument.content}
													</div>
												</div>
											</div>
										</div>
									</div>
								)}
							</>
						)}
					</div>
				)}
			</main>
		</div>
	);
};

export default App;
