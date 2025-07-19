import React, { useState } from "react";
import { printImage } from "../API";

export default function Result() {
  const [qrCode, setQRCode] = useState(false);
  const [print, setPrint] = useState(false);
  const [printMessage, setPrintMessage] = useState(false);
  const [printer, setPrinter] = useState(""); // Printer selection
  const [printSize, setPrintSize] = useState("4x6"); // Default print size

  const handlePrint = async () => {
    const result = localStorage.getItem("swappedPhoto");

    if (!result) {
      alert("No image found to print!");
      return;
    }

    try {
      const imageBlob = await fetch(result).then((res) => res.blob());
      const response = await printImage(imageBlob, printer, printSize);

      if (response.message) {
        setPrint(false);
        PopUpPrint();
      } else {
        alert("Failed to print image.");
      }
    } catch (error) {
      console.error("Error during print:", error);
      alert("An error occurred while printing.");
    }
  };

  const PopUpPrint = () => {
    setPrintMessage(true);

    setTimeout(() => {
      setPrintMessage(false);
    }, 2000);
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="">
        <div className="w-[966px] h-[1526px] border-4 border-black rounded-3xl flex items-center justify-center overflow-hidden">
          <img
            src={localStorage.getItem("swappedPhoto")}
            alt="Swapped result"
            className="w-full h-full object-cover rounded-3xl"
          />
        </div>
      </div>

      <div className="flex mt-16 gap-x-[67px]">
        <button
          onClick={() => {
            setQRCode((prevState) => !prevState);
            setPrint(false);
          }}
          className="w-[418px] h-[126px] rounded-3xl border-4 border-[#002448] text-[3.25em] font-semibold flex items-center justify-center gap-4"
        >
          <img src="/qrcode.png" alt="QR code icon" className="w-12 h-12" />
          <span>QR</span>
        </button>
        <button
          onClick={() => {
            setPrint((prevState) => !prevState);
            setQRCode(false);
          }}
          className="w-[418px] h-[126px] border-4 rounded-3xl main-button flex items-center justify-center gap-4"
        >
          <span>Print</span>
        </button>
      </div>

      {qrCode && (
        <div className="z-10 absolute inset-0 bg-black/80 grid">
          <img
            src="/qr_code_result_demo.png"
            alt="QR Code Result"
            onClick={() => setQRCode(false)}
            className="w-3/5 m-auto"
          />
        </div>
      )}

      {print && (
        <div className="z-10 absolute inset-0 bg-black/80 text-white grid text-[4em] p-4">
          <div className="m-auto">
            <h1 className="mb-4">Print the image?</h1>
            <div className="flex gap-4">
              <button
                className="bg-red-500 text-white p-2 w-1/2 rounded-md"
                onClick={() => setPrint(false)}
              >
                No
              </button>
              <button
                className="bg-green-500 text-white p-2 w-1/2 rounded-md"
                onClick={handlePrint}
              >
                Yes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Print Pop-up */}
      {printMessage ? (
        <div className="bg-[#BF9A30] z-10 absolute w-fit mx-auto text-[5em] text-white py-2 px-8 rounded-md">
          Printed!
        </div>
      ) : null}
    </div>
  );
}
