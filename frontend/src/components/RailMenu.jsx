import React, { useState } from 'react';
import { Home, BarChart2, FileText, Settings, Menu, X, ChevronLeft, ChevronRight } from 'lucide-react';

const RailMenu = ({ activeTab, setActiveTab }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    const menuItems = [
        { icon: Home, label: 'Dashboard' },
        { icon: BarChart2, label: 'Analytics' },
        { icon: FileText, label: 'Reports' },
        { icon: Settings, label: 'Settings' },
    ];

    return (
        <div
            className={`h-screen bg-white shadow-xl z-50 transition-all duration-300 ease-in-out border-r border-gray-100 flex flex-col
      ${isExpanded ? 'w-64' : 'w-20'}`}
        >
            {/* Logo Area */}
            <div className="h-20 flex items-center justify-center border-b border-gray-100 relative">
                <div className="w-10 h-10 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg transform transition-transform hover:scale-110">
                    <span className="text-white font-bold text-xl">S</span>
                </div>

                {isExpanded && (
                    <span className="ml-3 font-extrabold text-gray-800 text-lg tracking-tight animate-fade-in">
                        SME<span className="text-blue-600">Health</span>
                    </span>
                )}

                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="absolute -right-3 top-8 bg-white border border-gray-100 p-1 rounded-full shadow-md text-gray-500 hover:text-blue-600 transition-colors"
                >
                    {isExpanded ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
                </button>
            </div>

            {/* Menu Items */}
            <div className="flex-1 py-6 space-y-2 px-3">
                {menuItems.map((item, index) => (
                    <button
                        key={index}
                        onClick={() => setActiveTab(item.label)}
                        className={`w-full flex items-center p-3 rounded-xl transition-all duration-200 group relative
              ${activeTab === item.label
                                ? 'bg-blue-50 text-blue-600 shadow-sm'
                                : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'
                            }
              ${!isExpanded ? 'justify-center' : 'px-4'}
            `}
                    >
                        <item.icon size={22} className={`transition-transform group-hover:scale-110 ${activeTab === item.label ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-600'}`} />

                        {isExpanded && (
                            <span className="ml-3 font-medium text-sm whitespace-nowrap overflow-hidden">
                                {item.label}
                            </span>
                        )}

                        {/* Tooltip for collapsed state */}
                        {!isExpanded && (
                            <div className="absolute left-full ml-4 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 whitespace-nowrap">
                                {item.label}
                            </div>
                        )}
                    </button>
                ))}
            </div>

            {/* User Profile / Bottom */}
            <div className="p-4 border-t border-gray-100">
                <div className={`flex items-center ${!isExpanded ? 'justify-center' : ''}`}>
                    <div className="w-10 h-10 rounded-full bg-gray-200 border-2 border-white shadow-sm flex-shrink-0 bg-cover bg-center overflow-hidden">
                        <img src="https://ui-avatars.com/api/?name=Admin+User&background=random" alt="User" />
                    </div>
                    {isExpanded && (
                        <div className="ml-3 overflow-hidden">
                            <p className="text-sm font-bold text-gray-800 truncate">Admin User</p>
                            <p className="text-xs text-gray-500 truncate">admin@sme.com</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default RailMenu;
