import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Bell, 
  Mail, 
  MessageSquare,
  Send,
  Filter,
  Search,
  Calendar,
  User,
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  Settings,
  Plus,
  Eye,
  Trash2
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
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
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert.jsx'

const Notifications = ({ ...motionProps }) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [isComposeDialogOpen, setIsComposeDialogOpen] = useState(false)
  const [selectedNotification, setSelectedNotification] = useState(null)
  const [newNotification, setNewNotification] = useState({
    recipients: '',
    subject: '',
    message: '',
    type: 'email'
  })

  // Mock data for notifications
  const notifications = [
    {
      id: 'notif-001',
      type: 'email',
      subject: 'Validation Completed: Product Requirements Document',
      recipients: ['john.doe@company.com'],
      status: 'sent',
      sentAt: '2024-01-15T11:30:00Z',
      validationId: 'result-001',
      contentId: 'CONF-12345',
      notificationType: 'validation_result',
      deliveryStatus: 'delivered'
    },
    {
      id: 'notif-002',
      type: 'email',
      subject: 'Action Plan Required: API Documentation',
      recipients: ['jane.smith@company.com'],
      status: 'sent',
      sentAt: '2024-01-15T10:45:00Z',
      validationId: 'result-002',
      contentId: 'CONF-67890',
      notificationType: 'action_plan',
      deliveryStatus: 'delivered'
    },
    {
      id: 'notif-003',
      type: 'email',
      subject: 'Validation Failed: User Guide',
      recipients: ['bob.wilson@company.com'],
      status: 'failed',
      sentAt: '2024-01-15T09:20:00Z',
      validationId: 'result-003',
      contentId: 'CONF-11111',
      notificationType: 'validation_result',
      deliveryStatus: 'failed',
      errorMessage: 'SMTP connection timeout'
    },
    {
      id: 'notif-004',
      type: 'email',
      subject: 'Daily Validation Summary Report',
      recipients: ['admin@company.com', 'manager@company.com'],
      status: 'sent',
      sentAt: '2024-01-15T08:00:00Z',
      validationId: null,
      contentId: null,
      notificationType: 'summary_report',
      deliveryStatus: 'delivered'
    },
    {
      id: 'notif-005',
      type: 'email',
      subject: 'System Maintenance Notification',
      recipients: ['all-users@company.com'],
      status: 'pending',
      sentAt: null,
      validationId: null,
      contentId: null,
      notificationType: 'system_announcement',
      deliveryStatus: 'pending'
    }
  ]

  const getTypeIcon = (type) => {
    switch (type) {
      case 'email':
        return <Mail className="h-4 w-4" />
      case 'slack':
        return <MessageSquare className="h-4 w-4" />
      default:
        return <Bell className="h-4 w-4" />
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'sent':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status) => {
    const variants = {
      sent: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
    }
    
    return (
      <Badge className={variants[status] || variants.pending}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    )
  }

  const getNotificationTypeBadge = (type) => {
    const variants = {
      validation_result: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      action_plan: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      summary_report: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      system_announcement: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
    
    return (
      <Badge variant="outline" className={variants[type]}>
        {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
      </Badge>
    )
  }

  const filteredNotifications = notifications.filter(notification => {
    const matchesSearch = notification.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         notification.recipients.some(r => r.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesStatus = statusFilter === 'all' || notification.status === statusFilter
    const matchesType = typeFilter === 'all' || notification.type === typeFilter
    return matchesSearch && matchesStatus && matchesType
  })

  const handleSendNotification = () => {
    // This would typically make an API call
    console.log('Sending notification:', newNotification)
    setIsComposeDialogOpen(false)
    setNewNotification({
      recipients: '',
      subject: '',
      message: '',
      type: 'email'
    })
  }

  const NotificationDetailDialog = ({ notification, open, onOpenChange }) => {
    if (!notification) return null

    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              {getTypeIcon(notification.type)}
              <span>{notification.subject}</span>
            </DialogTitle>
            <DialogDescription>
              Notification details and delivery information
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium">Type</Label>
                <div className="flex items-center space-x-2 mt-1">
                  {getTypeIcon(notification.type)}
                  <span className="capitalize">{notification.type}</span>
                </div>
              </div>
              <div>
                <Label className="text-sm font-medium">Status</Label>
                <div className="flex items-center space-x-2 mt-1">
                  {getStatusIcon(notification.status)}
                  {getStatusBadge(notification.status)}
                </div>
              </div>
            </div>
            
            <div>
              <Label className="text-sm font-medium">Recipients</Label>
              <div className="mt-1">
                {notification.recipients.map((recipient, index) => (
                  <Badge key={index} variant="outline" className="mr-2 mb-1">
                    {recipient}
                  </Badge>
                ))}
              </div>
            </div>
            
            <div>
              <Label className="text-sm font-medium">Notification Type</Label>
              <div className="mt-1">
                {getNotificationTypeBadge(notification.notificationType)}
              </div>
            </div>
            
            {notification.sentAt && (
              <div>
                <Label className="text-sm font-medium">Sent At</Label>
                <p className="text-sm text-muted-foreground mt-1">
                  {new Date(notification.sentAt).toLocaleString()}
                </p>
              </div>
            )}
            
            {notification.contentId && (
              <div>
                <Label className="text-sm font-medium">Related Content</Label>
                <p className="text-sm text-muted-foreground mt-1">
                  {notification.contentId}
                </p>
              </div>
            )}
            
            {notification.errorMessage && (
              <Alert className="border-red-200">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Delivery Error</AlertTitle>
                <AlertDescription>{notification.errorMessage}</AlertDescription>
              </Alert>
            )}
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <motion.div className="space-y-6" {...motionProps}>
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground">Notifications</h2>
          <p className="text-muted-foreground">
            Manage notification history and send custom messages
          </p>
        </div>
        
        <Dialog open={isComposeDialogOpen} onOpenChange={setIsComposeDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Compose
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[525px]">
            <DialogHeader>
              <DialogTitle>Send Custom Notification</DialogTitle>
              <DialogDescription>
                Send a custom notification to specific recipients.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="notificationType" className="text-right">
                  Type
                </Label>
                <Select 
                  value={newNotification.type} 
                  onValueChange={(value) => setNewNotification({...newNotification, type: value})}
                >
                  <SelectTrigger className="col-span-3">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="email">Email</SelectItem>
                    <SelectItem value="slack">Slack</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="recipients" className="text-right">
                  Recipients
                </Label>
                <Input
                  id="recipients"
                  value={newNotification.recipients}
                  onChange={(e) => setNewNotification({...newNotification, recipients: e.target.value})}
                  className="col-span-3"
                  placeholder="email1@company.com, email2@company.com"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="subject" className="text-right">
                  Subject
                </Label>
                <Input
                  id="subject"
                  value={newNotification.subject}
                  onChange={(e) => setNewNotification({...newNotification, subject: e.target.value})}
                  className="col-span-3"
                  placeholder="Notification subject"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="message" className="text-right">
                  Message
                </Label>
                <Textarea
                  id="message"
                  value={newNotification.message}
                  onChange={(e) => setNewNotification({...newNotification, message: e.target.value})}
                  className="col-span-3"
                  placeholder="Notification message..."
                  rows={4}
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="submit" onClick={handleSendNotification}>
                <Send className="h-4 w-4 mr-2" />
                Send Notification
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sent</CardTitle>
            <Send className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {notifications.filter(n => n.status === 'sent').length}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <Clock className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {notifications.filter(n => n.status === 'pending').length}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Failed</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {notifications.filter(n => n.status === 'failed').length}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((notifications.filter(n => n.status === 'sent').length / notifications.length) * 100).toFixed(1)}%
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
                  placeholder="Search notifications..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="sent">Sent</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="email">Email</SelectItem>
                <SelectItem value="slack">Slack</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Notifications Table */}
      <Card>
        <CardHeader>
          <CardTitle>Notification History</CardTitle>
          <CardDescription>
            {filteredNotifications.length} of {notifications.length} notifications
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Subject</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Recipients</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Sent At</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredNotifications.map((notification) => (
                <TableRow key={notification.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div className="space-y-1">
                      <span className="font-medium">{notification.subject}</span>
                      <div className="flex items-center space-x-2">
                        {getNotificationTypeBadge(notification.notificationType)}
                        {notification.contentId && (
                          <Badge variant="outline" className="text-xs">
                            {notification.contentId}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      {getTypeIcon(notification.type)}
                      <span className="capitalize">{notification.type}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="space-y-1">
                      {notification.recipients.slice(0, 2).map((recipient, index) => (
                        <div key={index} className="flex items-center space-x-1 text-sm">
                          <User className="h-3 w-3 text-muted-foreground" />
                          <span>{recipient}</span>
                        </div>
                      ))}
                      {notification.recipients.length > 2 && (
                        <span className="text-xs text-muted-foreground">
                          +{notification.recipients.length - 2} more
                        </span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(notification.status)}
                      {getStatusBadge(notification.status)}
                    </div>
                  </TableCell>
                  <TableCell>
                    {notification.sentAt ? (
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">
                          {new Date(notification.sentAt).toLocaleDateString()}
                        </span>
                      </div>
                    ) : (
                      <span className="text-sm text-muted-foreground">Not sent</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => setSelectedNotification(notification)}
                      >
                        <Eye className="h-4 w-4" />
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

      {/* Notification Detail Dialog */}
      <NotificationDetailDialog 
        notification={selectedNotification}
        open={!!selectedNotification}
        onOpenChange={(open) => !open && setSelectedNotification(null)}
      />
    </motion.div>
  )
}

export default Notifications

