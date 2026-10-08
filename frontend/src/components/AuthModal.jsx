import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { X, Lock, User, Mail, ShieldAlert, CheckCircle2 } from "lucide-react";

export default function AuthModal({ isOpen, onClose }) {
  const { login, register } = useAuth();
  const [isLoginTab, setIsLoginTab] = useState(true);
  
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [bio, setBio] = useState("");
  
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isLoginTab) {
        if (!username.trim() || !password) {
          throw new Error("Username and password are required.");
        }
        await login(username.trim(), password);
        onClose();
      } else {
        if (!username.trim() || !email.trim() || !password) {
          throw new Error("Username, email, and password are required.");
        }
        if (password.length < 8) {
          throw new Error("Password must be at least 8 characters in length.");
        }
        await register({
          username: username.trim(),
          email: email.trim(),
          password,
          full_name: fullName.trim(),
          bio: bio.trim(),
        });
        onClose();
      }
    } catch (err) {
      setError(err.message || "An error occurred during authentication.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-backdrop">
      <div className="modal-container auth-modal">
        <div className="modal-header">
          <div className="modal-title-group">
            <h3>{isLoginTab ? "Sign In to ConnectMe" : "Create ConnectMe Account"}</h3>
            <p className="modal-subtitle">
              {isLoginTab
                ? "Enter your credentials to access your secure profile and social feed."
                : "Join the security-hardened community with end-to-end access controls."}
            </p>
          </div>
          <button className="close-btn" onClick={onClose} aria-label="Close modal">
            <X size={20} />
          </button>
        </div>

        <div className="tab-switcher">
          <button
            className={`tab-btn ${isLoginTab ? "active" : ""}`}
            onClick={() => {
              setIsLoginTab(true);
              setError(null);
            }}
          >
            Log In
          </button>
          <button
            className={`tab-btn ${!isLoginTab ? "active" : ""}`}
            onClick={() => {
              setIsLoginTab(false);
              setError(null);
            }}
          >
            Register
          </button>
        </div>

        {error && (
          <div className="alert-box error">
            <ShieldAlert size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="auth-username">Username</label>
            <div className="input-wrapper">
              <User size={18} className="input-icon" />
              <input
                id="auth-username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. secure_user"
                required
                autoComplete="username"
              />
            </div>
          </div>

          {!isLoginTab && (
            <>
              <div className="form-group">
                <label htmlFor="auth-email">Email Address</label>
                <div className="input-wrapper">
                  <Mail size={18} className="input-icon" />
                  <input
                    id="auth-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="user@connectme.io"
                    required
                    autoComplete="email"
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="auth-fullname">Full Name (Optional)</label>
                <input
                  id="auth-fullname"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Jane Doe"
                  className="standard-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="auth-bio">Bio (Optional)</label>
                <textarea
                  id="auth-bio"
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="Write a brief profile summary..."
                  className="standard-textarea"
                  rows={2}
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label htmlFor="auth-password">Password</label>
            <div className="input-wrapper">
              <Lock size={18} className="input-icon" />
              <input
                id="auth-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={isLoginTab ? "••••••••" : "Minimum 8 characters"}
                required
                autoComplete={isLoginTab ? "current-password" : "new-password"}
              />
            </div>
          </div>

          <button
            type="submit"
            className="submit-btn"
            disabled={loading}
          >
            {loading ? "Processing..." : isLoginTab ? "Log In" : "Create Account"}
          </button>
        </form>
      </div>
    </div>
  );
}
