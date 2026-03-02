import { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [tab, setTab] = useState('executions');

  useEffect(() => {
    fetch(`${API_URL}/api/v1/analytics/metrics`)
      .then(r => r.json())
      .then(setMetrics)
      .catch(console.error);
  }, []);

  if (!metrics) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
        <div className="h-48 bg-gray-100 rounded-xl" />
      </div>
    );
  }

  const tabs = [
    { key: 'executions', label: 'Executions' },
    { key: 'success',    label: 'Success Rate' },
    { key: 'tokens',     label: 'Token Usage' },
  ];

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <div className="flex justify-between items-center mb-5">
        <h2 className="text-lg font-bold text-gray-900">Analytics</h2>
        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
          {tabs.map(t => (
            <button key={t.key} onClick={() => setTab(t.key)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                tab === t.key ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
              }`}>
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {tab === 'executions' && (
        <>
          <p className="text-xs text-gray-400 mb-3">Last 7 days</p>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={metrics.executionsPerDay}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={v => v.slice(5)} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#3B82F6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </>
      )}

      {tab === 'success' && (
        <>
          <p className="text-xs text-gray-400 mb-3">By workflow</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={metrics.successRateByWorkflow}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="workflow" tick={{ fontSize: 10 }} />
              <YAxis domain={[80, 100]} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Bar dataKey="successRate" fill="#10B981" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </>
      )}

      {tab === 'tokens' && (
        <>
          <p className="text-xs text-gray-400 mb-3">Token consumption</p>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={metrics.tokenUsage}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={v => v.slice(5)} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="tokens" stroke="#F59E0B" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </>
      )}

      {metrics.summary && (
        <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-2 gap-3">
          <div className="bg-blue-50 rounded-lg p-3">
            <p className="text-xs text-blue-600 font-medium">Total Executions</p>
            <p className="text-xl font-bold text-blue-700">{metrics.summary.total_executions.toLocaleString()}</p>
          </div>
          <div className="bg-green-50 rounded-lg p-3">
            <p className="text-xs text-green-600 font-medium">Avg Success Rate</p>
            <p className="text-xl font-bold text-green-700">{metrics.summary.avg_success_rate}%</p>
          </div>
        </div>
      )}
    </div>
  );
}
