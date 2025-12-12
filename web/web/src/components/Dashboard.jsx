import React, { useState, useEffect } from 'react';
import { Server, Globe, Users, Clock, RefreshCw, Moon, Sun } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getServers, getDomainsByServer, getSummary } from '@/api/axigen';

const Dashboard = () => {
  const [darkMode, setDarkMode] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalServers: 0,
    totalDomains: 0,
    totalAccounts: 0,
    lastSnapshot: null
  });
  const [servers, setServers] = useState([]);
  const [allDomains, setAllDomains] = useState([]);

const fetchData = async () => {
  try {
    setLoading(true);
    setError(null);
    
    // Fetch summary stats from API
    const summaryData = await getSummary();
    
    setStats({
      totalServers: summaryData.servers_count,
      totalDomains: summaryData.domains_count,
      totalAccounts: summaryData.accounts_count,
      lastSnapshot: summaryData.last_snapshot_time
    });
    
    // Fetch servers
    const serversData = await getServers();
    setServers(serversData);
    
    // Fetch domains for all servers
    const domainsPromises = serversData.map(server => 
      getDomainsByServer(server.id).catch(() => [])
    );
    const domainsArrays = await Promise.all(domainsPromises);
    const allDomainsData = domainsArrays.flat();
    setAllDomains(allDomainsData);
    
    setLoading(false);
  } catch (err) {
    setError(err.message);
    setLoading(false);
  }
};
  useEffect(() => {
    fetchData();
  }, []);

  const toggleTheme = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No data';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'dark bg-gradient-to-br from-gray-900 via-blue-950 to-gray-900' : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-violet-50'}`}>
      {/* Top Navbar */}
      <nav className={`backdrop-blur-lg border-b sticky top-0 z-50 ${darkMode ? 'bg-gray-900/50 border-blue-500/20' : 'bg-white/70 border-blue-200 shadow-sm'}`}>
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg">
                <Server className="text-white" size={24} />
              </div>
              <h1 className={`text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent`}>
                Axigen Monitor
              </h1>
            </div>
            
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                size="icon"
                onClick={toggleTheme}
                className={darkMode ? 'bg-gray-800/50 border-blue-500/30 hover:bg-gray-700/50' : 'bg-white border-blue-200 hover:bg-blue-50'}
              >
                {darkMode ? <Sun className="text-blue-400" size={20} /> : <Moon className="text-blue-600" size={20} />}
              </Button>
              <Button
                variant="outline"
                onClick={fetchData}
                disabled={loading}
                className={darkMode ? 'bg-gray-800/50 border-blue-500/30 hover:bg-gray-700/50 text-blue-400' : 'bg-white border-blue-200 hover:bg-blue-50 text-blue-600'}
              >
                <RefreshCw className={loading ? 'animate-spin' : ''} size={20} />
                <span className="ml-2">Refresh</span>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8">
        {/* Error Banner */}
        {error && (
          <div className={`mb-6 p-4 rounded-lg ${darkMode ? 'bg-red-500/10 border border-red-500/30' : 'bg-red-50 border border-red-200'}`}>
            <p className={darkMode ? 'text-red-400' : 'text-red-600'}>Network Error: {error}</p>
          </div>
        )}

        {/* Section 1: Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Servers Card */}
          <Card className={`transition-all ${darkMode ? 'bg-gradient-to-br from-blue-500/10 to-blue-600/5 border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/20' : 'bg-white border-blue-200 hover:shadow-xl hover:shadow-blue-500/30'}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Total Servers</CardTitle>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${darkMode ? 'bg-blue-500/20' : 'bg-blue-100'}`}>
                <Server className={darkMode ? 'text-blue-400' : 'text-blue-600'} size={20} />
              </div>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>{stats.totalServers}</div>
              <p className={`text-xs mt-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Active mail servers</p>
            </CardContent>
          </Card>

          {/* Total Domains Card */}
          <Card className={`transition-all ${darkMode ? 'bg-gradient-to-br from-indigo-500/10 to-indigo-600/5 border-indigo-500/30 hover:shadow-lg hover:shadow-indigo-500/20' : 'bg-white border-indigo-200 hover:shadow-xl hover:shadow-indigo-500/30'}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Total Domains</CardTitle>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${darkMode ? 'bg-indigo-500/20' : 'bg-indigo-100'}`}>
                <Globe className={darkMode ? 'text-indigo-400' : 'text-indigo-600'} size={20} />
              </div>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${darkMode ? 'text-indigo-400' : 'text-indigo-600'}`}>{stats.totalDomains}</div>
              <p className={`text-xs mt-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Hosted domains</p>
            </CardContent>
          </Card>

          {/* Total Accounts Card */}
          <Card className={`transition-all ${darkMode ? 'bg-gradient-to-br from-violet-500/10 to-violet-600/5 border-violet-500/30 hover:shadow-lg hover:shadow-violet-500/20' : 'bg-white border-violet-200 hover:shadow-xl hover:shadow-violet-500/30'}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Total Accounts</CardTitle>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${darkMode ? 'bg-violet-500/20' : 'bg-violet-100'}`}>
                <Users className={darkMode ? 'text-violet-400' : 'text-violet-600'} size={20} />
              </div>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${darkMode ? 'text-violet-400' : 'text-violet-600'}`}>{stats.totalAccounts}</div>
              <p className={`text-xs mt-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Email accounts</p>
            </CardContent>
          </Card>

          {/* Last Snapshot Card */}
          <Card className={`transition-all ${darkMode ? 'bg-gradient-to-br from-cyan-500/10 to-cyan-600/5 border-cyan-500/30 hover:shadow-lg hover:shadow-cyan-500/20' : 'bg-white border-cyan-200 hover:shadow-xl hover:shadow-cyan-500/30'}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Last Snapshot</CardTitle>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${darkMode ? 'bg-cyan-500/20' : 'bg-cyan-100'}`}>
                <Clock className={darkMode ? 'text-cyan-400' : 'text-cyan-600'} size={20} />
              </div>
            </CardHeader>
            <CardContent>
              <div className={`text-sm font-semibold ${darkMode ? 'text-cyan-400' : 'text-cyan-600'}`}>{formatDate(stats.lastSnapshot)}</div>
              <div className="flex items-center mt-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2"></div>
                <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Live data</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Section 2: Server Overview */}
        <Card className={`mb-8 ${darkMode ? 'bg-gray-800/50 border-gray-700/50' : 'bg-white border-gray-200 shadow-md'}`}>
          <CardHeader>
            <CardTitle className={`text-xl font-bold flex items-center ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>
              <Server className="mr-2" size={24} />
              Server Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className={`text-center py-8 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Loading servers...</div>
            ) : servers.length === 0 ? (
              <div className={`text-center py-8 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>No servers found</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className={`border-b ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
                      <th className={`text-left py-3 px-4 text-sm font-semibold ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Server Name</th>
                      <th className={`text-left py-3 px-4 text-sm font-semibold ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Hostname/IP</th>
                      <th className={`text-left py-3 px-4 text-sm font-semibold ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>CLI Port</th>
                      <th className={`text-left py-3 px-4 text-sm font-semibold ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>WebAdmin Port</th>
                    </tr>
                  </thead>
                  <tbody>
                    {servers.map((server, idx) => (
                      <tr key={server.id} className={`border-b transition-colors ${darkMode ? 'border-gray-700/50 hover:bg-blue-500/5' : 'border-gray-100 hover:bg-blue-50'}`}>
                        <td className={`py-3 px-4 font-medium ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>{server.name}</td>
                        <td className={`py-3 px-4 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>{server.hostname}</td>
                        <td className={`py-3 px-4 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>{server.cli_port}</td>
                        <td className={`py-3 px-4 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>{server.webadmin_port}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Section 3: Domain Overview */}
        <Card className={`mb-8 ${darkMode ? 'bg-gray-800/50 border-gray-700/50' : 'bg-white border-gray-200 shadow-md'}`}>
          <CardHeader>
            <CardTitle className={`text-xl font-bold flex items-center ${darkMode ? 'text-indigo-400' : 'text-indigo-600'}`}>
              <Globe className="mr-2" size={24} />
              Domain Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className={`text-center py-8 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Loading domains...</div>
            ) : allDomains.length === 0 ? (
              <div className={`text-center py-8 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>No domains found</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {allDomains.map((domain) => (
                  <div
                    key={domain.id}
                    className={`p-4 rounded-lg transition-all ${darkMode ? 'bg-gradient-to-br from-gray-700/30 to-gray-800/30 border border-gray-600/50 hover:border-indigo-500/50' : 'bg-gradient-to-br from-white to-indigo-50/30 border border-indigo-100 hover:border-indigo-300 hover:shadow-lg'}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className={`font-semibold ${darkMode ? 'text-indigo-400' : 'text-indigo-600'}`}>{domain.name}</h3>
                      <Badge variant={domain.status === 'enabled' ? 'default' : 'secondary'} className={domain.status === 'enabled' ? (darkMode ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' : 'bg-blue-100 text-blue-700 border-blue-200') : (darkMode ? '' : 'bg-gray-100 text-gray-600 border-gray-200')}>
                        {domain.status}
                      </Badge>
                    </div>
                    <div className={`flex items-center text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                      <Users size={16} className={`mr-2 ${darkMode ? 'text-violet-400' : 'text-violet-600'}`} />
                      <span>{domain.total_accounts} accounts</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Section 4: Footer Banner */}
        <div className={`rounded-lg p-4 text-center ${darkMode ? 'bg-gradient-to-r from-blue-500/10 to-indigo-500/10 border border-blue-500/30' : 'bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200'}`}>
          <p className={darkMode ? 'text-gray-300' : 'text-gray-700'}>
            Last Snapshot taken at: <span className={`font-semibold ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>{formatDate(stats.lastSnapshot)}</span>
            {' '}<span className={darkMode ? 'text-gray-500' : 'text-gray-400'}>• Auto-refreshed on demand</span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;