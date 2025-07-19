import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { exportTableToCSV } from "../API";

export default function ExportCSV() {
  const [isExporting, setIsExporting] = useState(false);
  const [currentBgIndex, setCurrentBgIndex] = useState(0);
  
  const backgroundImages = ["/ui/1.png", "/ui/2.png", "/ui/3.png", "/ui/4.png", "/ui/5.png"];

  // Cycle through background images
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentBgIndex((prevIndex) => (prevIndex + 1) % backgroundImages.length);
    }, 5000); // Change background every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const result = await exportTableToCSV();

      if (result.success) {
        alert("Export successful! The file has been downloaded.");
      } else {
        alert("Export failed. Please check the console for errors.");
      }
    } catch (error) {
      console.error("Export error:", error);
      alert("Export failed. Please try again.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div 
      className="h-screen m-0 p-0 flex flex-col justify-center items-center relative overflow-hidden"
      style={{
        backgroundImage: `url(${backgroundImages[currentBgIndex]})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        transition: "background-image 0.6s ease-in-out",
      }}
    >
      {/* Main Content Container */}
      <div className="flex flex-col items-center justify-center h-full max-w-4xl mx-auto px-6">
        
        {/* Logo */}
        <div className="mb-8">
          <img src="/logo.png" alt="logo" className="w-32 h-auto opacity-90" />
        </div>

        {/* Main Card */}
        <div className="bg-black/30 backdrop-blur-md text-white flex flex-col justify-center items-center p-12 rounded-2xl shadow-2xl border border-white/10 max-w-2xl w-full">
          
          {/* Title */}
          <h1 className="text-5xl font-bold text-center mb-6 tracking-wide">
            📊 Export Database
          </h1>
          
          {/* Subtitle */}
          <p className="text-2xl text-center mb-8 opacity-90 leading-relaxed max-w-lg">
            Download all user data as a CSV file for analysis and record keeping
          </p>

          {/* Export Statistics */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-8 w-full">
            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <div className="text-3xl font-bold text-[#00]">📈</div>
                <div className="text-lg opacity-80">Ready to Export</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-[#00]">💾</div>
                <div className="text-lg opacity-80">CSV Format</div>
              </div>
            </div>
          </div>

          {/* Export Button */}
          <button
            className={`bg-[#002448] hover:bg-[#A68129] px-12 py-4 rounded-xl text-3xl font-semibold mb-6 transition-all duration-300 transform hover:scale-105 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none w-full max-w-sm ${
              isExporting ? 'animate-pulse' : ''
            }`}
            onClick={handleExport}
            disabled={isExporting}
          >
            {isExporting ? '⏳ Exporting...' : '📊 Export CSV'}
          </button>

          {/* Back Link */}
          <Link 
            to="/" 
            className="text-xl text-white/80 hover:text-white underline transition-all duration-300 hover:scale-105 flex items-center gap-2"
          >
            <span>←</span> Back to Face Swap App
          </Link>
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center text-white/60">
          <p className="text-lg">
            Data will be exported to your default downloads folder
          </p>
        </div>
      </div>
    </div>
  );
}
