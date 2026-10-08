import React from "react";
import { useAuth } from "../context/AuthContext";
import { Compass, PlusSquare, User, LogOut, LogIn, ShieldCheck } from "lucide-react";

export default function Navbar({ onOpenUpload, onOpenAuth, onSelectTab, currentTab, onOpenMyProfile }) {
  const { user, logout } = useAuth();

  return (
    <header className="navbar">
      <div className="navbar-container">
        <div className="brand" onClick={() => onSelectTab("feed")}>
          <div className="brand-logo">
            <ShieldCheck size={28} className="brand-icon" />
          </div>
          <div className="brand-text">
            <span className="brand-name">ConnectMe</span>
            <span className="brand-subtitle">Secure Social Network</span>
          </div>
        </div>

        <nav className="nav-actions">
          {user ? (
            <>
              <button
                className={`nav-btn ${currentTab === "feed" ? "active" : ""}`}
                onClick={() => onSelectTab("feed")}
                title="Feed"
              >
                <Compass size={20} />
                <span>Feed</span>
              </button>

              <button
                className="nav-btn primary-action"
                onClick={onOpenUpload}
                title="Upload Photo"
              >
                <PlusSquare size={20} />
                <span>New Post</span>
              </button>

              <button
                className={`nav-btn ${currentTab === "profile" ? "active" : ""}`}
                onClick={onOpenMyProfile}
                title="Profile"
              >
                <User size={20} />
                <span>{user.username}</span>
              </button>

              <button
                className="nav-btn logout-btn"
                onClick={logout}
                title="Log Out"
              >
                <LogOut size={20} />
                <span>Log Out</span>
              </button>
            </>
          ) : (
            <button
              className="nav-btn primary-action"
              onClick={onOpenAuth}
            >
              <LogIn size={20} />
              <span>Log In / Register</span>
            </button>
          )}
        </nav>
      </div>
    </header>
  );
}
