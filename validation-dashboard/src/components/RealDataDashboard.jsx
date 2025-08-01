import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Clock, 
  TrendingUp,
  TrendingDown,
  Activity,
  FileText,
  Shield,
  Users,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Button } from '@/components/ui/button.jsx'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts'

const RealDataDashboard = ({ ...motionProps }) => {
  const [dashboardData, setDashboardData] = useState(null)
  const [validationHistory, setValidationHistory] = useState([])
  const [commonIssues, setCommonIssues] = useState([])
  const [analyticsData, setAnalyticsData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // API base URL - updated to new deployed backend
  // const API_BASE = 'https://ogh5izceny33.manus.space'
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000';


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
        setValidationHistory(historyResult.data.validation_history || [])
      }

      // Fetch common issues
      const issuesResponse = await fetch(`${API_BASE}/api/real-data/common-issues`)
      if (issuesResponse.ok) {
        const issuesResult = await issuesResponse.json()
        setCommonIssues(issuesResult.data.common_issues || [])
      }

      // Fetch analytics data
      const analyticsResponse = await fetch(`${API_BASE}/api/real-data/analytics`)
      if (analyticsResponse.ok) {
        const analyticsResult = await analyticsResponse.json()
        setAnalyticsData(analyticsResult.data)
      }

    } catch (err) {
      console.error('Error fetching real data:', err)
      setError('Failed to load real data. Using fallback data.')
      
      // Fallback to QA test data if API fails
      setDashboardData({
        overall_score: 85.2,
        passed_checks: 43,
        failed_checks: 3,
        warning_checks: 4,
        total_checks: 50,
        execution_time: 2.3,
        last_run: new Date().toISOString(),
        system_metrics: {
          total_validations: { value: 1, unit: 'count' },
          success_rate: { value: 100.0, unit: 'percentage' },
          avg_processing_time: { value: 2.3, unit: 'minutes' }
        },
        categories: {
          'Document Completeness': { score: 92.0, status: 'pass' },
          'Technical Requirements': { score: 78.0, status: 'warning' },
          'SFDC Integration': { score: 95.0, status: 'pass' },
          'Cross-Document Consistency': { score: 76.0, status: 'warning' }
        }
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRealData()
  }, [])

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pass':
      case 'passed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
      default:
        return <Clock className="h-4 w-4 text-blue-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'pass':
      case 'passed':
        return 'text-green-500'
      case 'failed':
        return 'text-red-500'
      case 'warning':
        return 'text-yellow-500'
      default:
        return 'text-blue-500'
    }
  }

  if (loading) {
    return (
      <motion.div 
        className="flex items-center justify-center h-64"
        {...motionProps}
      >
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span>Loading real data...</span>
        </div>
      </motion.div>
    )
  }

  if (!dashboardData) {
    return (
      <motion.div 
        className="flex items-center justify-center h-64"
        {...motionProps}
      >
        <div className="text-center">
          <XCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No Data Available</h3>
          <p className="text-gray-600 mb-4">Unable to load validation data</p>
          <Button onClick={fetchRealData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </motion.div>
    )
  }

  // Prepare chart data from real data
  const statusDistribution = [
    { 
      name: 'Passed', 
      value: dashboardData.passed_checks, 
      color: '#22c55e',
      percentage: ((dashboardData.passed_checks / dashboardData.total_checks) * 100).toFixed(1)
    },
    { 
      name: 'Failed', 
      value: dashboardData.failed_checks, 
      color: '#ef4444',
      percentage: ((dashboardData.failed_checks / dashboardData.total_checks) * 100).toFixed(1)
    },
    { 
      name: 'Warnings', 
      value: dashboardData.warning_checks, 
      color: '#f59e0b',
      percentage: ((dashboardData.warning_checks / dashboardData.total_checks) * 100).toFixed(1)
    }
  ]

  return (
    <motion.div 
      className="space-y-6"
      {...motionProps}
    >
      {error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-yellow-600 mr-2" />
            <span className="text-yellow-800">{error}</span>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={fetchRealData}
              className="ml-auto"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>
      )}

      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overall Score</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {dashboardData.overall_score}%
            </div>
            <Progress value={dashboardData.overall_score} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-2">
              {dashboardData.passed_checks} passed • {dashboardData.warning_checks} warnings • {dashboardData.failed_checks} failed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Validations</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboardData.system_metrics?.total_validations?.value || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Real validation runs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {dashboardData.system_metrics?.success_rate?.value || 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              Based on actual runs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Processing Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboardData.execution_time}m
            </div>
            <p className="text-xs text-muted-foreground">
              Real processing time
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Validation Results Distribution</CardTitle>
            <CardDescription>Real results from latest validation run</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {statusDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value, name) => [`${value} checks`, name]}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center space-x-4 mt-4">
              {statusDistribution.map((item, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-sm">
                    {item.name}: {item.value} ({item.percentage}%)
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Category Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Category Performance</CardTitle>
            <CardDescription>Real scores by validation category</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(dashboardData.categories || {}).map(([category, data]) => (
                <div key={category} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(data.status)}
                      <span className="text-sm font-medium">{category}</span>
                    </div>
                    <span className={`text-sm font-bold ${getStatusColor(data.status)}`}>
                      {data.score}%
                    </span>
                  </div>
                  <Progress value={data.score} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Validation Activity</CardTitle>
          <CardDescription>Real validation runs and results</CardDescription>
        </CardHeader>
        <CardContent>
          {validationHistory.length > 0 ? (
            <div className="space-y-4">
              {validationHistory.slice(0, 5).map((run, index) => (
                <div key={run.validation_id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(run.status)}
                    <div>
                      <p className="font-medium">
                        {run.document_type} validation
                      </p>
                      <p className="text-sm text-gray-600">
                        {new Date(run.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-bold ${getStatusColor(run.status)}`}>
                      {run.overall_score}%
                    </p>
                    <p className="text-sm text-gray-600">
                      {run.passed_checks}/{run.total_checks} passed
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No validation history available</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Common Issues */}
      {commonIssues.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Common Issues</CardTitle>
            <CardDescription>Real issues identified in validation runs</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {commonIssues.slice(0, 5).map((issue, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    {issue.severity === 'critical' ? (
                      <XCircle className="h-5 w-5 text-red-500" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-yellow-500" />
                    )}
                    <div>
                      <p className="font-medium">{issue.description}</p>
                      <p className="text-sm text-gray-600">{issue.category}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant={issue.severity === 'critical' ? 'destructive' : 'secondary'}>
                      {issue.frequency} occurrence{issue.frequency !== 1 ? 's' : ''}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </motion.div>
  )
}

export default RealDataDashboard

