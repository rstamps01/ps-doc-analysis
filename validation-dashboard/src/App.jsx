import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Clock, 
  FileText, 
  Settings, 
  Bell,
  BarChart3,
  Shield,
  Database,
  Users,
  Activity,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react'

import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert.jsx'

import RealDataDashboard from './components/RealDataDashboard';
import ValidationRequests from './components/ValidationRequests';
import ValidationResults from './components/ValidationResults';
import RulesManagement from './components/RulesManagement';
import SystemSettings from './components/SystemSettings';
import Notifications from './components/Notifications';
import EnhancedValidation from './components/EnhancedValidation';
import GoogleIntegration from './components/GoogleIntegration';
import Sidebar from './components/Sidebar.jsx'

import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [darkMode, setDarkMode] = useState(false)
  const [systemStats, setSystemStats] = useState({
    totalValidations: 0,
    passRate: 0,
    avgScore: 0,
    activeProjects: 0
  })

  useEffect(() => {
    // Simulate loading system stats
    const loadStats = async () => {
      // Mock API call
      setTimeout(() => {
        setSystemStats({
          totalValidations: 1247,
          passRate: 94.2,
          avgScore: 8.7,
          activeProjects: 23
        })
      }, 1000)
    }
    
    loadStats()
  }, [])

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
  }

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <RealDataDashboard />
      case 'requests':
        return <ValidationRequests />
      case 'results':
        return <ValidationResults />
      case 'rules':
        return <RulesManagement />
      case 'enhanced':
        return <EnhancedValidation />
      case 'google':
        return <GoogleIntegration />
      case 'notifications':
        return <Notifications />
      case 'settings':
        return <SystemSettings />
      default:
        return <RealDataDashboard />
    }
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
        {/* Sidebar */}
        <Sidebar 
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          darkMode={darkMode}
          toggleDarkMode={toggleDarkMode}
        />

        {/* Main Content */}
        <div className={`flex-1 flex flex-col overflow-hidden transition-all duration-300 ${
          sidebarOpen ? 'ml-64' : 'ml-16'
        }`}>
          {/* Header */}
          <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
            <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Information Validation Tool
                  </h1>
                </div>
                
                <div className="flex items-center space-x-4">
                  {/* System Stats */}
                  <div className="hidden md:flex items-center space-x-6 text-sm text-gray-600 dark:text-gray-300">
                    <div className="flex items-center space-x-1">
                      <Activity className="w-4 h-4" />
                      <span>{systemStats.totalValidations} validations</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>{systemStats.passRate}% pass rate</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <FileText className="w-4 h-4" />
                      <span>{systemStats.activeProjects} active projects</span>
                    </div>
                  </div>
                  
                  {/* Dark Mode Toggle */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setDarkMode(!darkMode)}
                    className="p-2"
                  >
                    {darkMode ? '☀️' : '🌙'}
                  </Button>
                  
                  {/* Notifications */}
                  <Button variant="ghost" size="sm" className="p-2">
                    <Bell className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </header>

          {/* Page Content */}
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 dark:bg-gray-900">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentPage}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
                className="h-full"
              >
                {renderCurrentPage()}
              </motion.div>
            </AnimatePresence>
          </main>
        </div>
      </div>
    </div>
  )
}

export default App

