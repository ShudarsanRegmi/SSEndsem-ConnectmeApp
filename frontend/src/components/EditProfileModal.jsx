import React, { useState } from "react";
import { updateMyProfile } from "../api";
import { useAuth } from "../context/AuthContext";
import { X, Lock, Unlock, AlertCircle } from "lucide-react";

export default function EditProfileModal({ isOpen, onClose, currentProfile, onProfileUpdated }) {
  const { refreshUser } = useAuth();
  const [fullName, setFullName] = useState(currentProfile?.full_name || "");
  const [bio, setBio] = useState(currentProfile?.bio || "");
  const [isPrivate, setIsPrivate] = useState(currentProfile?.is_private || false);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  if (!isOpen) return null;

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSaving(true);

    try {
      await updateMyProfile({
        full_name: fullName.trim(),
        bio: bio.trim(),
        is_private: isPrivate,
      });
      await refreshUser();
      if (onProfileUpdated) {
        onProfileUpdated();
      }
      onClose();
    } catch (err) {
      setError(err.message || "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="modal-backdrop">
      <div className="modal-container edit-profile-modal">
        <div className="modal-header">
          <div className="modal-title-group">
            <h3>Edit Profile & Privacy</h3>
            <p className="modal-subtitle">Customize your identity and manage account exposure controls.</p>
          </div>
          <button className="close-btn" onClick={onClose} aria-label="Close modal">
            <X size={20} />
          </button>
        </div>

        {error && (
          <div className="alert-box error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="edit-profile-form">
          <div className="form-group">
            <label htmlFor="edit-fullname">Full Name</label>
            <input
              id="edit-fullname"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Your full name"
              className="standard-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="edit-bio">Bio (Anti-XSS Sanitized)</label>
            <textarea
              id="edit-bio"
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Write a bio..."
              className="standard-textarea"
              rows={3}
            />
          </div>

          <div className="privacy-toggle-group">
            <div className="privacy-info">
              <div className="privacy-header">
                {isPrivate ? <Lock size={18} className="lock-icon" /> : <Unlock size={18} />}
                <span className="privacy-title">Private Account</span>
              </div>
              <p className="privacy-desc">
                When enabled, only approved followers can view your media posts and profile details.
              </p>
            </div>
            <label className="switch">
              <input
                type="checkbox"
                checked={isPrivate}
                onChange={(e) => setIsPrivate(e.target.checked)}
              />
              <span className="slider round"></span>
            </label>
          </div>

          <button
            type="submit"
            className="submit-btn"
            disabled={saving}
          >
            {saving ? "Saving Changes..." : "Save Profile"}
          </button>
        </form>
      </div>
    </div>
  );
}
