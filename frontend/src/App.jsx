import React, { useState, useEffect, useRef, useCallback } from 'react'

const API = ''  // proxied via vite → localhost:8000

// ─────────────────────────────────────────
// API helpers
// ─────────────────────────────────────────
async function submitAnalysis(text, repo) {
  const r = await fetch(`${API}/api/v1/analysis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, repo })
  })
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return r.json()
}

async function fetchAnalysis(id) {
  const r = await fetch(`${API}/api/v1/analysis/${id}`)
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return r.json()
}

async function fetchStatus(id) {
  const r = await fetch(`${API}/api/v1/analysis/${id}/status`)
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return r.json()
}

// ─────────────────────────────────────────
// Nav
// ─────────────────────────────────────────
function Nav({ onHome }) {
  return (
    <nav className="nav">
      <div className="nav-logo" onClick={onHome}>
        💥 <span>Change</span>Blast
      </div>
      <span className="nav-tagline">See the blast radius before you change the code</span>
    </nav>
  )
}

// ─────────────────────────────────────────
// HOME
// ─────────────────────────────────────────
function HomeScreen({ onStart }) {
  return (
    <div className="home">
      <div className="home-hero-icon">💥</div>
      <h1 className="home-title">
        <span className="blast">Change</span>Blast
      </h1>
      <p className="home-tagline">
        See the blast radius before you change the code. Analyze any proposed change across your entire codebase instantly.
      </p>
      <button className="btn btn-primary btn-lg" onClick={onStart}>
        🔍 Analyze a Change
      </button>
      <div className="home-demo-hint">Try the primary demo:</div>
      <div
        className="home-demo-pill"
        onClick={() => onStart('Replace User.id from Integer to UUID')}
      >
        "Replace User.id from Integer to UUID" →
      </div>
      <div className="home-features">
        {[
          ['🗂', 'Blast Radius Graph'],
          ['⚠️', 'Risk Scoring'],
          ['🔎', 'Impact Explorer'],
          ['📋', 'Change Plan'],
          ['🧪', 'Test Coverage'],
          ['🗄', 'DB Migrations'],
        ].map(([icon, label]) => (
          <div className="home-feature" key={label}>
            <div className="home-feature-icon">{icon}</div>
            <div className="home-feature-label">{label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────
// ANALYZE FORM
// ─────────────────────────────────────────
const QUICK_EXAMPLES = [
  'Replace User.id from Integer to UUID',
  'Rename email field to email_address in User model',
  'Remove deprecated /v1/users endpoint',
  'Add rate limiting to auth routes',
  'Change payment status enum values',
]

function AnalyzeScreen({ prefill, onSubmit, onBack }) {
  const [text, setText] = useState(prefill || '')
  const [repo, setRepo] = useState('sample-ecommerce')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!text.trim()) return
    setLoading(true)
    setError(null)
    try {
      const res = await submitAnalysis(text.trim(), repo)
      onSubmit(res.analysis_id, text.trim())
    } catch (err) {
      setError('Failed to submit: ' + err.message)
      setLoading(false)
    }
  }

  return (
    <div className="analyze-screen">
      <div className="analyze-form">
        <button className="back-btn" onClick={onBack}>← Back</button>
        <h2 className="analyze-title">Analyze a Change</h2>
        <p className="analyze-sub">Describe your proposed change and ChangeBlast will find everything it affects.</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Repository</label>
            <input
              className="form-input"
              value={repo}
              onChange={e => setRepo(e.target.value)}
              placeholder="sample-ecommerce"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Proposed Change</label>
            <textarea
              className="form-input form-textarea"
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder="Describe what you want to change…"
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label">Quick Examples</label>
            <div className="form-row">
              {QUICK_EXAMPLES.map(ex => (
                <button
                  type="button"
                  key={ex}
                  className="quick-pill"
                  onClick={() => setText(ex)}
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>

          {error && <div style={{ color: 'var(--red)', marginBottom: 12, fontSize: 13 }}>{error}</div>}

          <button className="btn btn-primary" type="submit" disabled={!text.trim() || loading}>
            {loading ? '⏳ Submitting…' : '🔍 Analyze Blast Radius'}
          </button>
        </form>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────
// PROGRESS
// ─────────────────────────────────────────
const PROGRESS_STEPS = [
  { id: 'queued',    icon: '📋', label: 'Change queued' },
  { id: 'analyzing', icon: '🔍', label: 'Scanning repository files' },
  { id: 'risk',      icon: '⚠️', label: 'Calculating risk score' },
  { id: 'graph',     icon: '🕸', label: 'Building blast radius graph' },
  { id: 'plan',      icon: '📋', label: 'Generating change plan' },
  { id: 'completed', icon: '✅', label: 'Analysis complete' },
]

function ProgressScreen({ analysisId, changeText, onComplete }) {
  const [status, setStatus] = useState('queued')
  const [fakeStep, setFakeStep] = useState(0)
  const intervalRef = useRef(null)

  useEffect(() => {
    // Advance fake steps for UX
    const stepInterval = setInterval(() => {
      setFakeStep(s => Math.min(s + 1, PROGRESS_STEPS.length - 2))
    }, 600)

    // Poll real status
    const pollInterval = setInterval(async () => {
      try {
        const s = await fetchStatus(analysisId)
        setStatus(s.status)
        if (s.status === 'completed' || s.status === 'failed') {
          clearInterval(pollInterval)
          clearInterval(stepInterval)
          setFakeStep(PROGRESS_STEPS.length - 1)
          if (s.status === 'completed') {
            setTimeout(async () => {
              const data = await fetchAnalysis(analysisId)
              onComplete(data)
            }, 600)
          }
        }
      } catch (e) {
        // keep polling
      }
    }, 800)

    return () => {
      clearInterval(pollInterval)
      clearInterval(stepInterval)
    }
  }, [analysisId])

  const activeIdx = fakeStep

  return (
    <div className="progress-screen">
      <div className="progress-box">
        <div className="progress-icon">💥</div>
        <h2 className="progress-title">Analyzing blast radius…</h2>
        <p className="progress-sub" style={{ marginBottom: 8 }}>
          <span style={{ fontFamily: 'monospace', color: 'var(--accent)', fontSize: 12 }}>
            {changeText}
          </span>
        </p>
        <p className="progress-sub">Scanning repository for all affected files, APIs, and tests.</p>

        <div className="progress-steps">
          {PROGRESS_STEPS.map((step, i) => {
            const isDone = i < activeIdx
            const isActive = i === activeIdx
            return (
              <div
                key={step.id}
                className={`progress-step ${isDone ? 'step-done' : ''} ${isActive ? 'step-active' : ''}`}
              >
                <span className="step-icon">
                  {isDone ? '✅' : isActive ? <span className="spin">⚙</span> : '⏺'}
                </span>
                <span className="step-label">{step.label}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────
// BLAST RADIUS GRAPH  (pure SVG / Canvas)
// ─────────────────────────────────────────
const CAT_COLORS = {
  core:     '#f97316',
  database: '#ef4444',
  api:      '#818cf8',
  code:     '#22c55e',
  frontend: '#f472b6',
  test:     '#fbbf24',
  service:  '#38bdf8',
  file:     '#94a3b8',
}

const CAT_ICONS = {
  core:     '💥',
  database: '🗄',
  api:      '🌐',
  code:     '📄',
  frontend: '🎨',
  test:     '🧪',
  service:  '⚙',
  file:     '📄',
}

function BlastGraph({ nodes, edges }) {
  const svgRef = useRef(null)
  const [positions, setPositions] = useState({})
  const [tooltip, setTooltip] = useState(null)
  const [hovered, setHovered] = useState(null)

  const W = 720, H = 460

  useEffect(() => {
    if (!nodes.length) return
    const pos = {}
    const core = nodes.find(n => n.category === 'core')
    const others = nodes.filter(n => n.category !== 'core')

    if (core) pos[core.id] = { x: W / 2, y: H / 2 }

    // Group by category for radial layout
    const groups = {}
    others.forEach(n => {
      if (!groups[n.category]) groups[n.category] = []
      groups[n.category].push(n)
    })

    const catList = Object.keys(groups)
    catList.forEach((cat, ci) => {
      const baseAngle = (ci / catList.length) * 2 * Math.PI
      const items = groups[cat]
      const radius = 160 + (items.length > 3 ? 40 : 0)
      items.forEach((n, i) => {
        const spread = 0.35
        const angle = baseAngle + (i - (items.length - 1) / 2) * spread / Math.max(items.length, 1)
        pos[n.id] = {
          x: W / 2 + radius * Math.cos(angle),
          y: H / 2 + radius * Math.sin(angle),
        }
      })
    })

    setPositions(pos)
  }, [nodes])

  if (!nodes.length) return <div className="empty-state">No graph data</div>

  // Only show up to 40 nodes to keep it readable
  const visibleNodes = nodes.slice(0, 40)
  const visibleIds = new Set(visibleNodes.map(n => n.id))
  const visibleEdges = edges.filter(e => visibleIds.has(e.source) && visibleIds.has(e.target))

  return (
    <div>
      <div className="graph-canvas" style={{ height: H }}>
        <svg
          ref={svgRef}
          width="100%"
          height={H}
          viewBox={`0 0 ${W} ${H}`}
          style={{ display: 'block' }}
        >
          <defs>
            <marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
              <path d="M0,0 L6,3 L0,6 Z" fill="rgba(100,116,139,0.5)" />
            </marker>
          </defs>

          {/* Edges */}
          {visibleEdges.map((e, i) => {
            const s = positions[e.source], t = positions[e.target]
            if (!s || !t) return null
            const isHovered = hovered === e.source || hovered === e.target
            return (
              <line
                key={i}
                x1={s.x} y1={s.y} x2={t.x} y2={t.y}
                stroke={isHovered ? 'rgba(249,115,22,0.5)' : 'rgba(100,116,139,0.2)'}
                strokeWidth={isHovered ? 1.5 : 1}
                markerEnd="url(#arrow)"
              />
            )
          })}

          {/* Nodes */}
          {visibleNodes.map(n => {
            const p = positions[n.id]
            if (!p) return null
            const color = CAT_COLORS[n.category] || '#94a3b8'
            const isCore = n.category === 'core'
            const r = isCore ? 22 : 14
            const isHov = hovered === n.id
            return (
              <g
                key={n.id}
                transform={`translate(${p.x},${p.y})`}
                onMouseEnter={() => { setHovered(n.id); setTooltip({ node: n, x: p.x, y: p.y }) }}
                onMouseLeave={() => { setHovered(null); setTooltip(null) }}
                style={{ cursor: 'pointer' }}
              >
                <circle
                  r={r + (isHov ? 3 : 0)}
                  fill={color + '22'}
                  stroke={color}
                  strokeWidth={isCore ? 2.5 : 1.5}
                />
                <text
                  textAnchor="middle"
                  dy="0.35em"
                  fontSize={isCore ? 14 : 10}
                  fill={color}
                >
                  {CAT_ICONS[n.category] || '📄'}
                </text>
                {(!isCore) && (
                  <text
                    y={r + 12}
                    textAnchor="middle"
                    fontSize={9}
                    fill="var(--muted)"
                    style={{ pointerEvents: 'none' }}
                  >
                    {n.label.length > 14 ? n.label.slice(0, 13) + '…' : n.label}
                  </text>
                )}
                {isCore && (
                  <text
                    y={r + 16}
                    textAnchor="middle"
                    fontSize={11}
                    fontWeight="700"
                    fill={color}
                  >
                    {n.label}
                  </text>
                )}
              </g>
            )
          })}
        </svg>

        {/* Tooltip */}
        {tooltip && (
          <div style={{
            position: 'absolute',
            left: Math.min(tooltip.x + 16, W - 200),
            top: Math.max(tooltip.y - 40, 8),
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            padding: '8px 12px',
            fontSize: 12,
            maxWidth: 220,
            pointerEvents: 'none',
            zIndex: 10,
            boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
          }}>
            <div style={{ fontWeight: 700, color: 'var(--text)', marginBottom: 2 }}>
              {tooltip.node.label}
            </div>
            <div style={{ color: 'var(--muted)' }}>{tooltip.node.description}</div>
            {tooltip.node.file && (
              <div style={{ fontFamily: 'monospace', color: 'var(--accent2)', marginTop: 4 }}>
                {tooltip.node.file}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="graph-legend">
        {Object.entries(CAT_COLORS).map(([cat, color]) => (
          <div className="legend-item" key={cat}>
            <div className="legend-dot" style={{ background: color }} />
            {cat}
          </div>
        ))}
      </div>

      {nodes.length > 40 && (
        <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 8 }}>
          Showing 40 of {nodes.length} nodes for readability.
        </div>
      )}
    </div>
  )
}

// ─────────────────────────────────────────
// RISK PANEL
// ─────────────────────────────────────────
function RiskPanel({ risk }) {
  if (!risk || !risk.level) return null
  return (
    <div className="card risk-panel">
      <div className="card-title">Risk Assessment</div>
      <div className="risk-score-row">
        <div className={`risk-score-num ${risk.level}`}>{risk.score}</div>
        <div>
          <div className={`risk-badge risk-${risk.level}`}>{risk.level} RISK</div>
          <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>
            {risk.level === 'HIGH' ? 'Requires careful planning' : risk.level === 'MEDIUM' ? 'Review before merging' : 'Low impact change'}
          </div>
        </div>
      </div>
      <div className="risk-reasons">
        {(risk.reasons || []).map((r, i) => (
          <div className="risk-reason" key={i}>{r}</div>
        ))}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────
// IMPACT EXPLORER
// ─────────────────────────────────────────
const TAB_LABELS = {
  code:     { label: 'Code',     icon: '📄' },
  api:      { label: 'API',      icon: '🌐' },
  database: { label: 'Database', icon: '🗄' },
  frontend: { label: 'Frontend', icon: '🎨' },
  tests:    { label: 'Tests',    icon: '🧪' },
  history:  { label: 'History',  icon: '📜' },
}

function ImpactExplorer({ impact }) {
  const [activeTab, setActiveTab] = useState('code')
  const [expanded, setExpanded] = useState(null)

  const tabs = Object.keys(TAB_LABELS)
  const items = (impact[activeTab] || [])

  return (
    <div className="card">
      <div className="section-title">🔎 Impact Explorer</div>
      <div className="tabs">
        {tabs.map(t => (
          <button
            key={t}
            className={`tab-btn ${activeTab === t ? 'active' : ''}`}
            onClick={() => { setActiveTab(t); setExpanded(null) }}
          >
            {TAB_LABELS[t].icon} {TAB_LABELS[t].label}
            <span className="tab-count">{(impact[t] || []).length}</span>
          </button>
        ))}
      </div>

      <div className="impact-list">
        {items.length === 0
          ? <div className="empty-state">No {activeTab} impacts found.</div>
          : items.map((item, i) => (
            <div
              key={i}
              className={`impact-item ${expanded === i ? 'expanded' : ''}`}
              onClick={() => setExpanded(expanded === i ? null : i)}
            >
              <div className="impact-item-header">
                <span className="impact-file">{item.file}</span>
                {item.line && <span className="impact-line">L{item.line}</span>}
                {item.relationship && <span className="impact-rel">{item.relationship}</span>}
              </div>
              {expanded === i && (
                <>
                  <div className="impact-desc">{item.description}</div>
                  {item.evidence_id && (
                    <div className="impact-ev-id">🔗 {item.evidence_id}</div>
                  )}
                </>
              )}
            </div>
          ))
        }
      </div>
    </div>
  )
}

// ─────────────────────────────────────────
// CHANGE PLAN
// ─────────────────────────────────────────
function ChangePlan({ plan }) {
  return (
    <div className="card">
      <div className="section-title">📋 Recommended Change Plan</div>
      <div className="plan-list">
        {(plan || []).map(step => (
          <div className="plan-item" key={step.order}>
            <div className="plan-num">{step.order}</div>
            <div className="plan-body">
              <div className={`plan-area-badge plan-area-${step.area}`}>{step.area}</div>
              <div className="plan-title">{step.title}</div>
              <div className="plan-desc">{step.description}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────
// SUMMARY STATS
// ─────────────────────────────────────────
function SummaryStats({ summary, risk }) {
  const stats = [
    { label: 'Direct Files', value: summary.direct_files ?? 0 },
    { label: 'Indirect Files', value: summary.indirect_files ?? 0 },
    { label: 'API Contracts', value: summary.api_contracts ?? 0 },
    { label: 'DB Migrations', value: summary.database_migrations ?? 0 },
    { label: 'Tests Affected', value: summary.tests_affected ?? 0 },
  ]
  return (
    <div className="stat-grid">
      {stats.map(s => (
        <div className="stat-card" key={s.label}>
          <div className="stat-label">{s.label}</div>
          <div className="stat-value">{s.value}</div>
        </div>
      ))}
    </div>
  )
}

// ─────────────────────────────────────────
// DASHBOARD
// ─────────────────────────────────────────
function Dashboard({ data, onBack }) {
  return (
    <div className="dashboard">
      <div className="container">
        <button className="back-btn" onClick={onBack}>← New Analysis</button>

        <div className="dash-header">
          <div>
            <div className="dash-title">Blast Radius Analysis</div>
            <div className="dash-change-text">"{data.request?.text}"</div>
          </div>
          <div className={`risk-badge risk-${data.risk?.level}`} style={{ fontSize: 14, padding: '6px 16px' }}>
            {data.risk?.level} RISK · Score {data.risk?.score}
          </div>
        </div>

        {/* Summary stats */}
        <SummaryStats summary={data.summary || {}} risk={data.risk || {}} />

        <div style={{ height: 20 }} />

        <div className="dash-grid">
          <div className="dash-main">
            {/* Graph */}
            <div className="card">
              <div className="section-title">🕸 Blast Radius Graph</div>
              <div style={{ position: 'relative' }}>
                <BlastGraph nodes={data.graph?.nodes || []} edges={data.graph?.edges || []} />
              </div>
            </div>

            {/* Impact Explorer */}
            <ImpactExplorer impact={data.impact || {}} />

            {/* Change Plan */}
            <ChangePlan plan={data.change_plan || []} />
          </div>

          <div className="dash-side">
            {/* Risk */}
            <RiskPanel risk={data.risk} />

            {/* Evidence Summary */}
            <div className="card">
              <div className="card-title">Evidence ({(data.evidence || []).length} findings)</div>
              <div style={{ maxHeight: 320, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
                {(data.evidence || []).slice(0, 30).map(ev => (
                  <div key={ev.id} style={{
                    background: 'var(--surface2)', borderRadius: 6, padding: '8px 10px',
                    border: '1px solid var(--border)', fontSize: 12
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 }}>
                      <span className="evidence-badge">{ev.id}</span>
                      <span style={{ color: 'var(--muted)', fontSize: 11 }}>L{ev.line_start}</span>
                    </div>
                    <div style={{ fontFamily: 'monospace', fontSize: 11, color: 'var(--accent2)', marginBottom: 2 }}>
                      {ev.file}
                    </div>
                    <div style={{ color: 'var(--muted)', lineHeight: 1.5 }}>{ev.description}</div>
                  </div>
                ))}
                {(data.evidence || []).length > 30 && (
                  <div style={{ textAlign: 'center', color: 'var(--muted)', fontSize: 11, padding: 8 }}>
                    +{data.evidence.length - 30} more findings
                  </div>
                )}
              </div>
            </div>

            {/* Analysis ID */}
            <div className="card" style={{ fontSize: 12 }}>
              <div className="card-title">Analysis Info</div>
              <div style={{ color: 'var(--muted)', marginBottom: 4 }}>ID</div>
              <div style={{ fontFamily: 'monospace', color: 'var(--text)', marginBottom: 10 }}>{data.analysis_id}</div>
              <div style={{ color: 'var(--muted)', marginBottom: 4 }}>Status</div>
              <div style={{ color: 'var(--green)', fontWeight: 600 }}>● {data.status}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────
// ROOT APP
// ─────────────────────────────────────────
export default function App() {
  const [screen, setScreen] = useState('home')   // home | analyze | progress | dashboard
  const [prefill, setPrefill] = useState('')
  const [analysisId, setAnalysisId] = useState(null)
  const [changeText, setChangeText] = useState('')
  const [analysisData, setAnalysisData] = useState(null)

  function goHome() {
    setScreen('home')
    setAnalysisData(null)
    setAnalysisId(null)
  }

  function startAnalyze(text) {
    setPrefill(text || '')
    setScreen('analyze')
  }

  function handleSubmit(id, text) {
    setAnalysisId(id)
    setChangeText(text)
    setScreen('progress')
  }

  function handleComplete(data) {
    setAnalysisData(data)
    setScreen('dashboard')
  }

  return (
    <div className="page">
      <Nav onHome={goHome} />
      {screen === 'home' && <HomeScreen onStart={startAnalyze} />}
      {screen === 'analyze' && (
        <AnalyzeScreen
          prefill={prefill}
          onSubmit={handleSubmit}
          onBack={goHome}
        />
      )}
      {screen === 'progress' && (
        <ProgressScreen
          analysisId={analysisId}
          changeText={changeText}
          onComplete={handleComplete}
        />
      )}
      {screen === 'dashboard' && analysisData && (
        <Dashboard data={analysisData} onBack={() => startAnalyze('')} />
      )}
    </div>
  )
}
