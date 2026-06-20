import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Activity, Brain, ShieldCheck } from 'lucide-react';

const Home = () => {
  return (
    <div className="max-w-7xl mx-auto px-6">
      {/* Hero Section */}
      <section className="py-20 md:py-32 flex flex-col items-center text-center relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-600/20 rounded-full blur-[120px] -z-10 pointer-events-none"></div>
        <div className="inline-block px-4 py-1.5 rounded-full glass border-purple-500/30 text-purple-300 text-sm font-medium mb-8 animate-float">
          ✨ The Future of Pet Care is Here
        </div>
        <h1 className="text-5xl md:text-7xl font-extrabold text-white tracking-tight leading-tight mb-8">
          Understand your pet with <br className="hidden md:block" />
          <span className="text-gradient">Superintelligent AI</span>
        </h1>
        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-12">
          PetVerse AI monitors health, translates behaviors, and provides real-time veterinary insights using bleeding-edge neural networks.
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <Link to="/signup" className="flex items-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-colors">
            Start Free Trial <ArrowRight size={20} />
          </Link>
          <Link to="/technology" className="flex items-center gap-2 glass px-8 py-4 rounded-full font-bold text-white hover:bg-white/10 transition-colors">
            View Technology
          </Link>
        </div>
      </section>

      {/* Feature Bento Grid */}
      <section className="py-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 glass-card p-8 rounded-3xl relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-600/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <Activity className="w-12 h-12 text-cyan-400 mb-6" />
            <h3 className="text-2xl font-bold text-white mb-4">Real-time Biometrics</h3>
            <p className="text-gray-400 max-w-md">Sync with any smart collar to track heart rate, activity levels, and sleep quality instantly.</p>
            <div className="mt-8 h-48 rounded-xl bg-black/50 border border-white/5 flex items-end p-4 gap-2">
              {/* Mock Bar Chart */}
              {[40, 70, 45, 90, 65, 80, 50].map((h, i) => (
                <div key={i} className="w-full bg-gradient-primary rounded-t-sm animate-pulse-slow" style={{ height: `${h}%`, animationDelay: `${i * 0.1}s` }}></div>
              ))}
            </div>
          </div>
          
          <div className="glass-card p-8 rounded-3xl relative overflow-hidden">
            <Brain className="w-12 h-12 text-purple-400 mb-6" />
            <h3 className="text-2xl font-bold text-white mb-4">Behavioral Analysis</h3>
            <p className="text-gray-400">Our LLM interprets barks, whines, and body language to tell you exactly how your pet is feeling.</p>
          </div>

          <div className="glass-card p-8 rounded-3xl relative overflow-hidden">
            <ShieldCheck className="w-12 h-12 text-green-400 mb-6" />
            <h3 className="text-2xl font-bold text-white mb-4">Vet-Grade Security</h3>
            <p className="text-gray-400">All data is encrypted and securely shared only with your authorized veterinary professionals.</p>
          </div>

          <div className="md:col-span-3 glass-card p-0 rounded-3xl relative overflow-hidden flex flex-col md:flex-row min-h-[300px]">
            <div className="p-10 flex flex-col justify-center relative z-10 w-full md:w-1/2">
              <h3 className="text-3xl font-bold text-white mb-4">Meet your new co-parent.</h3>
              <p className="text-gray-400 max-w-sm mb-8">Join thousands of pet owners who have upgraded their pet's lifestyle with PetVerse AI.</p>
              <Link to="/signup" className="inline-block bg-gradient-primary px-8 py-4 rounded-full text-white font-bold w-max hover:scale-105 transition-transform">
                Join the Revolution
              </Link>
            </div>
            <div className="w-full md:w-1/2 relative min-h-[250px]">
              <img src="https://images.unsplash.com/photo-1583337130417-3346a1be7dee?q=80&w=1000&auto=format&fit=crop" alt="Cute Dog" className="absolute inset-0 w-full h-full object-cover opacity-60 mix-blend-luminosity" style={{ maskImage: 'linear-gradient(to right, transparent, black 20%)', WebkitMaskImage: 'linear-gradient(to right, transparent, black 20%)' }} />
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
