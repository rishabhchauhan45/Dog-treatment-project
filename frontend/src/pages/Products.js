import React from 'react';
import { ArrowRight, ShoppingBag, Star, Zap, Shield, Heart } from 'lucide-react';

const products = [
  {
    id: 1,
    name: "PetVerse Collar Pro",
    tagline: "The smartest collar ever built.",
    price: "$199",
    image: "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?q=80&w=600&auto=format&fit=crop",
    features: ["Real-time Vitals", "GPS Tracking", "Behavioral Insights"],
    icon: <Zap className="w-5 h-5 text-yellow-400" />
  },
  {
    id: 2,
    name: "Nutrition Analyzer Bowl",
    tagline: "Perfect portions, every time.",
    price: "$129",
    image: "https://images.unsplash.com/photo-1589924691995-400dc9ecc119?q=80&w=600&auto=format&fit=crop",
    features: ["Calorie Tracking", "Diet Recommendations", "Auto-weighing"],
    icon: <Heart className="w-5 h-5 text-pink-400" />
  },
  {
    id: 3,
    name: "AI Sleep Pod",
    tagline: "Recovery & comfort reimagined.",
    price: "$299",
    image: "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?q=80&w=600&auto=format&fit=crop",
    features: ["Temperature Control", "Sleep Analysis", "Orthopedic Foam"],
    icon: <Shield className="w-5 h-5 text-blue-400" />
  }
];

const Products = () => {
  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      {/* Header */}
      <div className="text-center mb-20 relative">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[400px] h-[400px] bg-cyan-500/20 rounded-full blur-[100px] -z-10 pointer-events-none"></div>
        <h1 className="text-4xl md:text-6xl font-extrabold text-white mb-6">
          Next-Generation <br className="hidden md:block" />
          <span className="text-gradient">Hardware Ecosystem</span>
        </h1>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto">
          Seamlessly integrated with PetVerse AI. Our hardware ecosystem gives you unprecedented insights into your pet's physical and mental wellbeing.
        </p>
      </div>

      {/* Product Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {products.map((product) => (
          <div key={product.id} className="glass-card rounded-3xl overflow-hidden group hover:-translate-y-2 transition-transform duration-300 flex flex-col">
            <div className="relative h-64 overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent z-10"></div>
              <img 
                src={product.image} 
                alt={product.name} 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
              />
              <div className="absolute bottom-4 left-4 z-20 flex items-center gap-2">
                <span className="glass px-3 py-1 rounded-full text-xs font-semibold text-white flex items-center gap-1">
                  <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" /> 4.9
                </span>
                <span className="glass px-3 py-1 rounded-full text-xs font-semibold text-white">
                  In Stock
                </span>
              </div>
            </div>
            
            <div className="p-6 flex flex-col flex-grow">
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-2xl font-bold text-white group-hover:text-cyan-400 transition-colors">
                  {product.name}
                </h3>
                <div className="p-2 glass rounded-lg bg-white/5">
                  {product.icon}
                </div>
              </div>
              <p className="text-gray-400 text-sm mb-6 flex-grow">{product.tagline}</p>
              
              <ul className="space-y-3 mb-8">
                {product.features.map((feature, idx) => (
                  <li key={idx} className="flex items-center gap-2 text-sm text-gray-300">
                    <div className="w-1.5 h-1.5 rounded-full bg-cyan-400"></div>
                    {feature}
                  </li>
                ))}
              </ul>
              
              <div className="flex items-center justify-between mt-auto pt-6 border-t border-white/10">
                <span className="text-3xl font-bold text-white">{product.price}</span>
                <button className="flex items-center gap-2 bg-white text-black px-5 py-2.5 rounded-full font-bold hover:bg-cyan-400 hover:text-white transition-colors group/btn">
                  <ShoppingBag size={18} />
                  Buy Now
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Call to Action Banner */}
      <div className="mt-24 glass-card p-10 md:p-16 rounded-3xl relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-8">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-cyan-500/20"></div>
        <div className="relative z-10 max-w-xl text-center md:text-left">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Subscribe to PetVerse Prime</h2>
          <p className="text-gray-400">Get the Collar Pro included free with an annual subscription to our AI health monitoring service.</p>
        </div>
        <button className="relative z-10 bg-gradient-primary px-8 py-4 rounded-full text-white font-bold flex items-center gap-2 hover:shadow-[0_0_20px_rgba(168,85,247,0.6)] transition-all whitespace-nowrap">
          View Subscription <ArrowRight size={20} />
        </button>
      </div>
    </div>
  );
};

export default Products;
