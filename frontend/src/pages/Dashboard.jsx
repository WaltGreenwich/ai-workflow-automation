import { Activity, Zap, CheckCircle, Clock } from 'lucide-react';
import WorkflowMonitor from '../components/WorkflowMonitor';
import AnalyticsDashboard from '../components/AnalyticsDashboard';

function MetricCard({ title, value, icon, trend, bgColor }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm text-gray-500 font-medium">{title}</p>
        <div className={`p-2 rounded-lg ${bgColor}`}>{icon}</div>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-xs text-gray-400 mt-1">{trend}</p>
    </div>
  );
}

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Zap size={16} className="text-white" />
            </div>
            <h1 className="text-lg font-bold text-gray-900">AI Workflow Hub</h1>
          </div>
          <a href="http://localhost:5678" target="_blank" rel="noreferrer"
            className="text-sm text-blue-600 hover:text-blue-700 font-medium">
            Open n8n →
          </a>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricCard title="Active Workflows" value="4" trend="+2 this week"
            bgColor="bg-blue-50 text-blue-600"
            icon={<Activity size={18} />} />
          <MetricCard title="Total Executions" value="1,651" trend="+15% vs last week"
            bgColor="bg-purple-50 text-purple-600"
            icon={<Zap size={18} />} />
          <MetricCard title="Success Rate" value="97.7%" trend="+0.5% improvement"
            bgColor="bg-green-50 text-green-600"
            icon={<CheckCircle size={18} />} />
          <MetricCard title="Avg Response" value="1.8s" trend="-0.3s faster"
            bgColor="bg-orange-50 text-orange-600"
            icon={<Clock size={18} />} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <WorkflowMonitor />
          <AnalyticsDashboard />
        </div>
      </div>
    </div>
  );
}
