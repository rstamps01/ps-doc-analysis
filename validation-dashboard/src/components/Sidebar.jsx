import { motion } from 'framer-motion'
import { 
  BarChart3, 
  FileText, 
  CheckCircle, 
  Settings, 
  Shield, 
  Bell,
  Moon,
  Sun,
  ChevronLeft,
  ChevronRight,
  Activity,
  Zap,
  Link2
} from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'

const Sidebar = ({ 
  currentPage, 
  setCurrentPage, 
  sidebarOpen, 
  setSidebarOpen, 
  darkMode, 
  toggleDarkMode 
}) => {
  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: BarChart3,
      badge: null
    },
    {
      id: 'requests',
      label: 'Validation Requests',
      icon: FileText,
      badge: '12'
    },
    {
      id: 'results',
      label: 'Results',
      icon: CheckCircle,
      badge: null
    },
    {
      id: 'rules',
      label: 'Rules Management',
      icon: Shield,
      badge: null
    },
    {
      id: 'enhanced',
      label: 'Enhanced Validation',
      icon: Zap,
      badge: 'NEW'
    },
    {
      id: 'google',
      label: 'Google Integration',
      icon: Link2,
      badge: 'NEW'
    },
    {
      id: 'notifications',
      label: 'Notifications',
      icon: Bell,
      badge: '3'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
      badge: null
    }
  ]

  const sidebarVariants = {
    open: { width: '16rem' },
    closed: { width: '4rem' }
  }

  const itemVariants = {
    open: { opacity: 1, x: 0 },
    closed: { opacity: 0, x: -10 }
  }

  return (
    <motion.div
      className="fixed left-0 top-0 h-full bg-sidebar border-r border-sidebar-border z-50"
      variants={sidebarVariants}
      animate={sidebarOpen ? 'open' : 'closed'}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
    >
      <div className="flex flex-col h-full">
        {/* Logo/Brand */}
        <div className="p-4 border-b border-sidebar-border">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Activity className="h-5 w-5 text-primary-foreground" />
            </div>
            {sidebarOpen && (
              <motion.div
                variants={itemVariants}
                animate={sidebarOpen ? 'open' : 'closed'}
                transition={{ delay: 0.1 }}
              >
                <h2 className="font-semibold text-sidebar-foreground">
                  Validation Tool
                </h2>
              </motion.div>
            )}
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = currentPage === item.id

            return (
              <Button
                key={item.id}
                variant={isActive ? 'default' : 'ghost'}
                className={`w-full justify-start h-12 ${
                  isActive 
                    ? 'bg-sidebar-primary text-sidebar-primary-foreground' 
                    : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                } ${!sidebarOpen ? 'px-3' : 'px-4'}`}
                onClick={() => setCurrentPage(item.id)}
              >
                <Icon className={`h-5 w-5 ${sidebarOpen ? 'mr-3' : ''}`} />
                {sidebarOpen && (
                  <motion.div
                    className="flex items-center justify-between w-full"
                    variants={itemVariants}
                    animate={sidebarOpen ? 'open' : 'closed'}
                    transition={{ delay: 0.1 }}
                  >
                    <span className="font-medium">{item.label}</span>
                    {item.badge && (
                      <Badge 
                        variant="secondary" 
                        className="ml-auto bg-sidebar-accent text-sidebar-accent-foreground"
                      >
                        {item.badge}
                      </Badge>
                    )}
                  </motion.div>
                )}
              </Button>
            )
          })}
        </nav>

        {/* Bottom Controls */}
        <div className="p-4 border-t border-sidebar-border space-y-2">
          {/* Dark Mode Toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleDarkMode}
            className={`w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground ${
              !sidebarOpen ? 'px-3' : 'px-4'
            }`}
          >
            {darkMode ? (
              <Sun className={`h-4 w-4 ${sidebarOpen ? 'mr-3' : ''}`} />
            ) : (
              <Moon className={`h-4 w-4 ${sidebarOpen ? 'mr-3' : ''}`} />
            )}
            {sidebarOpen && (
              <motion.span
                variants={itemVariants}
                animate={sidebarOpen ? 'open' : 'closed'}
                transition={{ delay: 0.1 }}
                className="font-medium"
              >
                {darkMode ? 'Light Mode' : 'Dark Mode'}
              </motion.span>
            )}
          </Button>

          {/* Collapse Toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className={`w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground ${
              !sidebarOpen ? 'px-3' : 'px-4'
            }`}
          >
            {sidebarOpen ? (
              <ChevronLeft className={`h-4 w-4 ${sidebarOpen ? 'mr-3' : ''}`} />
            ) : (
              <ChevronRight className={`h-4 w-4 ${sidebarOpen ? 'mr-3' : ''}`} />
            )}
            {sidebarOpen && (
              <motion.span
                variants={itemVariants}
                animate={sidebarOpen ? 'open' : 'closed'}
                transition={{ delay: 0.1 }}
                className="font-medium"
              >
                Collapse
              </motion.span>
            )}
          </Button>
        </div>
      </div>
    </motion.div>
  )
}

export default Sidebar

