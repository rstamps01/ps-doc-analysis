import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Plus, 
  Search, 
  Filter, 
  Edit,
  Trash2,
  Shield,
  ToggleLeft,
  ToggleRight,
  Settings,
  Code,
  FileText,
  AlertTriangle
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Switch } from '@/components/ui/switch.jsx'
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
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'

const RulesManagement = ({ ...motionProps }) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [selectedRule, setSelectedRule] = useState(null)
  const [newRule, setNewRule] = useState({
    name: '',
    description: '',
    category: 'content',
    priority: 'medium',
    enabled: true,
    conditions: '',
    actions: ''
  })

  // Mock data for validation rules
  const validationRules = [
    {
      id: 'rule-001',
      name: 'Content Completeness',
      description: 'Ensures all required sections are present in the document',
      category: 'content',
      priority: 'high',
      enabled: true,
      lastModified: '2024-01-10T14:30:00Z',
      usageCount: 1247,
      successRate: 78.5,
      conditions: {
        requiredSections: ['introduction', 'overview', 'requirements', 'conclusion'],
        minWordCount: 500
      },
      actions: {
        onPass: 'mark_complete',
        onFail: 'generate_action_plan'
      }
    },
    {
      id: 'rule-002',
      name: 'Format Consistency',
      description: 'Validates consistent formatting throughout the document',
      category: 'formatting',
      priority: 'medium',
      enabled: true,
      lastModified: '2024-01-08T09:15:00Z',
      usageCount: 892,
      successRate: 85.2,
      conditions: {
        headingLevels: 'consistent',
        bulletPoints: 'uniform',
        codeBlocks: 'formatted'
      },
      actions: {
        onPass: 'mark_complete',
        onFail: 'suggest_improvements'
      }
    },
    {
      id: 'rule-003',
      name: 'Image Quality',
      description: 'Checks image resolution and accessibility requirements',
      category: 'media',
      priority: 'medium',
      enabled: false,
      lastModified: '2024-01-05T16:45:00Z',
      usageCount: 234,
      successRate: 92.1,
      conditions: {
        minResolution: '1920x1080',
        altTextRequired: true,
        maxFileSize: '5MB'
      },
      actions: {
        onPass: 'mark_complete',
        onFail: 'request_image_update'
      }
    },
    {
      id: 'rule-004',
      name: 'Code Examples',
      description: 'Validates presence and quality of code examples',
      category: 'technical',
      priority: 'high',
      enabled: true,
      lastModified: '2024-01-12T11:20:00Z',
      usageCount: 567,
      successRate: 73.8,
      conditions: {
        syntaxHighlighting: true,
        workingExamples: true,
        explanations: 'required'
      },
      actions: {
        onPass: 'mark_complete',
        onFail: 'request_code_review'
      }
    },
    {
      id: 'rule-005',
      name: 'Link Validation',
      description: 'Checks all external and internal links for validity',
      category: 'technical',
      priority: 'low',
      enabled: true,
      lastModified: '2024-01-07T13:10:00Z',
      usageCount: 1089,
      successRate: 96.3,
      conditions: {
        checkExternal: true,
        checkInternal: true,
        timeout: 5000
      },
      actions: {
        onPass: 'mark_complete',
        onFail: 'report_broken_links'
      }
    }
  ]

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'content':
        return <FileText className="h-4 w-4" />
      case 'formatting':
        return <Settings className="h-4 w-4" />
      case 'media':
        return <Shield className="h-4 w-4" />
      case 'technical':
        return <Code className="h-4 w-4" />
      default:
        return <Shield className="h-4 w-4" />
    }
  }

  const getCategoryBadge = (category) => {
    const variants = {
      content: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      formatting: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      media: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      technical: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
    }
    
    return (
      <Badge className={variants[category] || variants.content}>
        {category.charAt(0).toUpperCase() + category.slice(1)}
      </Badge>
    )
  }

  const getPriorityBadge = (priority) => {
    const variants = {
      low: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
      medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      high: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    }
    
    return (
      <Badge variant="outline" className={variants[priority]}>
        {priority.charAt(0).toUpperCase() + priority.slice(1)}
      </Badge>
    )
  }

  const filteredRules = validationRules.filter(rule => {
    const matchesSearch = rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         rule.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = categoryFilter === 'all' || rule.category === categoryFilter
    return matchesSearch && matchesCategory
  })

  const toggleRuleEnabled = (ruleId) => {
    // This would typically make an API call
    console.log('Toggling rule:', ruleId)
  }

  const handleCreateRule = () => {
    // This would typically make an API call
    console.log('Creating rule:', newRule)
    setIsCreateDialogOpen(false)
    setNewRule({
      name: '',
      description: '',
      category: 'content',
      priority: 'medium',
      enabled: true,
      conditions: '',
      actions: ''
    })
  }

  const RuleDetailDialog = ({ rule, open, onOpenChange }) => {
    if (!rule) return null

    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              {getCategoryIcon(rule.category)}
              <span>{rule.name}</span>
            </DialogTitle>
            <DialogDescription>
              Rule configuration and performance details
            </DialogDescription>
          </DialogHeader>
          
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="conditions">Conditions</TabsTrigger>
              <TabsTrigger value="actions">Actions</TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Usage Count</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{rule.usageCount.toLocaleString()}</div>
                    <p className="text-sm text-muted-foreground">Total validations</p>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Success Rate</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">{rule.successRate}%</div>
                    <p className="text-sm text-muted-foreground">Pass rate</p>
                  </CardContent>
                </Card>
              </div>
              
              <Card>
                <CardHeader>
                  <CardTitle>Rule Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="font-medium">Description:</span>
                      <span className="text-muted-foreground">{rule.description}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Category:</span>
                      {getCategoryBadge(rule.category)}
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Priority:</span>
                      {getPriorityBadge(rule.priority)}
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Status:</span>
                      <Badge className={rule.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                        {rule.enabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Last Modified:</span>
                      <span className="text-muted-foreground">
                        {new Date(rule.lastModified).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="conditions" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Validation Conditions</CardTitle>
                  <CardDescription>
                    Criteria that must be met for this rule
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto">
                    {JSON.stringify(rule.conditions, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="actions" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Rule Actions</CardTitle>
                  <CardDescription>
                    Actions taken based on validation results
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto">
                    {JSON.stringify(rule.actions, null, 2)}
                  </pre>
                </CardContent>
              </Card>
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
          <h2 className="text-3xl font-bold text-foreground">Rules Management</h2>
          <p className="text-muted-foreground">
            Configure and manage validation rules
          </p>
        </div>
        
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Rule
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[525px]">
            <DialogHeader>
              <DialogTitle>Create Validation Rule</DialogTitle>
              <DialogDescription>
                Define a new validation rule for content assessment.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="ruleName" className="text-right">
                  Rule Name
                </Label>
                <Input
                  id="ruleName"
                  value={newRule.name}
                  onChange={(e) => setNewRule({...newRule, name: e.target.value})}
                  className="col-span-3"
                  placeholder="e.g., Content Completeness"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="ruleDescription" className="text-right">
                  Description
                </Label>
                <Textarea
                  id="ruleDescription"
                  value={newRule.description}
                  onChange={(e) => setNewRule({...newRule, description: e.target.value})}
                  className="col-span-3"
                  placeholder="Brief description of what this rule validates..."
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="ruleCategory" className="text-right">
                  Category
                </Label>
                <Select 
                  value={newRule.category} 
                  onValueChange={(value) => setNewRule({...newRule, category: value})}
                >
                  <SelectTrigger className="col-span-3">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="content">Content</SelectItem>
                    <SelectItem value="formatting">Formatting</SelectItem>
                    <SelectItem value="media">Media</SelectItem>
                    <SelectItem value="technical">Technical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="rulePriority" className="text-right">
                  Priority
                </Label>
                <Select 
                  value={newRule.priority} 
                  onValueChange={(value) => setNewRule({...newRule, priority: value})}
                >
                  <SelectTrigger className="col-span-3">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button type="submit" onClick={handleCreateRule}>
                Create Rule
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Rules</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{validationRules.length}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Rules</CardTitle>
            <ToggleRight className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {validationRules.filter(rule => rule.enabled).length}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">High Priority</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {validationRules.filter(rule => rule.priority === 'high').length}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Success Rate</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(validationRules.reduce((acc, rule) => acc + rule.successRate, 0) / validationRules.length).toFixed(1)}%
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search rules..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-[180px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter by category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="content">Content</SelectItem>
                <SelectItem value="formatting">Formatting</SelectItem>
                <SelectItem value="media">Media</SelectItem>
                <SelectItem value="technical">Technical</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Rules Table */}
      <Card>
        <CardHeader>
          <CardTitle>Validation Rules</CardTitle>
          <CardDescription>
            {filteredRules.length} of {validationRules.length} rules
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rule</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Usage</TableHead>
                <TableHead>Success Rate</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredRules.map((rule) => (
                <TableRow key={rule.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        {getCategoryIcon(rule.category)}
                        <span className="font-medium">{rule.name}</span>
                      </div>
                      <p className="text-sm text-muted-foreground">{rule.description}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    {getCategoryBadge(rule.category)}
                  </TableCell>
                  <TableCell>
                    {getPriorityBadge(rule.priority)}
                  </TableCell>
                  <TableCell>
                    <span className="text-sm">{rule.usageCount.toLocaleString()}</span>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm font-medium text-green-600">
                      {rule.successRate}%
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Switch
                        checked={rule.enabled}
                        onCheckedChange={() => toggleRuleEnabled(rule.id)}
                      />
                      <span className="text-sm">
                        {rule.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => setSelectedRule(rule)}
                      >
                        <Settings className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" className="text-red-600">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Rule Detail Dialog */}
      <RuleDetailDialog 
        rule={selectedRule}
        open={!!selectedRule}
        onOpenChange={(open) => !open && setSelectedRule(null)}
      />
    </motion.div>
  )
}

export default RulesManagement

