
import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Sidebar from './components/SideBar'
import SingleServerPage from './pages/SingleServerPage'
import './App.css'
import DashboardPage from './pages/DashboardPage'
import PlaceholderPage from './pages/PlaceholderPage'
import DomainPage from "./pages/DomainPage" // The domain page component
import ServersPage from './pages/ServerPage'
import AddServerPage from './pages/add_server'
import DeleteServerPage from './pages/delete_server'
import PollDataPage from './pages/PollDataPage'


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
              <Route path="/servers" element={<ServersPage title="Servers" />} />
              <Route path="/add-server" element={<AddServerPage title="Add Server" />} />
              <Route path="/delete-server" element={<DeleteServerPage title="Delete Server" />} />
              <Route path="/server/:serverName" element={<SingleServerPage title="Server Details" />} />
              <Route path="/domain/:domain" element={<DomainPage title="Domain Details"/>} />
              <Route path="/poll-data" element={<PollDataPage title="Poll Data"/>} />
              
              
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App
