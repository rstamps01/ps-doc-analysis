import React, { useState, useEffect } from 'react';
import './App.css';
import GoogleIntegration from './components/GoogleIntegration';
import ComprehensiveValidation from './components/ComprehensiveValidation';
import ResultsManagement from './components/ResultsManagement';
import AdvancedAnalytics from './components/AdvancedAnalytics';
import ExportManager from './components/ExportManager';
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('upload')
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [existingFiles, setExistingFiles] = useState([])
  const [uploadProgress, setUploadProgress] = useState({})
  const [isDragOver, setIsDragOver] = useState(false)
  const [validationResults, setValidationResults] = useState([])
  
  // Google Integration state
  const [driveUrl, setDriveUrl] = useState('')
  const [sheetsUrl, setSheetsUrl] = useState('')
  const [processing, setProcessing] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState({ drive: null, sheets: null })
  
  // Settings state
  const [credentialsText, setCredentialsText] = useState('')
  const [credentialsStatus, setCredentialsStatus] = useState(null)
  const [settingsLoading, setSettingsLoading] = useState(false)

  // Load existing files on component mount and when switching to upload tab
  useEffect(() => {
    if (activeTab === 'upload') {
      loadExistingFiles()
    }
  }, [activeTab])

  const loadExistingFiles = async () => {
    try {
      const response = await fetch('/api/documents/list')
      if (response.ok) {
        const result = await response.json()
        setExistingFiles(result.files || [])
        console.log('Loaded existing files:', result.files?.length || 0)
      } else {
        console.error('Failed to load existing files:', response.status)
      }
    } catch (error) {
      console.error('Error loading existing files:', error)
    }
  }

  // Test Google API connections
  const testConnections = async () => {
    setProcessing(true)
    try {
      const response = await fetch('/api/google/test-connection')
      const data = await response.json()
      setConnectionStatus(data.connections)
    } catch (error) {
      console.error('Connection test failed:', error)
    } finally {
      setProcessing(false)
    }
  }

  // Process Google Drive URL
  const processGoogleDriveUrl = async () => {
    if (!driveUrl.trim()) {
      alert('Please enter a Google Drive URL')
      return
    }

    setProcessing(true)
    try {
      const response = await fetch('/api/documents/process-google-drive', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: driveUrl }),
      })

      const data = await response.json()
      
      if (data.success) {
        const newFile = {
          id: data.file_id,
          name: data.filename,
          size: data.size,
          uploadTime: data.upload_time,
          status: 'ready',
          source: 'google_drive'
        }
        
        setUploadedFiles(prev => [...prev, newFile])
        setDriveUrl('')
        alert('Google Drive file processed successfully!')
        loadExistingFiles() // Refresh the files list
      } else {
        alert(`Error: ${data.error}`)
      }
    } catch (error) {
      console.error('Drive processing failed:', error)
      alert('Failed to process Google Drive URL')
    } finally {
      setProcessing(false)
    }
  }

  // Process Google Sheets URL
  const processGoogleSheetsUrl = async () => {
    if (!sheetsUrl.trim()) {
      alert('Please enter a Google Sheets URL')
      return
    }

    setProcessing(true)
    try {
      const response = await fetch('/api/documents/process-google-sheets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: sheetsUrl }),
      })

      const data = await response.json()
      
      if (data.success) {
        const newFile = {
          id: data.file_id,
          name: data.filename,
          uploadTime: data.upload_time,
          status: 'ready',
          source: 'google_sheets',
          requirementsCount: data.requirements_count
        }
        
        setUploadedFiles(prev => [...prev, newFile])
        setSheetsUrl('')
        alert('Google Sheets document processed successfully!')
        loadExistingFiles() // Refresh the files list
      } else {
        alert(`Error: ${data.error}`)
      }
    } catch (error) {
      console.error('Sheets processing failed:', error)
      alert('Failed to process Google Sheets URL')
    } finally {
      setProcessing(false)
    }
  }

  // Settings functions
  const loadCredentialsStatus = async () => {
    try {
      const response = await fetch('https://w5hni7c71de6.manus.space/api/settings/credentials/status')
      const data = await response.json()
      
      if (data.success) {
        setCredentialsStatus(data.status)
      }
    } catch (error) {
      console.error('Failed to load credentials status:', error)
    }
  }

  const uploadCredentials = async () => {
    if (!credentialsText.trim()) {
      alert('Please paste your Google service account credentials JSON')
      return
    }

    setSettingsLoading(true)
    try {
      const response = await fetch('https://w5hni7c71de6.manus.space/api/settings/credentials/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ credentials: credentialsText }),
      })

      const data = await response.json()
      
      if (data.success) {
        alert('Credentials saved successfully!')
        setCredentialsText('')
        loadCredentialsStatus()
        // Refresh connection status
        testConnections()
      } else {
        alert(`Error: ${data.error}`)
      }
    } catch (error) {
      console.error('Failed to upload credentials:', error)
      alert('Failed to save credentials')
    } finally {
      setSettingsLoading(false)
    }
  }

  const clearCredentials = async () => {
    if (!confirm('Are you sure you want to clear the stored credentials?')) {
      return
    }

    setSettingsLoading(true)
    try {
      const response = await fetch('https://w5hni7c71de6.manus.space/api/settings/credentials/clear', {
        method: 'DELETE'
      })

      const data = await response.json()
      
      if (data.success) {
        alert('Credentials cleared successfully!')
        setCredentialsStatus(null)
        setConnectionStatus({ drive: null, sheets: null })
      } else {
        alert(`Error: ${data.error}`)
      }
    } catch (error) {
      console.error('Failed to clear credentials:', error)
      alert('Failed to clear credentials')
    } finally {
      setSettingsLoading(false)
    }
  }

  const testCredentialsConnection = async () => {
    setSettingsLoading(true)
    try {
      const response = await fetch('https://w5hni7c71de6.manus.space/api/settings/credentials/test', {
        method: 'POST'
      })

      const data = await response.json()
      
      if (data.success) {
        setConnectionStatus(data.connections)
        alert('Connection test completed! Check the status indicators.')
      } else {
        alert(`Error: ${data.error}`)
      }
    } catch (error) {
      console.error('Failed to test credentials:', error)
      alert('Failed to test credentials')
    } finally {
      setSettingsLoading(false)
    }
  }

  // Load credentials status when settings tab is accessed
  useEffect(() => {
    if (activeTab === 'settings') {
      loadCredentialsStatus()
    }
  }, [activeTab])

  const deleteFile = async (fileId) => {
    try {
      console.log('Deleting file:', fileId)
      const response = await fetch(`/api/documents/delete/${fileId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        // Remove from existing files list
        setExistingFiles(prev => prev.filter(f => f.file_id !== fileId))
        // Remove from uploaded files list if present
        setUploadedFiles(prev => prev.filter(f => f.id !== fileId))
        console.log('File deleted successfully:', fileId)
      } else {
        const errorText = await response.text()
        console.error('Delete failed:', response.status, errorText)
        alert(`Failed to delete file: ${errorText}`)
      }
    } catch (error) {
      console.error('Delete error:', error)
      alert(`Error deleting file: ${error.message}`)
    }
  }

  const handleFileUpload = async (files) => {
    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      const fileId = `${Date.now()}_${i}_${file.name}`
      
      // Add file to uploaded files list immediately
      const newFile = {
        id: fileId,
        name: file.name,
        size: file.size,
        uploadTime: new Date().toLocaleString(),
        status: 'uploading',
        progress: 0
      }
      
      setUploadedFiles(prev => [...prev, newFile])
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }))
      
      // Create FormData
      const formData = new FormData()
      formData.append('file', file)
      
      try {
        console.log('Starting upload for:', file.name)
        
        // Simulate progress
        const progressInterval = setInterval(() => {
          setUploadProgress(prev => {
            const currentProgress = prev[fileId] || 0
            if (currentProgress < 90) {
              return { ...prev, [fileId]: currentProgress + 10 }
            }
            return prev
          })
        }, 100)
        
        const response = await fetch('/api/documents/upload', {
          method: 'POST',
          body: formData
        })
        
        clearInterval(progressInterval)
        
        if (response.ok) {
          const result = await response.json()
          console.log('Upload successful:', result)
          
          // Update file status
          setUploadedFiles(prev => 
            prev.map(f => 
              f.id === fileId 
                ? { ...f, status: 'completed', progress: 100, serverFileId: result.file_id }
                : f
            )
          )
          setUploadProgress(prev => ({ ...prev, [fileId]: 100 }))
          
          // Refresh existing files list
          loadExistingFiles()
        } else {
          const errorText = await response.text()
          console.error('Upload failed:', response.status, errorText)
          
          // Update file status to failed
          setUploadedFiles(prev => 
            prev.map(f => 
              f.id === fileId 
                ? { ...f, status: 'failed', error: errorText }
                : f
            )
          )
        }
      } catch (error) {
        console.error('Upload error:', error)
        
        // Update file status to failed
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === fileId 
              ? { ...f, status: 'failed', error: error.message }
              : f
          )
        )
      }
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragOver(false)
    const files = Array.from(e.dataTransfer.files)
    handleFileUpload(files)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleFileInputChange = (e) => {
    const files = Array.from(e.target.files)
    handleFileUpload(files)
    e.target.value = '' // Reset input
  }

  const validateFile = async (fileId) => {
    try {
      console.log('Starting validation for file:', fileId)
      
      const response = await fetch(`/api/documents/validate/${fileId}`, {
        method: 'POST'
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('Validation completed:', result)
        
        // Add to validation results
        setValidationResults(prev => [result.validation_results, ...prev])
        
        // Switch to results tab to show the results
        setActiveTab('results')
        
        alert(`Validation completed! Score: ${Math.round(result.validation_results.score * 100)}%`)
      } else {
        const errorText = await response.text()
        console.error('Validation failed:', response.status, errorText)
        alert(`Validation failed: ${errorText}`)
      }
    } catch (error) {
      console.error('Validation error:', error)
      alert(`Validation error: ${error.message}`)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'uploading': return '#3b82f6'
      case 'completed': return '#10b981'
      case 'failed': return '#ef4444'
      case 'ready': return '#8b5cf6'
      default: return '#6b7280'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'uploading': return '⏳'
      case 'completed': return '✅'
      case 'failed': return '❌'
      case 'ready': return '📄'
      default: return '📄'
    }
  }

  const getConnectionBadge = (connected) => {
    if (connected === null) return '🔍 Not Tested'
    return connected ? '✅ Connected' : '❌ Disconnected'
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <h1>📋 Enhanced Information Validation Tool</h1>
        <p>Automated validation for Site Survey and Install Plan documents</p>
        <div className="header-status">
          <span className="status-indicator">✅ API Operational</span>
          <span className="version-badge">v2.0 Enhanced</span>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="nav-tabs">
        <button 
          className={`nav-tab ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          📁 Document Upload
        </button>
        <button 
          className={`nav-tab ${activeTab === 'google' ? 'active' : ''}`}
          onClick={() => setActiveTab('google')}
        >
          🔗 Google Integration
        </button>
        <button 
          className={`nav-tab ${activeTab === 'comprehensive' ? 'active' : ''}`}
          onClick={() => setActiveTab('comprehensive')}
        >
          🔍 Comprehensive Validation
        </button>
        <button 
          className={`nav-tab ${activeTab === 'results-management' ? 'active' : ''}`}
          onClick={() => setActiveTab('results-management')}
        >
          📊 Results Management
        </button>
        <button 
          className={`nav-tab ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          📈 Advanced Analytics
        </button>
        <button 
          className={`nav-tab ${activeTab === 'export' ? 'active' : ''}`}
          onClick={() => setActiveTab('export')}
        >
          📤 Export Manager
        </button>
        <button 
          className={`nav-tab ${activeTab === 'results' ? 'active' : ''}`}
          onClick={() => setActiveTab('results')}
        >
          📊 Validation Results
        </button>
        <button 
          className={`nav-tab ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
        <button 
          className={`nav-tab ${activeTab === 'criteria' ? 'active' : ''}`}
          onClick={() => setActiveTab('criteria')}
        >
          📋 Validation Criteria
        </button>
      </nav>

      {/* Tab Content */}
      <main className="tab-content">
        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="upload-section">
            <h2>Upload Documents for Validation</h2>
            
            {/* Upload Area */}
            <div 
              className={`upload-area ${isDragOver ? 'drag-over' : ''}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => document.getElementById('file-input').click()}
            >
              <div className="upload-icon">📄</div>
              <p>Drop files here or click to upload</p>
              <small>Supports: PDF, XLSX, DOCX files (Site Survey Parts 1 & 2, Install Plans)</small>
              <input
                id="file-input"
                type="file"
                multiple
                accept=".pdf,.xlsx,.docx"
                onChange={handleFileInputChange}
                style={{ display: 'none' }}
              />
            </div>

            {/* Uploaded Files */}
            {uploadedFiles.length > 0 && (
              <div className="files-section">
                <h3>📤 Recently Uploaded ({uploadedFiles.length})</h3>
                <div className="files-list">
                  {uploadedFiles.map((file) => (
                    <div key={file.id} className="file-item">
                      <div className="file-info">
                        <div className="file-header">
                          <span className="file-icon">{getStatusIcon(file.status)}</span>
                          <span className="file-name">{file.name}</span>
                          <span className="file-source">
                            {file.source === 'google_drive' ? '🔗 Google Drive' : 
                             file.source === 'google_sheets' ? '📊 Google Sheets' : '💻 Upload'}
                          </span>
                        </div>
                        <div className="file-details">
                          {file.size && <span>{formatFileSize(file.size)}</span>}
                          {file.requirementsCount && <span>{file.requirementsCount} criteria</span>}
                          <span>{file.uploadTime}</span>
                          <span style={{ color: getStatusColor(file.status) }}>
                            {file.status}
                          </span>
                        </div>
                        {file.status === 'uploading' && (
                          <div className="progress-bar">
                            <div 
                              className="progress-fill" 
                              style={{ width: `${uploadProgress[file.id] || 0}%` }}
                            ></div>
                          </div>
                        )}
                        {file.error && (
                          <div className="error-message">❌ {file.error}</div>
                        )}
                      </div>
                      <div className="file-actions">
                        {(file.status === 'completed' || file.status === 'ready') && (
                          <button 
                            className="btn btn-primary"
                            onClick={() => validateFile(file.serverFileId || file.id)}
                          >
                            🔍 Validate
                          </button>
                        )}
                        <button 
                          className="btn btn-danger"
                          onClick={() => deleteFile(file.serverFileId || file.id)}
                        >
                          🗑️ Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Existing Files */}
            {existingFiles.length > 0 && (
              <div className="files-section">
                <h3>💾 Existing Files ({existingFiles.length})</h3>
                <div className="files-list">
                  {existingFiles.map((file) => (
                    <div key={file.file_id} className="file-item">
                      <div className="file-info">
                        <div className="file-header">
                          <span className="file-icon">📄</span>
                          <span className="file-name">{file.filename}</span>
                        </div>
                        <div className="file-details">
                          <span>{formatFileSize(file.size)}</span>
                          <span>{file.upload_time}</span>
                        </div>
                      </div>
                      <div className="file-actions">
                        <button 
                          className="btn btn-primary"
                          onClick={() => validateFile(file.file_id)}
                        >
                          🔍 Validate
                        </button>
                        <button 
                          className="btn btn-danger"
                          onClick={() => deleteFile(file.file_id)}
                        >
                          🗑️ Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Google Integration Tab */}
        {activeTab === 'google' && (
          <div className="google-section">
            <h2>🔗 Google Integration</h2>
            <p>Process documents from Google Drive and Google Sheets</p>

            {/* Connection Status */}
            <div className="connection-status">
              <h3>📡 Connection Status</h3>
              <div className="status-grid">
                <div className="status-item">
                  <span>🔗 Google Drive:</span>
                  <span>{getConnectionBadge(connectionStatus.drive?.connected)}</span>
                </div>
                <div className="status-item">
                  <span>📊 Google Sheets:</span>
                  <span>{getConnectionBadge(connectionStatus.sheets?.connected)}</span>
                </div>
              </div>
              <button 
                className="btn btn-secondary"
                onClick={testConnections}
                disabled={processing}
              >
                {processing ? '⏳ Testing...' : '🔄 Test Connections'}
              </button>
            </div>

            {/* Google Drive Section */}
            <div className="google-drive-section">
              <h3>🔗 Google Drive Documents</h3>
              <p>Process PDF, XLSX, DOCX files from Google Drive</p>
              <div className="url-input-group">
                <input
                  type="url"
                  placeholder="https://drive.google.com/file/d/..."
                  value={driveUrl}
                  onChange={(e) => setDriveUrl(e.target.value)}
                  className="url-input"
                />
                <button 
                  className="btn btn-primary"
                  onClick={processGoogleDriveUrl}
                  disabled={processing || !driveUrl.trim()}
                >
                  {processing ? '⏳ Processing...' : '🔗 Process'}
                </button>
              </div>
              <small>⚠️ Ensure the file is shared with appropriate permissions</small>
            </div>

            {/* Google Sheets Section */}
            <div className="google-sheets-section">
              <h3>📊 Google Sheets Documents</h3>
              <p>Process Site Survey documents and validation criteria</p>
              <div className="url-input-group">
                <input
                  type="url"
                  placeholder="https://docs.google.com/spreadsheets/d/..."
                  value={sheetsUrl}
                  onChange={(e) => setSheetsUrl(e.target.value)}
                  className="url-input"
                />
                <button 
                  className="btn btn-primary"
                  onClick={processGoogleSheetsUrl}
                  disabled={processing || !sheetsUrl.trim()}
                >
                  {processing ? '⏳ Processing...' : '📊 Process'}
                </button>
              </div>
              <small>⚠️ Ensure the sheet is shared with appropriate permissions</small>
            </div>
          </div>
        )}

        {/* Comprehensive Validation Tab */}
        {activeTab === 'comprehensive' && (
          <ComprehensiveValidation />
        )}

        {/* Results Management Tab */}
        {activeTab === 'results-management' && (
          <ResultsManagement />
        )}

        {/* Advanced Analytics Tab */}
        {activeTab === 'analytics' && (
          <AdvancedAnalytics />
        )}

        {/* Export Manager Tab */}
        {activeTab === 'export' && (
          <ExportManager />
        )}

        {/* Results Tab */}
        {activeTab === 'results' && (
          <div className="results-section">
            <h2>📊 Validation Results</h2>
            {validationResults.length === 0 ? (
              <div className="empty-state">
                <p>No validation results yet. Upload and validate documents to see results here.</p>
              </div>
            ) : (
              <div className="results-list">
                {validationResults.map((result, index) => (
                  <div key={index} className="result-item">
                    <div className="result-header">
                      <h3>{result.filename || 'Document'}</h3>
                      <div className="result-score">
                        <span className={`score ${result.status}`}>
                          {Math.round(result.score * 100)}%
                        </span>
                        <span className={`status ${result.status}`}>
                          {result.status.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    
                    <div className="result-details">
                      <p><strong>Processed:</strong> {result.processed_time}</p>
                      
                      {result.categories && (
                        <div className="categories">
                          <h4>📋 Category Breakdown:</h4>
                          {result.categories.map((cat, catIndex) => (
                            <div key={catIndex} className="category-item">
                              <span className="category-name">{cat.name}</span>
                              <span className="category-score">
                                {cat.passed}/{cat.total} passed
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {result.issues && result.issues.length > 0 && (
                        <div className="issues">
                          <h4>⚠️ Issues Found:</h4>
                          <ul>
                            {result.issues.map((issue, issueIndex) => (
                              <li key={issueIndex}>{issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="settings-section">
            <h2>⚙️ Settings</h2>
            <p>Configure Google API credentials for Drive and Sheets integration</p>

            {/* Current Status */}
            <div className="credentials-status">
              <h3>📊 Current Status</h3>
              {credentialsStatus ? (
                <div className="status-info">
                  <div className="status-item">
                    <span>✅ Credentials:</span>
                    <span>Configured</span>
                  </div>
                  <div className="status-item">
                    <span>🏢 Project ID:</span>
                    <span>{credentialsStatus.project_id || 'Not available'}</span>
                  </div>
                  <div className="status-item">
                    <span>📧 Service Account:</span>
                    <span>{credentialsStatus.client_email || 'Not available'}</span>
                  </div>
                </div>
              ) : (
                <div className="status-info">
                  <div className="status-item">
                    <span>❌ Credentials:</span>
                    <span>Not configured</span>
                  </div>
                </div>
              )}
            </div>

            {/* Connection Status */}
            <div className="connection-status">
              <h3>📡 API Connection Status</h3>
              <div className="status-grid">
                <div className="status-item">
                  <span>🔗 Google Drive:</span>
                  <span>{getConnectionBadge(connectionStatus.drive?.connected)}</span>
                </div>
                <div className="status-item">
                  <span>📊 Google Sheets:</span>
                  <span>{getConnectionBadge(connectionStatus.sheets?.connected)}</span>
                </div>
              </div>
              <button 
                className="btn btn-secondary"
                onClick={testCredentialsConnection}
                disabled={settingsLoading || !credentialsStatus?.has_credentials}
              >
                {settingsLoading ? '⏳ Testing...' : '🔄 Test Connection'}
              </button>
            </div>

            {/* Credentials Upload */}
            <div className="credentials-upload">
              <h3>🔑 Google Service Account Credentials</h3>
              <p>Paste your Google Cloud service account JSON credentials below:</p>
              
              <div className="credentials-input">
                <textarea
                  placeholder="Paste your service account JSON here..."
                  value={credentialsText}
                  onChange={(e) => setCredentialsText(e.target.value)}
                  rows={10}
                  className="credentials-textarea"
                />
              </div>
              
              <div className="credentials-actions">
                <button 
                  className="btn btn-primary"
                  onClick={uploadCredentials}
                  disabled={settingsLoading || !credentialsText.trim()}
                >
                  {settingsLoading ? '⏳ Saving...' : '💾 Save Credentials'}
                </button>
                
                {credentialsStatus?.has_credentials && (
                  <button 
                    className="btn btn-danger"
                    onClick={clearCredentials}
                    disabled={settingsLoading}
                  >
                    {settingsLoading ? '⏳ Clearing...' : '🗑️ Clear Credentials'}
                  </button>
                )}
              </div>
            </div>

            {/* Instructions */}
            <div className="credentials-instructions">
              <h3>📋 Setup Instructions</h3>
              <ol>
                <li>Go to the <a href="https://console.cloud.google.com/" target="_blank" rel="noopener noreferrer">Google Cloud Console</a></li>
                <li>Create a new project or select an existing one</li>
                <li>Enable the Google Drive API and Google Sheets API</li>
                <li>Create a service account in IAM & Admin → Service Accounts</li>
                <li>Generate a JSON key for the service account</li>
                <li>Copy the entire JSON content and paste it above</li>
                <li>Share your Google Drive files/folders with the service account email</li>
              </ol>
              
              <div className="warning-box">
                <p>⚠️ <strong>Important:</strong> Your credentials are stored securely and only used for API access. Make sure to share your Google Drive files and Sheets with the service account email address.</p>
              </div>
            </div>
          </div>
        )}

        {/* Criteria Tab */}
        {activeTab === 'criteria' && (
          <div className="criteria-section">
            <h2>📋 Validation Criteria</h2>
            <div className="criteria-overview">
              <div className="criteria-stats">
                <div className="stat-item">
                  <span className="stat-number">65</span>
                  <span className="stat-label">Total Criteria</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">8</span>
                  <span className="stat-label">Categories</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">42</span>
                  <span className="stat-label">Enhanced Checks</span>
                </div>
              </div>
              
              <div className="criteria-categories">
                <h3>📂 Validation Categories:</h3>
                <div className="category-grid">
                  <div className="category-card">
                    <h4>🏢 Basic Project Information</h4>
                    <p>Project name, opportunity ID, customer details, timeline, approvals</p>
                    <span className="category-count">6 criteria</span>
                  </div>
                  <div className="category-card">
                    <h4>🔗 SFDC & Documentation Integration</h4>
                    <p>Salesforce integration and documentation links</p>
                    <span className="category-count">2 criteria</span>
                  </div>
                  <div className="category-card">
                    <h4>📄 Template & Documentation Standards</h4>
                    <p>Template compliance and documentation standards</p>
                    <span className="category-count">2 criteria</span>
                  </div>
                  <div className="category-card">
                    <h4>⚙️ Installation Plan Content Validation</h4>
                    <p>Installation procedures and technical specifications</p>
                    <span className="category-count">6 criteria</span>
                  </div>
                  <div className="category-card">
                    <h4>🌐 Network Configuration & Technical</h4>
                    <p>Network setup, IP addressing, VLAN configuration</p>
                    <span className="category-count">9 criteria</span>
                  </div>
                  <div className="category-card">
                    <h4>📋 Site Survey Documentation</h4>
                    <p>Site survey completeness and accuracy</p>
                    <span className="category-count">12 criteria</span>
                  </div>
                  <div className="category-card">
                    <h4>🔄 Cross-Document Consistency</h4>
                    <p>Consistency between Site Survey parts and Install Plan</p>
                    <span className="category-count">15 criteria</span>
                  </div>
                  <div className="category-card">
                    <h4>✨ Enhanced Features</h4>
                    <p>Advanced validation and quality checks</p>
                    <span className="category-count">13 criteria</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App

