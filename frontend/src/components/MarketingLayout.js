import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { Bot } from 'lucide-react';

const MarketingLayout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col font-sans">
      <nav className="fixed w-full z-50 glass border-b-0 px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="bg-gradient-primary p-2 rounded-lg group-hover:animate-pulse">
            <Bot size={24} className="text-white" />
          </div>
          <span className="text-xl font-bold text-white tracking-wide">PetVerse <span className="text-purple-400">AI</span></span>
        </Link>
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-300">
          <Link to="/about" className="hover:text-white transition-colors">About</Link>
          <Link to="/products" className="hover:text-white transition-colors">Products</Link>
          <Link to="/solutions" className="hover:text-white transition-colors">Solutions</Link>
          <Link to="/pricing" className="hover:text-white transition-colors">Pricing</Link>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/login" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">Login</Link>
          <Link to="/signup" className="text-sm font-semibold bg-gradient-primary text-white px-5 py-2 rounded-full hover:shadow-[0_0_15px_rgba(168,85,247,0.5)] transition-all">Get Started</Link>
        </div>
      </nav>
      
      <main className="flex-grow pt-24 pb-12">
        {children}
      </main>

      <footer className="glass-card mt-auto border-t border-white/5 py-12 px-6">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Bot size={20} className="text-purple-400" />
              <span className="text-lg font-bold text-white">PetVerse AI</span>
            </div>
            <p className="text-sm text-gray-400">Empowering pet parents with state-of-the-art artificial intelligence.</p>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Platform</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link to="/products">Features</Link></li>
              <li><Link to="/pricing">Pricing</Link></li>
              <li><Link to="/technology">Technology</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link to="/about">About Us</Link></li>
              <li><Link to="/contact">Contact</Link></li>
              <li><Link to="#">Careers</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link to="#">Privacy Policy</Link></li>
              <li><Link to="#">Terms of Service</Link></li>
            </ul>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MarketingLayout;
