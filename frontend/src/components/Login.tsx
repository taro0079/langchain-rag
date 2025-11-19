import React, { type FC, useState } from "react";
import { useAuth } from "../hooks/useAuth";

interface LoginProps {
	onLoginSuccess?: () => void;
}

export function Login({ onLoginSuccess }: LoginProps): React.ReactElement {
	const auth = useAuth();
	const [isLogin, setIsLogin] = useState(true);
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [localError, setLocalError] = useState<string | null>(null);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setLocalError(null);

		try {
			if (isLogin) {
				const result = await auth.login(username, password);
				if (result.success) {
					// ログイン成功後、ページをリロードして auth 状態を更新
					setTimeout(() => window.location.reload(), 500);
				} else {
					setLocalError(result.error || "Login failed");
				}
			} else {
				const result = await auth.register(username, password);
				if (result.success) {
					setLocalError("Registration successful! Please login.");
					setUsername("");
					setPassword("");
					setIsLogin(true);
				} else {
					setLocalError(result.error || "Registration failed");
				}
			}
		} catch (err) {
			const errorMessage =
				err instanceof Error ? err.message : "Authentication failed";
			setLocalError(errorMessage);
		}
	};

	return (
		<div className="min-h-screen bg-gray-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
			<div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
				<h2 className="text-2xl font-bold text-gray-900 mb-6">
					{isLogin ? "Login" : "Register"}
				</h2>

				{(localError || auth.error) && (
					<div
						className={`mb-4 p-4 rounded ${
							(localError || auth.error)?.includes("successful")
								? "bg-green-100 text-green-700"
								: "bg-red-100 text-red-700"
						}`}
					>
						{localError || auth.error}
					</div>
				)}

				<form onSubmit={handleSubmit} className="space-y-4">
					<div>
						<label
							htmlFor="username"
							className="block text-sm font-medium text-gray-700"
						>
							Username
						</label>
						<input
							id="username"
							type="text"
							value={username}
							onChange={(e) => setUsername(e.target.value)}
							required
							disabled={auth.loading}
							className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
						/>
					</div>

					<div>
						<label
							htmlFor="password"
							className="block text-sm font-medium text-gray-700"
						>
							Password
						</label>
						<input
							id="password"
							type="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							required
							disabled={auth.loading}
							className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
						/>
					</div>

					<button
						type="submit"
						disabled={auth.loading}
						className="w-full bg-blue-600 text-white py-2 px-4 rounded-md font-medium hover:bg-blue-700 disabled:bg-blue-400 transition"
					>
						{auth.loading ? "Processing..." : isLogin ? "Login" : "Register"}
					</button>
				</form>

				<div className="mt-4 text-center">
					<button
						type="button"
						onClick={() => {
							setIsLogin(!isLogin);
							setLocalError(null);
							setUsername("");
							setPassword("");
						}}
						className="text-blue-600 hover:text-blue-700 text-sm"
					>
						{isLogin
							? "Need an account? Register"
							: "Already have an account? Login"}
					</button>
				</div>

				{isLogin && (
					<div className="mt-4 text-xs text-gray-600">
						<p className="font-semibold">Demo credentials:</p>
						<p>Username: testuser</p>
						<p>Password: password123</p>
					</div>
				)}
			</div>
		</div>
	);
}
