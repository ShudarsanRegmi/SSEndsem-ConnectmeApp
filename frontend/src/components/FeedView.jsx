import React, { useState, useEffect } from "react";
import { getFeed } from "../api";
import PostCard from "./PostCard";
import { RefreshCw, CameraOff, AlertCircle } from "lucide-react";

export default function FeedView({ onSelectUser, onOpenUpload }) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function loadFeed() {
    setLoading(true);
    setError(null);
    try {
      const data = await getFeed();
      setPosts(data);
    } catch (err) {
      console.error("Feed loading error:", err);
      setError(err.message || "Failed to load feed.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadFeed();
  }, []);

  function handlePostDeleted(deletedId) {
    setPosts((prev) => prev.filter((p) => p.id !== deletedId));
  }

  return (
    <div className="feed-container">
      <div className="feed-header">
        <h2 className="feed-title">Latest Updates</h2>
        <button
          className="refresh-btn"
          onClick={loadFeed}
          disabled={loading}
          title="Refresh feed"
        >
          <RefreshCw size={18} className={loading ? "spin" : ""} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="alert-box error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="feed-loading">
          <RefreshCw size={28} className="spin" />
          <p>Loading your secure social feed...</p>
        </div>
      ) : posts.length === 0 ? (
        <div className="empty-feed">
          <CameraOff size={48} className="empty-icon" />
          <h3>No Posts in Feed</h3>
          <p>
            Your feed shows content from users you follow and public accounts.
            Follow users or share your first post!
          </p>
          <button className="primary-action-btn" onClick={onOpenUpload}>
            Create First Post
          </button>
        </div>
      ) : (
        <div className="posts-stream">
          {posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              onPostDeleted={handlePostDeleted}
              onSelectUser={onSelectUser}
            />
          ))}
        </div>
      )}
    </div>
  );
}
