import { useState, useRef } from 'react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('upload')
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [validationResults, setValidationResults] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [isDragOver, setIsDragOver] = useState(false)
  const [uploadProgress, setUploadProgress] = useState({})
  const fileInputRef = useRef(null)

  const handleFileUpload = async (files) => {
    const fileArray = Array.from(files)
    
    for (const file of fileArray) {
      const fileId = `temp_${Date.now()}_${file.name}`
      
      // Add file to list immediately with uploading status
      const newFile = {
        id: fileId,
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'uploading',
        uploadTime: new Date().toLocaleString(),
        progress: 0
      }
      setUploadedFiles(prev => [...prev, newFile])
      
      const formData = new FormData()
      formData.append('file', file)
      
      try {
        // Simulate upload progress
        setUploadProgress(prev => ({ ...prev, [fileId]: 0 }))
        
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
          
          // Update file with actual server response
          setUploadedFiles(prev => prev.map(f => 
            f.id === fileId ? {
              ...f,
              id: result.file_id,
              status: 'uploaded',
              uploadTime: new Date(result.upload_time).toLocaleString(),
              progress: 100
            } : f
          ))
          
          setUploadProgress(prev => ({ ...prev, [fileId]: 100 }))
          
          // Show success message briefly
          setTimeout(() => {
            setUploadProgress(prev => {
              const newProgress = { ...prev }
              delete newProgress[fileId]
              return newProgress
            })
          }, 2000)
          
        } else {
          const errorText = await response.text()
          console.error('Upload failed:', errorText)
          
          // Update file status to failed
          setUploadedFiles(prev => prev.map(f => 
            f.id === fileId ? { ...f, status: 'failed', error: errorText } : f
          ))
        }
      } catch (error) {
        console.error('Upload error:', error)
        
        // Update file status to failed
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileId ? { ...f, status: 'failed', error: error.message } : f
        ))
      }
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

  const handleValidation = async (fileId) => {
    setIsProcessing(true)
    const file = uploadedFiles.find(f => f.id === fileId)
    
    // Update file status to processing
    setUploadedFiles(prev => prev.map(f => 
      f.id === fileId ? { ...f, status: 'processing' } : f
    ))

    try {
      const response = await fetch(`/api/documents/validate/${fileId}`, {
        method: 'POST'
      })
      
      if (response.ok) {
        const result = await response.json()
        const validationData = result.validation_results
        
        const newResult = {
          id: Date.now(),
          fileName: validationData.filename,
          fileId: fileId,
          totalCriteria: validationData.total_criteria,
          passedCriteria: validationData.passed_criteria,
          score: validationData.score,
          status: validationData.status,
          processedTime: new Date(validationData.processed_time).toLocaleString(),
          categories: validationData.categories,
          issues: validationData.issues || [],
          recommendations: validationData.recommendations || [],
          strengths: validationData.strengths || []
        }
        
        setValidationResults(prev => [...prev, newResult])
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileId ? { ...f, status: 'completed' } : f
        ))
        
        // Auto-switch to results tab
        setActiveTab('results')
      } else {
        const errorText = await response.text()
        console.error('Validation failed:', errorText)
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileId ? { ...f, status: 'failed', error: errorText } : f
        ))
      }
    } catch (error) {
      console.error('Validation error:', error)
      setUploadedFiles(prev => prev.map(f => 
        f.id === fileId ? { ...f, status: 'failed', error: error.message } : f
      ))
    }
    
    setIsProcessing(false)
  }

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId))
    setValidationResults(prev => prev.filter(r => r.fileId !== fileId))
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Enhanced Information Validation Tool
              </h1>
              <p className="text-gray-600 mt-1">
                Automated validation for Site Survey and Install Plan documents
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="bg-green-100 px-3 py-1 rounded-full">
                <span className="text-green-800 text-sm font-medium">✅ API Operational</span>
              </div>
              <div className="bg-blue-100 px-3 py-1 rounded-full">
                <span className="text-blue-800 text-sm font-medium">v2.0 Enhanced</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'upload', name: 'Document Upload', icon: '📁' },
              { id: 'results', name: 'Validation Results', icon: '📊' },
              { id: 'criteria', name: 'Validation Criteria', icon: '📋' }
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
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            {/* Upload Area */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Upload Documents for Validation
              </h2>
              
              <div 
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-all cursor-pointer ${
                  isDragOver 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                }`}
                onClick={() => fileInputRef.current?.click()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div className="text-4xl mb-4">
                  {isDragOver ? '📥' : '📄'}
                </div>
                <p className="text-lg text-gray-600 mb-2">
                  {isDragOver ? 'Drop files here!' : 'Drop files here or click to upload'}
                </p>
                <p className="text-sm text-gray-500">
                  Supports: PDF, XLSX, DOCX files (Site Survey Parts 1 & 2, Install Plans)
                </p>
                <input
                  ref={fileInputRef}
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
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Uploaded Files ({uploadedFiles.length})
                </h3>
                <div className="space-y-3">
                  {uploadedFiles.map((file) => (
                    <div key={file.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="text-2xl">
                          {file.type.includes('pdf') ? '📄' : 
                           file.type.includes('sheet') ? '📊' : '📝'}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{file.name}</p>
                          <p className="text-sm text-gray-500">
                            {formatFileSize(file.size)} • {file.uploadTime}
                          </p>
                          
                          {/* Progress Bar */}
                          {file.status === 'uploading' && uploadProgress[file.id] !== undefined && (
                            <div className="mt-2">
                              <div className="bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${uploadProgress[file.id]}%` }}
                                ></div>
                              </div>
                              <p className="text-xs text-gray-500 mt-1">
                                Uploading... {uploadProgress[file.id]}%
                              </p>
                            </div>
                          )}
                          
                          {/* Error Message */}
                          {file.status === 'failed' && file.error && (
                            <p className="text-sm text-red-600 mt-1">
                              Error: {file.error}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          file.status === 'uploading' ? 'bg-yellow-100 text-yellow-800' :
                          file.status === 'uploaded' ? 'bg-blue-100 text-blue-800' :
                          file.status === 'processing' ? 'bg-purple-100 text-purple-800' :
                          file.status === 'completed' ? 'bg-green-100 text-green-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {file.status === 'uploading' ? 'Uploading...' :
                           file.status === 'uploaded' ? 'Ready' :
                           file.status === 'processing' ? 'Processing...' :
                           file.status === 'completed' ? 'Completed' : 'Failed'}
                        </span>
                        {file.status === 'uploaded' && (
                          <button
                            onClick={() => handleValidation(file.id)}
                            disabled={isProcessing}
                            className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-3 py-1 rounded text-sm transition-colors"
                          >
                            Validate
                          </button>
                        )}
                        <button
                          onClick={() => removeFile(file.id)}
                          className="text-red-500 hover:text-red-700 text-sm transition-colors"
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Results Tab */}
        {activeTab === 'results' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Validation Results ({validationResults.length})
              </h2>
              
              {validationResults.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">📊</div>
                  <p className="text-gray-500">No validation results yet. Upload and validate documents to see results here.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {validationResults.map((result) => (
                    <div key={result.id} className="border rounded-lg p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">{result.fileName}</h3>
                          <p className="text-sm text-gray-500">Processed: {result.processedTime}</p>
                        </div>
                        <div className="text-right">
                          <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                            result.status === 'passed' ? 'bg-green-100 text-green-800' : 
                            result.status === 'partial' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {result.status === 'passed' ? '✅ Passed' : 
                             result.status === 'partial' ? '⚠️ Partial' : '❌ Failed'}
                          </div>
                          <p className="text-lg font-bold text-gray-900 mt-1">
                            Score: {(result.score * 100).toFixed(1)}% ({result.passedCriteria}/{result.totalCriteria})
                          </p>
                        </div>
                      </div>

                      {/* Category Breakdown */}
                      <div className="mb-4">
                        <h4 className="font-medium text-gray-900 mb-2">Category Breakdown:</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {result.categories.map((category, index) => (
                            <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                              <span className="text-sm text-gray-700">{category.name}</span>
                              <span className={`text-sm font-medium ${
                                category.passed === category.total ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {category.passed}/{category.total}
                                {category.percentage && ` (${category.percentage}%)`}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Strengths */}
                      {result.strengths && result.strengths.length > 0 && (
                        <div className="mb-4">
                          <h4 className="font-medium text-gray-900 mb-2">✅ Strengths:</h4>
                          <ul className="space-y-1">
                            {result.strengths.map((strength, index) => (
                              <li key={index} className="text-sm text-green-600 flex items-start">
                                <span className="mr-2">•</span>
                                {strength}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Issues */}
                      {result.issues && result.issues.length > 0 && (
                        <div className="mb-4">
                          <h4 className="font-medium text-gray-900 mb-2">⚠️ Issues Found:</h4>
                          <ul className="space-y-1">
                            {result.issues.map((issue, index) => (
                              <li key={index} className="text-sm text-red-600 flex items-start">
                                <span className="mr-2">•</span>
                                {issue}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Recommendations */}
                      {result.recommendations && result.recommendations.length > 0 && (
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">💡 Recommendations:</h4>
                          <ul className="space-y-1">
                            {result.recommendations.map((recommendation, index) => (
                              <li key={index} className="text-sm text-blue-600 flex items-start">
                                <span className="mr-2">•</span>
                                {recommendation}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Criteria Tab */}
        {activeTab === 'criteria' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Enhanced Validation Criteria (65 Total)
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                { name: 'Basic Project Information', count: 6, color: 'blue' },
                { name: 'SFDC & Documentation Integration', count: 2, color: 'green' },
                { name: 'Template & Documentation Standards', count: 2, color: 'purple' },
                { name: 'Installation Plan Content Validation', count: 6, color: 'yellow' },
                { name: 'Network Configuration & Technical', count: 9, color: 'red' },
                { name: 'Site Survey Documentation', count: 12, color: 'indigo' },
                { name: 'Cross-Document Consistency', count: 15, color: 'pink' },
                { name: 'Enhanced Features', count: 13, color: 'gray' }
              ].map((category, index) => (
                <div key={index} className={`p-4 rounded-lg bg-${category.color}-50 border border-${category.color}-200`}>
                  <h3 className={`font-medium text-${category.color}-900 mb-2`}>{category.name}</h3>
                  <p className={`text-${category.color}-700 text-sm`}>{category.count} validation checks</p>
                  <div className={`mt-2 text-xs text-${category.color}-600`}>
                    Includes automated pattern matching, content analysis, and cross-reference validation
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-medium text-blue-900 mb-2">Enhanced Features</h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>✅ Conditional Logic Processing</li>
                <li>✅ Cross-Document Validation</li>
                <li>✅ Automation Complexity Classification</li>
                <li>✅ Confidence Scoring</li>
                <li>✅ Real-Time Accuracy Monitoring</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

