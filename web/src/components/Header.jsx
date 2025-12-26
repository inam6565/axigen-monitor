import { FiSearch, FiMenu, FiBell, FiUser } from 'react-icons/fi';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Header = ({ setSidebarOpen }) => {
  const [searchQuery, setSearchQuery] = useState(""); // Manage search input
  const navigate = useNavigate(); // Navigate to search results

  // Handle search logic when user presses Enter or clicks the search button
  const handleSearch = () => {
    if (!searchQuery) return;

    if (searchQuery.includes('@')) {
      // If search query contains '@', it's an account search
      const accountEmail = searchQuery;
      const domain = accountEmail.split('@')[1]; // Extract domain from email
      navigate(`/domain/${domain}?account=${accountEmail}`);
    } else {
      // If search query doesn't contain '@', it's a domain search
      navigate(`/domain/${searchQuery}`);
    }
  };

  // Handle the Enter key press
  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch(); // Trigger search when Enter key is pressed
    }
  };

  return (
    <header className="bg-white shadow-sm z-10">
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center">
          <button
            onClick={() => setSidebarOpen(prev => !prev)}
            className="text-gray-500 hover:text-gray-600 focus:outline-none"
          >
            <FiMenu className="h-6 w-6" />
          </button>
          
          <div className="ml-4 flex items-center space-x-2"> {/* Flex container for input and button */}
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FiSearch className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)} // Update search query
                onKeyDown={handleKeyPress} // Trigger search on Enter key press
                placeholder="Search domains..."
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
            {/* Search Button */}
            <button
              onClick={handleSearch}
              className="px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-800" // Light black color on default and dark black on hover
            >
              Search
            </button>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <button className="p-1 rounded-full text-gray-400 hover:text-gray-500 focus:outline-none">
            <FiBell className="h-6 w-6" />
          </button>
          <div className="flex items-center">
            <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
              <FiUser className="h-5 w-5 text-primary-600" />
            </div>
            <span className="ml-2 text-sm font-medium text-gray-700">Admin</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
