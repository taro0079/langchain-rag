import { useCallback, useState, useEffect } from "react";

interface AuthState {
	isAuthenticated: boolean;
	user: { id: string; username: string } | null;
	token: string | null;
	loading: boolean;
	error: string | null;
}

const API_BASE_URL =
	import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export function useAuth() {
	const [state, setState] = useState<AuthState>(() => {
		// ローカルストレージからトークンを復元
		const storedToken = localStorage.getItem("authToken");
		const storedUser = localStorage.getItem("authUser");

		if (storedToken && storedUser) {
			try {
				const user = JSON.parse(storedUser);
				return {
					isAuthenticated: true,
					user,
					token: storedToken,
					loading: false,
					error: null,
				};
			} catch {
				localStorage.removeItem("authToken");
				localStorage.removeItem("authUser");
			}
		}

		return {
			isAuthenticated: false,
			user: null,
			token: null,
			loading: false,
			error: null,
		};
	});

	// ローカルストレージの変更を監視
	useEffect(() => {
		const handleStorageChange = () => {
			const storedToken = localStorage.getItem("authToken");
			const storedUser = localStorage.getItem("authUser");

			if (storedToken && storedUser) {
				try {
					const user = JSON.parse(storedUser);
					setState({
						isAuthenticated: true,
						user,
						token: storedToken,
						loading: false,
						error: null,
					});
				} catch {
					setState({
						isAuthenticated: false,
						user: null,
						token: null,
						loading: false,
						error: null,
					});
				}
			} else {
				setState({
					isAuthenticated: false,
					user: null,
					token: null,
					loading: false,
					error: null,
				});
			}
		};

		window.addEventListener("storage", handleStorageChange);
		return () => window.removeEventListener("storage", handleStorageChange);
	}, []);

	const register = useCallback(async (username: string, password: string) => {
		setState((prev) => ({ ...prev, loading: true, error: null }));
		try {
			const response = await fetch(`${API_BASE_URL}/auth/register`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ username, password }),
			});

			const data = (await response.json()) as {
				success: boolean;
				message: string;
				user_id?: string;
			};

			if (!response.ok || !data.success) {
				throw new Error(data.message || "Registration failed");
			}

			setState((prev) => ({
				...prev,
				loading: false,
				error: null,
			}));
			return { success: true };
		} catch (error) {
			const errorMessage =
				error instanceof Error ? error.message : "Registration failed";
			setState((prev) => ({ ...prev, loading: false, error: errorMessage }));
			return { success: false, error: errorMessage };
		}
	}, []);

	const login = useCallback(async (username: string, password: string) => {
		setState((prev) => ({ ...prev, loading: true, error: null }));
		try {
			const response = await fetch(`${API_BASE_URL}/auth/login`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ username, password }),
			});

			const data = (await response.json()) as {
				success: boolean;
				message: string;
				access_token?: string;
				user_id?: string;
				username?: string;
			};

			if (!response.ok || !data.success) {
				throw new Error(data.message || "Login failed");
			}

			if (!data.access_token || !data.user_id || !data.username) {
				throw new Error("Invalid response from server");
			}

			const user = { id: data.user_id, username: data.username };

			// トークンとユーザー情報をローカルストレージに保存
			localStorage.setItem("authToken", data.access_token);
			localStorage.setItem("authUser", JSON.stringify(user));

			setState((prev) => ({
				...prev,
				isAuthenticated: true,
				user,
				token: data.access_token,
				loading: false,
				error: null,
			}));

			return { success: true };
		} catch (error) {
			const errorMessage =
				error instanceof Error ? error.message : "Login failed";
			setState((prev) => ({ ...prev, loading: false, error: errorMessage }));
			return { success: false, error: errorMessage };
		}
	}, []);

	const logout = useCallback(async () => {
		setState((prev) => ({ ...prev, loading: true }));
		try {
			const token = state.token;
			if (token) {
				await fetch(`${API_BASE_URL}/auth/logout`, {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`,
					},
				});
			}
		} catch (error) {
			console.error("Logout error:", error);
		} finally {
			// トークンとユーザー情報をローカルストレージから削除
			localStorage.removeItem("authToken");
			localStorage.removeItem("authUser");

			setState({
				isAuthenticated: false,
				user: null,
				token: null,
				loading: false,
				error: null,
			});
		}
	}, [state.token]);

	return {
		...state,
		register,
		login,
		logout,
	};
}
