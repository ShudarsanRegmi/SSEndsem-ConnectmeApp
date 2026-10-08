import React, { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import FeedView from "./components/FeedView";
import ProfileView from "./components/ProfileView";
import AuthModal from "./components/AuthModal";
import UploadModal from "./components/UploadModal";
import "./App.css";

function MainContent() {
  const { user, loading } = useAuth();
  const [currentTab, setCurrentTab] = useState("feed");
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);

  if (loading) {
    return (
      <div className="app-loading-screen">
        <div className="loading-spinner"></div>
        <p>Initializing ConnectMe application...</p>
      </div>
    );
  }

  function handleSelectUser(userId) {
    setSelectedUserId(userId);
    setCurrentTab("profile");
  }

  function handleOpenMyProfile() {
    setSelectedUserId(null); // null represents authenticated user's own profile
    setCurrentTab("profile");
  }

  function handlePostCreated() {
    setCurrentTab("feed");
    // Trigger feed refresh by remounting or state update
  }

  return (
    <div className="app-layout">
      <Navbar
        currentTab={currentTab}
        onSelectTab={(tab) => {
          setSelectedUserId(null);
          setCurrentTab(tab);
        }}
        onOpenUpload={() => {
          if (!user) {
            setShowAuthModal(true);
          } else {
            setShowUploadModal(true);
          }
        }}
        onOpenAuth={() => setShowAuthModal(true)}
        onOpenMyProfile={handleOpenMyProfile}
      />

      <main className="main-viewport">
        {currentTab === "feed" && (
          <FeedView
            onSelectUser={handleSelectUser}
            onOpenUpload={() => {
              if (!user) {
                setShowAuthModal(true);
              } else {
                setShowUploadModal(true);
              }
            }}
          />
        )}

        {currentTab === "profile" && (
          <ProfileView
            targetUserId={selectedUserId}
            onBackToFeed={() => setCurrentTab("feed")}
          />
        )}
      </main>

      {/* Modals */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />

      <UploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onPostCreated={handlePostCreated}
      />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainContent />
    </AuthProvider>
  );
}
