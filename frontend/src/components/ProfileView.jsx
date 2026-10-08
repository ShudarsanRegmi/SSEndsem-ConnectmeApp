import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { getUserProfile, getMyProfile, followUser, unfollowUser } from "../api";
import EditProfileModal from "./EditProfileModal";
import { User, Lock, Unlock, Settings, UserPlus, UserMinus, ShieldCheck, Mail, AlertCircle } from "lucide-react";

export default function ProfileView({ targetUserId, onBackToFeed }) {
  const { user: currentUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFollowing, setIsFollowing] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  const isOwnProfile = !targetUserId || (currentUser && (currentUser.id === targetUserId || currentUser.user_id === targetUserId));

  async function loadProfile() {
    setLoading(true);
    setError(null);
    try {
      if (isOwnProfile) {
        const data = await getMyProfile();
        setProfile(data);
      } else {
        const data = await getUserProfile(targetUserId);
        setProfile(data);
      }
    } catch (err) {
      console.error("Profile load failed:", err);
      setError(err.message || "Failed to load profile.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProfile();
  }, [targetUserId, currentUser]);

  async function handleToggleFollow() {
    if (!profile || isOwnProfile) return;
    setActionLoading(true);
    try {
      if (isFollowing) {
        await unfollowUser(profile.id);
        setIsFollowing(false);
        setProfile((prev) => ({
          ...prev,
          followers_count: Math.max(0, (prev.followers_count || 1) - 1),
        }));
      } else {
        await followUser(profile.id);
        setIsFollowing(true);
        setProfile((prev) => ({
          ...prev,
          followers_count: (prev.followers_count || 0) + 1,
        }));
      }
    } catch (err) {
      console.error("Follow action failed:", err);
      alert(err.message || "Action failed.");
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="profile-container loading-state">
        <p>Loading profile details...</p>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="profile-container error-state">
        <div className="alert-box error">
          <AlertCircle size={18} />
          <span>{error || "Profile not found."}</span>
        </div>
        <button className="primary-action-btn" onClick={onBackToFeed}>
          Return to Feed
        </button>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <header className="profile-card">
        <div className="profile-avatar-wrapper">
          <div className="profile-avatar-large">
            <User size={48} />
          </div>
        </div>

        <div className="profile-main-info">
          <div className="profile-title-row">
            <h2 className="profile-username">{profile.username}</h2>
            
            <div className="profile-badges">
              {profile.is_private ? (
                <span className="badge private-badge" title="Private Account">
                  <Lock size={12} />
                  <span>Private</span>
                </span>
              ) : (
                <span className="badge public-badge" title="Public Account">
                  <Unlock size={12} />
                  <span>Public</span>
                </span>
              )}
              <span className="badge role-badge">
                <ShieldCheck size={12} />
                <span>{profile.role.toUpperCase()}</span>
              </span>
            </div>

            <div className="profile-actions-wrapper">
              {isOwnProfile ? (
                <button
                  className="secondary-btn edit-profile-btn"
                  onClick={() => setShowEditModal(true)}
                >
                  <Settings size={16} />
                  <span>Edit Profile</span>
                </button>
              ) : (
                <button
                  className={`primary-btn follow-action-btn ${isFollowing ? "following" : ""}`}
                  onClick={handleToggleFollow}
                  disabled={actionLoading}
                >
                  {isFollowing ? (
                    <>
                      <UserMinus size={16} />
                      <span>Unfollow</span>
                    </>
                  ) : (
                    <>
                      <UserPlus size={16} />
                      <span>Follow</span>
                    </>
                  )}
                </button>
              )}
            </div>
          </div>

          <div className="profile-stats">
            <div className="stat-item">
              <span className="stat-number">{profile.posts_count || 0}</span>
              <span className="stat-label">Posts</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{profile.followers_count || 0}</span>
              <span className="stat-label">Followers</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{profile.following_count || 0}</span>
              <span className="stat-label">Following</span>
            </div>
          </div>

          <div className="profile-bio-section">
            {profile.full_name && (
              <h3 className="profile-full-name">{profile.full_name}</h3>
            )}
            
            {profile.bio && (
              <p className="profile-bio-text">{profile.bio}</p>
            )}

            <div className="profile-email-meta">
              <Mail size={14} className="email-icon" />
              <span className="email-value">{profile.email}</span>
              {!isOwnProfile && profile.email === "[Protected]" && (
                <span className="confidential-note">(Confidential data protected by RBAC)</span>
              )}
            </div>
          </div>
        </div>
      </header>

      {showEditModal && (
        <EditProfileModal
          isOpen={showEditModal}
          onClose={() => setShowEditModal(false)}
          currentProfile={profile}
          onProfileUpdated={loadProfile}
        />
      )}
    </div>
  );
}
