
import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Sidebar from './components/SideBar'
import Placeholder from './pages/PlaceholderPage'
import './App.css'
import DashboardPage from './pages/DashboardPage'
import PlaceholderPage from './pages/PlaceholderPage'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header setSidebarOpen={setSidebarOpen} />
          
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-4">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/servers" element={<PlaceholderPage title="Servers" />} />
              <Route path="/domains" element={<PlaceholderPage title="Domains" />} />
              <Route path="/add-server" element={<PlaceholderPage title="Add Server" />} />
              <Route path="/delete-server" element={<PlaceholderPage title="Delete Server" />} />
              <Route path="//server/:serverName" element={<PlaceholderPage title="Server Details" />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App
