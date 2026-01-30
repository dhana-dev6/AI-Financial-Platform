import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, Activity, AlertTriangle, CheckCircle, TrendingUp, DollarSign, PieChart, Wallet, FileText, ShieldCheck } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, Pie, PieChart as RePieChart, AreaChart, Area } from 'recharts';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadMode, setUploadMode] = useState('file');
  const [result, setResult] = useState(null);
  const [aiData, setAiData] = useState(null);
  const [formData, setFormData] = useState({
    companyName: '',
    industry: 'Retail',
    language: 'English'
  });
  const [logs, setLogs] = useState([]);

  // Fetch Audit Logs
  const fetchLogs = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/compliance_logs");
      setLogs(res.data);
    } catch (err) {
      console.error("Error fetching logs", err);
    }
  };

  /* Mock Bank Logic */
  const handleConnectBank = async (bankName) => {
    if (!formData.companyName.trim()) {
      alert("Please enter a Company Name first.");
      return;
    }

    setLoading(true);
    try {
      // 1. Fetch Mock Data
      const response = await axios.get(`/connect_bank/${bankName}`);
      console.log("Bank API Response:", response.data);
      const bankData = response.data;

      if (!bankData || !bankData.transactions) {
        alert("Received invalid data from bank: " + JSON.stringify(bankData));
        throw new Error("Invalid bank data structure");
      }

      // 2. Convert mock transactions to CSV-like format for the existing analyze logic
      // Ideally we would send JSON to backend, but to reuse existing pipeline quickly:
      // We can construct a CSV string or just send the JSON if we refactor backend.
      // Let's refactor frontend to send this data to a new analysis endpoint OR
      // Quick hack: Generate a CSV file from this data and upload it!

      const csvHeader = "Date,Description,Amount\n";
      const csvRows = bankData.transactions.map(t => `${t.date},${t.description},${t.amount}`).join("\n");
      const csvContent = csvHeader + csvRows;

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const file = new File([blob], `${bankName}_Statement.csv`, { type: 'text/csv' });

      setFile(file);
      // Auto-submit
      const fData = new FormData();
      fData.append("file", file);
      fData.append("company_name", formData.companyName);
      fData.append("industry", formData.industry);
      fData.append("language", formData.language);

      const resultRes = await axios.post("/analyze", fData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(resultRes.data);

      try {
        const parsed = JSON.parse(resultRes.data.ai_analysis);
        setAiData(parsed);
      } catch (err) {
        console.error("Failed to parse AI JSON", err);
        setAiData({ executive_summary: resultRes.data.ai_analysis });
      }
    } catch (e) {
      console.error("Bank Error Details:", e);
      let errorMsg = e.message || "Unknown Error";
      if (e.response && e.response.data) {
        errorMsg = typeof e.response.data.detail === 'object'
          ? JSON.stringify(e.response.data.detail)
          : e.response.data.detail;
      }
      alert(`Bank connection failed: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setAiData(null); // Reset previous analysis

    try {
      let response;
      if (uploadMode === 'file') {
        if (!file) {
          setError("Please select a file to upload.");
          setLoading(false);
          return;
        }
        const formDataObj = new FormData();
        formDataObj.append("file", file);
        formDataObj.append("company_name", formData.companyName);
        formDataObj.append("industry", formData.industry);
        formDataObj.append("language", formData.language);

        response = await axios.post("http://127.0.0.1:8000/analyze", formDataObj, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      } else {
        // Bank Connect Mode
        const bankResp = await axios.get(`http://127.0.0.1:8000/connect_bank/${formData.selectedBank}`);

        // Simulate sending this bank data to analyze endpoint (mock)
        // For now, we reuse the analyze logic but ideally backend handles this.
        // Let's just mock the response structure as if backend analyzed it.
        // simplified for hackathon demo:
        response = { data: bankResp.data };
      }

      setResult(response.data);
      if (response.data.ai_analysis) {
        try {
          setAiData(JSON.parse(response.data.ai_analysis));
        } catch (e) {
          // If parsing fails, show check raw text
          setAiData({ executive_summary: response.data.ai_analysis });
        }
      }

      // Fetch updated logs
      fetchLogs();

    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "An error occurred during analysis.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch catch
    fetchLogs();
  }, []);

  const handleDownloadReport = async () => {
    if (!result) return;
    try {
      const response = await axios.post('/generate_report', {
        company_name: formData.companyName,
        result: result
      }, { responseType: 'blob' });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Report_${formData.companyName}.pdf`);
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      alert("Failed to generate report. try again.");
      console.error(error);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return alert("Please select a file");

    const data = new FormData();
    data.append('file', file);
    data.append('company_name', formData.companyName);
    data.append('industry', formData.industry);
    data.append('language', formData.language);

    setLoading(true);
    setResult(null);
    setAiData(null);

    try {
      // Using Vite Proxy to handle CORS and network resolution
      const response = await axios.post('/analyze', data);
      setResult(response.data);

      // Parse AI Analysis JSON safely
      try {
        const parsed = JSON.parse(response.data.ai_analysis);
        setAiData(parsed);
      } catch (err) {
        console.error("Failed to parse AI JSON", err);
        setAiData({ executive_summary: response.data.ai_analysis }); // Fallback
      }

    } catch (error) {
      console.error(error);
      alert(`Analysis failed: ${error.message || "Unknown Error"}. Check console for details.`);
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart data
  const chartData = result ? [
    { name: 'Revenue', amount: result.metrics['Total Revenue'] },
    { name: 'Expenses', amount: result.metrics['Total Expenses'] },
    { name: 'Profit', amount: result.metrics['Net Profit'] }
  ] : [];

  const COLORS = [
    '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
    '#ec4899', '#6366f1', '#14b8a6', '#f97316', '#06b6d4',
    '#84cc16', '#a855f7', '#d946ef', '#f43f5e', '#64748b'
  ];

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-800">
      <div className="max-w-6xl mx-auto p-6">

        {/* Header */}
        <header className="mb-10 text-center">
          <div className="inline-flex items-center justify-center p-3 bg-blue-50 rounded-full mb-4 ring-4 ring-blue-100">
            <Activity className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-5xl font-extrabold tracking-tight mb-2">
            <span className="text-gradient">SME Financial Health</span> Platform
          </h1>
          <p className="text-slate-500 text-lg font-medium">AI-Powered CFO for Strategy & Growth</p>
        </header>

        {/* Input Form */}
        {!result && (
          <div className="max-w-2xl mx-auto bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
            <form onSubmit={handleUpload} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
                  <input
                    type="text"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                    onChange={e => setFormData({ ...formData, companyName: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Industry</label>
                  <select
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                    onChange={e => setFormData({ ...formData, industry: e.target.value })}
                  >
                    <option value="Retail">Retail</option>
                    <option value="Manufacturing">Manufacturing</option>
                    <option value="Agri-Tech">Agri-Tech</option>
                    <option value="Services">Services</option>
                    <option value="Logistics">Logistics</option>
                  </select>
                </div>

                <div>

                </div>
              </div>

              {/* Toggle Mode */}
              <div className="flex bg-gray-100 p-1 rounded-lg mb-6">
                <button
                  type="button"
                  onClick={() => setUploadMode('file')}
                  className={`flex-1 py-2 rounded-md text-sm font-bold transition ${uploadMode === 'file' ? 'bg-white shadow-sm text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}
                >
                  Upload File
                </button>
                <button
                  type="button"
                  onClick={() => setUploadMode('bank')}
                  className={`flex-1 py-2 rounded-md text-sm font-bold transition ${uploadMode === 'bank' ? 'bg-white shadow-sm text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}
                >
                  Connect Bank
                </button>
              </div>

              {uploadMode === 'file' ? (
                <div className="border-2 border-dashed border-gray-300 p-10 text-center rounded-xl hover:bg-gray-50 transition cursor-pointer relative">
                  <input
                    type="file"
                    accept=".csv, .pdf, .json"
                    onChange={e => setFile(e.target.files[0])}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <div className="flex flex-col items-center pointer-events-none">
                    <Upload className="w-12 h-12 text-blue-400 mb-3" />
                    <span className="text-gray-600 font-medium">{file ? file.name : "Drop CSV / PDF / GST JSON Here"}</span>
                    <span className="text-xs text-gray-400 mt-1">Supported: .csv, .pdf, .json (GSTR-1)</span>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-sm text-gray-500 text-center">Securely connect your bank account for real-time analysis.</p>
                  <div className="grid grid-cols-2 gap-4">
                    {['HDFC Bank', 'ICICI Bank', 'SBI', 'Chase'].map(bank => (
                      <button
                        type="button"
                        key={bank}
                        disabled={loading}
                        onClick={() => handleConnectBank(bank)}
                        className={`p-4 border border-gray-200 rounded-xl transition flex flex-col items-center justify-center text-center group
                        ${loading ? "opacity-50 cursor-not-allowed bg-gray-50" : "hover:border-indigo-500 hover:bg-indigo-50"}`}
                      >
                        <div className={`w-10 h-10 bg-gray-100 rounded-full mb-2 flex items-center justify-center transition
                          ${loading ? "bg-gray-200" : "group-hover:bg-indigo-200"}`}>
                          <span className={`text-lg font-bold text-gray-600 ${!loading && "group-hover:text-indigo-700"}`}> {bank[0]} </span>
                        </div>
                        <span className={`text-sm font-bold text-gray-700 ${!loading && "group-hover:text-indigo-800"}`}>{bank}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {uploadMode === 'file' && (
                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full py-4 rounded-xl text-white font-bold text-lg shadow-lg transition transform hover:scale-[1.02] flex items-center justify-center
                ${loading ? "bg-gray-400 cursor-not-allowed" : "bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"}`}
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Analyzing Financials...
                    </>
                  ) : "Generate Health Report"}
                </button>
              )}
            </form>
          </div>
        )}

        {/* Dashboard */}
        {result && (
          <div className="space-y-8 animate-fade-in-up">

            {/* Top Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="glass-card p-6 rounded-3xl flex flex-col justify-between">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Health Score</p>
                <div className="mt-2 flex items-baseline">
                  <span className={`text-6xl font-black tracking-tighter
                            ${result.health_score > 70 ? 'text-emerald-500' : result.health_score > 40 ? 'text-amber-500' : 'text-rose-500'}`}>
                    {result.health_score}
                  </span>
                  <span className="text-slate-400 ml-1 font-medium">/100</span>
                </div>
              </div>
              <div className="glass-card p-6 rounded-3xl">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Net Profit</p>
                <p className="text-3xl font-bold text-slate-800 mt-2">${result.metrics['Net Profit'].toLocaleString()}</p>
                <p className="text-sm text-emerald-600 mt-1 font-bold bg-emerald-50 inline-block px-2 py-0.5 rounded-full">{result.metrics['Profit Margin']} Margin</p>
              </div>
              <div className="glass-card p-6 rounded-3xl">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Revenue</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">${result.metrics['Total Revenue'].toLocaleString()}</p>
              </div>
              <div className="glass-card p-6 rounded-3xl">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Expenses</p>
                <p className="text-3xl font-bold text-rose-500 mt-2">${result.metrics['Total Expenses'].toLocaleString()}</p>
              </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

              {/* Left Col: Charts & Visuals */}
              <div className="lg:col-span-1 space-y-8">
                {/* Financial Breakdown Chart */}
                <div className="glass p-6 rounded-3xl h-96">
                  <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center">
                    <PieChart className="w-5 h-5 mr-2 text-indigo-500" /> Financial Breakdown
                  </h3>
                  <ResponsiveContainer width="100%" height="80%">
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} />
                      <YAxis hide />
                      <Tooltip cursor={{ fill: 'transparent' }} />
                      <Bar dataKey="amount" radius={[8, 8, 0, 0]}>
                        {chartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % 20]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Financial Forecast Chart */}
                {result.forecast && result.forecast.revenue_forecast.length > 0 && (
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 h-96">
                    <h3 className="text-lg font-bold text-gray-800 mb-6 flex items-center">
                      <TrendingUp className="w-5 h-5 mr-2 text-blue-500" /> 6-Month Forecast
                    </h3>
                    <ResponsiveContainer width="100%" height="80%">
                      <AreaChart data={result.forecast.revenue_forecast}>
                        <defs>
                          <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 12 }} />
                        <YAxis hide />
                        <Tooltip />
                        <Area type="monotone" dataKey="amount" stroke="#3b82f6" fillOpacity={1} fill="url(#colorRev)" name="Projected Revenue" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Creditworthiness */}
                {aiData?.creditworthiness && (
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <h3 className="text-lg font-bold text-gray-800 mb-4">Creditworthiness</h3>
                    <div className={`p-4 rounded-xl text-center font-bold text-xl ${aiData.creditworthiness === 'High' ? 'bg-green-100 text-green-700' :
                      aiData.creditworthiness === 'Medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
                      }`}>
                      {aiData.creditworthiness} {aiData.creditworthiness === 'High' ? 'Confidence' : 'Risk'}
                    </div>
                  </div>
                )}
              </div>

              {/* Right Col: AI Insights */}
              <div className="lg:col-span-2 space-y-6">

                {/* Executive Summary */}
                <div className="relative overflow-hidden rounded-3xl p-[1px] bg-slate-200 border border-slate-200 shadow-sm">
                  <div className="bg-white p-8 rounded-[22px] relative h-full">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                      <Activity className="w-40 h-40 text-slate-300" />
                    </div>
                    <h2 className="text-2xl font-bold text-slate-900 mb-4 flex items-center relative z-10">
                      <Activity className="w-6 h-6 mr-3 text-blue-600" /> Executive Summary
                    </h2>
                    <div className="text-gray-700 leading-relaxed whitespace-pre-line relative z-10 text-lg">
                      {(() => {
                        // Fallback logic: If aiData is populated (parsed JSON), show summary.
                        // If not, and it's a string, try to parse it or show clean text.
                        if (aiData && aiData.executive_summary) return aiData.executive_summary;

                        if (typeof result.ai_analysis === 'string') {
                          try {
                            const clean = result.ai_analysis.replace(/```json/g, '').replace(/```/g, '').trim();
                            if (clean.startsWith('{')) {
                              const parsed = JSON.parse(clean);
                              return parsed.executive_summary || "See analysis below.";
                            }
                            return result.ai_analysis;
                          } catch (e) { return "Raw Analysis (Parse Error): " + result.ai_analysis; }
                        }
                        return "Analysis Loading... (Please wait)";
                      })()}
                    </div>
                  </div>
                </div>

                {/* Split: Strategies & Risks */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {aiData?.cost_optimization && (
                    <div className="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-green-500">
                      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                        <TrendingUp className="w-5 h-5 mr-2 text-green-500" /> Cost Optimization
                      </h3>
                      <ul className="space-y-3">
                        {aiData.cost_optimization.map((strategy, idx) => (
                          <li key={idx} className="flex items-start text-gray-600 text-sm">
                            <span className="mr-2 mt-1 bg-green-200 rounded-full p-1 min-w-[1.25rem] h-5 flex items-center justify-center text-[10px] text-green-800 font-bold">{idx + 1}</span>
                            {strategy}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {aiData?.risk_assessment && (
                    <div className="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-orange-500">
                      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                        <AlertTriangle className="w-5 h-5 mr-2 text-orange-500" /> Risk Assessment
                      </h3>
                      <p className="text-gray-600 text-sm leading-relaxed">
                        {aiData.risk_assessment}
                      </p>
                    </div>
                  )}
                </div>

                {/* Recommended Products */}
                {aiData?.recommended_products && (
                  <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100">
                    <h3 className="text-lg font-bold text-blue-900 mb-4 flex items-center">
                      <DollarSign className="w-5 h-5 mr-2 text-blue-600" /> Recommended Financial Products
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {aiData.recommended_products.map((product, idx) => (
                        <span key={idx} className="px-4 py-2 bg-white text-blue-700 rounded-full text-sm font-semibold shadow-sm hover:shadow-md transition cursor-default border border-blue-100">
                          {product}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

              </div>
            </div>

            {/* Bookkeeping Section */}
            {result.bookkeeping && (
              <div className="mt-8 space-y-6">
                <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                  <PieChart className="w-6 h-6 mr-3 text-purple-600" /> Automated Bookkeeping
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Expense Breakdown Pie */}
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 h-96">
                    <h3 className="text-lg font-bold text-gray-800 mb-4">Expense Categories</h3>
                    <ResponsiveContainer width="100%" height="80%">
                      <RePieChart>
                        <Pie
                          data={result.bookkeeping.breakdown}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {result.bookkeeping.breakdown.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[(index + 5) % 20]} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend layout="vertical" align="right" verticalAlign="middle" />
                      </RePieChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Recent Transactions List */}
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 h-96 overflow-y-auto">
                    <h3 className="text-lg font-bold text-gray-800 mb-4">Classified Transactions</h3>
                    <table className="min-w-full text-sm text-left text-gray-500">
                      <thead className="text-xs text-gray-700 uppercase bg-gray-50 sticky top-0">
                        <tr>
                          <th className="px-3 py-2">Date</th>
                          <th className="px-3 py-2">Desc</th>
                          <th className="px-3 py-2 text-right">Amount</th>
                          <th className="px-3 py-2">Category</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.bookkeeping.recent_transactions.map((tx, idx) => (
                          <tr key={idx} className="bg-white border-b hover:bg-gray-50">
                            <td className="px-3 py-2 font-medium text-gray-900 whitespace-nowrap">{tx.date}</td>
                            <td className="px-3 py-2 truncate max-w-[120px]" title={tx.description}>{tx.description}</td>
                            <td className={`px-3 py-2 text-right font-bold ${tx.amount > 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {tx.amount > 0 ? '+' : ''}{Math.abs(tx.amount).toLocaleString()}
                            </td>
                            <td className="px-3 py-2">
                              <span className="bg-gray-100 text-gray-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded border border-gray-500">
                                {tx.category}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* Tax Compliance Section */}
            {result.tax && (
              <div className="mt-8 space-y-6">
                <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                  <CheckCircle className="w-6 h-6 mr-3 text-emerald-600" /> Tax Compliance (Est.)
                </h2>
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Tax Liability */}
                  <div className="bg-red-50 p-4 rounded-xl text-center">
                    <p className="text-sm text-gray-600 font-medium uppercase tracking-wide">Est. Tax Liability (25%)</p>
                    <p className="text-3xl font-extrabold text-red-600 mt-2">${result.tax.estimated_tax.toLocaleString()}</p>
                  </div>

                  {/* Deductions */}
                  <div className="bg-green-50 p-4 rounded-xl text-center">
                    <p className="text-sm text-gray-600 font-medium uppercase tracking-wide">Identified Deductions</p>
                    <p className="text-3xl font-extrabold text-green-600 mt-2">${result.tax.total_deductible_expenses.toLocaleString()}</p>
                  </div>

                  {/* Net Position/Advice */}
                  <div className="bg-blue-50 p-4 rounded-xl text-center flex flex-col justify-center items-center">
                    <p className="text-sm text-gray-600 font-medium uppercase tracking-wide mb-2">Analysis</p>
                    <p className="text-md font-bold text-blue-800">{result.tax.message}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Working Capital Section */}
            {result.working_capital && (
              <div className="mt-8 space-y-6">
                <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                  <Wallet className="w-6 h-6 mr-3 text-indigo-600" /> Working Capital Optimization
                </h2>
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Burn Rate */}
                  <div className="p-4 rounded-xl border border-gray-100">
                    <p className="text-sm text-gray-500 uppercase tracking-wide font-semibold">Monthly Burn Rate</p>
                    <p className="text-3xl font-bold text-gray-800 mt-2">${result.working_capital.burn_rate.toLocaleString()}</p>
                    <p className="text-xs text-gray-400 mt-1">Avg. monthly operational output</p>
                  </div>
                  {/* Efficiency */}
                  <div className="p-4 rounded-xl border border-gray-100">
                    <p className="text-sm text-gray-500 uppercase tracking-wide font-semibold">Marketing ROAS</p>
                    <p className="text-3xl font-bold text-gray-800 mt-2">{result.working_capital.marketing_efficiency}x</p>
                    <p className="text-xs text-gray-400 mt-1">Revenue per $1 marketing spend</p>
                  </div>

                  {/* Recommendations */}
                  <div className="md:col-span-2 bg-indigo-50 p-5 rounded-xl">
                    <h4 className="font-bold text-indigo-900 mb-2">Optimization Recommendations</h4>
                    <ul className="space-y-2">
                      {result.working_capital.recommendations.map((rec, i) => (
                        <li key={i} className="flex items-start text-sm text-indigo-800">
                          <CheckCircle className="w-4 h-4 mr-2 mt-0.5 text-indigo-500" />
                          {rec}
                        </li>
                      ))}
                      {result.working_capital.recommendations.length === 0 && (
                        <li className="text-sm text-indigo-800">No critical issues detected. Maintain current efficiency.</li>
                      )}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            <div className="flex justify-center mt-8 gap-4">
              <button
                onClick={handleDownloadReport}
                className="bg-gray-900 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-800 transition flex items-center justify-center gap-2 shadow-lg"
              >
                <FileText size={20} />
                Download Investor Report (PDF)
              </button>

              <button
                onClick={() => window.location.reload()}
                className="bg-white text-gray-700 border border-gray-300 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 transition shadow-sm"
              >
                Upload Another File
              </button>
            </div>

            {/* Regulatory Compliance / Audit Log Section */}
            <div className="mt-16 border-t pt-8">
              <div className="flex items-center gap-2 mb-6">
                <ShieldCheck className="text-gray-600" size={24} />
                <h2 className="text-2xl font-bold text-gray-800">AI Regulatory Audit Log</h2>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-50 text-gray-500 text-sm uppercase tracking-wider">
                      <th className="p-4 font-semibold">Timestamp</th>
                      <th className="p-4 font-semibold">Company</th>
                      <th className="p-4 font-semibold">Action</th>
                      <th className="p-4 font-semibold">AI Model</th>
                      <th className="p-4 font-semibold">Verdict</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {Array.isArray(logs) && logs.length > 0 ? (
                      logs.map((log) => (
                        <tr key={log.id} className="hover:bg-gray-50 transition">
                          <td className="p-4 text-sm text-gray-600">{new Date(log.timestamp).toLocaleString()}</td>
                          <td className="p-4 text-sm font-medium text-gray-900">{log.company_name}</td>
                          <td className="p-4 text-sm text-gray-600">{log.action_type}</td>
                          <td className="p-4 text-sm text-gray-500 font-mono">{log.ai_model}</td>
                          <td className="p-4 text-sm text-blue-600 font-medium">{log.decision_summary}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="5" className="p-8 text-center text-gray-500 italic">No audit records found. Run an analysis to generate logs.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}

export default App;
