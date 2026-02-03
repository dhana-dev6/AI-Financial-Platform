import React from 'react';
import { Search, Bell, Grid, Calendar } from 'lucide-react';

const DashboardHeader = () => {
    return (
        <header className="bg-white/80 backdrop-blur-md sticky top-0 z-40 px-8 py-4 flex items-center justify-between border-b border-gray-100 shadow-sm transition-all duration-300">

            {/* Left: Page Title / Breadcrumbs */}
            <div>
                <h1 className="text-2xl font-bold text-gray-800 tracking-tight">Dashboard Overview</h1>
                <p className="text-sm text-gray-500 font-medium mt-0.5 flex items-center">
                    <Calendar size={14} className="mr-1" /> {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </p>
            </div>

            {/* Right: Actions */}
            <div className="flex items-center gap-4">

                {/* Search Bar */}
                <div className="hidden md:flex items-center bg-gray-50 px-4 py-2.5 rounded-full border border-gray-200 focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-300 transition-all w-64">
                    <Search size={18} className="text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search analytics..."
                        className="bg-transparent border-none outline-none text-sm text-gray-700 ml-2 w-full placeholder-gray-400"
                    />
                </div>

                {/* Icons */}
                <button className="p-2.5 rounded-full hover:bg-gray-100 text-gray-500 hover:text-blue-600 transition relative group">
                    <Bell size={20} />
                    <span className="absolute top-2 right-2.5 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
                    <span className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-xs bg-gray-900 text-white px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition pointer-events-none">Notifications</span>
                </button>

                <button className="p-2.5 rounded-full hover:bg-gray-100 text-gray-500 hover:text-purple-600 transition group relative">
                    <Grid size={20} />
                    <span className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-xs bg-gray-900 text-white px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition pointer-events-none">Apps</span>
                </button>
            </div>
        </header>
    );
};

export default DashboardHeader;
