import { useState, useEffect } from 'react';
import { Play, Pause, Settings, Zap } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function WorkflowCard({ wf, onToggle }) {
  const active = wf.status === 'active';
  return (
    <div className="border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow bg-white">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`w-2.5 h-2.5 rounded-full ${active ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`} />
          <div>
            <h3 className="font-semibold text-gray-900 text-sm">{wf.name}</h3>
            <p className="text-xs text-gray-500 mt-0.5">{wf.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button className="p-1.5 hover:bg-gray-100 rounded-lg">
            <Settings size={15} className="text-gray-400" />
          </button>
          <button
            onClick={() => onToggle(wf.id)}
            className={`p-1.5 rounded-lg ${active ? 'hover:bg-orange-50 text-orange-500' : 'hover:bg-green-50 text-green-500'}`}
          >
            {active ? <Pause size={15} /> : <Play size={15} />}
          </button>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3 pt-3 border-t border-gray-100 text-xs">
        <div>
          <span className="text-gray-400 block">Last Run</span>
          <span className="font-medium text-gray-700">{wf.lastRun}</span>
        </div>
        <div>
          <span className="text-gray-400 block">Success</span>
          <span className="font-medium text-green-600">{wf.successRate}%</span>
        </div>
        <div>
          <span className="text-gray-400 block">Avg Time</span>
          <span className="font-medium text-gray-700">{wf.avgTime}ms</span>
        </div>
      </div>
    </div>
  );
}

export default function WorkflowMonitor() {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchWorkflows = async () => {
    try {
      const res = await fetch(`${API_URL}/api/v1/workflows`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setWorkflows(data.workflows || []);
      setError(null);
    } catch {
      setError('Cannot connect to backend. Make sure it is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows();
    const t = setInterval(fetchWorkflows, 10000);
    return () => clearInterval(t);
  }, []);

  const toggle = (id) =>
    setWorkflows(prev =>
      prev.map(w => w.id === id ? { ...w, status: w.status === 'active' ? 'paused' : 'active' } : w)
    );

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <div className="flex justify-between items-center mb-5">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Active Workflows</h2>
          <p className="text-sm text-gray-400 mt-0.5">
            {workflows.filter(w => w.status === 'active').length} of {workflows.length} running
          </p>
        </div>
        <span className="flex items-center gap-1.5 bg-green-50 text-green-700 text-xs font-medium px-3 py-1 rounded-full">
          <Zap size={11} /> Live
        </span>
      </div>

      {loading && (
        <div className="space-y-3">
          {[1,2,3,4].map(i => <div key={i} className="h-24 bg-gray-100 rounded-xl animate-pulse" />)}
        </div>
      )}
      {error && (
        <div className="text-center py-8">
          <p className="text-sm text-red-500">{error}</p>
          <button onClick={fetchWorkflows} className="mt-2 text-xs text-blue-600 hover:underline">Retry</button>
        </div>
      )}
      {!loading && !error && (
        <div className="space-y-3">
          {workflows.map(wf => <WorkflowCard key={wf.id} wf={wf} onToggle={toggle} />)}
        </div>
      )}
    </div>
  );
}
