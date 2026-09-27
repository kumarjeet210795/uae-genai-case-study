export default function Message({item, onApproval}) {
  const meta = item.meta;
  return <div className={`message ${item.role}`}><div className="bubble">
    <div className="message-role">{item.role === "user" ? "You" : "GovAI OSS"}</div>
    <div className="message-text">{item.text}</div>
    {meta && <div className="meta-grid"><div><b>Grounded:</b> {meta.grounded ? "Yes" : "No"}</div><div><b>Trace:</b> {meta.trace_id}</div></div>}
    {meta?.citations?.length>0 && <div className="citations"><b>Sources</b>{meta.citations.map((c,i)=><div className="citation" key={i}><span>{c.title}</span><small>{c.chunk_id} · {c.department} · {c.source}</small></div>)}</div>}
    {meta?.guardrails?.length>0 && <div className="guardrails"><b>Security checks</b>{meta.guardrails.map((g,i)=><div key={i} className={g.allowed?"ok":"blocked"}>{g.allowed?"✓":"⚠"} {g.reason}</div>)}</div>}
    {meta?.approval && <div className="approval"><b>Human approval required</b><p>Action: {meta.approval.tool.tool}</p><p>Status: <strong>{meta.approval.status}</strong></p>{meta.approval.status === "PENDING" && <div className="approval-actions"><button onClick={()=>onApproval(meta.approval,"approve")}>Approve & execute</button><button onClick={()=>onApproval(meta.approval,"reject")}>Reject</button></div>}</div>}
    {meta?.tool_calls?.length>0 && <div className="toolcalls"><b>MCP tool calls</b>{meta.tool_calls.map((t,i)=><div key={i}>{t.server} / {t.tool}</div>)}</div>}
  </div></div>;
}
