/// <reference types="vite/client" />

/**
 * API クライアント（TypeScript版）
 * バックエンド API との通信を管理します
 */

interface ChatResponse {
	answer: string;
}

interface DocumentUploadRequest {
	content: string;
	metadata?: Record<string, unknown>;
}

interface DocumentUploadResponse {
	success: boolean;
	message: string;
	documents_count?: number;
}

export interface DocumentInfo {
	id: string;
	content: string;
	metadata?: Record<string, unknown>;
	created_at?: string;
}

interface DocumentListResponse {
	success: boolean;
	message: string;
	documents: DocumentInfo[];
	total_count: number;
}

export interface DocumentDetailResponse {
	id: string;
	content: string;
	metadata?: Record<string, unknown>;
	created_at?: string;
}

interface ClearDocumentsResponse {
	success: boolean;
	message: string;
}

const API_BASE_URL =
	import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

/**
 * ローカルストレージからトークンを取得
 */
function getAuthToken(): string | null {
	return localStorage.getItem("authToken");
}

/**
 * APIリクエストを実行する共通関数
 */
async function apiRequest<T>(
	endpoint: string,
	options: RequestInit = {},
): Promise<T> {
	const url = `${API_BASE_URL}${endpoint}`;
	const token = getAuthToken();

	const defaultOptions: RequestInit = {
		headers: {
			"Content-Type": "application/json",
		},
	};

	// トークンがある場合は認証ヘッダーを追加
	if (token) {
		(defaultOptions.headers as Record<string, string>)[
			"Authorization"
		] = `Bearer ${token}`;
	}

	const mergedOptions: RequestInit = {
		...defaultOptions,
		...options,
		headers: {
			...(defaultOptions.headers as Record<string, string>),
			...(options.headers as Record<string, string>),
		},
	};

	try {
		const response = await fetch(url, mergedOptions);

		// ステータスコードが2xxでない場合はエラー
		if (!response.ok) {
			const errorData = (await response.json().catch(() => ({}))) as Record<
				string,
				unknown
			>;
			const errorMessage =
				(errorData.detail as string) ||
				`API Error: ${response.status} ${response.statusText}`;
			throw new Error(errorMessage);
		}

		// レスポンスがJSONでない場合（204 No Contentなど）
		if (response.status === 204) {
			return null as T;
		}

		return (await response.json()) as T;
	} catch (error) {
		console.error("API Request Error:", error);
		throw error;
	}
}

/**
 * チャットエンドポイント
 */
export async function chat(question: string): Promise<ChatResponse> {
	return apiRequest<ChatResponse>("/chat", {
		method: "POST",
		body: JSON.stringify({ question }),
	});
}

/**
 * ドキュメント投入エンドポイント
 */
export async function uploadDocument(
	content: string,
	metadata?: Record<string, unknown>,
): Promise<DocumentUploadResponse> {
	return apiRequest<DocumentUploadResponse>("/documents", {
		method: "POST",
		body: JSON.stringify({
			content,
			metadata,
		}),
	});
}

/**
 * ドキュメント一覧取得エンドポイント
 */
export async function listDocuments(): Promise<DocumentListResponse> {
	return apiRequest<DocumentListResponse>("/documents", {
		method: "GET",
	});
}

/**
 * ドキュメント詳細取得エンドポイント
 */
export async function getDocument(
	documentId: string,
): Promise<DocumentDetailResponse> {
	return apiRequest<DocumentDetailResponse>(`/documents/${documentId}`, {
		method: "GET",
	});
}

/**
 * ドキュメント全削除エンドポイント
 */
export async function clearDocuments(): Promise<ClearDocumentsResponse> {
	return apiRequest<ClearDocumentsResponse>("/documents", {
		method: "DELETE",
	});
}
