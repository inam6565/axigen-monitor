
import { FiHome, FiServer, FiGlobe, FiPlusCircle, FiTrash2 } from 'react-icons/fi'
import { NavLink } from 'react-router-dom'

const Sidebar = ({ sidebarOpen, setSidebarOpen }) => {
  return (
    <div className={`${sidebarOpen ? 'w-64' : 'w-20'} sidebar-transition bg-white shadow-md flex flex-col`}>
      <div className="flex items-center justify-center h-16 border-b border-gray-200">
        <h1 className={`${sidebarOpen ? 'block' : 'hidden'} text-xl font-semibold text-primary-600`}>Axigen Monitor</h1>
        <div className={`${sidebarOpen ? 'hidden' : 'block'} text-primary-600`}>
          <FiServer className="h-6 w-6" />
        </div>
      </div>
      
      <nav className="flex-1 overflow-y-auto">
        <ul className="py-4">
          <li>
            <NavLink
              to="/"
              className={({ isActive }) => 
                `flex items-center px-4 py-3 ${isActive ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-50'}`
              }
            >
              <FiHome className="h-5 w-5" />
              <span className={`ml-3 ${sidebarOpen ? 'block' : 'hidden'}`}>Dashboard</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/servers"
              className={({ isActive }) => 
                `flex items-center px-4 py-3 ${isActive ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-50'}`
              }
            >
              <FiServer className="h-5 w-5" />
              <span className={`ml-3 ${sidebarOpen ? 'block' : 'hidden'}`}>Servers</span>
            </NavLink>
          </li>

          <li className="border-t border-gray-200 mt-2 pt-2">
            <NavLink
              to="/add-server"
              className={({ isActive }) => 
                `flex items-center px-4 py-3 ${isActive ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-50'}`
              }
            >
              <FiPlusCircle className="h-5 w-5" />
              <span className={`ml-3 ${sidebarOpen ? 'block' : 'hidden'}`}>Add Server</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/delete-server"
              className={({ isActive }) => 
                `flex items-center px-4 py-3 ${isActive ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-50'}`
              }
            >
              <FiTrash2 className="h-5 w-5" />
              <span className={`ml-3 ${sidebarOpen ? 'block' : 'hidden'}`}>Delete Server</span>
            </NavLink>
          </li>
        </ul>
      </nav>
    </div>
  )
}

export default Sidebar

