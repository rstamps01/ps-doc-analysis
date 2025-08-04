import React, { useState, useEffect } from 'react';

const ExportManager = () => {
  const [validationHistory, setValidationHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedValidations, setSelectedValidations] = useState([]);
  const [exportFormat, setExportFormat] = useState('pdf');
  const [customTemplate, setCustomTemplate] = useState({
    include_sections: {
      categimport React, { useState, useEffect } from 'react';
import { API_BASE_URL, apiRequest, buildApiUrl } from '../config/apiConfig';


  useEffect(() => {
    loadValidationHistory();
  }, []);

  const loadValidationHistory = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/results/history`);
      const result = await response.json();
      
      if (result.status === 'success') {
        setValidationHistory(result.validation_history || []);
      } else {
        console.error('Failed to load validation history:', result.message);
      }
    } catch (error) {
      console.error('Error loading validation history:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportSingleValidation = async (validationId, format) => {
    try {
      setLoading(true);
      
      let endpoint;
      let filename;
      
      switch (format) {
        case 'pdf':
          endpoint = `/api/export/validation/pdf/${validationId}`;
          filename = `validation_report_${validationId}.pdf`;
          break;
        case 'excel':
          endpoint = `/api/export/validation/excel/${validationId}`;
          filename = `validation_results_${validationId}.xlsx`;
          break;
        case 'csv':
          endpoint = `/api/export/validation/csv/${validationId}?type=summary`;
          filename = `validation_summary_${validationId}.csv`;
          break;
        default:
          throw new Error(`Unsupported format: ${format}`);
      }
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      
      if (!response.ok) {
        throw new Error(`Export failed: ${response.statusText}`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      alert(`${format.toUpperCase()} export completed successfully!`);
      
    } catch (error) {
      console.error('Error exporting validation:', error);
      alert(`Export failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const exportBatchValidations = async () => {
    if (selectedValidations.length === 0) {
      alert('Please select at least one validation to export.');
      return;
    }

    try {
      setLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/api/export/batch/validations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          validation_ids: selectedValidations,
          format: exportFormat
        })
      });
      
      if (!response.ok) {
        throw new Error(`Batch export failed: ${response.statusText}`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `batch_validation_${exportFormat}_${selectedValidations.length}_items.${exportFormat === 'excel' ? 'xlsx' : exportFormat}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      alert(`Batch ${exportFormat.toUpperCase()} export completed successfully!`);
      setSelectedValidations([]);
      
    } catch (error) {
      console.error('Error exporting batch:', error);
      alert(`Batch export failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const exportCustomTemplate = async (validationId) => {
    try {
      setLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/api/export/template/custom`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          validation_id: validationId,
          template_config: customTemplate,
          format: exportFormat
        })
      });
      
      if (!response.ok) {
        throw new Error(`Custom export failed: ${response.statusText}`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `custom_validation_${validationId}.${exportFormat === 'excel' ? 'xlsx' : exportFormat}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      alert(`Custom ${exportFormat.toUpperCase()} export completed successfully!`);
      
    } catch (error) {
      console.error('Error exporting custom template:', error);
      alert(`Custom export failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const exportTrendsReport = async () => {
    try {
      setLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/api/export/trends/pdf?days=30`);
      
      if (!response.ok) {
        throw new Error(`Trends export failed: ${response.statusText}`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'trends_report_30days.pdf';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      alert('Trends report exported successfully!');
      
    } catch (error) {
      console.error('Error exporting trends report:', error);
      alert(`Trends export failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const toggleValidationSelection = (validationId) => {
    setSelectedValidations(prev => 
      prev.includes(validationId) 
        ? prev.filter(id => id !== validationId)
        : [...prev, validationId]
    );
  };

  const selectAllValidations = () => {
    if (selectedValidations.length === validationHistory.length) {
      setSelectedValidations([]);
    } else {
      setSelectedValidations(validationHistory.map(v => v.id));
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Export Manager</h2>
          <p className="text-gray-600">Export validation results in multiple formats</p>
        </div>
        
        <button 
          onClick={exportTrendsReport}
          className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded"
          disabled={loading}
        >
          📈 Export Trends Report
        </button>
      </div>

      {/* Export Format Selection */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Export Settings</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Format Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Export Format</label>
            <select 
              value={exportFormat} 
              onChange={(e) => setExportFormat(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="pdf">📄 PDF Report</option>
              <option value="excel">📊 Excel Workbook</option>
              <option value="csv">📋 CSV Data</option>
            </select>
          </div>

          {/* Batch Export */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Batch Export</label>
            <button 
              onClick={exportBatchValidations}
              className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              disabled={loading || selectedValidations.length === 0}
            >
              Export Selected ({selectedValidations.length})
            </button>
          </div>

          {/* Select All */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Selection</label>
            <button 
              onClick={selectAllValidations}
              className="w-full bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
            >
              {selectedValidations.length === validationHistory.length ? 'Deselect All' : 'Select All'}
            </button>
          </div>
        </div>
      </div>

      {/* Custom Template Configuration */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Custom Export Template</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Minimum Severity</label>
            <select 
              value={customTemplate.include_sections.min_severity} 
              onChange={(e) => setCustomTemplate(prev => ({
                ...prev,
                include_sections: {
                  ...prev.include_sections,
                  min_severity: e.target.value
                }
              }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="low">Low and above</option>
              <option value="medium">Medium and above</option>
              <option value="high">High and above</option>
              <option value="critical">Critical only</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Template Note</label>
            <p className="text-sm text-gray-600 p-2 bg-gray-50 rounded">
              Custom templates filter content based on severity and selected categories.
            </p>
          </div>
        </div>
      </div>

      {/* Validation History Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Validation History</h3>
          <p className="text-sm text-gray-600">Select validations to export individually or in batch</p>
        </div>
        
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <span className="ml-3">Loading validation history...</span>
          </div>
        ) : validationHistory.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No validation history available</p>
            <button 
              onClick={loadValidationHistory}
              className="mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              Refresh
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <input
                      type="checkbox"
                      checked={selectedValidations.length === validationHistory.length && validationHistory.length > 0}
                      onChange={selectAllValidations}
                      className="rounded"
                    />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Validation ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {validationHistory.map((validation) => (
                  <tr key={validation.id} className={selectedValidations.includes(validation.id) ? 'bg-blue-50' : ''}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        checked={selectedValidations.includes(validation.id)}
                        onChange={() => toggleValidationSelection(validation.id)}
                        className="rounded"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {validation.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        validation.overall_score >= 90 ? 'bg-green-100 text-green-800' :
                        validation.overall_score >= 80 ? 'bg-yellow-100 text-yellow-800' :
                        validation.overall_score >= 70 ? 'bg-orange-100 text-orange-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {validation.overall_score?.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        validation.status === 'completed' ? 'bg-green-100 text-green-800' :
                        validation.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {validation.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(validation.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      <button
                        onClick={() => exportSingleValidation(validation.id, 'pdf')}
                        className="text-red-600 hover:text-red-900"
                        disabled={loading}
                        title="Export as PDF"
                      >
                        📄
                      </button>
                      <button
                        onClick={() => exportSingleValidation(validation.id, 'excel')}
                        className="text-green-600 hover:text-green-900"
                        disabled={loading}
                        title="Export as Excel"
                      >
                        📊
                      </button>
                      <button
                        onClick={() => exportSingleValidation(validation.id, 'csv')}
                        className="text-blue-600 hover:text-blue-900"
                        disabled={loading}
                        title="Export as CSV"
                      >
                        📋
                      </button>
                      <button
                        onClick={() => exportCustomTemplate(validation.id)}
                        className="text-purple-600 hover:text-purple-900"
                        disabled={loading}
                        title="Export with Custom Template"
                      >
                        ⚙️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Export Status */}
      {loading && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
            <span className="ml-3 text-blue-700">Processing export request...</span>
          </div>
        </div>
      )}

      {/* Export Information */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Export Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">📄 PDF Reports</h4>
            <ul className="text-gray-600 space-y-1">
              <li>• Formatted reports with charts</li>
              <li>• Executive summaries</li>
              <li>• Detailed issue analysis</li>
              <li>• Professional presentation</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-700 mb-2">📊 Excel Workbooks</h4>
            <ul className="text-gray-600 space-y-1">
              <li>• Multiple sheets with data</li>
              <li>• Charts and visualizations</li>
              <li>• Raw data for analysis</li>
              <li>• Formulas and calculations</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-700 mb-2">📋 CSV Data</h4>
            <ul className="text-gray-600 space-y-1">
              <li>• Lightweight data export</li>
              <li>• Easy import to other tools</li>
              <li>• Summary, categories, or issues</li>
              <li>• Analysis-ready format</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportManager;

