import React, { createContext, useContext, useState, useEffect } from "react";
import { getMyProfile, loginUser, registerUser } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("connectme_token") || null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function initAuth() {
      if (token) {
        try {
          const profile = await getMyProfile();
          setUser(profile);
        } catch (err) {
          console.error("Token verification failed:", err);
          logout();
        }
      }
      setLoading(false);
    }
    initAuth();
  }, [token]);

  async function login(username, password) {
    const data = await loginUser(username, password);
    localStorage.setItem("connectme_token", data.access_token);
    setToken(data.access_token);
    const profile = await getMyProfile();
    setUser(profile);
    return data;
  }

  async function register(payload) {
    const data = await registerUser(payload);
    // Automatically log in after registration
    await login(payload.username, payload.password);
    return data;
  }

  function logout() {
    localStorage.removeItem("connectme_token");
    setToken(null);
    setUser(null);
  }

  async function refreshUser() {
    if (token) {
      try {
        const profile = await getMyProfile();
        setUser(profile);
      } catch (err) {
        console.error("Failed to refresh user profile:", err);
      }
    }
  }

  return (
    <AuthContext.Provider value={{ token, user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
