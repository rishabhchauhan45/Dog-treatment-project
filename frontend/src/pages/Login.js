import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, ArrowRight, Bot } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleMockLogin = (e) => {
    e.preventDefault();
    // Mock login just navigates to dashboard
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen flex bg-black relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-purple-600/20 rounded-full blur-[150px] pointer-events-none"></div>
      <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-cyan-600/10 rounded-full blur-[120px] pointer-events-none"></div>

      <div className="flex-1 flex flex-col justify-center px-4 sm:px-6 lg:flex-none lg:px-20 xl:px-24 z-10 w-full lg:w-1/2">
        <div className="mx-auto w-full max-w-sm lg:w-96 glass-card p-10 rounded-3xl relative">
          <Link to="/" className="flex items-center gap-2 mb-10 group">
            <div className="bg-gradient-primary p-2 rounded-lg group-hover:animate-pulse">
              <Bot size={24} className="text-white" />
            </div>
            <span className="text-xl font-bold text-white tracking-wide">PetVerse <span className="text-purple-400">AI</span></span>
          </Link>
          
          <h2 className="text-3xl font-extrabold text-white mb-2">Welcome back</h2>
          <p className="text-sm text-gray-400 mb-8">Please enter your details to sign in.</p>

          <form onSubmit={handleMockLogin} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Email address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-500" />
                </div>
                <input
                  type="email"
                  className="block w-full pl-10 pr-3 py-3 border border-white/10 rounded-xl leading-5 bg-white/5 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 sm:text-sm transition-all"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-500" />
                </div>
                <input
                  type="password"
                  className="block w-full pl-10 pr-3 py-3 border border-white/10 rounded-xl leading-5 bg-white/5 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 sm:text-sm transition-all"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input type="checkbox" className="h-4 w-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500 bg-white/5" />
                <label className="ml-2 block text-sm text-gray-400">Remember me</label>
              </div>
              <div className="text-sm">
                <a href="#" className="font-medium text-purple-400 hover:text-purple-300">Forgot password?</a>
              </div>
            </div>

            <button type="submit" className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-bold text-white bg-gradient-primary hover:shadow-[0_0_15px_rgba(168,85,247,0.5)] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 focus:ring-offset-gray-900 transition-all">
              Sign in
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-gray-400">
            Don't have an account?{' '}
            <Link to="/signup" className="font-medium text-purple-400 hover:text-purple-300">Sign up now</Link>
          </p>
        </div>
      </div>

      <div className="hidden lg:block relative w-0 flex-1 z-10 p-4">
        <div className="absolute inset-0 m-4 rounded-[2.5rem] overflow-hidden">
          <img className="absolute inset-0 h-full w-full object-cover opacity-80 mix-blend-luminosity" src="https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=2000&auto=format&fit=crop" alt="Digital retro futuristic landscape" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
          <div className="absolute bottom-12 left-12 right-12 text-white">
            <h2 className="text-4xl font-bold mb-4">Discover the true voice of your companion.</h2>
            <p className="text-xl text-gray-300 max-w-lg">Advanced LLMs mapping bio-signals to human language. Know when they are happy, anxious, or needing care.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
