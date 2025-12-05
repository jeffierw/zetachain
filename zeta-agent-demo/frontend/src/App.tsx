import { useState } from 'react'
import './App.css'

interface AgentResponse {
  type: string;
  recipient: string;
  amount: number;
  token: string;
  error?: string;
  raw?: string;
}

function App() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [agentResponse, setAgentResponse] = useState<AgentResponse | null>(null)
  const [txHash, setTxHash] = useState<string | null>(null)
  const [explorerUrl, setExplorerUrl] = useState<string | null>(null)
  const [logs, setLogs] = useState<string[]>([])

  const addLog = (msg: string) => setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`])

  const handleChat = async () => {
    if (!prompt) return;
    setLoading(true);
    setAgentResponse(null);
    setTxHash(null);
    setExplorerUrl(null);
    addLog(`Sending prompt to Agent: "${prompt}"`);

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });

      if (!res.ok) throw new Error('Failed to talk to agent');

      const data = await res.json();
      addLog('Agent parsed user intent.');
      setAgentResponse(data);
    } catch (err) {
      addLog(`Error: ${err}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleExecute = async () => {
    if (!agentResponse) return;
    setLoading(true);
    addLog('Executing transaction on ZetaChain...');

    try {
      const res = await fetch('http://localhost:8000/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(agentResponse)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Execution failed');
      }

      const data = await res.json();
      addLog(`Transaction sent! Hash: ${data.tx_hash}`);
      setTxHash(data.tx_hash);
      setExplorerUrl(data.explorer_url);
    } catch (err) {
      addLog(`Execution Error: ${err}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1>Day 12: Natural Language - ZetaChain</h1>

      <div className="card">
        <h3>1. Ask the Agent</h3>
        <input
          type="text"
          placeholder="e.g. Send 0.001 ZETA to 0x123..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={loading}
        />
        <button onClick={handleChat} disabled={loading || !prompt}>
          {loading ? 'Thinking...' : 'Analyze Intent'}
        </button>
      </div>

      {agentResponse && (
        <div className="card">
          <h3>2. Confirm Plan</h3>
          <p>The agent identified the following intent:</p>
          <pre>{JSON.stringify(agentResponse, null, 2)}</pre>

          {agentResponse.error ? (
            <p style={{ color: 'red' }}>Agent parse error. Please try again.</p>
          ) : (
            <button onClick={handleExecute} disabled={loading} style={{ marginTop: '10px', backgroundColor: '#646cff' }}>
              {loading ? 'Sending...' : 'Confirm & Execute Transaction'}
            </button>
          )}
        </div>
      )}

      {txHash && (
        <div className="card">
          <h3>3. Success!</h3>
          <p>Transaction Hash: {txHash}</p>
          {explorerUrl && (
            <a href={explorerUrl} target="_blank" rel="noreferrer" className="success-link">
              View on ZetaScan
            </a>
          )}
        </div>
      )}

      <div className="card" style={{ marginTop: '40px', fontSize: '0.8em', color: '#888' }}>
        <h4>Logs</h4>
        {logs.map((log, i) => (
          <div key={i}>{log}</div>
        ))}
      </div>
    </>
  )
}

export default App
