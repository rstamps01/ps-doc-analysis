import React, { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('upload')
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [existingFiles, setExistingFiles] = useState([])
  const [uploadProgress, setUploadProgress] = useState({})
  const [isDragOver, setIsDragOver] = useState(false)
  const [validationResults, setValidationResults] = useState([])

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
        
        console.log('Upload response status:', response.status)
        
        if (response.ok) {
          const result = await response.json()
          console.log('Upload success:', result)
          
          // Update file with actual server response
          setUploadedFiles(prev => prev.map(f => 
            f.id === fileId ? {
              ...f,
              id: result.file_id || fileId,
              status: 'uploaded',
              uploadTime: result.upload_time ? new Date(result.upload_time).toLocaleString() : f.uploadTime,
              progress: 100
            } : f
          ))
          
          setUploadProgress(prev => ({ ...prev, [fileId]: 100 }))
          
          // Clear progress after 2 seconds
          setTimeout(() => {
            setUploadProgress(prev => {
              const newProgress = { ...prev }
              delete newProgress[fileId]
              return newProgress
            })
          }, 2000)
          
        } else {
          const errorText = await response.text()
          console.error('Upload failed:', response.status, errorText)
          
          // Update file status to failed
          setUploadedFiles(prev => prev.map(f => 
            f.id === fileId ? { 
              ...f, 
              status: 'failed', 
              error: `Upload failed (${response.status}): ${errorText}` 
            } : f
          ))
          
          setUploadProgress(prev => {
            const newProgress = { ...prev }
            delete newProgress[fileId]
            return newProgress
          })
        }
      } catch (error) {
        console.error('Upload error:', error)
        
        // Update file status to failed
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileId ? { 
            ...f, 
            status: 'failed', 
            error: `Network error: ${error.message}` 
          } : f
        ))
        
        setUploadProgress(prev => {
          const newProgress = { ...prev }
          delete newProgress[fileId]
          return newProgress
        })
      }
    }
  }

  const handleValidate = async (fileId) => {
    console.log('Starting validation for file:', fileId)
    
    // Update file status to processing
    setUploadedFiles(prev => prev.map(f => 
      f.id === fileId ? { ...f, status: 'processing' } : f
    ))
    
    try {
      const response = await fetch(`/api/documents/validate/${fileId}`, {
        method: 'POST'
      })
      
      console.log('Validation response status:', response.status)
      
      if (response.ok) {
        const result = await response.json()
        console.log('Validation success:', result)
        
        // Update file status to completed
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileId ? { ...f, status: 'completed' } : f
        ))
        
        // Add to validation results
        setValidationResults(prev => [...prev, result.validation_results])
        
        // Switch to results tab
        setActiveTab('results')
        
      } else {
        const errorText = await response.text()
        console.error('Validation failed:', response.status, errorText)
        
        // Update file status to failed
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileId ? { 
            ...f, 
            status: 'failed', 
            error: `Validation failed (${response.status}): ${errorText}` 
          } : f
        ))
      }
    } catch (error) {
      console.error('Validation error:', error)
      
      // Update file status to failed
      setUploadedFiles(prev => prev.map(f => 
        f.id === fileId ? { 
          ...f, 
          status: 'failed', 
          error: `Validation error: ${error.message}` 
        } : f
      ))
    }
  }

  const handleInputChange = (event) => {
    const files = event.target.files
    if (files && files.length > 0) {
      handleFileUpload(files)
    }
  }

  const handleDragOver = (event) => {
    event.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (event) => {
    event.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragOver(false)
    
    const files = event.dataTransfer.files
    if (files && files.length > 0) {
      handleFileUpload(files)
    }
  }

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId))
    setUploadProgress(prev => {
      const newProgress = { ...prev }
      delete newProgress[fileId]
      return newProgress
    })
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
      case 'uploading': return 'text-blue-600'
      case 'uploaded': return 'text-green-600'
      case 'processing': return 'text-purple-600'
      case 'completed': return 'text-green-600'
      case 'failed': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusBadge = (status) => {
    const colors = {
      'passed': 'bg-green-100 text-green-800',
      'partial': 'bg-yellow-100 text-yellow-800',
      'failed': 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Enhanced Information Validation Tool</h1>
              <p className="text-sm text-gray-600">Automated validation for Site Survey and Install Plan documents</p>
            </div>
            <div className="flex space-x-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                ✅ API Operational
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                v2.0 Enhanced
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('upload')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'upload'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📁 Document Upload
            </button>
            <button
              onClick={() => setActiveTab('results')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'results'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📊 Validation Results
            </button>
            <button
              onClick={() => setActiveTab('criteria')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'criteria'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📋 Validation Criteria
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'upload' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Upload Documents for Validation</h2>
              
              {/* Upload Area */}
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  isDragOver
                    ? 'border-blue-400 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-input').click()}
              >
                <div className="text-6xl mb-4">📄</div>
                <p className="text-lg text-gray-600 mb-2">
                  {isDragOver ? 'Drop files here!' : 'Drop files here or click to upload'}
                </p>
                <p className="text-sm text-gray-500">
                  Supports: PDF, XLSX, DOCX files (Site Survey Parts 1 & 2, Install Plans)
                </p>
                <input
                  id="file-input"
                  type="file"
                  multiple
                  accept=".pdf,.xlsx,.docx"
                  onChange={handleInputChange}
                  className="hidden"
                />
              </div>
            </div>

            {/* Uploaded Files */}
            {uploadedFiles.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Recently Uploaded Files ({uploadedFiles.length})
                </h3>
                <div className="space-y-3">
                  {uploadedFiles.map((file) => (
                    <div key={file.id} className="bg-white p-4 rounded-lg shadow border">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="text-2xl">📄</div>
                          <div>
                            <p className="font-medium text-gray-900">{file.name}</p>
                            <p className="text-sm text-gray-500">
                              {formatFileSize(file.size)} • {file.uploadTime}
                            </p>
                            {file.error && (
                              <p className="text-sm text-red-600 mt-1">
                                Error: {file.error}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className={`text-sm font-medium ${getStatusColor(file.status)}`}>
                            {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                          </span>
                          {file.status === 'uploaded' && (
                            <button
                              onClick={() => handleValidate(file.id)}
                              className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                            >
                              Validate
                            </button>
                          )}
                          <button
                            onClick={() => removeFile(file.id)}
                            className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                      {uploadProgress[file.id] !== undefined && (
                        <div className="mt-3">
                          <div className="bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${uploadProgress[file.id]}%` }}
                            ></div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {uploadProgress[file.id]}% uploaded
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Existing Files */}
            {existingFiles.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  All Files in Upload Directory ({existingFiles.length})
                </h3>
                <div className="space-y-3">
                  {existingFiles.map((file) => (
                    <div key={file.file_id} className="bg-gray-50 p-4 rounded-lg border">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="text-2xl">📄</div>
                          <div>
                            <p className="font-medium text-gray-900">{file.filename}</p>
                            <p className="text-sm text-gray-500">
                              {formatFileSize(file.size)} • {new Date(file.upload_time).toLocaleString()}
                            </p>
                            <p className="text-xs text-gray-400">
                              File ID: {file.file_id}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className="text-sm font-medium text-green-600">
                            Stored
                          </span>
                          <button
                            onClick={() => handleValidate(file.file_id)}
                            className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                          >
                            Validate
                          </button>
                          <button
                            onClick={() => deleteFile(file.file_id)}
                            className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'results' && (
          <div className="space-y-6">
            <h2 className="text-lg font-medium text-gray-900">Validation Results</h2>
            
            {validationResults.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📊</div>
                <p className="text-gray-500">No validation results yet. Upload and validate documents to see results here.</p>
              </div>
            ) : (
              <div className="space-y-6">
                {validationResults.map((result, index) => (
                  <div key={index} className="bg-white p-6 rounded-lg shadow border">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium text-gray-900">{result.filename}</h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadge(result.status)}`}>
                        {result.status.toUpperCase()}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {Math.round(result.score * 100)}%
                        </div>
                        <div className="text-sm text-gray-500">Overall Score</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          {result.passed_criteria}
                        </div>
                        <div className="text-sm text-gray-500">Criteria Passed</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-600">
                          {result.total_criteria}
                        </div>
                        <div className="text-sm text-gray-500">Total Criteria</div>
                      </div>
                    </div>

                    {result.categories && (
                      <div className="mb-6">
                        <h4 className="font-medium text-gray-900 mb-3">Category Breakdown</h4>
                        <div className="space-y-2">
                          {result.categories.map((category, catIndex) => (
                            <div key={catIndex} className="flex items-center justify-between">
                              <span className="text-sm text-gray-700">{category.name}</span>
                              <div className="flex items-center space-x-2">
                                <span className="text-sm text-gray-600">
                                  {category.passed}/{category.total}
                                </span>
                                <div className="w-20 bg-gray-200 rounded-full h-2">
                                  <div
                                    className="bg-green-600 h-2 rounded-full"
                                    style={{ width: `${(category.passed / category.total) * 100}%` }}
                                  ></div>
                                </div>
                                <span className="text-sm font-medium text-gray-900 w-12">
                                  {Math.round((category.passed / category.total) * 100)}%
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {result.strengths && result.strengths.length > 0 && (
                      <div className="mb-4">
                        <h4 className="font-medium text-gray-900 mb-2">✅ Strengths</h4>
                        <ul className="list-disc list-inside space-y-1">
                          {result.strengths.map((strength, i) => (
                            <li key={i} className="text-sm text-green-700">{strength}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {result.issues && result.issues.length > 0 && (
                      <div className="mb-4">
                        <h4 className="font-medium text-gray-900 mb-2">⚠️ Issues Found</h4>
                        <ul className="list-disc list-inside space-y-1">
                          {result.issues.map((issue, i) => (
                            <li key={i} className="text-sm text-red-700">{issue}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {result.recommendations && result.recommendations.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">💡 Recommendations</h4>
                        <ul className="list-disc list-inside space-y-1">
                          {result.recommendations.map((rec, i) => (
                            <li key={i} className="text-sm text-blue-700">{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'criteria' && (
          <div className="space-y-6">
            <h2 className="text-lg font-medium text-gray-900">Enhanced Validation Criteria (65 Total)</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow border">
                <h3 className="font-medium text-gray-900 mb-3">📋 Basic Project Information (6)</h3>
                <p className="text-sm text-gray-600">Project name, opportunity ID, customer details, timeline, approvals</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow border">
                <h3 className="font-medium text-gray-900 mb-3">🔗 SFDC & Documentation Integration (2)</h3>
                <p className="text-sm text-gray-600">Salesforce integration and documentation links</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow border">
                <h3 className="font-medium text-gray-900 mb-3">📄 Template & Documentation Standards (2)</h3>
                <p className="text-sm text-gray-600">Template compliance and documentation standards</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow border">
                <h3 className="font-medium text-gray-900 mb-3">⚙️ Installation Plan Content Validation (6)</h3>
                <p className="text-sm text-gray-600">Installation procedures and technical specifications</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow border">
                <h3 className="font-medium text-gray-900 mb-3">🌐 Network Configuration & Technical (9)</h3>
                <p className="text-sm text-gray-600">Network setup, VLAN configuration, IP addressing</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow border">
                <h3 className="font-medium text-gray-900 mb-3">🏢 Site Survey Documentation (12)</h3>
                <p className="text-sm text-gray-600">Physical site requirements and constraints</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow border">
                <h3 className="font-medium text-gray-900 mb-3">🔄 Cross-Document Consistency (15)</h3>
                <p className="text-sm text-gray-600">Consistency between Site Survey parts and Install Plan</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow border">
                <h3 className="font-medium text-gray-900 mb-3">⚡ Enhanced Features (13)</h3>
                <p className="text-sm text-gray-600">Advanced validation capabilities</p>
              </div>
            </div>

            <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
              <h3 className="font-medium text-blue-900 mb-3">🚀 Enhanced Capabilities</h3>
              <ul className="space-y-2 text-sm text-blue-800">
                <li>• Conditional Logic Processing</li>
                <li>• Cross-Document Validation</li>
                <li>• Automation Complexity Classification</li>
                <li>• Confidence Scoring</li>
                <li>• Real-Time Accuracy Monitoring</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

