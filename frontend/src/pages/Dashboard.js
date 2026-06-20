import React from 'react';
import { Link } from 'react-router-dom';
import { Bot, Home, Activity, MessageSquare, Settings, Bell, Search, HeartPulse, Sparkles } from 'lucide-react';

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-[#0a0a0c] flex text-white font-sans">
      {/* Sidebar */}
      <aside className="w-64 glass border-r border-white/5 flex flex-col hidden md:flex">
        <div className="p-6 border-b border-white/5">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="bg-gradient-primary p-2 rounded-lg">
              <Bot size={20} className="text-white" />
            </div>
            <span className="text-lg font-bold tracking-wide">PetVerse <span className="text-purple-400">AI</span></span>
          </Link>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <a href="#" className="flex items-center gap-3 px-4 py-3 bg-white/10 text-white rounded-xl font-medium transition-colors">
            <Home size={18} /> Overview
          </a>
          <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-400 hover:bg-white/5 hover:text-white rounded-xl font-medium transition-colors">
            <Activity size={18} /> Health Metrics
          </a>
          <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-400 hover:bg-white/5 hover:text-white rounded-xl font-medium transition-colors">
            <MessageSquare size={18} /> AI Assistant
          </a>
          <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-400 hover:bg-white/5 hover:text-white rounded-xl font-medium transition-colors">
            <Settings size={18} /> Settings
          </a>
        </nav>
        <div className="p-4 border-t border-white/5">
          <div className="flex items-center gap-3 px-4 py-2">
            <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center font-bold">U</div>
            <div className="text-sm">
              <p className="font-semibold">User</p>
              <p className="text-gray-400 text-xs">Free Plan</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none"></div>
        
        {/* Top Header */}
        <header className="glass border-b border-white/5 px-8 py-4 flex items-center justify-between z-10">
          <div className="flex items-center bg-black/50 border border-white/10 rounded-full px-4 py-2 w-96">
            <Search size={18} className="text-gray-400" />
            <input type="text" placeholder="Search insights, logs..." className="bg-transparent border-none outline-none text-sm text-white ml-2 w-full placeholder-gray-500" />
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 rounded-full hover:bg-white/10 text-gray-400 hover:text-white transition-colors relative">
              <Bell size={20} />
              <span className="absolute top-1 right-1 w-2 h-2 bg-purple-500 rounded-full"></span>
            </button>
            <button className="bg-gradient-primary px-4 py-2 rounded-full text-sm font-bold flex items-center gap-2">
              <Sparkles size={16} /> Upgrade
            </button>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="flex-1 overflow-y-auto p-8 z-10">
          <div className="flex justify-between items-end mb-8">
            <div>
              <h1 className="text-3xl font-bold mb-1">Max's Overview</h1>
              <p className="text-gray-400">Here's what your AI has analyzed today.</p>
            </div>
            <div className="bg-green-500/10 text-green-400 border border-green-500/20 px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-2 animate-pulse-slow">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div> Live Syncing
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="glass-card p-6 rounded-3xl">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-red-500/20 rounded-xl"><HeartPulse size={24} className="text-red-400" /></div>
                <h3 className="text-gray-400 font-medium">Heart Rate</h3>
              </div>
              <p className="text-4xl font-bold mb-2">102 <span className="text-lg text-gray-500 font-normal">bpm</span></p>
              <p className="text-sm text-green-400 flex items-center gap-1">Resting normal</p>
            </div>
            
            <div className="glass-card p-6 rounded-3xl">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-cyan-500/20 rounded-xl"><Activity size={24} className="text-cyan-400" /></div>
                <h3 className="text-gray-400 font-medium">Activity Level</h3>
              </div>
              <p className="text-4xl font-bold mb-2">High</p>
              <p className="text-sm text-gray-400">2.5 hours active today</p>
            </div>

            <div className="glass-card p-6 rounded-3xl bg-gradient-to-br from-purple-900/40 to-black border-purple-500/30 relative overflow-hidden">
              <Sparkles size={100} className="absolute -bottom-4 -right-4 text-purple-500/10" />
              <h3 className="text-purple-300 font-medium mb-2">AI Assessment</h3>
              <p className="text-xl font-semibold leading-snug">Max is feeling exceptionally energetic and happy.</p>
              <button className="mt-4 text-sm text-white bg-purple-600/30 hover:bg-purple-600/50 px-4 py-2 rounded-lg transition-colors border border-purple-500/30">View Full Report</button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-card p-6 rounded-3xl min-h-[300px] flex flex-col">
              <h3 className="text-lg font-bold mb-4">Recent Behavioral Logs</h3>
              <div className="flex-1 flex items-center justify-center text-gray-500">
                Mock Timeline Chart Area
              </div>
            </div>
            <div className="glass-card p-6 rounded-3xl min-h-[300px] flex flex-col relative overflow-hidden group">
               <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent z-10"></div>
               <img src="https://images.unsplash.com/photo-1543466835-00a7907e9de1?q=80&w=1000&auto=format&fit=crop" alt="Dog Cam" className="absolute inset-0 w-full h-full object-cover opacity-50 mix-blend-luminosity" />
               <div className="relative z-20 flex justify-between items-center mb-4">
                 <h3 className="text-lg font-bold text-white shadow-black drop-shadow-md">Live Smart-Cam Feed</h3>
                 <span className="bg-red-500 px-2 py-1 rounded text-xs font-bold uppercase tracking-wider animate-pulse">Live</span>
               </div>
               <div className="relative z-20 mt-auto">
                 <p className="text-sm text-gray-300 drop-shadow-md">AI detecting: Resting near window.</p>
               </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
