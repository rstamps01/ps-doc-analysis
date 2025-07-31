import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Upload, 
  Link, 
  FileText, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Loader2,
  ExternalLink,
  Download,
  Eye,
  Trash2,
  RefreshCw
} from 'lucide-react'

import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Label } from '@/components/ui/label.jsx'

const GoogleIntegration = () => {
  const [activeTab, setActiveTab] = useState('drive')
  const [driveUrl, setDriveUrl] = useState('')
  const [sheetsUrl, setSheetsUrl] = useState('')
  const [processing, setProcessing] = useState(false)
  const [processedFiles, setProcessedFiles] = useState([])
  const [connectionStatus, setConnectionStatus] = useState({ drive: null, sheets: null })

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
          filename: data.filename,
          size: data.size,
          source: 'google_drive',
          url: driveUrl,
          uploadTime: data.upload_time,
          status: 'ready',
          metadata: data.metadata
        }
        
        setProcessedFiles(prev => [...prev, newFile])
        setDriveUrl('')
        alert('Google Drive file processed successfully!')
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
          filename: data.filename,
          source: 'google_sheets',
          url: sheetsUrl,
          uploadTime: data.upload_time,
          status: 'ready',
          metadata: data.metadata,
          requirementsCount: data.requirements_count
        }
        
        setProcessedFiles(prev => [...prev, newFile])
        setSheetsUrl('')
        alert('Google Sheets document processed successfully!')
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

  // Validate a processed file
  const validateFile = async (fileId) => {
    setProcessing(true)
    try {
      const response = await fetch(`/api/documents/validate/${fileId}`, {
        method: 'POST'
      })

      const data = await response.json()
      
      if (data.success) {
        // Update file status
        setProcessedFiles(prev => 
          prev.map(file => 
            file.id === fileId 
              ? { ...file, status: 'validated', validationResults: data.validation_results }
              : file
          )
        )
        alert('File validated successfully!')
      } else {
        alert(`Validation error: ${data.error}`)
      }
    } catch (error) {
      console.error('Validation failed:', error)
      alert('Failed to validate file')
    } finally {
      setProcessing(false)
    }
  }

  // Remove a processed file
  const removeFile = (fileId) => {
    setProcessedFiles(prev => prev.filter(file => file.id !== fileId))
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'ready':
        return <Badge variant="outline" className="text-blue-600 border-blue-600">Ready</Badge>
      case 'validated':
        return <Badge variant="outline" className="text-green-600 border-green-600">Validated</Badge>
      case 'processing':
        return <Badge variant="outline" className="text-yellow-600 border-yellow-600">Processing</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const getConnectionBadge = (connected) => {
    if (connected === null) return <Badge variant="outline">Not Tested</Badge>
    return connected 
      ? <Badge variant="outline" className="text-green-600 border-green-600">Connected</Badge>
      : <Badge variant="outline" className="text-red-600 border-red-600">Disconnected</Badge>
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Google Integration</h1>
          <p className="text-gray-600 mt-1">Process documents from Google Drive and Google Sheets</p>
        </div>
        <Button 
          onClick={testConnections}
          disabled={processing}
          variant="outline"
          className="flex items-center gap-2"
        >
          {processing ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          Test Connections
        </Button>
      </div>

      {/* Connection Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            Connection Status
          </CardTitle>
          <CardDescription>
            Current status of Google API connections
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Download className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-medium">Google Drive</h3>
                  <p className="text-sm text-gray-600">File download and processing</p>
                </div>
              </div>
              {getConnectionBadge(connectionStatus.drive?.connected)}
            </div>
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h3 className="font-medium">Google Sheets</h3>
                  <p className="text-sm text-gray-600">Spreadsheet data processing</p>
                </div>
              </div>
              {getConnectionBadge(connectionStatus.sheets?.connected)}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Interface */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="drive" className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            Google Drive
          </TabsTrigger>
          <TabsTrigger value="sheets" className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Google Sheets
          </TabsTrigger>
        </TabsList>

        {/* Google Drive Tab */}
        <TabsContent value="drive" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Download className="w-5 h-5 text-blue-600" />
                Google Drive Document Processing
              </CardTitle>
              <CardDescription>
                Enter a Google Drive URL to download and process documents (PDF, XLSX, DOCX)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="drive-url">Google Drive URL</Label>
                <div className="flex gap-2">
                  <Input
                    id="drive-url"
                    type="url"
                    placeholder="https://drive.google.com/file/d/..."
                    value={driveUrl}
                    onChange={(e) => setDriveUrl(e.target.value)}
                    className="flex-1"
                  />
                  <Button 
                    onClick={processGoogleDriveUrl}
                    disabled={processing || !driveUrl.trim()}
                    className="flex items-center gap-2"
                  >
                    {processing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Link className="w-4 h-4" />}
                    Process
                  </Button>
                </div>
              </div>
              
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Supported Formats</AlertTitle>
                <AlertDescription>
                  PDF files (Install Plans), XLSX files (Site Surveys), and DOCX files are supported. 
                  Ensure the file is shared with appropriate permissions.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Google Sheets Tab */}
        <TabsContent value="sheets" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-green-600" />
                Google Sheets Document Processing
              </CardTitle>
              <CardDescription>
                Enter a Google Sheets URL to process Site Survey documents or validation criteria
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="sheets-url">Google Sheets URL</Label>
                <div className="flex gap-2">
                  <Input
                    id="sheets-url"
                    type="url"
                    placeholder="https://docs.google.com/spreadsheets/d/..."
                    value={sheetsUrl}
                    onChange={(e) => setSheetsUrl(e.target.value)}
                    className="flex-1"
                  />
                  <Button 
                    onClick={processGoogleSheetsUrl}
                    disabled={processing || !sheetsUrl.trim()}
                    className="flex items-center gap-2"
                  >
                    {processing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Link className="w-4 h-4" />}
                    Process
                  </Button>
                </div>
              </div>
              
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Supported Documents</AlertTitle>
                <AlertDescription>
                  Site Survey Part 1, Site Survey Part 2, and Validation Criteria sheets are supported. 
                  Ensure the sheet is shared with appropriate permissions.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Processed Files */}
      {processedFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Processed Files ({processedFiles.length})
            </CardTitle>
            <CardDescription>
              Files processed from Google Drive and Google Sheets
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {processedFiles.map((file) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      {file.source === 'google_drive' ? (
                        <Download className="w-5 h-5 text-blue-600" />
                      ) : (
                        <FileText className="w-5 h-5 text-green-600" />
                      )}
                    </div>
                    <div>
                      <h3 className="font-medium">{file.filename}</h3>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <span>{file.source === 'google_drive' ? 'Google Drive' : 'Google Sheets'}</span>
                        {file.size && <span>• {file.size}</span>}
                        {file.requirementsCount && <span>• {file.requirementsCount} criteria</span>}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {getStatusBadge(file.status)}
                    
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => window.open(file.url, '_blank')}
                      className="flex items-center gap-1"
                    >
                      <ExternalLink className="w-3 h-3" />
                      View
                    </Button>
                    
                    {file.status === 'ready' && (
                      <Button
                        size="sm"
                        onClick={() => validateFile(file.id)}
                        disabled={processing}
                        className="flex items-center gap-1"
                      >
                        {processing ? <Loader2 className="w-3 h-3 animate-spin" /> : <Eye className="w-3 h-3" />}
                        Validate
                      </Button>
                    )}
                    
                    {file.status === 'validated' && file.validationResults && (
                      <Badge 
                        variant="outline" 
                        className={`${
                          file.validationResults.status === 'passed' 
                            ? 'text-green-600 border-green-600' 
                            : file.validationResults.status === 'partial'
                            ? 'text-yellow-600 border-yellow-600'
                            : 'text-red-600 border-red-600'
                        }`}
                      >
                        {Math.round(file.validationResults.overall_score * 100)}%
                      </Badge>
                    )}
                    
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => removeFile(file.id)}
                      className="flex items-center gap-1 text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default GoogleIntegration

