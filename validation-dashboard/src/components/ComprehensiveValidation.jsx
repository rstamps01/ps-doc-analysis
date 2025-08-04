import React, { useState, useEffect } from 'react';
import { API_BASE, apiRequest, buildApiUrl } from '../config/apiConfig';

const ComprehensiveValidation = () => {
  const [validationState, setValidationState] = useState({
    isRunning: false,
    validationId: null,
    progress: null,
    results: null,
    error: null
  });

  const [testUrls, setTestUrls] = useState({
    evaluation_criteria: 'https://docs.google.com/spreadsheets/d/1MgJ77VGjvuphf45z_0LJ77zWlAslPEvJWOrTgrgsZb8/edit?usp=sharing',
    site_survey_1: 'https://docs.google.com/spreadsheets/d/1aQVhSNNmDJ0FXhejoXi84GHxD8iIyuIYuhld9lxTZPY/edit?usp=sharing',
    site_survey_2: 'https://docs.google.com/spreadsheets/d/1p2X4Pvleis2s0pgQ1FRpf-o2e4LsgfOA0LxlmLVxH_k/edit?usp=sharing',
    install_plan: 'https://drive.google.com/file/d/1ez3eMHrKXKJJBXMgJLnj3RQcENZQZgkm/view?usp=sharing'
  });

  const [customizationSettings, setCustomizationSettings] = useState({
    enabledCategories: {
      'Document Completeness': true,
      'SFDC Integration': true,
      'Install Plan Validation': true,
      'Site Survey Validation': true
    },
    categoryWeights: {
      'Document Completeness': 25,
      'SFDC Integration': 25,
      'Install Plan Validation': 25,
      'Site Survey Validation': 25
    },
    selectedSheets: {
      site_survey_1: ['Project Details', 'VAST Cluster', 'Network Details'],
      site_survey_2: ['Features and Configuration', 'IP Addresses', 'Network Diagram']
    },
    validationThresholds: {
      pass: 80,
      warning: 60,
      fail: 0
    }
  });

  const [validationHistory, setValidationHistory] = useState([]);
  const [showCustomization, setShowCustomization] = useState(false);

  const runValidation = async () => {
    try {
      setValidationState({
        isRunning: true,
        validationId: null,
        progress: null,
        results: null,
        error: null
      });

      const response = await fetch(`${API_BASE}/api/validation/comprehensive`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...testUrls,
          customization: customizationSettings
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setValidationState({
          isRunning: true,
          validationId: data.validation_id,
          progress: { status: 'started', percentage: 0 },
          results: null,
          error: null
        });

        // Start polling for progress
        pollValidationProgress(data.validation_id);
      } else {
        throw new Error(data.error || 'Validation failed');
      }
    } catch (error) {
      console.error('Validation error:', error);
      setValidationState({
        isRunning: false,
        validationId: null,
        progress: null,
        results: null,
        error: error.message
      });
    }
  };

  const pollValidationProgress = async (validationId) => {
    try {
      const response = await fetch(`${API_BASE}/api/validation/api-key/progress/${validationId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      setValidationState(prev => ({
        ...prev,
        progress: data.progress,
        results: data.results,
        isRunning: data.status === 'running'
      }));

      if (data.status === 'running') {
        setTimeout(() => pollValidationProgress(validationId), 2000);
      } else if (data.status === 'completed') {
        // Add to history
        setValidationHistory(prev => [data, ...prev.slice(0, 9)]);
      }
    } catch (error) {
      console.error('Progress polling error:', error);
      setValidationState(prev => ({
        ...prev,
        error: error.message,
        isRunning: false
      }));
    }
  };

  const testConnection = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/validation/test-connection`);
      const data = await response.json();
      
      if (data.success) {
        alert('✅ Connection successful! Backend is responding.');
      } else {
        alert('❌ Connection failed: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      alert('❌ Connection failed: ' + error.message);
    }
  };

  const formatProgress = (progress) => {
    if (!progress) return 'Initializing...';
    return `${progress.status} - ${progress.percentage || 0}%`;
  };

  const formatResults = (results) => {
    if (!results) return null;
    
    return (
      <div className="validation-results">
        <h3>Validation Results</h3>
        <div className="results-summary">
          <div className="score">Overall Score: {results.overall_score}%</div>
          <div className="status">Status: {results.status}</div>
        </div>
        
        {results.categories && (
          <div className="categories">
            <h4>Category Results:</h4>
            {Object.entries(results.categories).map(([category, data]) => (
              <div key={category} className="category-result">
                <span className="category-name">{category}:</span>
                <span className="category-score">{data.score}%</span>
                <span className={`category-status ${data.status}`}>{data.status}</span>
              </div>
            ))}
          </div>
        )}
        
        {results.issues && results.issues.length > 0 && (
          <div className="issues">
            <h4>Issues Found:</h4>
            {results.issues.map((issue, index) => (
              <div key={index} className="issue">
                <span className={`severity ${issue.severity}`}>{issue.severity}</span>
                <span className="description">{issue.description}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="comprehensive-validation">
      <div className="validation-header">
        <h2>Comprehensive Document Validation</h2>
        <div className="header-actions">
          <button onClick={testConnection} className="test-connection-btn">
            Test Connection
          </button>
          <button 
            onClick={() => setShowCustomization(!showCustomization)}
            className="customization-toggle"
          >
            {showCustomization ? 'Hide' : 'Show'} Customization
          </button>
        </div>
      </div>

      {showCustomization && (
        <div className="customization-panel">
          <h3>Validation Customization</h3>
          
          <div className="url-inputs">
            <h4>Document URLs</h4>
            {Object.entries(testUrls).map(([key, url]) => (
              <div key={key} className="url-input">
                <label>{key.replace('_', ' ').toUpperCase()}:</label>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setTestUrls(prev => ({
                    ...prev,
                    [key]: e.target.value
                  }))}
                  placeholder={`Enter ${key} URL`}
                />
              </div>
            ))}
          </div>

          <div className="category-settings">
            <h4>Category Settings</h4>
            {Object.entries(customizationSettings.enabledCategories).map(([category, enabled]) => (
              <div key={category} className="category-setting">
                <label>
                  <input
                    type="checkbox"
                    checked={enabled}
                    onChange={(e) => setCustomizationSettings(prev => ({
                      ...prev,
                      enabledCategories: {
                        ...prev.enabledCategories,
                        [category]: e.target.checked
                      }
                    }))}
                  />
                  {category}
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={customizationSettings.categoryWeights[category]}
                  onChange={(e) => setCustomizationSettings(prev => ({
                    ...prev,
                    categoryWeights: {
                      ...prev.categoryWeights,
                      [category]: parseInt(e.target.value)
                    }
                  }))}
                  disabled={!enabled}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="validation-controls">
        <button 
          onClick={runValidation}
          disabled={validationState.isRunning}
          className="run-validation-btn"
        >
          {validationState.isRunning ? 'Running Validation...' : 'Run Comprehensive Validation'}
        </button>
      </div>

      {validationState.error && (
        <div className="error-message">
          <h3>Error:</h3>
          <p>{validationState.error}</p>
        </div>
      )}

      {validationState.isRunning && (
        <div className="validation-progress">
          <h3>Validation Progress</h3>
          <div className="progress-info">
            <p>Validation ID: {validationState.validationId}</p>
            <p>Status: {formatProgress(validationState.progress)}</p>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${validationState.progress?.percentage || 0}%` }}
            ></div>
          </div>
        </div>
      )}

      {validationState.results && formatResults(validationState.results)}

      {validationHistory.length > 0 && (
        <div className="validation-history">
          <h3>Recent Validations</h3>
          {validationHistory.map((validation, index) => (
            <div key={index} className="history-item">
              <div className="history-header">
                <span className="validation-id">{validation.validation_id}</span>
                <span className="timestamp">{new Date(validation.timestamp).toLocaleString()}</span>
              </div>
              <div className="history-summary">
                <span className="score">Score: {validation.results?.overall_score}%</span>
                <span className={`status ${validation.status}`}>{validation.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ComprehensiveValidation;

