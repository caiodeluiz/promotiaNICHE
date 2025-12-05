import React, { useState, useRef } from 'react';
import { ThreeDElement } from './components/ThreeDElement';
import { GlassCard } from './components/GlassCard';
import { generateListing } from './services/geminiService';
import { GeneratedListing, Platform } from './types';
import {
    Upload,
    Sparkles,
    ArrowRight,
    Check,
    Loader2,
    Tag,
    DollarSign,
    FileText,
    RefreshCw,
    Clock,
    TrendingDown,
    SearchX,
    Layers,
    ShoppingBag,
    Store,
    Globe,
    Handshake,
    ShoppingCart,
    Zap,
    Mic,
    Languages,
    BarChart3,
    Star,
    TrendingUp,
    CreditCard,
    Heart
} from 'lucide-react';

const OctopusLogo = () => (
    <svg width="42" height="42" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-white drop-shadow-md">
        <path d="M100 25C60 25 30 55 30 95C30 115 40 130 50 140" stroke="currentColor" strokeWidth="8" strokeLinecap="round" />
        <path d="M170 95C170 55 140 25 100 25" stroke="currentColor" strokeWidth="8" strokeLinecap="round" />
        <path d="M170 95C170 115 160 130 150 140" stroke="currentColor" strokeWidth="8" strokeLinecap="round" />

        <path d="M50 140C40 160 20 165 10 155" stroke="currentColor" strokeWidth="8" strokeLinecap="round" />
        <path d="M65 135C65 165 55 185 40 195" stroke="currentColor" strokeWidth="8" strokeLinecap="round" />
        <path d="M90 135C90 165 95 185 105 195" stroke="currentColor" strokeWidth="8" strokeLinecap="round" />
        <path d="M110 135C110 165 105 185 95 195" stroke="currentColor" strokeWidth="8" strokeLinecap="round" />
        <path d="M135 135C135 165 145 185 160 195" stroke="currentColor" strokeWidth="8" strokeLinecap="round" />
        <path d="M150 140C160 160 180 165 190 155" stroke="currentColor" strokeWidth="8" strokeLinecap="round" />

        <ellipse cx="100" cy="85" rx="12" ry="16" fill="currentColor" />
    </svg>
);

// Data for platforms
const platformsData = [
    {
        id: Platform.AMAZON,
        name: "Amazon",
        desc: "SEO & Bullets",
        color: "bg-white",
        icon: <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" alt="Amazon" className="w-full h-auto" />
    },
    {
        id: Platform.SHOPIFY,
        name: "Shopify",
        desc: "Brand Story",
        color: "bg-[#95BF47]",
        icon: <span className="font-bold text-white text-xl">S</span>
    },
    {
        id: Platform.EBAY,
        name: "eBay",
        desc: "Auction Copy",
        color: "bg-white",
        icon: <span className="font-bold text-slate-800 text-sm">eBay</span>
    },
    {
        id: Platform.MERCADO_LIVRE,
        name: "Mercado Livre",
        desc: "High Conversion",
        color: "bg-[#ffe600]",
        icon: <Handshake className="w-6 h-6 text-slate-900" />
    },
    {
        id: Platform.SHOPEE,
        name: "Shopee",
        desc: "Engagement",
        color: "bg-[#ee4d2d]",
        icon: <ShoppingBag className="w-6 h-6 text-white" />
    },
    {
        id: Platform.MAGALU,
        name: "Magalu",
        desc: "Retail Reach",
        color: "bg-[#0086ff]",
        icon: <Store className="w-6 h-6 text-white" />
    },
    {
        id: Platform.OLX,
        name: "OLX",
        desc: "Local Sales",
        color: "bg-[#6e0b7b]",
        icon: <Globe className="w-6 h-6 text-white" />
    },
    {
        id: Platform.AMAZON, // Reuse Amazon ID for typing, but it's WooCommerce
        name: "WooCommerce",
        desc: "Custom Store",
        color: "bg-[#96588a]",
        icon: <ShoppingCart className="w-6 h-6 text-white" />
    }
];

