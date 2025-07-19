import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchPrinters, updatePrinterConfig } from "../API";

export default function Print() {
  const [printers, setPrinters] = useState([]);
  const [selectedPrinter, setSelectedPrinter] = useState("");
  const [printSize, setPrintSize] = useState("4x6");
  const [isSaving, setIsSaving] = useState(false);
  const [currentBgIndex, setCurrentBgIndex] = useState(0);
  
  const backgroundImages = ["/ui/1.png", "/ui/2.png", "/ui/3.png", "/ui/4.png", "/ui/5.png"];

  // Cycle through background images
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentBgIndex((prevIndex) => (prevIndex + 1) % backgroundImages.length);
    }, 5000); // Change background every 5 seconds

    return () => clearInterval(interval);
  }, []);

  // Fetch available printers
  useEffect(() => {
    const loadPrinters = async () => {
      try {
        const data = await fetchPrinters();
        setPrinters(data.printers);
        setSelectedPrinter(data.default_printer); // Set default printer
      } catch (error) {
        console.error("Error loading printers:", error);
      }
    };

    loadPrinters();
  }, []);

  // Save settings
  const saveSettings = async () => {
    setIsSaving(true);
    const config = {
      default_printer: selectedPrinter,
      hot_folder: {
        enabled: false, // Adjust this if needed
      },
    };

    try {
      await updatePrinterConfig(config);
      alert("Settings saved successfully!");
    } catch (error) {
      console.error("Error saving printer settings:", error);
      alert("Failed to save settings. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const isFormValid = selectedPrinter && printSize;

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
      <div className="flex flex-col items-center justify-center h-full max-w-5xl mx-auto px-6">
        
        {/* Logo */}
        <div className="mb-8">
          <img src="/logo.png" alt="logo" className="w-32 h-auto opacity-90" />
        </div>

        {/* Main Card */}
        <div className="bg-black/30 backdrop-blur-md text-white flex flex-col justify-center items-center p-12 rounded-2xl shadow-2xl border border-white/10 max-w-4xl w-full">
          
          {/* Title */}
          <h1 className="text-5xl font-bold text-center mb-8 tracking-wide">
            🖨️ Printer Settings
          </h1>

          {/* Settings Form */}
          <div className="w-full space-y-8 max-w-2xl">
            
            {/* Printer Selection */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
              <label htmlFor="select-printer" className="block text-2xl font-semibold mb-4 text-[#002]">
                📱 Select Printer
              </label>
              <select
                id="select-printer"
                className="text-black w-full text-xl p-4 rounded-lg border-2 border-transparent focus:border-[#002] focus:outline-none transition-all duration-300 bg-white/90"
                value={selectedPrinter}
                onChange={(e) => setSelectedPrinter(e.target.value)}
              >
                <option value="" className="text-lg">-- Select a Printer --</option>
                {printers.map((printer, index) => (
                  <option key={index} value={printer} className="text-lg">
                    {printer}
                  </option>
                ))}
              </select>
              {printers.length === 0 && (
                <p className="text-[#002448] text-lg mt-2">⚠️ No printers found. Please check your printer connections.</p>
              )}
            </div>

            {/* Print Size Selection */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
              <label htmlFor="print-size" className="block text-2xl font-semibold mb-4 text-[#002]">
                📏 Print Size
              </label>
              <select
                id="print-size"
                className="text-black w-full text-xl p-4 rounded-lg border-2 border-transparent focus:border-[#002] focus:outline-none transition-all duration-300 bg-white/90"
                value={printSize}
                onChange={(e) => setPrintSize(e.target.value)}
              >
                <option value="4x6" className="text-lg">4x6 Portrait</option>
                <option value="6x4 Landscape" className="text-lg">6x4 Landscape</option>
              </select>
            </div>

            {/* Settings Preview */}
            <div className="bg-gradient-to-r from-[#002]/20 to-[#A68129]/20 backdrop-blur-sm rounded-xl p-6 border border-[#002]/30">
              <h3 className="text-xl font-semibold mb-3 text-[#002]">📋 Current Settings</h3>
              <div className="space-y-2 text-lg">
                <div className="flex justify-between">
                  <span className="opacity-80">Printer:</span>
                  <span className="font-semibold">{selectedPrinter || "Not selected"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="opacity-80">Size:</span>
                  <span className="font-semibold">{printSize}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <button 
            className={`bg-[#002448] px-12 py-4 text-2xl font-semibold rounded-xl mt-10 transition-all duration-300 transform hover:scale-105 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none w-full max-w-md ${
              isSaving ? 'animate-pulse' : ''
            }`}
            onClick={saveSettings}
            disabled={!isFormValid || isSaving}
          >
            {isSaving ? '⏳ Saving...' : '💾 Save Settings'}
          </button>

          {/* Back Link */}
          <Link 
            to="/" 
            className="text-xl text-white/80 hover:text-white underline transition-all duration-300 hover:scale-105 flex items-center gap-2 mt-6"
          >
            <span>←</span> Back to Face Swap App
          </Link>
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center text-white/60">
          <p className="text-lg">
            Settings will be applied to all future print jobs
          </p>
        </div>
      </div>
    </div>
  );
}
