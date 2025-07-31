import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Clock, 
  FileText, 
  Settings, 
  BarChart3,
  Zap,
  GitBranch,
  Target,
  TrendingUp,
  Filter,
  Search,
  RefreshCw
} from 'lucide-react';

const EnhancedValidation = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [validationData, setValidationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    category: '',
    complexity: '',
    status: ''
  });

  // Mock data for enhanced validation
  const mockEnhancedData = {
    overview: {
      totalCriteria: 65,
      activeCriteria: 58,
      projectsValidated: 127,
      averageAccuracy: 94.2,
      categories: [
        { name: 'Basic Project Information', criteria: 8, passed: 7, accuracy: 87.5 },
        { name: 'SFDC & Documentation Integration', criteria: 4, passed: 4, accuracy: 100 },
        { name: 'Template & Documentation Standards', criteria: 6, passed: 5, accuracy: 83.3 },
        { name: 'Installation Plan Content Validation', criteria: 12, passed: 11, accuracy: 91.7 },
        { name: 'Network Configuration & Technical', criteria: 15, passed: 14, accuracy: 93.3 },
        { name: 'Site Survey Documentation', criteria: 16, passed: 15, accuracy: 93.8 },
        { name: 'Cross-Document Consistency', criteria: 8, passed: 7, accuracy: 87.5 }
      ]
    },
    criteria: [
      {
        id: 'PROJ_001_ENH',
        name: 'Project Name Consistency Validation',
        category: 'Basic Project Information',
        complexity: 'medium',
        validationLevel: 2,
        automationSupport: true,
        conditionalLogic: true,
        accuracy: 96.8,
        lastExecuted: '2025-01-30T14:30:00Z',
        status: 'active',
        description: 'Validates project name consistency across all documents and systems'
      },
      {
        id: 'NET_005_ENH',
        name: 'Advanced Network Configuration Validation',
        category: 'Network Configuration & Technical',
        complexity: 'high',
        validationLevel: 4,
        automationSupport: true,
        conditionalLogic: true,
        accuracy: 89.2,
        lastExecuted: '2025-01-30T13:45:00Z',
        status: 'active',
        description: 'Comprehensive validation of network configurations including VLANs, IP ranges, and MTU settings'
      },
      {
        id: 'CROSS_001_ENH',
        name: 'Site Survey Cross-Document Synchronization',
        category: 'Cross-Document Consistency',
        complexity: 'high',
        validationLevel: 3,
        automationSupport: true,
        conditionalLogic: true,
        accuracy: 92.1,
        lastExecuted: '2025-01-30T12:15:00Z',
        status: 'active',
        description: 'Validates synchronization between Site Survey Part 1 and Part 2 documents'
      }
    ],
    workflows: [
      {
        id: 'WF_001',
        projectId: 'PROJ_CERES_2025',
        status: 'completed',
        totalCriteria: 42,
        executedCriteria: 38,
        conditionalExclusions: 4,
        successRate: 94.7,
        executionTime: 2340,
        createdAt: '2025-01-30T10:00:00Z',
        completedAt: '2025-01-30T10:02:20Z'
      },
      {
        id: 'WF_002',
        projectId: 'PROJ_ATLAS_2025',
        status: 'running',
        totalCriteria: 45,
        executedCriteria: 32,
        conditionalExclusions: 2,
        successRate: 91.2,
        executionTime: 1890,
        createdAt: '2025-01-30T14:15:00Z',
        completedAt: null
      }
    ],
    analytics: {
      accuracyTrend: [
        { date: '2025-01-24', accuracy: 91.2 },
        { date: '2025-01-25', accuracy: 92.8 },
        { date: '2025-01-26', accuracy: 93.1 },
        { date: '2025-01-27', accuracy: 94.5 },
        { date: '2025-01-28', accuracy: 93.9 },
        { date: '2025-01-29', accuracy: 94.8 },
        { date: '2025-01-30', accuracy: 94.2 }
      ],
      executionStats: {
        totalExecutions: 1247,
        averageExecutionTime: 1850,
        automationRate: 87.3,
        conditionalOptimization: 23.1
      }
    }
  };

  useEffect(() => {
    setValidationData(mockEnhancedData);
  }, []);

  const handleRefresh = async () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'inactive':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getComplexityColor = (complexity) => {
    switch (complexity) {
      case 'low':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'high':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Criteria</p>
              <p className="text-2xl font-bold text-gray-900">{validationData?.overview.totalCriteria}</p>
            </div>
            <Target className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Criteria</p>
              <p className="text-2xl font-bold text-green-600">{validationData?.overview.activeCriteria}</p>
            </div>
            <Zap className="w-8 h-8 text-green-500" />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Projects Validated</p>
              <p className="text-2xl font-bold text-purple-600">{validationData?.overview.projectsValidated}</p>
            </div>
            <FileText className="w-8 h-8 text-purple-500" />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Average Accuracy</p>
              <p className="text-2xl font-bold text-indigo-600">{validationData?.overview.averageAccuracy}%</p>
            </div>
            <TrendingUp className="w-8 h-8 text-indigo-500" />
          </div>
        </div>
      </div>

      {/* Category Performance */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Category Performance</h3>
        <div className="space-y-4">
          {validationData?.overview.categories.map((category, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{category.name}</h4>
                <p className="text-sm text-gray-600">{category.criteria} criteria • {category.passed} passed</p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{category.accuracy}%</p>
                  <p className="text-xs text-gray-500">accuracy</p>
                </div>
                <div className="w-16 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${category.accuracy}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderCriteria = () => (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filters:</span>
          </div>
          
          <select 
            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
            value={filters.category}
            onChange={(e) => setFilters({...filters, category: e.target.value})}
          >
            <option value="">All Categories</option>
            <option value="basic">Basic Project Information</option>
            <option value="network">Network Configuration</option>
            <option value="cross-document">Cross-Document Consistency</option>
          </select>
          
          <select 
            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
            value={filters.complexity}
            onChange={(e) => setFilters({...filters, complexity: e.target.value})}
          >
            <option value="">All Complexity</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          
          <select 
            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
            value={filters.status}
            onChange={(e) => setFilters({...filters, status: e.target.value})}
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      {/* Criteria List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Enhanced Validation Criteria</h3>
          <p className="text-sm text-gray-600 mt-1">Comprehensive validation rules with automation support</p>
        </div>
        
        <div className="divide-y divide-gray-200">
          {validationData?.criteria.map((criterion) => (
            <div key={criterion.id} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    {getStatusIcon(criterion.status)}
                    <h4 className="font-medium text-gray-900">{criterion.name}</h4>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getComplexityColor(criterion.complexity)}`}>
                      {criterion.complexity}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3">{criterion.description}</p>
                  
                  <div className="flex items-center space-x-6 text-xs text-gray-500">
                    <span>ID: {criterion.id}</span>
                    <span>Level: {criterion.validationLevel}</span>
                    <span>Accuracy: {criterion.accuracy}%</span>
                    <span>Last: {new Date(criterion.lastExecuted).toLocaleDateString()}</span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  {criterion.automationSupport && (
                    <div className="flex items-center space-x-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                      <Zap className="w-3 h-3" />
                      <span>Auto</span>
                    </div>
                  )}
                  {criterion.conditionalLogic && (
                    <div className="flex items-center space-x-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                      <GitBranch className="w-3 h-3" />
                      <span>Conditional</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderWorkflows = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Validation Workflows</h3>
          <p className="text-sm text-gray-600 mt-1">Automated validation execution with conditional logic</p>
        </div>
        
        <div className="divide-y divide-gray-200">
          {validationData?.workflows.map((workflow) => (
            <div key={workflow.id} className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h4 className="font-medium text-gray-900">{workflow.projectId}</h4>
                  <p className="text-sm text-gray-600">Workflow ID: {workflow.id}</p>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    workflow.status === 'completed' ? 'bg-green-100 text-green-800' :
                    workflow.status === 'running' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {workflow.status}
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-500">Total Criteria</p>
                  <p className="text-sm font-medium text-gray-900">{workflow.totalCriteria}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Executed</p>
                  <p className="text-sm font-medium text-gray-900">{workflow.executedCriteria}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Success Rate</p>
                  <p className="text-sm font-medium text-gray-900">{workflow.successRate}%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Execution Time</p>
                  <p className="text-sm font-medium text-gray-900">{(workflow.executionTime / 1000).toFixed(1)}s</p>
                </div>
              </div>
              
              {workflow.conditionalExclusions > 0 && (
                <div className="flex items-center space-x-2 text-xs text-amber-600 bg-amber-50 px-3 py-2 rounded-lg">
                  <GitBranch className="w-3 h-3" />
                  <span>{workflow.conditionalExclusions} criteria excluded by conditional logic</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderAnalytics = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Accuracy Trend */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Accuracy Trend</h3>
          <div className="space-y-2">
            {validationData?.analytics.accuracyTrend.slice(-5).map((point, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{point.date}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${point.accuracy}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900">{point.accuracy}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Execution Stats */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Execution Statistics</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Total Executions</span>
              <span className="text-sm font-medium text-gray-900">
                {validationData?.analytics.executionStats.totalExecutions.toLocaleString()}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Avg Execution Time</span>
              <span className="text-sm font-medium text-gray-900">
                {(validationData?.analytics.executionStats.averageExecutionTime / 1000).toFixed(1)}s
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Automation Rate</span>
              <span className="text-sm font-medium text-gray-900">
                {validationData?.analytics.executionStats.automationRate}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Conditional Optimization</span>
              <span className="text-sm font-medium text-gray-900">
                {validationData?.analytics.executionStats.conditionalOptimization}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  if (!validationData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Enhanced Validation System</h1>
          <p className="text-gray-600">Advanced validation with automation and conditional logic</p>
        </div>
        
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview', icon: BarChart3 },
            { id: 'criteria', name: 'Criteria', icon: Settings },
            { id: 'workflows', name: 'Workflows', icon: GitBranch },
            { id: 'analytics', name: 'Analytics', icon: TrendingUp }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-96">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'criteria' && renderCriteria()}
        {activeTab === 'workflows' && renderWorkflows()}
        {activeTab === 'analytics' && renderAnalytics()}
      </div>
    </div>
  );
};

export default EnhancedValidation;

