import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Save, 
  RefreshCw,
  Database,
  Mail,
  Shield,
  Globe,
  Bell,
  Key,
  Server,
  CheckCircle,
  AlertCircle,
  Settings
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert.jsx'
import { Badge } from '@/components/ui/badge.jsx'

const SystemSettings = ({ ...motionProps }) => {
  const [settings, setSettings] = useState({
    // General Settings
    systemName: 'Information Validation Tool',
    systemDescription: 'Automated content validation and quality assurance',
    timezone: 'UTC',
    language: 'en',
    
    // API Integrations
    googleSheetsApiKey: '',
    confluenceBaseUrl: 'https://company.atlassian.net',
    confluenceUsername: '',
    confluenceApiToken: '',
    salesforceInstanceUrl: '',
    salesforceClientId: '',
    salesforceClientSecret: '',
    
    // Email Configuration
    smtpServer: 'smtp.gmail.com',
    smtpPort: 587,
    smtpUsername: '',
    smtpPassword: '',
    smtpUseTls: true,
    defaultSenderEmail: '',
    
    // Notification Settings
    enableEmailNotifications: true,
    enableSlackNotifications: false,
    notifyOnPass: true,
    notifyOnFail: true,
    notifyOnPartial: true,
    sendDailyReports: true,
    sendWeeklyReports: true,
    
    // Security Settings
    enableApiAuthentication: true,
    sessionTimeout: 3600,
    maxLoginAttempts: 5,
    enableAuditLogging: true,
    
    // Performance Settings
    maxConcurrentValidations: 10,
    validationTimeout: 300,
    cacheResults: true,
    cacheExpiration: 3600
  })

  const [connectionStatus, setConnectionStatus] = useState({
    googleSheets: 'unknown',
    confluence: 'unknown',
    salesforce: 'unknown',
    email: 'unknown'
  })

  const [isSaving, setIsSaving] = useState(false)

  const updateSetting = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const testConnection = async (service) => {
    setConnectionStatus(prev => ({
      ...prev,
      [service]: 'testing'
    }))
    
    // Simulate API call
    setTimeout(() => {
      const success = Math.random() > 0.3 // 70% success rate for demo
      setConnectionStatus(prev => ({
        ...prev,
        [service]: success ? 'connected' : 'failed'
      }))
    }, 2000)
  }

  const saveSettings = async () => {
    setIsSaving(true)
    
    // Simulate API call
    setTimeout(() => {
      setIsSaving(false)
      // Show success message
    }, 1500)
  }

  const getConnectionStatusBadge = (status) => {
    switch (status) {
      case 'connected':
        return <Badge className="bg-green-100 text-green-800">Connected</Badge>
      case 'failed':
        return <Badge className="bg-red-100 text-red-800">Failed</Badge>
      case 'testing':
        return <Badge className="bg-blue-100 text-blue-800">Testing...</Badge>
      default:
        return <Badge className="bg-gray-100 text-gray-800">Unknown</Badge>
    }
  }

  const getConnectionIcon = (status) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'testing':
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />
    }
  }

  return (
    <motion.div className="space-y-6" {...motionProps}>
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground">System Settings</h2>
          <p className="text-muted-foreground">
            Configure system integrations and preferences
          </p>
        </div>
        <Button onClick={saveSettings} disabled={isSaving}>
          {isSaving ? (
            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <Save className="h-4 w-4 mr-2" />
          )}
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>

      <Tabs defaultValue="general" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        {/* General Settings */}
        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="h-5 w-5" />
                <span>General Configuration</span>
              </CardTitle>
              <CardDescription>
                Basic system configuration and preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="systemName">System Name</Label>
                  <Input
                    id="systemName"
                    value={settings.systemName}
                    onChange={(e) => updateSetting('systemName', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="timezone">Timezone</Label>
                  <Select value={settings.timezone} onValueChange={(value) => updateSetting('timezone', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="UTC">UTC</SelectItem>
                      <SelectItem value="America/New_York">Eastern Time</SelectItem>
                      <SelectItem value="America/Chicago">Central Time</SelectItem>
                      <SelectItem value="America/Denver">Mountain Time</SelectItem>
                      <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="systemDescription">System Description</Label>
                <Textarea
                  id="systemDescription"
                  value={settings.systemDescription}
                  onChange={(e) => updateSetting('systemDescription', e.target.value)}
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Integration Settings */}
        <TabsContent value="integrations" className="space-y-6">
          {/* Google Sheets Integration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Database className="h-5 w-5" />
                  <span>Google Sheets Integration</span>
                </div>
                <div className="flex items-center space-x-2">
                  {getConnectionIcon(connectionStatus.googleSheets)}
                  {getConnectionStatusBadge(connectionStatus.googleSheets)}
                </div>
              </CardTitle>
              <CardDescription>
                Configure Google Sheets API for requirements management
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="googleSheetsApiKey">API Key</Label>
                <div className="flex space-x-2">
                  <Input
                    id="googleSheetsApiKey"
                    type="password"
                    value={settings.googleSheetsApiKey}
                    onChange={(e) => updateSetting('googleSheetsApiKey', e.target.value)}
                    placeholder="Enter Google Sheets API key"
                  />
                  <Button 
                    variant="outline" 
                    onClick={() => testConnection('googleSheets')}
                    disabled={connectionStatus.googleSheets === 'testing'}
                  >
                    Test
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Confluence Integration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Globe className="h-5 w-5" />
                  <span>Confluence Integration</span>
                </div>
                <div className="flex items-center space-x-2">
                  {getConnectionIcon(connectionStatus.confluence)}
                  {getConnectionStatusBadge(connectionStatus.confluence)}
                </div>
              </CardTitle>
              <CardDescription>
                Configure Confluence API for content validation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="confluenceBaseUrl">Base URL</Label>
                <Input
                  id="confluenceBaseUrl"
                  value={settings.confluenceBaseUrl}
                  onChange={(e) => updateSetting('confluenceBaseUrl', e.target.value)}
                  placeholder="https://company.atlassian.net"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="confluenceUsername">Username</Label>
                  <Input
                    id="confluenceUsername"
                    value={settings.confluenceUsername}
                    onChange={(e) => updateSetting('confluenceUsername', e.target.value)}
                    placeholder="user@company.com"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confluenceApiToken">API Token</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="confluenceApiToken"
                      type="password"
                      value={settings.confluenceApiToken}
                      onChange={(e) => updateSetting('confluenceApiToken', e.target.value)}
                      placeholder="Enter API token"
                    />
                    <Button 
                      variant="outline" 
                      onClick={() => testConnection('confluence')}
                      disabled={connectionStatus.confluence === 'testing'}
                    >
                      Test
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Salesforce Integration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Server className="h-5 w-5" />
                  <span>Salesforce Integration</span>
                  <Badge variant="outline">Optional</Badge>
                </div>
                <div className="flex items-center space-x-2">
                  {getConnectionIcon(connectionStatus.salesforce)}
                  {getConnectionStatusBadge(connectionStatus.salesforce)}
                </div>
              </CardTitle>
              <CardDescription>
                Configure Salesforce API for extended validation (stretch goal)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="salesforceInstanceUrl">Instance URL</Label>
                <Input
                  id="salesforceInstanceUrl"
                  value={settings.salesforceInstanceUrl}
                  onChange={(e) => updateSetting('salesforceInstanceUrl', e.target.value)}
                  placeholder="https://company.salesforce.com"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="salesforceClientId">Client ID</Label>
                  <Input
                    id="salesforceClientId"
                    value={settings.salesforceClientId}
                    onChange={(e) => updateSetting('salesforceClientId', e.target.value)}
                    placeholder="Enter client ID"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="salesforceClientSecret">Client Secret</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="salesforceClientSecret"
                      type="password"
                      value={settings.salesforceClientSecret}
                      onChange={(e) => updateSetting('salesforceClientSecret', e.target.value)}
                      placeholder="Enter client secret"
                    />
                    <Button 
                      variant="outline" 
                      onClick={() => testConnection('salesforce')}
                      disabled={connectionStatus.salesforce === 'testing'}
                    >
                      Test
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notification Settings */}
        <TabsContent value="notifications" className="space-y-6">
          {/* Email Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Mail className="h-5 w-5" />
                  <span>Email Configuration</span>
                </div>
                <div className="flex items-center space-x-2">
                  {getConnectionIcon(connectionStatus.email)}
                  {getConnectionStatusBadge(connectionStatus.email)}
                </div>
              </CardTitle>
              <CardDescription>
                Configure SMTP settings for email notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="smtpServer">SMTP Server</Label>
                  <Input
                    id="smtpServer"
                    value={settings.smtpServer}
                    onChange={(e) => updateSetting('smtpServer', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="smtpPort">SMTP Port</Label>
                  <Input
                    id="smtpPort"
                    type="number"
                    value={settings.smtpPort}
                    onChange={(e) => updateSetting('smtpPort', parseInt(e.target.value))}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="smtpUsername">Username</Label>
                  <Input
                    id="smtpUsername"
                    value={settings.smtpUsername}
                    onChange={(e) => updateSetting('smtpUsername', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="smtpPassword">Password</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="smtpPassword"
                      type="password"
                      value={settings.smtpPassword}
                      onChange={(e) => updateSetting('smtpPassword', e.target.value)}
                    />
                    <Button 
                      variant="outline" 
                      onClick={() => testConnection('email')}
                      disabled={connectionStatus.email === 'testing'}
                    >
                      Test
                    </Button>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="smtpUseTls"
                  checked={settings.smtpUseTls}
                  onCheckedChange={(checked) => updateSetting('smtpUseTls', checked)}
                />
                <Label htmlFor="smtpUseTls">Use TLS encryption</Label>
              </div>
            </CardContent>
          </Card>

          {/* Notification Preferences */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="h-5 w-5" />
                <span>Notification Preferences</span>
              </CardTitle>
              <CardDescription>
                Configure when and how notifications are sent
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="enableEmailNotifications">Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">Send email notifications for validation results</p>
                  </div>
                  <Switch
                    id="enableEmailNotifications"
                    checked={settings.enableEmailNotifications}
                    onCheckedChange={(checked) => updateSetting('enableEmailNotifications', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="notifyOnPass">Notify on Pass</Label>
                    <p className="text-sm text-muted-foreground">Send notifications when validation passes</p>
                  </div>
                  <Switch
                    id="notifyOnPass"
                    checked={settings.notifyOnPass}
                    onCheckedChange={(checked) => updateSetting('notifyOnPass', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="notifyOnFail">Notify on Fail</Label>
                    <p className="text-sm text-muted-foreground">Send notifications when validation fails</p>
                  </div>
                  <Switch
                    id="notifyOnFail"
                    checked={settings.notifyOnFail}
                    onCheckedChange={(checked) => updateSetting('notifyOnFail', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="sendDailyReports">Daily Reports</Label>
                    <p className="text-sm text-muted-foreground">Send daily summary reports</p>
                  </div>
                  <Switch
                    id="sendDailyReports"
                    checked={settings.sendDailyReports}
                    onCheckedChange={(checked) => updateSetting('sendDailyReports', checked)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Settings */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5" />
                <span>Security Configuration</span>
              </CardTitle>
              <CardDescription>
                Configure security and authentication settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="enableApiAuthentication">API Authentication</Label>
                  <p className="text-sm text-muted-foreground">Require authentication for API access</p>
                </div>
                <Switch
                  id="enableApiAuthentication"
                  checked={settings.enableApiAuthentication}
                  onCheckedChange={(checked) => updateSetting('enableApiAuthentication', checked)}
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="sessionTimeout">Session Timeout (seconds)</Label>
                  <Input
                    id="sessionTimeout"
                    type="number"
                    value={settings.sessionTimeout}
                    onChange={(e) => updateSetting('sessionTimeout', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="maxLoginAttempts">Max Login Attempts</Label>
                  <Input
                    id="maxLoginAttempts"
                    type="number"
                    value={settings.maxLoginAttempts}
                    onChange={(e) => updateSetting('maxLoginAttempts', parseInt(e.target.value))}
                  />
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="enableAuditLogging">Audit Logging</Label>
                  <p className="text-sm text-muted-foreground">Log all system activities for security auditing</p>
                </div>
                <Switch
                  id="enableAuditLogging"
                  checked={settings.enableAuditLogging}
                  onCheckedChange={(checked) => updateSetting('enableAuditLogging', checked)}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Settings */}
        <TabsContent value="performance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Server className="h-5 w-5" />
                <span>Performance Configuration</span>
              </CardTitle>
              <CardDescription>
                Configure system performance and resource limits
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="maxConcurrentValidations">Max Concurrent Validations</Label>
                  <Input
                    id="maxConcurrentValidations"
                    type="number"
                    value={settings.maxConcurrentValidations}
                    onChange={(e) => updateSetting('maxConcurrentValidations', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="validationTimeout">Validation Timeout (seconds)</Label>
                  <Input
                    id="validationTimeout"
                    type="number"
                    value={settings.validationTimeout}
                    onChange={(e) => updateSetting('validationTimeout', parseInt(e.target.value))}
                  />
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="cacheResults">Cache Results</Label>
                  <p className="text-sm text-muted-foreground">Cache validation results to improve performance</p>
                </div>
                <Switch
                  id="cacheResults"
                  checked={settings.cacheResults}
                  onCheckedChange={(checked) => updateSetting('cacheResults', checked)}
                />
              </div>
              
              {settings.cacheResults && (
                <div className="space-y-2">
                  <Label htmlFor="cacheExpiration">Cache Expiration (seconds)</Label>
                  <Input
                    id="cacheExpiration"
                    type="number"
                    value={settings.cacheExpiration}
                    onChange={(e) => updateSetting('cacheExpiration', parseInt(e.target.value))}
                  />
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </motion.div>
  )
}

export default SystemSettings

