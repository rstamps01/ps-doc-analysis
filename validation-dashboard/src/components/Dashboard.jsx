import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
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
  ArrowDownRight
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

const Dashboard = ({ systemStats, ...motionProps }) => {
  // Real data states
  const [validationTrends, setValidationTrends] = useState([])
  const [statusDistribution, setStatusDistribution] = useState([])
  const [recentActivity, setRecentActivity] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Load real data on component mount
  useEffect(() => {
    loadRealDashboardData()
  }, [])

  const loadRealDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load validation history for trends
      const historyResponse = await fetch('/api/real-data/validation-history')
      if (historyResponse.ok) {
        const historyData = await historyResponse.json()
        if (historyData.status === 'success') {
          // Transform history data for chart
          const trends = historyData.data.validation_history.map(run => ({
            date: new Date(run.timestamp).toISOString().split('T')[0],
            validations: 1,
            passed: run.passed_checks,
            failed: run.failed_checks
          }))
          setValidationTrends(trends)
        }
      }

      // Load dashboard stats for status distribution
      const statsResponse = await fetch('/api/real-data/dashboard-stats')
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        if (statsData.status === 'success') {
          const data = statsData.data
          const total = data.total_checks
          const passedPercent = ((data.passed_checks / total) * 100).toFixed(1)
          const failedPercent = ((data.failed_checks / total) * 100).toFixed(1)
          const warningPercent = ((data.warning_checks / total) * 100).toFixed(1)
          
          setStatusDistribution([
            { name: 'Passed', value: parseFloat(passedPercent), color: '#22c55e' },
            { name: 'Failed', value: parseFloat(failedPercent), color: '#ef4444' },
            { name: 'Warnings', value: parseFloat(warningPercent), color: '#f59e0b' }
          ])
        }
      }

      // Load common issues for recent activity
      const issuesResponse = await fetch('/api/real-data/common-issues')
      if (issuesResponse.ok) {
        const issuesData = await issuesResponse.json()
        if (issuesData.status === 'success') {
          const activities = issuesData.data.common_issues.slice(0, 4).map((issue, index) => ({
            id: index + 1,
            type: 'validation_issue',
            title: issue.description,
            status: issue.severity === 'critical' ? 'failed' : issue.severity === 'warning' ? 'partial' : 'passed',
            time: 'Recent validation',
            score: issue.severity === 'critical' ? 0.3 : issue.severity === 'warning' ? 0.7 : 0.9
          }))
          setRecentActivity(activities)
        }
      }

    } catch (error) {
      console.error('Error loading dashboard data:', error)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

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
      partial: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      info: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
    }
    
    return (
      <Badge className={variants[status] || variants.info}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    )
  }

  return (
    <motion.div className="space-y-6" {...motionProps}>
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground">Dashboard</h2>
          <p className="text-muted-foreground">
            Overview of validation system performance and activity
          </p>
        </div>
        <Button onClick={loadRealDashboardData} disabled={loading}>
          <BarChart3 className="h-4 w-4 mr-2" />
          {loading ? 'Loading...' : 'Refresh Data'}
        </Button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center p-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading dashboard data...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-destructive" />
            <p className="text-destructive font-medium">Error loading dashboard data</p>
          </div>
          <p className="text-sm text-muted-foreground mt-2">{error}</p>
        </div>
      )}

      {/* Dashboard Content - Only show when not loading and no error */}
      {!loading && !error && (
        <>
          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Validations</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStats?.totalValidations?.toLocaleString() || '0'}</div>
                <div className="flex items-center text-xs text-muted-foreground">
                  <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
                  Real-time data
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pass Rate</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStats?.passRate || '0'}%</div>
                <div className="flex items-center text-xs text-muted-foreground">
                  <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
                  From latest validation
                </div>
                <Progress value={systemStats?.passRate || 0} className="mt-2" />
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average Score</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStats?.avgScore?.toFixed(3) || '0.000'}</div>
                <div className="flex items-center text-xs text-muted-foreground">
                  <Activity className="h-3 w-3 mr-1 text-blue-500" />
                  Real validation data
                </div>
                <Progress value={(systemStats?.avgScore || 0) * 100} className="mt-2" />
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Rules</CardTitle>
                <Shield className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStats?.activeRules || '0'}</div>
                <div className="flex items-center text-xs text-muted-foreground">
                  <Shield className="h-3 w-3 mr-1 text-green-500" />
                  Validation criteria
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Validation Trends */}
        <Card>
          <CardHeader>
            <CardTitle>Validation Trends</CardTitle>
            <CardDescription>
              Daily validation activity over the past week
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={validationTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <Bar dataKey="passed" stackId="a" fill="#22c55e" name="Passed" />
                <Bar dataKey="failed" stackId="a" fill="#ef4444" name="Failed" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Validation Status Distribution</CardTitle>
            <CardDescription>
              Breakdown of validation results
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {statusDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value}%`} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex justify-center space-x-4 mt-4">
              {statusDistribution.map((entry, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: entry.color }}
                  ></div>
                  <span className="text-sm text-muted-foreground">
                    {entry.name}: {entry.value}%
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Latest validation results and system updates
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div 
                key={activity.id}
                className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  {getStatusIcon(activity.status)}
                  <div>
                    <p className="font-medium text-foreground">{activity.title}</p>
                    <p className="text-sm text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  {activity.score && (
                    <div className="text-right">
                      <p className="text-sm font-medium">Score: {activity.score}</p>
                      <Progress value={activity.score * 100} className="w-20" />
                    </div>
                  )}
                  {getStatusBadge(activity.status)}
                  <Button variant="ghost" size="sm">
                    <ArrowUpRight className="h-4 w-4" />
                  </Button>
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

export default Dashboard

