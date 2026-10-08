import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { toggleLike, getComments, addComment, deletePost } from "../api";
import { Heart, MessageCircle, Trash2, Send, Clock, User, Shield } from "lucide-react";

export default function PostCard({ post, onPostDeleted, onSelectUser }) {
  const { user } = useAuth();
  const [likesCount, setLikesCount] = useState(post.likes_count || 0);
  const [isLiked, setIsLiked] = useState(false);
  
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState([]);
  const [commentsCount, setCommentsCount] = useState(post.comments_count || 0);
  const [newComment, setNewComment] = useState("");
  const [loadingComments, setLoadingComments] = useState(false);
  const [submittingComment, setSubmittingComment] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // Relative media URL for same-origin production deployment
  const fullImageUrl = post.image_url;

  // Check if current authenticated user owns this post (Anti-IDOR UI Gate)
  const isAuthor = user && (user.id === post.user_id || user.user_id === post.user_id);

  async function handleToggleLike() {
    if (!user) return;
    try {
      const prevLiked = isLiked;
      setIsLiked(!prevLiked);
      setLikesCount((prev) => (prevLiked ? Math.max(0, prev - 1) : prev + 1));
      
      const res = await toggleLike(post.id);
      if (res.message === "Post liked.") {
        setIsLiked(true);
      } else {
        setIsLiked(false);
      }
    } catch (err) {
      console.error("Like toggle failed:", err);
      // Revert optimistic update
      setIsLiked(isLiked);
    }
  }

  async function handleToggleComments() {
    if (!showComments) {
      setShowComments(true);
      setLoadingComments(true);
      try {
        const data = await getComments(post.id);
        setComments(data);
      } catch (err) {
        console.error("Failed to fetch comments:", err);
      } finally {
        setLoadingComments(false);
      }
    } else {
      setShowComments(false);
    }
  }

  async function handleAddComment(e) {
    e.preventDefault();
    if (!newComment.trim() || !user) return;

    setSubmittingComment(true);
    try {
      const added = await addComment(post.id, newComment.trim());
      setComments((prev) => [...prev, added]);
      setCommentsCount((prev) => prev + 1);
      setNewComment("");
    } catch (err) {
      console.error("Comment submission failed:", err);
      alert(err.message || "Failed to submit comment.");
    } finally {
      setSubmittingComment(false);
    }
  }

  async function handleDeletePost() {
    if (!window.confirm("Are you sure you want to delete this post? This action is permanent.")) {
      return;
    }

    setDeleting(true);
    try {
      await deletePost(post.id);
      if (onPostDeleted) {
        onPostDeleted(post.id);
      }
    } catch (err) {
      console.error("Delete failed:", err);
      alert(err.message || "Failed to delete post.");
      setDeleting(false);
    }
  }

  return (
    <article className="post-card">
      <header className="post-header">
        <div
          className="post-author"
          onClick={() => onSelectUser && onSelectUser(post.user_id)}
          role="button"
          tabIndex={0}
        >
          <div className="author-avatar">
            <User size={18} />
          </div>
          <div className="author-info">
            <span className="author-username">{post.username}</span>
            <span className="post-timestamp">
              <Clock size={12} />
              <span>{post.created_at}</span>
            </span>
          </div>
        </div>

        {/* Anti-IDOR UI Gate: Delete button is strictly rendered only for the verified owner */}
        {isAuthor && (
          <button
            className="delete-post-btn"
            onClick={handleDeletePost}
            disabled={deleting}
            title="Delete your post"
          >
            <Trash2 size={16} />
          </button>
        )}
      </header>

      <div className="post-image-container">
        <img
          src={fullImageUrl}
          alt={post.caption || "Social post media"}
          className="post-image"
          loading="lazy"
        />
      </div>

      <div className="post-content">
        <div className="post-actions">
          <button
            className={`action-btn like-btn ${isLiked ? "liked" : ""}`}
            onClick={handleToggleLike}
            title={isLiked ? "Unlike" : "Like"}
          >
            <Heart size={20} fill={isLiked ? "#e11d48" : "none"} color={isLiked ? "#e11d48" : "currentColor"} />
            <span className="action-count">{likesCount}</span>
          </button>

          <button
            className="action-btn comment-btn"
            onClick={handleToggleComments}
            title="Comments"
          >
            <MessageCircle size={20} />
            <span className="action-count">{commentsCount}</span>
          </button>
        </div>

        {post.caption && (
          <div className="post-caption">
            <span className="caption-author">{post.username}</span>
            <span className="caption-text">{post.caption}</span>
          </div>
        )}

        {/* Comments Section */}
        {showComments && (
          <div className="comments-section">
            <div className="comments-divider" />
            
            {loadingComments ? (
              <p className="comments-loading">Loading comments...</p>
            ) : comments.length === 0 ? (
              <p className="no-comments">No comments yet. Start the conversation.</p>
            ) : (
              <ul className="comments-list">
                {comments.map((c) => (
                  <li key={c.id} className="comment-item">
                    <span className="comment-user">{c.username}</span>
                    <span className="comment-body">{c.comment_text}</span>
                  </li>
                ))}
              </ul>
            )}

            {user && (
              <form onSubmit={handleAddComment} className="comment-form">
                <input
                  type="text"
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Add a comment..."
                  className="comment-input"
                  disabled={submittingComment}
                />
                <button
                  type="submit"
                  className="comment-submit-btn"
                  disabled={!newComment.trim() || submittingComment}
                >
                  <Send size={16} />
                </button>
              </form>
            )}
          </div>
        )}
      </div>
    </article>
  );
}
