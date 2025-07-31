import React, { useState, useEffect } from 'react';

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

  // API base URL
  const API_BASE = 'https://58hpi8c7mpvo.manus.space';

  const runComprehensiveValidation = async () => {
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
          test_urls: testUrls,
          customization: customizationSettings
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        setValidationState(prev => ({
          ...prev,
          validationId: data.data.validation_id,
          results: data.data
        }));

        // Add to history
        setValidationHistory(prev => [
          {
            id: data.validation_id,
            timestamp: new Date().toISOString(),
            status: data.results.overall_status,
            score: data.results.overall_score,
            checks_completed: data.results.checks_completed,
            total_checks: data.results.total_checks
          },
          ...prev.slice(0, 9) // Keep last 10 results
        ]);

        // Start progress monitoring
        monitorProgress(data.validation_id);
      } else {
        setValidationState(prev => ({
          ...prev,
          error: data.error
        }));
      }
    } catch (error) {
      setValidationState(prev => ({
        ...prev,
        error: error.message
      }));
    } finally {
      setValidationState(prev => ({
        ...prev,
        isRunning: false
      }));
    }
  };

  const monitorProgress = async (validationId) => {
    try {
      const response = await fetch(`${API_BASE}/api/validation/api-key/progress/${validationId}`);
      const data = await response.json();

      if (data.success) {
        setValidationState(prev => ({
          ...prev,
          progress: data.progress
        }));

        // Continue monitoring if not completed
        if (data.progress.status === 'Running' || data.progress.status === 'Starting') {
          setTimeout(() => monitorProgress(validationId), 2000);
        }
      }
    } catch (error) {
      console.error('Error monitoring progress:', error);
    }
  };

  const testApiConnection = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/validation/test-connection`);
      const data = await response.json();
      
      if (data.status === 'success') {
        alert('✅ API connection successful! Ready for validation.');
      } else {
        alert('❌ API connection failed: ' + (data.message || 'Unknown error'));
      }
    } catch (error) {
      alert('❌ Connection test failed: ' + error.message);
    }
  };

  const updateCategoryWeight = (category, weight) => {
    setCustomizationSettings(prev => ({
      ...prev,
      categoryWeights: {
        ...prev.categoryWeights,
        [category]: weight
      }
    }));
  };

  const toggleCategory = (category) => {
    setCustomizationSettings(prev => ({
      ...prev,
      enabledCategories: {
        ...prev.enabledCategories,
        [category]: !prev.enabledCategories[category]
      }
    }));
  };

  const updateSheetSelection = (surveyType, sheets) => {
    setCustomizationSettings(prev => ({
      ...prev,
      selectedSheets: {
        ...prev.selectedSheets,
        [surveyType]: sheets
      }
    }));
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getStatusColor = (status) => {
    if (status === 'Completed') return 'text-green-600';
    if (status === 'Running') return 'text-blue-600';
    if (status === 'Failed') return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-900">🔍 Comprehensive Validation</h2>
          <div className="flex space-x-3">
            <button
              onClick={testApiConnection}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              🔄 Test Connection
            </button>
            <button
              onClick={() => setShowCustomization(!showCustomization)}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              ⚙️ Customize
            </button>
          </div>
        </div>
        
        <p className="text-gray-600 mb-4">
          Run comprehensive validation across all documents with real-time progress monitoring and customizable criteria.
        </p>

        {/* Test URLs Configuration */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📊 Evaluation Criteria URL
            </label>
            <input
              type="url"
              value={testUrls.evaluation_criteria}
              onChange={(e) => setTestUrls(prev => ({ ...prev, evaluation_criteria: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Google Sheets URL for evaluation criteria"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📋 Site Survey Part 1 URL
            </label>
            <input
              type="url"
              value={testUrls.site_survey_1}
              onChange={(e) => setTestUrls(prev => ({ ...prev, site_survey_1: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Google Sheets URL for Site Survey Part 1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📋 Site Survey Part 2 URL
            </label>
            <input
              type="url"
              value={testUrls.site_survey_2}
              onChange={(e) => setTestUrls(prev => ({ ...prev, site_survey_2: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Google Sheets URL for Site Survey Part 2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📄 Install Plan URL
            </label>
            <input
              type="url"
              value={testUrls.install_plan}
              onChange={(e) => setTestUrls(prev => ({ ...prev, install_plan: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Google Drive URL for Install Plan"
            />
          </div>
        </div>

        {/* Run Validation Button */}
        <button
          onClick={runComprehensiveValidation}
          disabled={validationState.isRunning}
          className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-colors ${
            validationState.isRunning
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700'
          }`}
        >
          {validationState.isRunning ? '🔄 Running Validation...' : '🚀 Run Comprehensive Validation'}
        </button>
      </div>

      {/* Customization Panel */}
      {showCustomization && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">⚙️ Validation Customization</h3>
          
          {/* Category Weights */}
          <div className="mb-6">
            <h4 className="text-lg font-semibold text-gray-800 mb-3">📊 Category Weights</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(customizationSettings.categoryWeights).map(([category, weight]) => (
                <div key={category} className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={customizationSettings.enabledCategories[category]}
                    onChange={() => toggleCategory(category)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="flex-1 text-sm font-medium text-gray-700">
                    {category}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="50"
                    value={weight}
                    onChange={(e) => updateCategoryWeight(category, parseInt(e.target.value))}
                    disabled={!customizationSettings.enabledCategories[category]}
                    className="w-20"
                  />
                  <span className="text-sm text-gray-600 w-8">{weight}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Validation Thresholds */}
          <div className="mb-6">
            <h4 className="text-lg font-semibold text-gray-800 mb-3">🎯 Validation Thresholds</h4>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pass Threshold</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={customizationSettings.validationThresholds.pass}
                  onChange={(e) => setCustomizationSettings(prev => ({
                    ...prev,
                    validationThresholds: {
                      ...prev.validationThresholds,
                      pass: parseInt(e.target.value)
                    }
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Warning Threshold</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={customizationSettings.validationThresholds.warning}
                  onChange={(e) => setCustomizationSettings(prev => ({
                    ...prev,
                    validationThresholds: {
                      ...prev.validationThresholds,
                      warning: parseInt(e.target.value)
                    }
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Fail Threshold</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={customizationSettings.validationThresholds.fail}
                  onChange={(e) => setCustomizationSettings(prev => ({
                    ...prev,
                    validationThresholds: {
                      ...prev.validationThresholds,
                      fail: parseInt(e.target.value)
                    }
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Progress Monitoring */}
      {validationState.progress && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">📈 Validation Progress</h3>
          
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Overall Progress</span>
              <span className="text-sm text-gray-600">
                {validationState.progress.steps_completed}/{validationState.progress.total_steps} steps
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-300 ${getProgressColor(validationState.progress.progress_percentage)}`}
                style={{ width: `${validationState.progress.progress_percentage}%` }}
              ></div>
            </div>
            <div className="flex justify-between items-center mt-2">
              <span className="text-sm text-gray-600">{validationState.progress.current_step}</span>
              <span className="text-sm font-medium text-gray-700">
                {Math.round(validationState.progress.progress_percentage)}%
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm text-blue-600 font-medium">Status</div>
              <div className={`text-lg font-bold ${getStatusColor(validationState.progress.status)}`}>
                {validationState.progress.status}
              </div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-sm text-green-600 font-medium">Start Time</div>
              <div className="text-lg font-bold text-green-800">
                {new Date(validationState.progress.start_time).toLocaleTimeString()}
              </div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-sm text-purple-600 font-medium">Validation ID</div>
              <div className="text-sm font-mono text-purple-800">
                {validationState.validationId?.substring(0, 8)}...
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Validation Results */}
      {validationState.results && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">📊 Validation Results</h3>
          
          {/* Overall Score */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-lg font-semibold text-gray-800">Overall Score</span>
              <span className="text-2xl font-bold text-blue-600">
                {validationState.results.overall_score}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className={`h-4 rounded-full ${getProgressColor(validationState.results.overall_score)}`}
                style={{ width: `${validationState.results.overall_score}%` }}
              ></div>
            </div>
          </div>

          {/* Category Scores */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {Object.entries(validationState.results.category_scores || {}).map(([category, score]) => (
              <div key={category} className="bg-gray-50 p-4 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">{category}</span>
                  <span className="text-lg font-bold text-gray-900">{score}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getProgressColor(score)}`}
                    style={{ width: `${score}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-600">
                {validationState.results.checks_completed}
              </div>
              <div className="text-sm text-blue-800">Checks Completed</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-600">
                {validationState.results.checks_passed}
              </div>
              <div className="text-sm text-green-800">Checks Passed</div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-red-600">
                {validationState.results.checks_failed}
              </div>
              <div className="text-sm text-red-800">Checks Failed</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-purple-600">
                {validationState.results.total_checks}
              </div>
              <div className="text-sm text-purple-800">Total Checks</div>
            </div>
          </div>

          {/* Issues and Recommendations */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Critical Issues */}
            <div className="bg-red-50 p-4 rounded-lg">
              <h4 className="text-lg font-semibold text-red-800 mb-3">
                🚨 Critical Issues ({validationState.results.critical_issues?.length || 0})
              </h4>
              <ul className="space-y-2">
                {(validationState.results.critical_issues || []).map((issue, index) => (
                  <li key={index} className="text-sm text-red-700">
                    • {issue}
                  </li>
                ))}
              </ul>
            </div>

            {/* Warnings */}
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h4 className="text-lg font-semibold text-yellow-800 mb-3">
                ⚠️ Warnings ({validationState.results.warnings?.length || 0})
              </h4>
              <ul className="space-y-2">
                {(validationState.results.warnings || []).map((warning, index) => (
                  <li key={index} className="text-sm text-yellow-700">
                    • {warning}
                  </li>
                ))}
              </ul>
            </div>

            {/* Recommendations */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="text-lg font-semibold text-blue-800 mb-3">
                💡 Recommendations ({validationState.results.recommendations?.length || 0})
              </h4>
              <ul className="space-y-2">
                {(validationState.results.recommendations || []).map((rec, index) => (
                  <li key={index} className="text-sm text-blue-700">
                    • {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Validation History */}
      {validationHistory.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">📚 Validation History</h3>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
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
                    Checks
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {validationHistory.map((validation) => (
                  <tr key={validation.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(validation.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getStatusColor(validation.status)}`}>
                        {validation.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {validation.score}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {validation.checks_completed}/{validation.total_checks}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500">
                      {validation.id.substring(0, 8)}...
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Error Display */}
      {validationState.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-red-400">❌</span>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Validation Error</h3>
              <div className="mt-2 text-sm text-red-700">
                {validationState.error}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComprehensiveValidation;

