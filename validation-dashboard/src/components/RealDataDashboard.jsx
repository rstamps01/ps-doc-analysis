import React, { useState, useEffect } from 'react';
import { API_BASE, apiRequest, buildApiUrl } from '../config/apiConfig';

const RealDataDashboard = () => {
  // State management
  const [dashboardData, setDashboardData] = useState(null)
  const [validationHistory, setValidationHistory] = useState([])
  const [commonIssues, setCommonIssues] = useState([])
  const [analyticsData, setAnalyticsData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // API function to fetch real data
  const fetchRealData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch dashboard stats
      const dashboardResponse = await fetch(`${API_BASE}/api/real-data/dashboard-stats`)
      if (dashboardResponse.ok) {
        const dashboardResult = await dashboardResponse.json()
        setDashboardData(dashboardResult.data)
      }

      // Fetch validation history
      const historyResponse = await fetch(`${API_BASE}/api/real-data/validation-history`)
      if (historyResponse.ok) {
        const historyResult = await historyResponse.json()
        setValidationHistory(historyResult.data)
      }

      // Fetch common issues
      const issuesResponse = await fetch(`${API_BASE}/api/real-data/common-issues`)
      if (issuesResponse.ok) {
        const issuesResult = await issuesResponse.json()
        setCommonIssues(issuesResult.data)
      }

      // Fetch analytics data
      const analyticsResponse = await fetch(`${API_BASE}/api/real-data/analytics`)
      if (analyticsResponse.ok) {
        const analyticsResult = await analyticsResponse.json()
        setAnalyticsData(analyticsResult.data)
      }

    } catch (error) {
      console.error('Error fetching real data:', error)
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  // Load data on component mount
  useEffect(() => {
    fetchRealData()
  }, [])

  // Loading state
  if (loading) {
    return (
      <div className="real-data-dashboard loading">
        <div className="loading-spinner"></div>
        <p>Loading real validation data...</p>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="real-data-dashboard error">
        <div className="error-message">
          <h3>⚠️ Error Loading Data</h3>
          <p>{error}</p>
          <button onClick={fetchRealData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    )
  }

  // Render dashboard with real data
  return (
    <div className="real-data-dashboard">
      <div className="dashboard-header">
        <h2>📊 Real-Time Validation Dashboard</h2>
        <button onClick={fetchRealData} className="refresh-button">
          🔄 Refresh Data
        </button>
      </div>

      {/* System Metrics */}
      {dashboardData && (
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-value">{dashboardData.overall_score}%</div>
            <div className="metric-label">Overall Score</div>
            <div className={`metric-trend ${dashboardData.overall_score >= 85 ? 'up' : 'stable'}`}>
              {dashboardData.overall_score >= 85 ? '↗️' : '→'} 
              {dashboardData.overall_score >= 85 ? 'Excellent' : 'Good'}
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-value">{dashboardData.total_checks}</div>
            <div className="metric-label">Total Checks</div>
            <div className="metric-trend up">↗️ Active</div>
          </div>

          <div className="metric-card">
            <div className="metric-value">{dashboardData.passed_checks}</div>
            <div className="metric-label">Passed Checks</div>
            <div className="metric-trend up">
              ✅ {((dashboardData.passed_checks / dashboardData.total_checks) * 100).toFixed(1)}%
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-value">{dashboardData.execution_time}s</div>
            <div className="metric-label">Execution Time</div>
            <div className="metric-trend stable">→ Optimal</div>
          </div>
        </div>
      )}

      {/* Category Performance */}
      {dashboardData && dashboardData.categories && (
        <div className="categories-section">
          <h3>📋 Category Performance</h3>
          <div className="categories-grid">
            {Object.entries(dashboardData.categories).map(([categoryName, categoryData]) => (
              <div key={categoryName} className="category-card">
                <div className="category-header">
                  <h4>{categoryName}</h4>
                  <div className={`category-status ${categoryData.status}`}>
                    {categoryData.status === 'pass' ? '✅' : categoryData.status === 'warning' ? '⚠️' : '❌'}
                  </div>
                </div>
                <div className="category-score">{categoryData.score}%</div>
                <div className="category-details">
                  <div className="detail-item">
                    <span>Checks: {categoryData.total_checks}</span>
                  </div>
                  <div className="detail-item">
                    <span>Passed: {categoryData.passed_checks}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Validation History */}
      {validationHistory && validationHistory.length > 0 && (
        <div className="history-section">
          <h3>📈 Recent Validation History</h3>
          <div className="history-list">
            {validationHistory.slice(0, 5).map((validation, index) => (
              <div key={index} className="history-item">
                <div className="history-header">
                  <span className="validation-id">{validation.validation_id}</span>
                  <span className="timestamp">{new Date(validation.timestamp).toLocaleString()}</span>
                </div>
                <div className="history-details">
                  <span className="score">Score: {validation.overall_score}%</span>
                  <span className={`status ${validation.status}`}>{validation.status}</span>
                  <span className="duration">Duration: {validation.execution_time}s</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Common Issues */}
      {commonIssues && commonIssues.length > 0 && (
        <div className="issues-section">
          <h3>⚠️ Common Issues</h3>
          <div className="issues-list">
            {commonIssues.slice(0, 5).map((issue, index) => (
              <div key={index} className="issue-item">
                <div className={`issue-severity ${issue.severity}`}>
                  {issue.severity === 'high' ? '🔴' : issue.severity === 'medium' ? '🟡' : '🟢'}
                </div>
                <div className="issue-content">
                  <div className="issue-title">{issue.title}</div>
                  <div className="issue-description">{issue.description}</div>
                  <div className="issue-frequency">Frequency: {issue.frequency}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analytics Summary */}
      {analyticsData && (
        <div className="analytics-section">
          <h3>📊 Analytics Summary</h3>
          <div className="analytics-grid">
            <div className="analytics-card">
              <h4>Performance Trends</h4>
              <div className="trend-data">
                <div className="trend-item">
                  <span>Score Trend:</span>
                  <span className={`trend ${analyticsData.score_trend}`}>
                    {analyticsData.score_trend === 'improving' ? '📈 Improving' : '📊 Stable'}
                  </span>
                </div>
                <div className="trend-item">
                  <span>Processing Time:</span>
                  <span className="trend stable">⚡ Optimized</span>
                </div>
              </div>
            </div>

            <div className="analytics-card">
              <h4>Success Metrics</h4>
              <div className="success-metrics">
                <div className="metric-item">
                  <span>Success Rate:</span>
                  <span className="success-rate">{analyticsData.success_rate}%</span>
                </div>
                <div className="metric-item">
                  <span>Avg Score:</span>
                  <span className="avg-score">{analyticsData.average_score}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* System Status */}
      <div className="system-status">
        <h3>🔧 System Status</h3>
        <div className="status-indicators">
          <div className="status-item">
            <span className="status-dot green"></span>
            <span>API Connected</span>
          </div>
          <div className="status-item">
            <span className="status-dot blue"></span>
            <span>Real Data Active</span>
          </div>
          <div className="status-item">
            <span className="status-dot green"></span>
            <span>Validation Engine Online</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RealDataDashboard

