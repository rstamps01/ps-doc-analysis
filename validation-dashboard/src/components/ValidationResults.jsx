import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Search, 
  Filter, 
  Download,
  CheckCircle,
  XCircle,
  AlertCircle,
  FileText,
  Calendar,
  Clock,
  BarChart3,
  Eye,
  Mail,
  ExternalLink,
  TrendingUp,
  TrendingDown
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table.jsx'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select.jsx'
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert.jsx'

const ValidationResults = ({ ...motionProps }) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedResult, setSelectedResult] = useState(null)

  // Mock data for validation results
  const validationResults = [
    {
      id: 'result-001',
      requestId: 'req-001',
      contentId: 'CONF-12345',
      contentTitle: 'Product Requirements Document',
      overallStatus: 'passed',
      score: 0.95,
      executedAt: '2024-01-15T11:30:00Z',
      executionTime: 847,
      ruleResults: [
        {
          ruleName: 'Content Completeness',
          status: 'passed',
          score: 1.0,
          message: 'All required sections are present',
          findings: []
        },
        {
          ruleName: 'Format Consistency',
          status: 'passed',
          score: 0.9,
          message: 'Minor formatting inconsistencies found',
          findings: [
            { type: 'warning', description: 'Inconsistent heading styles in section 3' }
          ]
        }
      ],
      actionPlan: null
    },
    {
      id: 'result-002',
      requestId: 'req-002',
      contentId: 'CONF-67890',
      contentTitle: 'API Documentation',
      overallStatus: 'partial',
      score: 0.73,
      executedAt: '2024-01-15T10:45:00Z',
      executionTime: 1205,
      ruleResults: [
        {
          ruleName: 'Content Completeness',
          status: 'failed',
          score: 0.6,
          message: 'Missing required sections',
          findings: [
            { type: 'error', description: 'Missing authentication section' },
            { type: 'error', description: 'Missing error handling examples' }
          ]
        },
        {
          ruleName: 'Code Examples',
          status: 'passed',
          score: 0.85,
          message: 'Good code examples provided',
          findings: []
        }
      ],
      actionPlan: {
        priorityTasks: [
          {
            title: 'Add Authentication Section',
            description: 'Document authentication methods and provide examples',
            estimatedEffort: 2
          },
          {
            title: 'Add Error Handling Examples',
            description: 'Include common error scenarios and responses',
            estimatedEffort: 1.5
          }
        ],
        optionalTasks: [
          {
            title: 'Improve Code Formatting',
            description: 'Standardize code block formatting',
            estimatedEffort: 0.5
          }
        ]
      }
    },
    {
      id: 'result-003',
      requestId: 'req-003',
      contentId: 'CONF-11111',
      contentTitle: 'User Guide',
      overallStatus: 'failed',
      score: 0.42,
      executedAt: '2024-01-15T09:20:00Z',
      executionTime: 923,
      ruleResults: [
        {
          ruleName: 'Content Completeness',
          status: 'failed',
          score: 0.3,
          message: 'Multiple required sections missing',
          findings: [
            { type: 'error', description: 'Missing getting started section' },
            { type: 'error', description: 'Missing troubleshooting section' },
            { type: 'error', description: 'Missing FAQ section' }
          ]
        },
        {
          ruleName: 'Image Quality',
          status: 'failed',
          score: 0.5,
          message: 'Poor image quality and missing alt text',
          findings: [
            { type: 'error', description: 'Images are low resolution' },
            { type: 'warning', description: 'Missing alt text for accessibility' }
          ]
        }
      ],
      actionPlan: {
        priorityTasks: [
          {
            title: 'Add Getting Started Section',
            description: 'Create comprehensive getting started guide',
            estimatedEffort: 4
          },
          {
            title: 'Add Troubleshooting Section',
            description: 'Document common issues and solutions',
            estimatedEffort: 3
          },
          {
            title: 'Improve Image Quality',
            description: 'Replace low-resolution images with high-quality versions',
            estimatedEffort: 2
          }
        ],
        optionalTasks: [
          {
            title: 'Add FAQ Section',
            description: 'Compile frequently asked questions',
            estimatedEffort: 2
          }
        ]
      }
    }
  ]

  const getStatusIcon = (status) => {
    switch (status) {
      case 'passed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'partial':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
      default:
        return <Clock className="h-4 w-4 text-blue-500" />
    }
  }

  const getStatusBadge = (status) => {
    const variants = {
      passed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      partial: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
    }
    
    return (
      <Badge className={variants[status] || variants.partial}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    )
  }

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const filteredResults = validationResults.filter(result => {
    const matchesSearch = result.contentId.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         result.contentTitle.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || result.overallStatus === statusFilter
    return matchesSearch && matchesStatus
  })

  const ResultDetailDialog = ({ result, open, onOpenChange }) => {
    if (!result) return null

    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              {getStatusIcon(result.overallStatus)}
              <span>{result.contentTitle}</span>
            </DialogTitle>
            <DialogDescription>
              Detailed validation results for {result.contentId}
            </DialogDescription>
          </DialogHeader>
          
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="rules">Rule Results</TabsTrigger>
              <TabsTrigger value="action-plan">Action Plan</TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Overall Score</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className={`text-2xl font-bold ${getScoreColor(result.score)}`}>
                      {result.score.toFixed(3)}
                    </div>
                    <Progress value={result.score * 100} className="mt-2" />
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Execution Time</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{result.executionTime}ms</div>
                    <p className="text-sm text-muted-foreground">
                      Executed at {new Date(result.executedAt).toLocaleString()}
                    </p>
                  </CardContent>
                </Card>
              </div>
              
              <Card>
                <CardHeader>
                  <CardTitle>Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Status:</span>
                      {getStatusBadge(result.overallStatus)}
                    </div>
                    <div className="flex justify-between">
                      <span>Rules Evaluated:</span>
                      <span>{result.ruleResults.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Rules Passed:</span>
                      <span>{result.ruleResults.filter(r => r.status === 'passed').length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Rules Failed:</span>
                      <span>{result.ruleResults.filter(r => r.status === 'failed').length}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="rules" className="space-y-4">
              {result.ruleResults.map((ruleResult, index) => (
                <Card key={index}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{ruleResult.ruleName}</CardTitle>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(ruleResult.status)}
                        {getStatusBadge(ruleResult.status)}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Score:</span>
                        <div className="flex items-center space-x-2">
                          <span className={`font-bold ${getScoreColor(ruleResult.score)}`}>
                            {ruleResult.score.toFixed(2)}
                          </span>
                          <Progress value={ruleResult.score * 100} className="w-20" />
                        </div>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Message:</span>
                        <p className="text-sm text-muted-foreground mt-1">{ruleResult.message}</p>
                      </div>
                      {ruleResult.findings.length > 0 && (
                        <div>
                          <span className="text-sm font-medium">Findings:</span>
                          <div className="mt-2 space-y-2">
                            {ruleResult.findings.map((finding, findingIndex) => (
                              <Alert key={findingIndex} className={
                                finding.type === 'error' ? 'border-red-200' : 'border-yellow-200'
                              }>
                                <AlertDescription>{finding.description}</AlertDescription>
                              </Alert>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </TabsContent>
            
            <TabsContent value="action-plan" className="space-y-4">
              {result.actionPlan ? (
                <>
                  {result.actionPlan.priorityTasks.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg text-red-600">Priority Tasks</CardTitle>
                        <CardDescription>
                          These tasks must be completed to improve the validation score
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {result.actionPlan.priorityTasks.map((task, index) => (
                            <div key={index} className="border border-border rounded-lg p-4">
                              <h4 className="font-medium">{task.title}</h4>
                              <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
                              <div className="flex items-center mt-2 text-xs text-muted-foreground">
                                <Clock className="h-3 w-3 mr-1" />
                                Estimated effort: {task.estimatedEffort} hours
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                  
                  {result.actionPlan.optionalTasks.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg text-blue-600">Optional Improvements</CardTitle>
                        <CardDescription>
                          These tasks can further enhance the content quality
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {result.actionPlan.optionalTasks.map((task, index) => (
                            <div key={index} className="border border-border rounded-lg p-4">
                              <h4 className="font-medium">{task.title}</h4>
                              <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
                              <div className="flex items-center mt-2 text-xs text-muted-foreground">
                                <Clock className="h-3 w-3 mr-1" />
                                Estimated effort: {task.estimatedEffort} hours
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </>
              ) : (
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center text-muted-foreground">
                      <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                      <h3 className="text-lg font-medium">No Action Required</h3>
                      <p>This content passed all validation rules successfully.</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <motion.div className="space-y-6" {...motionProps}>
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground">Validation Results</h2>
          <p className="text-muted-foreground">
            Review and analyze content validation results
          </p>
        </div>
        <Button>
          <Download className="h-4 w-4 mr-2" />
          Export Results
        </Button>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search results..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="passed">Passed</SelectItem>
                <SelectItem value="partial">Partial</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Results Table */}
      <Card>
        <CardHeader>
          <CardTitle>Validation Results</CardTitle>
          <CardDescription>
            {filteredResults.length} of {validationResults.length} results
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Content</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Executed At</TableHead>
                <TableHead>Execution Time</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredResults.map((result) => (
                <TableRow key={result.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">{result.contentId}</span>
                      </div>
                      <p className="text-sm text-muted-foreground">{result.contentTitle}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(result.overallStatus)}
                      {getStatusBadge(result.overallStatus)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="space-y-1">
                      <div className={`font-bold ${getScoreColor(result.score)}`}>
                        {result.score.toFixed(3)}
                      </div>
                      <Progress value={result.score * 100} className="w-16" />
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">
                        {new Date(result.executedAt).toLocaleDateString()}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">{result.executionTime}ms</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => setSelectedResult(result)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Mail className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Result Detail Dialog */}
      <ResultDetailDialog 
        result={selectedResult}
        open={!!selectedResult}
        onOpenChange={(open) => !open && setSelectedResult(null)}
      />
    </motion.div>
  )
}

export default ValidationResults

