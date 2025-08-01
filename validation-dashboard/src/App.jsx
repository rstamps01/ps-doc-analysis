import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardStats, setDashboardStats] = useState({
    totalValidations: 156,
    successRate: 94.2,
    avgProcessingTime: 2.3,
    activeRuns: 3
  });
  const [validationResults, setValidationResults] = useState({
    overallScore: 85.2,
    passed: 43,
    failed: 3,
    warnings: 4,
    categories: [
      { name: 'Site Survey Part 1', score: 92, status: 'passed' },
      { name: 'Site Survey Part 2', score: 88, status: 'passed' },
      { name: 'Install Plan', score: 76, status: 'warning' },
      { name: 'Network Config', score: 45, status: 'failed' }
    ]
  });

  const tabs = [
    { id: 'dashboard', label: '1. Dashboard', icon: '📊' },
    { id: 'validation', label: '2. Validation', icon: '✅' },
    { id: 'analytics', label: '3. Analytics', icon: '📈' },
    { id: 'export', label: '4. Export', icon: '📤' },
    { id: 'settings', label: '5. Settings', icon: '⚙️' }
  ];

  const renderDashboard = () => (
    <div className="n8n-dashboard">
      <div className="dashboard-header">
        <h2>Enhanced Information Validation Tool</h2>
        <div className="status-indicators">
          <div className="status-item">
            <span className="status-dot green"></span>
            <span>API Connected</span>
          </div>
          <div className="status-item">
            <span className="status-dot blue"></span>
            <span>Google APIs Active</span>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{dashboardStats.totalValidations}</div>
          <div className="stat-label">Total Validations</div>
          <div className="stat-trend">+12% this month</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{dashboardStats.successRate}%</div>
          <div className="stat-label">Success Rate</div>
          <div className="stat-trend">+2.1% improvement</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{dashboardStats.avgProcessingTime}s</div>
          <div className="stat-label">Avg Processing Time</div>
          <div className="stat-trend">-15% faster</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{dashboardStats.activeRuns}</div>
          <div className="stat-label">Active Runs</div>
          <div className="stat-trend">Currently processing</div>
        </div>
      </div>

      <div className="workflow-section">
        <h3>Validation Workflow</h3>
        <div className="workflow-steps">
          <div className="workflow-step active">
            <div className="step-number">1</div>
            <div className="step-content">
              <div className="step-title">Document Upload</div>
              <div className="step-desc">Google Drive/Sheets Integration</div>
            </div>
          </div>
          <div className="workflow-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <div className="step-title">Validation Engine</div>
              <div className="step-desc">50+ Criteria Analysis</div>
            </div>
          </div>
          <div className="workflow-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <div className="step-title">Results Generation</div>
              <div className="step-desc">Scoring & Recommendations</div>
            </div>
          </div>
          <div className="workflow-step">
            <div className="step-number">4</div>
            <div className="step-content">
              <div className="step-title">Export & Analytics</div>
              <div className="step-desc">PDF, Excel, CSV Reports</div>
            </div>
          </div>
        </div>
      </div>

      <div className="recent-results">
        <h3>Recent Validation Results</h3>
        <div className="results-summary">
          <div className="summary-score">
            <div className="score-circle">
              <span className="score-value">{validationResults.overallScore}%</span>
            </div>
            <div className="score-details">
              <div className="score-breakdown">
                <span className="passed">✅ {validationResults.passed} Passed</span>
                <span className="warnings">⚠️ {validationResults.warnings} Warnings</span>
                <span className="failed">❌ {validationResults.failed} Failed</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderValidation = () => (
    <div className="n8n-validation">
      <div className="validation-header">
        <h2>Document Validation</h2>
        <p>Configure and run comprehensive validation on your Site Survey and Install Plan documents</p>
      </div>

      <div className="validation-config">
        <h3>Document Configuration</h3>
        <div className="config-grid">
          <div className="input-group">
            <label>Site Survey Part 1 (Google Sheets)</label>
            <input 
              type="text" 
              placeholder="https://docs.google.com/spreadsheets/..." 
              defaultValue="https://docs.google.com/spreadsheets/d/1example1"
            />
          </div>
          <div className="input-group">
            <label>Site Survey Part 2 (Google Sheets)</label>
            <input 
              type="text" 
              placeholder="https://docs.google.com/spreadsheets/..." 
              defaultValue="https://docs.google.com/spreadsheets/d/1example2"
            />
          </div>
          <div className="input-group">
            <label>Install Plan (Google Drive)</label>
            <input 
              type="text" 
              placeholder="https://drive.google.com/file/..." 
              defaultValue="https://drive.google.com/file/d/1example3"
            />
          </div>
        </div>
        <button className="btn-primary">Run Comprehensive Validation</button>
      </div>

      <div className="validation-settings">
        <h3>Validation Settings</h3>
        <div className="settings-grid">
          <div className="setting-item">
            <label>Validation Threshold</label>
            <select defaultValue="75">
              <option value="60">60% - Basic</option>
              <option value="75">75% - Standard</option>
              <option value="90">90% - Strict</option>
            </select>
          </div>
          <div className="setting-item">
            <label>Category Weights</label>
            <div className="weight-controls">
              <div>Site Survey: <input type="range" min="1" max="10" defaultValue="8" /></div>
              <div>Install Plan: <input type="range" min="1" max="10" defaultValue="7" /></div>
              <div>Network Config: <input type="range" min="1" max="10" defaultValue="9" /></div>
            </div>
          </div>
        </div>
      </div>

      <div className="validation-results">
        <h3>Latest Results</h3>
        {validationResults.categories.map((category, index) => (
          <div key={index} className={`result-item ${category.status}`}>
            <div className="result-name">{category.name}</div>
            <div className="result-score">{category.score}%</div>
            <div className={`result-status ${category.status}`}>
              {category.status === 'passed' ? '✅' : category.status === 'warning' ? '⚠️' : '❌'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAnalytics = () => (
    <div className="n8n-analytics">
      <div className="analytics-header">
        <h2>Analytics & Trends</h2>
        <p>Performance insights and validation trends over time</p>
      </div>

      <div className="analytics-grid">
        <div className="analytics-card">
          <h3>Validation Trends</h3>
          <div className="trend-chart">
            <div className="chart-placeholder">📈 Trend Chart Placeholder</div>
          </div>
        </div>
        
        <div className="analytics-card">
          <h3>Category Performance</h3>
          <div className="performance-bars">
            <div className="perf-item">
              <span>Document Completeness</span>
              <div className="perf-bar">
                <div className="perf-fill" style={{width: '92%'}}></div>
              </div>
              <span>92%</span>
            </div>
            <div className="perf-item">
              <span>Technical Requirements</span>
              <div className="perf-bar">
                <div className="perf-fill" style={{width: '78%'}}></div>
              </div>
              <span>78%</span>
            </div>
            <div className="perf-item">
              <span>SFDC Integration</span>
              <div className="perf-bar">
                <div className="perf-fill" style={{width: '95%'}}></div>
              </div>
              <span>95%</span>
            </div>
            <div className="perf-item">
              <span>Cross-Document Consistency</span>
              <div className="perf-bar">
                <div className="perf-fill" style={{width: '76%'}}></div>
              </div>
              <span>76%</span>
            </div>
          </div>
        </div>

        <div className="analytics-card">
          <h3>Common Issues</h3>
          <div className="issues-list">
            <div className="issue-item">
              <span className="issue-count">7</span>
              <span className="issue-text">Missing VAST cluster config</span>
              <span className="issue-trend">↑</span>
            </div>
            <div className="issue-item">
              <span className="issue-count">5</span>
              <span className="issue-text">Incomplete network diagrams</span>
              <span className="issue-trend">→</span>
            </div>
            <div className="issue-item">
              <span className="issue-count">3</span>
              <span className="issue-text">Power calculations missing</span>
              <span className="issue-trend">↓</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderExport = () => (
    <div className="n8n-export">
      <div className="export-header">
        <h2>Export & Reports</h2>
        <p>Generate and download validation reports in various formats</p>
      </div>

      <div className="export-options">
        <div className="export-card">
          <h3>📄 PDF Report</h3>
          <p>Comprehensive validation report with charts and recommendations</p>
          <button className="btn-primary">Generate PDF</button>
        </div>
        
        <div className="export-card">
          <h3>📊 Excel Spreadsheet</h3>
          <p>Detailed data export with validation results and metrics</p>
          <button className="btn-primary">Export Excel</button>
        </div>
        
        <div className="export-card">
          <h3>📋 CSV Data</h3>
          <p>Raw validation data for further analysis</p>
          <button className="btn-primary">Download CSV</button>
        </div>
      </div>

      <div className="export-history">
        <h3>Export History</h3>
        <div className="history-list">
          <div className="history-item">
            <span>📄 Validation_Report_2024-01-15.pdf</span>
            <span>2.3 MB</span>
            <span>Jan 15, 2024</span>
            <button className="btn-secondary">Download</button>
          </div>
          <div className="history-item">
            <span>📊 Validation_Data_2024-01-10.xlsx</span>
            <span>1.8 MB</span>
            <span>Jan 10, 2024</span>
            <button className="btn-secondary">Download</button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="n8n-settings">
      <div className="settings-header">
        <h2>Settings & Configuration</h2>
        <p>Configure API credentials and system settings</p>
      </div>

      <div className="settings-grid">
        <div className="settings-card">
          <h3>Google API Credentials</h3>
          <textarea 
            placeholder="Paste your Google service account JSON here..."
            rows="8"
          ></textarea>
          <button className="btn-primary">Save Credentials</button>
        </div>

        <div className="settings-card">
          <h3>System Configuration</h3>
          <div className="config-options">
            <label>
              <input type="checkbox" defaultChecked />
              Enable real-time validation
            </label>
            <label>
              <input type="checkbox" defaultChecked />
              Auto-export results
            </label>
            <label>
              <input type="checkbox" />
              Email notifications
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard': return renderDashboard();
      case 'validation': return renderValidation();
      case 'analytics': return renderAnalytics();
      case 'export': return renderExport();
      case 'settings': return renderSettings();
      default: return renderDashboard();
    }
  };

  return (
    <div className="n8n-app">
      <div className="n8n-sidebar">
        <div className="sidebar-header">
          <h1>Enhanced Information Validation Tool</h1>
          <p>Automated validation for Site Survey and Install Plan documents</p>
        </div>
        
        <nav className="sidebar-nav">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="nav-icon">{tab.icon}</span>
              <span className="nav-label">{tab.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="system-status">
            <div className="status-item">
              <span className="status-dot green"></span>
              <span>System Operational</span>
            </div>
            <div className="status-item">
              <span className="status-dot blue"></span>
              <span>99.8% Uptime</span>
            </div>
          </div>
        </div>
      </div>

      <div className="n8n-main">
        <div className="main-content">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

export default App;

