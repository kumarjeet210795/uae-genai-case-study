export default function Sidebar({user, onLogout}) {
  return (
    <aside className="sidebar">
      <div className="brand">GovAI</div>
      <div className="badge">Enterprise AI Assistant</div>

      <div className="user-card">
        <div className="avatar">{user?.name?.slice(0,1) || "U"}</div>
        <div>
          <strong>{user?.name}</strong>
          <span>{user?.department}</span>
        </div>
      </div>

      <div className="security-panel">
        <div>✓ Identity verified</div>
        <div>✓ ACL-aware retrieval</div>
        <div>✓ MCP tool policy</div>
        <div>✓ Human approval</div>
        <div>✓ Audit trail</div>
      </div>

      <button className="logout" onClick={onLogout}>Sign out</button>
    </aside>
  );
}

