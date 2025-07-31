import React, { useState, useEffect } from 'react';

const ResultsManagement = () => {
  const [validationHistory, setValidationHistory] = useState([]);
  const [selectedRuns, setSelectedRuns] = useState([]);
  const [comparisonData, setComparisonData] = useState(null);
  const [projectTimeline, setProjectTimeline] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('history');
  const [selectedProject, setSelectedProject] = useState('');

  // Fetch validation history
  const fetchValidationHistory = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/results/history?limit=50');
      const data = await response.json();
      
      if (data.status === 'success') {
        setValidationHistory(data.data);
      }
    } catch (error) {
      console.error('Error fetching validation history:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch analytics
  const fetchAnalytics = async () => {
    try {
      const response = await fetch('/api/workflow/analytics?days=30');
      const data = await response.json();
      
      if (data.status === 'success') {
        setAnalytics(data.data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  // Fetch project timeline
  const fetchProjectTimeline = async (projectName) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/results/project/${encodeURIComponent(projectName)}/timeline`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setProjectTimeline(data.data);
      }
    } catch (error) {
      console.error('Error fetching project timeline:', error);
    } finally {
      setLoading(false);
    }
  };

  // Compare validation runs
  const compareRuns = async (runId1, runId2) => {
    try {
      setLoading(true);
      const response = await fetch('/api/workflow/compare-runs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          run_id1: runId1,
          run_id2: runId2
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setComparisonData(data.data);
      }
    } catch (error) {
      console.error('Error comparing runs:', error);
    } finally {
      setLoading(false);
    }
  };

  // Trigger re-evaluation
  const triggerReEvaluation = async (originalRunId, changeReason) => {
    try {
      setLoading(true);
      const response = await fetch('/api/workflow/re-evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          original_run_id: originalRunId,
          change_reason: changeReason,
          changed_by: 'User',
          user_id: 'default'
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        alert(`Re-evaluation triggered successfully! New run ID: ${data.new_run_id}`);
        fetchValidationHistory(); // Refresh the history
      } else {
        alert(`Error: ${data.message}`);
      }
    } catch (error) {
      console.error('Error triggering re-evaluation:', error);
      alert('Error triggering re-evaluation');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchValidationHistory();
    fetchAnalytics();
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'PASS': return 'text-green-600 bg-green-100';
      case 'FAIL': return 'text-red-600 bg-red-100';
      case 'WARNING': return 'text-yellow-600 bg-yellow-100';
      case 'RUNNING': return 'text-blue-600 bg-blue-100';
      case 'ERROR': return 'text-red-600 bg-red-200';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">📊 Results Management</h1>
        <p className="text-gray-600">Manage validation results, compare runs, and track project progress</p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'history', label: '📋 Validation History', icon: '📋' },
            { id: 'comparison', label: '🔄 Run Comparison', icon: '🔄' },
            { id: 'timeline', label: '📈 Project Timeline', icon: '📈' },
            { id: 'analytics', label: '📊 Analytics', icon: '📊' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Validation History Tab */}
      {activeTab === 'history' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Validation History</h2>
            <button
              onClick={fetchValidationHistory}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              disabled={loading}
            >
              {loading ? '🔄 Refreshing...' : '🔄 Refresh'}
            </button>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Loading validation history...</p>
            </div>
          ) : (
            <div className="bg-white shadow-lg rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Run ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Project
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Timestamp
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Score
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Execution Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {validationHistory.map((run) => (
                      <tr key={run.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                          {run.id.substring(0, 8)}...
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {run.project_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatDate(run.timestamp)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(run.status)}`}>
                            {run.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`font-semibold ${getScoreColor(run.overall_score)}`}>
                            {run.overall_score ? `${run.overall_score.toFixed(1)}%` : 'N/A'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {run.execution_time ? `${run.execution_time.toFixed(2)}s` : 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          <button
                            onClick={() => {
                              const reason = prompt('Enter reason for re-evaluation:');
                              if (reason) {
                                triggerReEvaluation(run.id, reason);
                              }
                            }}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            🔄 Re-evaluate
                          </button>
                          <button
                            onClick={() => {
                              if (selectedRuns.length === 0) {
                                setSelectedRuns([run.id]);
                              } else if (selectedRuns.length === 1 && selectedRuns[0] !== run.id) {
                                compareRuns(selectedRuns[0], run.id);
                                setActiveTab('comparison');
                              }
                            }}
                            className="text-green-600 hover:text-green-900"
                          >
                            📊 Compare
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Run Comparison Tab */}
      {activeTab === 'comparison' && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold">Run Comparison</h2>
          
          {comparisonData ? (
            <div className="bg-white shadow-lg rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Comparison Results</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="border rounded-lg p-4">
                  <h4 className="font-semibold text-gray-700 mb-2">Run 1</h4>
                  <p><strong>ID:</strong> {comparisonData.basic_comparison.run1.id.substring(0, 8)}...</p>
                  <p><strong>Score:</strong> <span className={getScoreColor(comparisonData.basic_comparison.run1.overall_score)}>
                    {comparisonData.basic_comparison.run1.overall_score.toFixed(1)}%
                  </span></p>
                  <p><strong>Status:</strong> <span className={`px-2 py-1 rounded text-xs ${getStatusColor(comparisonData.basic_comparison.run1.status)}`}>
                    {comparisonData.basic_comparison.run1.status}
                  </span></p>
                  <p><strong>Date:</strong> {formatDate(comparisonData.basic_comparison.run1.timestamp)}</p>
                </div>
                
                <div className="border rounded-lg p-4">
                  <h4 className="font-semibold text-gray-700 mb-2">Run 2</h4>
                  <p><strong>ID:</strong> {comparisonData.basic_comparison.run2.id.substring(0, 8)}...</p>
                  <p><strong>Score:</strong> <span className={getScoreColor(comparisonData.basic_comparison.run2.overall_score)}>
                    {comparisonData.basic_comparison.run2.overall_score.toFixed(1)}%
                  </span></p>
                  <p><strong>Status:</strong> <span className={`px-2 py-1 rounded text-xs ${getStatusColor(comparisonData.basic_comparison.run2.status)}`}>
                    {comparisonData.basic_comparison.run2.status}
                  </span></p>
                  <p><strong>Date:</strong> {formatDate(comparisonData.basic_comparison.run2.timestamp)}</p>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-semibold text-gray-700 mb-2">Overall Comparison</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Score Difference</p>
                    <p className={`text-2xl font-bold ${comparisonData.basic_comparison.overall_score_difference > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {comparisonData.basic_comparison.overall_score_difference > 0 ? '+' : ''}
                      {comparisonData.basic_comparison.overall_score_difference.toFixed(1)}%
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Improvement</p>
                    <p className={`text-lg font-semibold ${comparisonData.basic_comparison.overall_improvement ? 'text-green-600' : 'text-red-600'}`}>
                      {comparisonData.basic_comparison.overall_improvement ? '✅ Yes' : '❌ No'}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Recommendation</p>
                    <p className="text-lg font-semibold text-blue-600">
                      {comparisonData.workflow_analysis.recommendation}
                    </p>
                  </div>
                </div>
              </div>

              {comparisonData.basic_comparison.category_comparison && (
                <div className="border-t pt-4 mt-4">
                  <h4 className="font-semibold text-gray-700 mb-2">Category Comparison</h4>
                  <div className="space-y-2">
                    {Object.entries(comparisonData.basic_comparison.category_comparison).map(([category, data]) => (
                      <div key={category} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="font-medium">{category}</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm">{data.old_score.toFixed(1)}% → {data.new_score.toFixed(1)}%</span>
                          <span className={`text-sm font-semibold ${data.improvement ? 'text-green-600' : 'text-red-600'}`}>
                            ({data.difference > 0 ? '+' : ''}{data.difference.toFixed(1)}%)
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 bg-gray-50 rounded-lg">
              <p className="text-gray-600">Select two runs from the history to compare them</p>
              <p className="text-sm text-gray-500 mt-2">Click "Compare" on any run, then click "Compare" on another run</p>
            </div>
          )}
        </div>
      )}

      {/* Project Timeline Tab */}
      {activeTab === 'timeline' && (
        <div className="space-y-6">
          <div className="flex items-center space-x-4">
            <h2 className="text-xl font-semibold">Project Timeline</h2>
            <input
              type="text"
              placeholder="Enter project name"
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg"
            />
            <button
              onClick={() => selectedProject && fetchProjectTimeline(selectedProject)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              disabled={!selectedProject || loading}
            >
              {loading ? '🔄 Loading...' : '📈 Load Timeline'}
            </button>
          </div>

          {projectTimeline ? (
            <div className="bg-white shadow-lg rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Timeline for {projectTimeline.project_name}</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600">Total Runs</p>
                  <p className="text-2xl font-bold text-blue-600">{projectTimeline.statistics.total_runs}</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-sm text-gray-600">Re-evaluations</p>
                  <p className="text-2xl font-bold text-green-600">{projectTimeline.statistics.total_re_evaluations}</p>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <p className="text-sm text-gray-600">Average Score</p>
                  <p className="text-2xl font-bold text-yellow-600">{projectTimeline.statistics.average_score.toFixed(1)}%</p>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <p className="text-sm text-gray-600">Best Score</p>
                  <p className="text-2xl font-bold text-purple-600">{projectTimeline.statistics.best_score.toFixed(1)}%</p>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold text-gray-700">Timeline Events</h4>
                {projectTimeline.timeline.map((event, index) => (
                  <div key={event.run_id} className="flex items-center space-x-4 p-4 border rounded-lg">
                    <div className="flex-shrink-0">
                      <div className={`w-3 h-3 rounded-full ${event.is_re_evaluation ? 'bg-orange-500' : 'bg-blue-500'}`}></div>
                    </div>
                    <div className="flex-grow">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium">
                            {event.is_re_evaluation ? '🔄 Re-evaluation' : '🆕 Initial Validation'}
                          </p>
                          <p className="text-sm text-gray-600">{formatDate(event.timestamp)}</p>
                          {event.is_re_evaluation && event.re_evaluation_info && (
                            <p className="text-xs text-orange-600">
                              Reason: {event.re_evaluation_info.change_reason}
                            </p>
                          )}
                        </div>
                        <div className="text-right">
                          <p className={`font-semibold ${getScoreColor(event.overall_score)}`}>
                            {event.overall_score.toFixed(1)}%
                          </p>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(event.status)}`}>
                            {event.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 bg-gray-50 rounded-lg">
              <p className="text-gray-600">Enter a project name to view its timeline</p>
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold">Analytics & Metrics</h2>
          
          {analytics ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-white shadow-lg rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">📊 Overall Performance</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Total Runs:</span>
                    <span className="font-semibold">{analytics.basic_analytics.total_runs}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Pass Rate:</span>
                    <span className={`font-semibold ${analytics.basic_analytics.pass_rate >= 70 ? 'text-green-600' : 'text-red-600'}`}>
                      {analytics.basic_analytics.pass_rate.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Average Score:</span>
                    <span className="font-semibold">{analytics.basic_analytics.average_score.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Trend:</span>
                    <span className={`font-semibold ${
                      analytics.basic_analytics.score_trend === 'improving' ? 'text-green-600' :
                      analytics.basic_analytics.score_trend === 'declining' ? 'text-red-600' : 'text-yellow-600'
                    }`}>
                      {analytics.basic_analytics.score_trend}
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow-lg rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">⚡ Performance Metrics</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Avg Execution Time:</span>
                    <span className="font-semibold">
                      {analytics.basic_analytics.performance_metrics.average_execution_time.toFixed(2)}s
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Fastest Run:</span>
                    <span className="font-semibold text-green-600">
                      {analytics.basic_analytics.performance_metrics.fastest_execution.toFixed(2)}s
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Slowest Run:</span>
                    <span className="font-semibold text-red-600">
                      {analytics.basic_analytics.performance_metrics.slowest_execution.toFixed(2)}s
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow-lg rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">🔄 Workflow Status</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Currently Running:</span>
                    <span className="font-semibold">{analytics.workflow_metrics.currently_running}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>System Load:</span>
                    <span className={`font-semibold ${
                      analytics.workflow_metrics.system_load === 'normal' ? 'text-green-600' : 'text-yellow-600'
                    }`}>
                      {analytics.workflow_metrics.system_load}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Data Completeness:</span>
                    <span className="font-semibold">
                      {analytics.basic_analytics.data_quality.data_completeness.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>

              {analytics.recommendations && analytics.recommendations.length > 0 && (
                <div className="md:col-span-2 lg:col-span-3 bg-white shadow-lg rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">💡 Recommendations</h3>
                  <div className="space-y-3">
                    {analytics.recommendations.map((rec, index) => (
                      <div key={index} className={`p-3 rounded-lg border-l-4 ${
                        rec.priority === 'high' ? 'border-red-500 bg-red-50' :
                        rec.priority === 'medium' ? 'border-yellow-500 bg-yellow-50' :
                        'border-blue-500 bg-blue-50'
                      }`}>
                        <p className="font-medium">{rec.type.replace('_', ' ').toUpperCase()}</p>
                        <p className="text-sm text-gray-700">{rec.message}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Loading analytics...</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ResultsManagement;