const App: React.FC = () => {
    const [view, setView] = useState<'landing' | 'app'>('landing');
    const [selectedPlatform, setSelectedPlatform] = useState<Platform>(Platform.AMAZON);
    const [loading, setLoading] = useState(false);
    const [listing, setListing] = useState<GeneratedListing | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);

    // Default background image
    const bgImage = '/assets/background.png';

    const fileInputRef = useRef<HTMLInputElement>(null);

    // --- Handlers ---

    const handleGetStarted = () => {
        setView('app');
        window.scrollTo(0, 0);
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result as string);
                setListing(null); // Reset previous listing
            };
            reader.readAsDataURL(file);
        }
    };

    const handleGenerate = async () => {
        if (!imagePreview) return;

        setLoading(true);
        try {
            const base64Data = imagePreview.split(',')[1];
            const result = await generateListing(base64Data, selectedPlatform);
            setListing(result);
        } catch (error) {
            alert("Failed to generate listing. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    // --- Components ---

    const Navbar = () => (
        <nav className="fixed top-0 w-full z-50 px-4 sm:px-6 py-4 sm:py-6 flex justify-center pointer-events-none">
            <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-full px-6 py-3 sm:px-8 sm:py-3 flex items-center gap-6 sm:gap-12 shadow-2xl pointer-events-auto max-w-[90%] sm:max-w-none">
                <div className="flex items-center gap-4 cursor-pointer" onClick={() => setView('landing')}>
                    <img src="/assets/PolvoListify.png" alt="Listify Logo" className="w-10 h-10 drop-shadow-md brightness-0 invert" />
                    <div className="font-sans text-xl sm:text-2xl font-bold text-white tracking-wide">Listify</div>
                </div>

                <div className="hidden md:flex gap-8 text-sm font-medium text-white/90">
                    <a href="#" className="hover:text-white transition-colors">Features</a>
                    <a href="#" className="hover:text-white transition-colors">Pricing</a>
                    <a href="#" className="hover:text-white transition-colors">About</a>
                </div>
                <div className="flex gap-3 sm:gap-4">
                    <button className="hidden sm:block px-5 py-2 text-sm font-medium text-white bg-transparent hover:bg-white/10 rounded-full transition-all">
                        Log in
                    </button>
                    <button
                        onClick={handleGetStarted}
                        className="px-4 py-2 sm:px-6 sm:py-2 text-xs sm:text-sm font-medium text-slate-900 bg-white rounded-full hover:bg-slate-200 transition-all shadow-lg whitespace-nowrap"
                    >
                        Get started
                    </button>
                </div>
            </div>
        </nav>
    );

    const LandingPage = () => (
        <div className="min-h-screen flex flex-col relative overflow-x-hidden pt-24 md:pt-32">

            {/* Main Content Area */}
            <div className="w-full max-w-8xl mx-auto flex flex-col lg:flex-row items-center justify-between px-6 md:px-12 lg:px-24 gap-8 lg:gap-12 z-10 mb-20 lg:mb-24">

                {/* Left: Typography */}
                <div className="w-full lg:w-1/2 space-y-6 md:space-y-8 animate-fade-in-up text-center lg:text-left order-1 pt-10 lg:pt-0">
                    <h1 className="text-5xl md:text-6xl lg:text-[5.5rem] leading-[1.05] text-white drop-shadow-xl">
                        <span className="font-serif italic font-light block mb-2">Marketplace</span>
                        <span className="font-serif font-medium block">Listing</span>
                        <span className="font-serif font-medium block">Generation Redefined</span>
                        <span className="font-serif font-medium block text-white/80">by AI.</span>
                    </h1>

                    <p className="text-base md:text-lg text-white/90 max-w-xl leading-relaxed font-light mx-auto lg:mx-0">
                        Effortlessly create high-converting product listings across multiple platforms with our advanced AI technology.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center gap-6 pt-4 justify-center lg:justify-start">
                        <button
                            onClick={handleGetStarted}
                            className="group flex items-center justify-center gap-3 px-8 py-4 bg-slate-900 text-white rounded-full font-medium text-lg hover:bg-slate-800 hover:scale-105 transition-all shadow-2xl border border-white/10"
                        >
                            Get started
                            <div className="bg-white/20 rounded-full p-1">
                                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </div>
                        </button>
                        <div className="text-white/80 text-sm font-medium">
                            Trusted by <span className="text-white font-bold">10,000+</span> businesses.
                        </div>
                    </div>
                </div>

                {/* Right: 3D Content */}
                <div className="w-full lg:w-1/2 h-[350px] md:h-[500px] lg:h-[600px] relative flex items-center justify-center order-2">
                    <ThreeDElement />
                </div>
            </div>

            {/* Integration & Reach (Infinite Carousel) */}
            <div className="w-full py-12 z-10 overflow-hidden relative">
                <div className="max-w-7xl mx-auto px-6 mb-8 text-center md:text-left">
                    <h3 className="text-white text-2xl md:text-3xl font-serif font-medium">Built for Your E-commerce Ecosystem.</h3>
                </div>

                {/* Infinite Carousel Container */}
                <div className="relative w-full flex overflow-hidden mask-linear-fade">
                    <div className="flex animate-scroll hover:pause gap-6 px-6 w-max">
                        {/* Duplicate the array to ensure seamless looping */}
                        {[...platformsData, ...platformsData, ...platformsData].map((p, i) => (
                            <div key={`${p.id}-${i}`} className="w-[280px] shrink-0 group">
                                <GlassCard
                                    hoverEffect
                                    onClick={() => { if (p.id !== Platform.AMAZON || p.name === 'Amazon') { setSelectedPlatform(p.id as Platform); handleGetStarted(); } }}
                                    className="!bg-transparent !border-white/10 flex flex-col justify-center h-full hover:!bg-white/5 transition-all duration-500"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center p-2 shrink-0 shadow-lg bg-white/10 grayscale group-hover:grayscale-0 transition-all duration-500 group-hover:shadow-[0_0_20px_rgba(255,255,255,0.3)]`}>
                                            {p.icon}
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-base text-white">{p.name}</h4>
                                            <p className="text-xs text-white/50">{p.desc}</p>
                                        </div>
                                    </div>
                                </GlassCard>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Pain Point Section */}
            <div className="w-full bg-slate-950 py-24 px-6 md:px-12 relative z-20 border-t border-white/5 shadow-2xl">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-5xl font-serif text-white mb-4">
                            The Hidden Cost of <span className="text-indigo-400 italic">Manual Listing.</span>
                        </h2>
                        <p className="text-white/50 text-lg font-light max-w-2xl mx-auto">
                            Stop letting inefficient processes drain your resources and stifle your growth.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {/* Pain Point 1: Time */}
                        <div className="p-8 rounded-2xl bg-white/[0.03] border border-white/5 hover:bg-white/[0.05] transition-all group">
                            <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                <Clock className="w-6 h-6 text-red-400" />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-3">Time Drain</h3>
                            <p className="text-white/50 text-sm leading-relaxed">
                                Weeks lost writing, formatting, and optimizing descriptions manually instead of focusing on business strategy.
                            </p>
                        </div>

                        {/* Pain Point 2: Money */}
                        <div className="p-8 rounded-2xl bg-white/[0.03] border border-white/5 hover:bg-white/[0.05] transition-all group">
                            <div className="w-12 h-12 rounded-full bg-orange-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                <TrendingDown className="w-6 h-6 text-orange-400" />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-3">Lost Revenue</h3>
                            <p className="text-white/50 text-sm leading-relaxed">
                                Higher return rates and customer dissatisfaction caused by vague, inaccurate, or missing product details.
                            </p>
                        </div>

                        {/* Pain Point 3: Performance */}
                        <div className="p-8 rounded-2xl bg-white/[0.03] border border-white/5 hover:bg-white/[0.05] transition-all group">
                            <div className="w-12 h-12 rounded-full bg-purple-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                <SearchX className="w-6 h-6 text-purple-400" />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-3">Invisible Products</h3>
                            <p className="text-white/50 text-sm leading-relaxed">
                                Poor SEO performance and lack of keywords resulting in zero visibility on crowded marketplaces.
                            </p>
                        </div>

                        {/* Pain Point 4: Scale */}
                        <div className="p-8 rounded-2xl bg-white/[0.03] border border-white/5 hover:bg-white/[0.05] transition-all group">
                            <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                <Layers className="w-6 h-6 text-blue-400" />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-3">Scaling Ceiling</h3>
                            <p className="text-white/50 text-sm leading-relaxed">
                                Impossible to expand your catalog or launch on new platforms without hiring an expensive army of copywriters.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* The Conversion Engine Section */}
            <div className="w-full py-24 px-6 md:px-12 relative z-20">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-5xl font-serif text-white mb-4">
                            Not Just AI. <span className="text-indigo-300 italic">Optimized Copywriting.</span>
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {/* Feature 1 */}
                        <GlassCard className="group hover:-translate-y-2 transition-transform duration-300 !bg-white/5">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-blue-600 p-[1px] mb-6 shadow-lg shadow-indigo-500/20 group-hover:shadow-indigo-500/40 transition-shadow">
                                <div className="w-full h-full rounded-2xl bg-slate-900/50 backdrop-blur-xl flex items-center justify-center">
                                    <Zap className="w-8 h-8 text-indigo-300" />
                                </div>
                            </div>
                            <h3 className="text-xl font-bold text-white mb-2">Instant SEO Optimization</h3>
                            <p className="text-white/60 text-sm leading-relaxed">
                                Automatically embeds high-ranking keywords specific to your niche and platform.
                            </p>
                        </GlassCard>

                        {/* Feature 2 */}
                        <GlassCard className="group hover:-translate-y-2 transition-transform duration-300 !bg-white/5">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-pink-500 to-rose-600 p-[1px] mb-6 shadow-lg shadow-pink-500/20 group-hover:shadow-pink-500/40 transition-shadow">
                                <div className="w-full h-full rounded-2xl bg-slate-900/50 backdrop-blur-xl flex items-center justify-center">
                                    <Mic className="w-8 h-8 text-pink-300" />
                                </div>
                            </div>
                            <h3 className="text-xl font-bold text-white mb-2">Adaptive Tone of Voice</h3>
                            <p className="text-white/60 text-sm leading-relaxed">
                                Switch seamlessly between professional, technical, or conversational styles to match your brand.
                            </p>
                        </GlassCard>

                        {/* Feature 3 */}
                        <GlassCard className="group hover:-translate-y-2 transition-transform duration-300 !bg-white/5">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-teal-600 p-[1px] mb-6 shadow-lg shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition-shadow">
                                <div className="w-full h-full rounded-2xl bg-slate-900/50 backdrop-blur-xl flex items-center justify-center">
                                    <Languages className="w-8 h-8 text-cyan-300" />
                                </div>
                            </div>
                            <h3 className="text-xl font-bold text-white mb-2">Multi-Market Translation</h3>
                            <p className="text-white/60 text-sm leading-relaxed">
                                Generate listings optimized for 10+ languages to expand your global reach instantly.
                            </p>
                        </GlassCard>

                        {/* Feature 4 */}
                        <GlassCard className="group hover:-translate-y-2 transition-transform duration-300 !bg-white/5">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 p-[1px] mb-6 shadow-lg shadow-amber-500/20 group-hover:shadow-amber-500/40 transition-shadow">
                                <div className="w-full h-full rounded-2xl bg-slate-900/50 backdrop-blur-xl flex items-center justify-center">
                                    <BarChart3 className="w-8 h-8 text-amber-300" />
                                </div>
                            </div>
                            <h3 className="text-xl font-bold text-white mb-2">Competitor Analysis</h3>
                            <p className="text-white/60 text-sm leading-relaxed">
                                AI analyzes top-performing competitor listings to suggest improvements for yours.
                            </p>
                        </GlassCard>
                    </div>
                </div>
            </div>

            {/* Social Proof Section */}
            <div className="w-full py-16 px-6 md:px-12 relative z-20 bg-slate-900/50 border-t border-white/5">
                <div className="max-w-7xl mx-auto">
                    <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
                        <div>
                            <h2 className="text-3xl md:text-5xl font-serif text-white mb-4">
                                Boost Your Sales. <span className="text-emerald-400 italic">Proven.</span>
                            </h2>
                            <p className="text-white/60 text-lg font-light max-w-xl">
                                Join thousands of sellers who have transformed their business with Listify. Real results, real growth.
                            </p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                        {/* Case Study Card */}
                        <div className="lg:col-span-7">
                            <GlassCard className="h-full !bg-gradient-to-br !from-slate-800/80 !to-slate-900/80">
                                <div className="flex justify-between items-start mb-8">
                                    <div>
                                        <div className="text-emerald-400 font-bold text-sm tracking-wider uppercase mb-2">Case Study</div>
                                        <h3 className="text-2xl font-bold text-white">SportFlex Gear</h3>
                                        <p className="text-white/50 text-sm mt-1">Amazon FBA Sports Category</p>
                                    </div>
                                    <div className="bg-emerald-500/10 text-emerald-300 px-4 py-1.5 rounded-full text-sm font-medium flex items-center gap-2">
                                        <TrendingUp className="w-4 h-4" /> +142% Revenue
                                    </div>
                                </div>

                                {/* Bar Chart Visualization */}
                                <div className="flex items-end justify-center gap-8 h-[250px] sm:h-[300px] w-full px-4 sm:px-12 pb-8 pt-4 border-b border-white/5">
                                    <div className="flex flex-col items-center gap-3 w-1/3 group">
                                        <div className="text-white/60 text-lg font-bold mb-1 opacity-0 group-hover:opacity-100 transition-opacity">$12k</div>
                                        <div className="w-full bg-slate-600/30 rounded-t-xl h-[100px] relative overflow-hidden">
                                            <div className="absolute inset-0 bg-gradient-to-t from-slate-700 to-transparent opacity-50"></div>
                                        </div>
                                        <span className="text-white/40 text-sm font-medium uppercase tracking-wide">Manual</span>
                                    </div>
                                    <div className="flex flex-col items-center gap-3 w-1/3 group">
                                        <div className="text-white text-xl font-bold mb-1 opacity-0 group-hover:opacity-100 transition-opacity drop-shadow-[0_0_10px_rgba(52,211,153,0.5)]">$29k</div>
                                        <div className="w-full bg-emerald-500 rounded-t-xl h-[240px] relative overflow-hidden shadow-[0_0_40px_rgba(16,185,129,0.3)]">
                                            <div className="absolute inset-0 bg-gradient-to-t from-emerald-600 via-emerald-400 to-emerald-300"></div>
                                            <div className="absolute inset-0 opacity-20 bg-[url('https://www.transparenttextures.com/patterns/diagonal-striped-brick.png')]"></div>
                                        </div>
                                        <span className="text-emerald-400 text-sm font-bold uppercase tracking-wide">With Listify</span>
                                    </div>
                                </div>
                                <div className="flex justify-between mt-6 text-sm text-white/60">
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                                        Monthly Sales Volume
                                    </div>
                                    <div>
                                        Result achieved in 30 days
                                    </div>
                                </div>
                            </GlassCard>
                        </div>

                        {/* Testimonials Column */}
                        <div className="lg:col-span-5 space-y-6">
                            {/* Testimonial 1 */}
                            <GlassCard className="hover:scale-[1.02] transition-transform duration-300">
                                <div className="flex items-center gap-4 mb-4">
                                    <img
                                        src="https://images.unsplash.com/photo-1599566150163-29194dcaad36?q=80&w=3387&auto=format&fit=crop"
                                        alt="User"
                                        className="w-12 h-12 rounded-full object-cover border-2 border-white/20"
                                    />
                                    <div>
                                        <h4 className="text-white font-bold">Alex Rivera</h4>
                                        <div className="flex items-center gap-1">
                                            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                                            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                                            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                                            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                                            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                                            <span className="text-xs text-white/40 ml-2">Power Seller</span>
                                        </div>
                                    </div>
                                </div>
                                <p className="text-white/80 italic leading-relaxed">
                                    "I literally fired my copywriter. Listify creates better descriptions in seconds than what I used to pay $50 for. My click-through rate doubled overnight."
                                </p>
                            </GlassCard>

                            {/* Testimonial 2 */}
                            <GlassCard className="hover:scale-[1.02] transition-transform duration-300">
                                <div className="flex items-center gap-4 mb-4">
                                    <img
                                        src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=3387&auto=format&fit=crop"
                                        alt="User"
                                        className="w-12 h-12 rounded-full object-cover border-2 border-white/20"
                                    />
                                    <div>
                                        <h4 className="text-white font-bold">Sarah Jenkins</h4>
                                        <div className="flex items-center gap-1">
                                            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                                            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                                            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                                            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                                            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                                            <span className="text-xs text-white/40 ml-2">Shopify Owner</span>
                                        </div>
                                    </div>
                                </div>
                                <p className="text-white/80 italic leading-relaxed">
                                    "The Augmented Reality feature is an absolute game changer. My sales grew as soon as I started sending the AR model in the ads. This is a meaningful innovation."
                                </p>
                            </GlassCard>
                        </div>
                    </div>
                </div>
            </div>

            {/* Pricing Section */}
            <div className="w-full py-24 px-6 md:px-12 relative z-20">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-5xl font-serif text-white mb-4">
                            Simple Pricing. <span className="text-blue-300 italic">Big Impact.</span>
                        </h2>
                        <p className="text-white/60 text-lg font-light max-w-xl mx-auto">
                            Start for free, upgrade as you scale. No hidden fees.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 items-end">
                        {/* Starter Plan */}
                        <GlassCard className="flex flex-col h-full !bg-white/10 hover:!bg-white/15 !border-white/20">
                            <div className="mb-4">
                                <span className="text-xs font-bold text-white/60 tracking-wider uppercase">Starter</span>
                                <h3 className="text-3xl font-serif font-bold text-white mt-1">Free</h3>
                            </div>
                            <div className="flex items-center gap-2 mb-6">
                                <CreditCard className="w-5 h-5 text-blue-300" />
                                <span className="text-white/90 font-medium">10 Credits / mo</span>
                            </div>
                            <p className="text-white/60 text-sm mb-8 leading-relaxed flex-1">
                                Perfect for testing the waters and generating your first few listings.
                            </p>
                            <button className="w-full py-3 rounded-xl border border-white/20 text-white font-medium hover:bg-white/10 transition-colors">
                                Start Free
                            </button>
                        </GlassCard>

                        {/* Growth Plan (Best Value) */}
                        <div className="relative lg:-mt-12 lg:mb-4 group">
                            <div className="absolute -inset-[2px] rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 opacity-75 blur-sm group-hover:opacity-100 transition-opacity"></div>
                            <GlassCard className="flex flex-col h-full relative !bg-[#1e1b4b]/60 backdrop-blur-2xl !border-white/20 lg:scale-105 shadow-2xl">
                                <div className="absolute top-0 right-0 bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl rounded-tr-xl tracking-wider uppercase">
                                    Best Value
                                </div>
                                <div className="mb-4 pt-2">
                                    <span className="text-xs font-bold text-indigo-300 tracking-wider uppercase">Growth</span>
                                    <h3 className="text-4xl font-serif font-bold text-white mt-1">$29<span className="text-lg text-white/50 font-sans font-normal">/mo</span></h3>
                                </div>
                                <div className="flex items-center gap-2 mb-6">
                                    <Zap className="w-5 h-5 text-yellow-300" />
                                    <span className="text-white font-bold text-lg">500 Credits / mo</span>
                                </div>
                                <p className="text-white/70 text-sm mb-8 leading-relaxed flex-1">
                                    For serious sellers scaling up operations. Unlocks multi-language & competitor analysis.
                                </p>
                                <button className="w-full py-4 rounded-xl bg-white text-slate-900 font-bold hover:bg-indigo-50 transition-colors shadow-lg">
                                    Get Started
                                </button>
                            </GlassCard>
                        </div>

                        {/* Power Plan */}
                        <GlassCard className="flex flex-col h-full !bg-white/10 hover:!bg-white/15 !border-white/20">
                            <div className="mb-4">
                                <span className="text-xs font-bold text-white/60 tracking-wider uppercase">Power</span>
                                <h3 className="text-3xl font-serif font-bold text-white mt-1">$79<span className="text-base text-white/50 font-sans font-normal">/mo</span></h3>
                            </div>
                            <div className="flex items-center gap-2 mb-6">
                                <Layers className="w-5 h-5 text-purple-300" />
                                <span className="text-white/90 font-medium">2,000 Credits / mo</span>
                            </div>
                            <p className="text-white/60 text-sm mb-8 leading-relaxed flex-1">
                                Dominating multiple niches? Get high volume generation at our best rate per listing.
                            </p>
                            <button className="w-full py-3 rounded-xl border border-white/20 text-white font-medium hover:bg-white/10 transition-colors">
                                Subscribe
                            </button>
                        </GlassCard>

                        {/* Enterprise Plan */}
                        <GlassCard className="flex flex-col h-full !bg-white/10 hover:!bg-white/15 !border-white/20">
                            <div className="mb-4">
                                <span className="text-xs font-bold text-white/60 tracking-wider uppercase">Enterprise</span>
                                <h3 className="text-3xl font-serif font-bold text-white mt-1">Custom</h3>
                            </div>
                            <div className="flex items-center gap-2 mb-6">
                                <Globe className="w-5 h-5 text-cyan-300" />
                                <span className="text-white/90 font-medium">Unlimited</span>
                            </div>
                            <p className="text-white/60 text-sm mb-8 leading-relaxed flex-1">
                                Custom solutions for large teams, API access, and dedicated support account manager.
                            </p>
                            <button className="w-full py-3 rounded-xl border border-white/20 text-white font-medium hover:bg-white/10 transition-colors">
                                Contact Sales
                            </button>
                        </GlassCard>
                    </div>
                </div>
            </div>



            {/* Institutional Footer */}
            <footer className="w-full py-12 px-6 border-t border-white/10 bg-slate-950/80 backdrop-blur-md relative z-20">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6 text-center md:text-left">
                    <div className="flex flex-col gap-2">
                        <div className="flex items-center justify-center md:justify-start gap-2 text-white/80">
                            <span className="font-serif font-bold text-lg">Listify</span>
                            <span className="text-white/20">|</span>
                            <span className="text-sm">Designed & Developed by <strong className="text-indigo-400">Caio Deluiz</strong></span>
                        </div>
                        <p className="text-xs text-white/30 max-w-md">
                            Listify is an independent AI tool. We are not affiliated with Amazon, Shopify, eBay, Mercado Livre, Shopee, Magalu, OLX, or WooCommerce. All trademarks and logos are the property of their respective owners.
                        </p>
                    </div>

                    <div className="flex gap-6 text-sm text-white/50">
                        <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
                        <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
                        <a href="#" className="hover:text-white transition-colors">Support</a>
                    </div>
                </div>
            </footer>
        </div>
    );

    const AppInterface = () => (
        <div className="min-h-screen flex flex-col pt-32 pb-20 px-4 md:px-10 max-w-7xl mx-auto z-10 relative w-full">
            <div className="flex items-center gap-4 mb-8">
                <button onClick={() => setView('landing')} className="text-white/80 hover:text-white flex items-center gap-2 px-4 py-2 bg-white/5 rounded-full hover:bg-white/10 transition-all">
                    <ArrowRight className="w-4 h-4 rotate-180" /> Back to Home
                </button>
            </div>

            <div className="grid lg:grid-cols-12 gap-8 h-full">
                {/* Left Panel: Input */}
                <div className="lg:col-span-5 space-y-6">
                    <GlassCard className="flex flex-col h-auto min-h-[600px]">
                        <div className="mb-6">
                            <h2 className="text-2xl font-serif font-medium text-white mb-1">Create Listing</h2>
                            <p className="text-white/50 text-sm">Upload a photo to generate content.</p>
                        </div>

                        <div className="mb-6">
                            <label className="block text-xs font-bold text-white/60 uppercase tracking-wider mb-3">Platform</label>
                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 bg-black/20 p-1.5 rounded-xl max-h-[150px] overflow-y-auto custom-scrollbar">
                                {Object.values(Platform).map((p) => (
                                    <button
                                        key={p}
                                        onClick={() => setSelectedPlatform(p)}
                                        className={`py-2 px-1 text-xs sm:text-sm font-medium rounded-lg transition-all truncate ${selectedPlatform === p ? 'bg-white text-slate-900 shadow-lg' : 'text-white/50 hover:text-white hover:bg-white/5'}`}
                                        title={p}
                                    >
                                        {p}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="flex-1 flex flex-col">
                            <div
                                className="flex-1 border-2 border-dashed border-white/20 rounded-2xl bg-white/5 hover:bg-white/10 transition-colors cursor-pointer relative overflow-hidden group min-h-[250px] flex flex-col items-center justify-center"
                                onClick={() => fileInputRef.current?.click()}
                            >
                                {imagePreview ? (
                                    <>
                                        <img src={imagePreview} alt="Preview" className="w-full h-full object-contain absolute inset-0 p-6" />
                                        <div className="absolute inset-0 bg-black/60 flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-sm">
                                            <RefreshCw className="w-8 h-8 text-white mb-2" />
                                            <span className="text-white font-medium">Change Image</span>
                                        </div>
                                    </>
                                ) : (
                                    <div className="text-center p-8">
                                        <div className="w-20 h-20 bg-indigo-500/20 rounded-full flex items-center justify-center mx-auto mb-4 border border-indigo-500/30">
                                            <Upload className="w-8 h-8 text-indigo-200" />
                                        </div>
                                        <h3 className="text-lg font-medium text-white mb-2">Upload Product</h3>
                                        <p className="text-sm text-white/50 max-w-[200px] mx-auto">Drag & drop or click to browse files</p>
                                    </div>
                                )}
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    className="hidden"
                                    accept="image/*"
                                    onChange={handleFileChange}
                                />
                            </div>
                        </div>

                        <button
                            onClick={handleGenerate}
                            disabled={!imagePreview || loading}
                            className={`mt-6 w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-3 transition-all shadow-xl ${!imagePreview || loading ? 'bg-slate-700/50 text-slate-400 cursor-not-allowed' : 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:scale-[1.02]'}`}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" /> Analyzing...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-5 h-5" /> Generate Content
                                </>
                            )}
                        </button>
                    </GlassCard>
                </div>

                {/* Right Panel: Output */}
                <div className="lg:col-span-7">
                    {listing ? (
                        <div className="space-y-6 animate-fade-in-up">
                            <GlassCard>
                                <div className="flex items-start gap-4 mb-6">
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center shrink-0 shadow-lg">
                                        <FileText className="w-5 h-5 text-white" />
                                    </div>
                                    <div className="flex-1">
                                        <label className="text-xs font-bold text-indigo-300 uppercase tracking-wider mb-1 block">Optimized Title</label>
                                        <h3 className="text-xl font-serif text-white leading-snug">{listing.title}</h3>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4 mb-6">
                                    <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                                        <div className="flex items-center gap-2 mb-2">
                                            <DollarSign className="w-4 h-4 text-emerald-400" />
                                            <label className="text-xs font-bold text-emerald-200 uppercase tracking-wider">Estimated Price</label>
                                        </div>
                                        <p className="text-2xl font-bold text-white">{listing.pricePrediction}</p>
                                    </div>
                                    <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Tag className="w-4 h-4 text-pink-400" />
                                            <label className="text-xs font-bold text-pink-200 uppercase tracking-wider">Keywords</label>
                                        </div>
                                        <div className="flex flex-wrap gap-1">
                                            {listing.tags.slice(0, 3).map((t, i) => (
                                                <span key={i} className="text-xs text-white/80 bg-white/10 px-1.5 py-0.5 rounded">#{t}</span>
                                            ))}
                                            {listing.tags.length > 3 && <span className="text-xs text-white/50">+{listing.tags.length - 3}</span>}
                                        </div>
                                    </div>
                                </div>

                                <div className="mb-6">
                                    <label className="text-xs font-bold text-blue-200 uppercase tracking-wider mb-3 block">Key Features</label>
                                    <ul className="space-y-3">
                                        {listing.features.map((f, i) => (
                                            <li key={i} className="flex gap-3 text-sm text-white/90 bg-white/5 p-3 rounded-lg border border-white/5">
                                                <Check className="w-5 h-5 text-blue-400 shrink-0" />
                                                {f}
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                <div className="mb-6">
                                    <label className="text-xs font-bold text-purple-200 uppercase tracking-wider mb-2 block">Marketing Description</label>
                                    <div className="bg-black/20 rounded-xl p-5 border border-white/5">
                                        <p className="text-white/80 text-sm leading-relaxed whitespace-pre-wrap font-light">{listing.description}</p>
                                    </div>
                                </div>

                                <div className="pt-4 border-t border-white/10 flex gap-3 items-center">
                                    <div className="p-2 bg-yellow-500/20 rounded-lg">
                                        <Sparkles className="w-4 h-4 text-yellow-300" />
                                    </div>
                                    <p className="text-xs text-white/70 italic">
                                        <strong className="text-yellow-200 not-italic">Pro Tip:</strong> {listing.platformSpecific}
                                    </p>
                                </div>
                            </GlassCard>
                        </div>
                    ) : (
                        <GlassCard className="h-full flex flex-col items-center justify-center text-center min-h-[600px] border-dashed border-2 border-white/10 !bg-white/5">
                            <div className="w-24 h-24 bg-gradient-to-tr from-white/10 to-transparent rounded-full flex items-center justify-center mb-6 animate-pulse">
                                <Sparkles className="w-10 h-10 text-white/30" />
                            </div>
                            <h3 className="text-2xl font-serif text-white mb-3">Ready to Create</h3>
                            <p className="text-white/50 max-w-sm leading-relaxed">
                                The AI is ready. Upload your product image on the left to generate a high-converting {selectedPlatform} listing in seconds.
                            </p>
                        </GlassCard>
                    )}
                </div>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen text-slate-900 bg-slate-900 relative transition-all duration-700 font-sans selection:bg-indigo-500/30">
            {/* Dynamic Background */}
            <div
                className="fixed inset-0 z-0 transition-opacity duration-1000 ease-in-out scale-105"
                style={{
                    backgroundImage: `url('${bgImage}')`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    opacity: 1
                }}
            />

            {/* Overlay Gradient for readability */}
            <div className="fixed inset-0 z-0 bg-gradient-to-r from-slate-900/90 via-slate-900/40 to-transparent pointer-events-none" />
            <div className="fixed inset-0 z-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent pointer-events-none" />

            <Navbar />

            {view === 'landing' ? <LandingPage /> : <AppInterface />}
        </div>
    );
};

export default App;