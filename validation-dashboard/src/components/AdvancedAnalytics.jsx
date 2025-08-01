import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Area, AreaChart } from 'recharts';

const AdvancedAnalytics = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [activeTab, setActiveTab] = useState('overview');

  // const API_BASE_URL = 'https://58hpi8c7mpvo.manus.space';
  const API_BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:5000';

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedPeriod]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/dashboard/data?days=${selectedPeriod}`);
      const result = await response.json();
      
      if (result.status === 'success') {
        setAnalyticsData(result.dashboard_data);
      } else {
        console.error('Failed to load analytics data:', result.message);
      }
    } catch (error) {
      console.error('Error loading analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportReport = async (format) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/report?days=${selectedPeriod}&format=${format}`);
      
      if (format === 'pdf') {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics_report_${selectedPeriod}days.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const result = await response.json();
        console.log('Report data:', result);
      }
    } catch (error) {
      console.error('Error exporting report:', error);
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <span className="ml-3 text-lg">Loading analytics data...</span>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 mb-4">No Analytics Data Available</h3>
        <p className="text-gray-600 mb-6">Run some validations to see analytics and trends.</p>
        <button 
          onClick={loadAnalyticsData}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Refresh Data
        </button>
      </div>
    );
  }

  const summaryCards = analyticsData.summary_cards || {};
  const charts = analyticsData.charts || {};
  const trends = analyticsData.trends || {};
  const recommendations = analyticsData.recommendations || [];

  // Prepare chart data
  const scoreDistributionData = Object.entries(charts.score_distribution || {}).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value: value,
    percentage: value
  }));

  const categoryPerformanceData = Object.entries(charts.category_performance || {}).map(([category, data]) => ({
    category: category.replace('_', ' ').replace(/\\b\\w/g, l => l.toUpperCase()),
    score: data.average_score || 0,
    passRate: data.pass_rate || 0
  }));

  const failurePatternsData = (charts.failure_patterns || []).slice(0, 5).map(([name, count]) => ({
    name: name.replace('_', ' ').replace(/\\b\\w/g, l => l.toUpperCase()),
    count: count
  }));

  const dailyCountsData = Object.entries(charts.daily_counts || {}).map(([date, count]) => ({
    date: date,
    validations: count
  })).sort((a, b) => new Date(a.date) - new Date(b.date));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Advanced Analytics Dashboard</h2>
          <p className="text-gray-600">Comprehensive validation trends and performance metrics</p>
        </div>
        
        <div className="flex space-x-4">
          {/* Period Selector */}
          <select 
            value={selectedPeriod} 
            onChange={(e) => setSelectedPeriod(parseInt(e.target.value))}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last year</option>
          </select>
          
          {/* Export Buttons */}
          <button 
            onClick={() => exportReport('pdf')}
            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
          >
            📄 Export PDF
          </button>
          
          <button 
            onClick={() => exportReport('json')}
            className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
          >
            📊 Export Data
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Validations</h3>
          <p className="text-3xl font-bold text-gray-900">{summaryCards.total_validations || 0}</p>
          <p className="text-sm text-gray-600 mt-1">Last {selectedPeriod} days</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Average Score</h3>
          <p className="text-3xl font-bold text-gray-900">{summaryCards.average_score || 0}%</p>
          <p className="text-sm text-gray-600 mt-1">
            Trend: <span className={`font-medium ${trends.score_trend === 'increasing' ? 'text-green-600' : trends.score_trend === 'decreasing' ? 'text-red-600' : 'text-gray-600'}`}>
              {trends.score_trend || 'stable'}
            </span>
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Success Rate</h3>
          <p className="text-3xl font-bold text-gray-900">{summaryCards.success_rate || 0}%</p>
          <p className="text-sm text-gray-600 mt-1">Validations ≥80% score</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-orange-500">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Avg Processing Time</h3>
          <p className="text-3xl font-bold text-gray-900">{summaryCards.avg_processing_time || 0}s</p>
          <p className="text-sm text-gray-600 mt-1">
            Trend: <span className={`font-medium ${trends.processing_time_trend === 'decreasing' ? 'text-green-600' : trends.processing_time_trend === 'increasing' ? 'text-red-600' : 'text-gray-600'}`}>
              {trends.processing_time_trend || 'stable'}
            </span>
          </p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview', icon: '📊' },
            { id: 'categories', name: 'Categories', icon: '📋' },
            { id: 'trends', name: 'Trends', icon: '📈' },
            { id: 'failures', name: 'Failure Analysis', icon: '⚠️' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Score Distribution */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Score Distribution</h3>
              {scoreDistributionData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={scoreDistributionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percentage }) => `${name}: ${percentage}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {scoreDistributionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center text-gray-500 py-12">No score distribution data available</div>
              )}
            </div>

            {/* Daily Validation Counts */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Daily Validation Activity</h3>
              {dailyCountsData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={dailyCountsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="validations" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center text-gray-500 py-12">No daily activity data available</div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'categories' && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Category Performance Analysis</h3>
            {categoryPerformanceData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={categoryPerformanceData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="score" fill="#8884d8" name="Average Score (%)" />
                  <Bar dataKey="passRate" fill="#82ca9d" name="Pass Rate (%)" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-gray-500 py-12">No category performance data available</div>
            )}
          </div>
        )}

        {activeTab === 'trends' && (
          <div className="space-y-6">
            {/* Improvement Trends */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Improvement Trends</h3>
              {Object.keys(trends.improvement_trends || {}).length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(trends.improvement_trends).map(([project, data]) => (
                    <div key={project} className="border-l-4 border-blue-500 pl-4">
                      <h4 className="font-medium text-gray-900">{project}</h4>
                      <div className="grid grid-cols-3 gap-4 mt-2 text-sm">
                        <div>
                          <span className="text-gray-500">Initial Score:</span>
                          <span className="ml-2 font-medium">{data.initial_score?.toFixed(1)}%</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Latest Score:</span>
                          <span className="ml-2 font-medium">{data.latest_score?.toFixed(1)}%</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Improvement:</span>
                          <span className={`ml-2 font-medium ${data.improvement >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {data.improvement >= 0 ? '+' : ''}{data.improvement?.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-12">No improvement trends data available</div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'failures' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Failure Patterns */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Most Common Failures</h3>
              {failurePatternsData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={failurePatternsData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={120} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#ff7300" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center text-gray-500 py-12">No failure pattern data available</div>
              )}
            </div>

            {/* Recommendations */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Key Recommendations</h3>
              {recommendations.length > 0 ? (
                <div className="space-y-4">
                  {recommendations.map((rec, index) => (
                    <div key={index} className={`p-4 rounded-lg border-l-4 ${
                      rec.priority === 'high' ? 'border-red-500 bg-red-50' :
                      rec.priority === 'medium' ? 'border-yellow-500 bg-yellow-50' :
                      'border-green-500 bg-green-50'
                    }`}>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">{rec.title}</h4>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                          rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {rec.priority}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">{rec.description}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-12">No recommendations available</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Refresh Button */}
      <div className="text-center">
        <button 
          onClick={loadAnalyticsData}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg"
          disabled={loading}
        >
          {loading ? 'Refreshing...' : '🔄 Refresh Analytics Data'}
        </button>
      </div>
    </div>
  );
};

export default AdvancedAnalytics;

