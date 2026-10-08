import React, { useState, useRef } from "react";
import { createPost } from "../api";
import { X, UploadCloud, Image as ImageIcon, AlertCircle } from "lucide-react";

export default function UploadModal({ isOpen, onClose, onPostCreated }) {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [caption, setCaption] = useState("");
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  function validateAndSelectFile(selectedFile) {
    setError(null);
    if (!selectedFile) return;

    // Allowed MIME types
    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
    if (!allowedTypes.includes(selectedFile.type)) {
      setError("Invalid file format. Only authentic JPEG, PNG, or WebP images are allowed.");
      return;
    }

    // Max 5MB
    const maxBytes = 5 * 1024 * 1024;
    if (selectedFile.size > maxBytes) {
      setError("File exceeds 5MB ceiling. Please select an image under 5MB.");
      return;
    }

    setFile(selectedFile);
    const objectUrl = URL.createObjectURL(selectedFile);
    setPreviewUrl(objectUrl);
  }

  function handleFileChange(e) {
    const selected = e.target.files[0];
    validateAndSelectFile(selected);
  }

  function handleDragOver(e) {
    e.preventDefault();
  }

  function handleDrop(e) {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSelectFile(e.dataTransfer.files[0]);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) {
      setError("Please select an image file to upload.");
      return;
    }

    setError(null);
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("image", file);
      formData.append("caption", caption.trim());

      const newPost = await createPost(formData);
      if (onPostCreated) {
        onPostCreated(newPost);
      }
      handleClose();
    } catch (err) {
      setError(err.message || "Failed to upload post.");
    } finally {
      setUploading(false);
    }
  }

  function handleClose() {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setFile(null);
    setPreviewUrl(null);
    setCaption("");
    setError(null);
    onClose();
  }

  return (
    <div className="modal-backdrop">
      <div className="modal-container upload-modal">
        <div className="modal-header">
          <div className="modal-title-group">
            <h3>Create New Post</h3>
            <p className="modal-subtitle">Share an authentic photo with magic-byte validation and anti-EXIF sanitization.</p>
          </div>
          <button className="close-btn" onClick={handleClose} aria-label="Close modal">
            <X size={20} />
          </button>
        </div>

        {error && (
          <div className="alert-box error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="upload-form">
          <div
            className={`dropzone ${previewUrl ? "has-preview" : ""}`}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={() => !previewUrl && fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/jpeg,image/png,image/webp"
              style={{ display: "none" }}
            />

            {previewUrl ? (
              <div className="preview-container">
                <img src={previewUrl} alt="Upload preview" className="preview-image" />
                <button
                  type="button"
                  className="change-image-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    fileInputRef.current?.click();
                  }}
                >
                  Change Photo
                </button>
              </div>
            ) : (
              <div className="dropzone-prompt">
                <UploadCloud size={48} className="dropzone-icon" />
                <p className="prompt-title">Drag & drop your photo here, or browse</p>
                <p className="prompt-specs">Supported formats: JPEG, PNG, WebP (Max 5MB)</p>
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="post-caption">Caption</label>
            <textarea
              id="post-caption"
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="Write an engaging caption..."
              className="standard-textarea"
              rows={3}
            />
          </div>

          <button
            type="submit"
            className="submit-btn"
            disabled={!file || uploading}
          >
            {uploading ? "Validating & Uploading..." : "Publish Post"}
          </button>
        </form>
      </div>
    </div>
  );
}
