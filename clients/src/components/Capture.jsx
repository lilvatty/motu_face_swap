import { useRef, useState, useEffect } from "react";
import { swapFace } from "../API";

export default function Capture({ goBack, goTo }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [capturedPhoto, setCapturedPhoto] = useState(null);
  const [isVideoVisible, setIsVideoVisible] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [isCountingDown, setIsCountingDown] = useState(false);
  const [countdown, setCountdown] = useState(3);

  useEffect(() => {
    startCamera();
    return () => {
      if (videoRef.current?.srcObject) {
        const tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, []);

  useEffect(() => {
    let countdownInterval;
    if (isCountingDown && countdown > 0) {
      countdownInterval = setInterval(() => {
        setCountdown((prev) => prev - 1);
      }, 1000);
    } else if (countdown === 0) {
      onCapture();
      setIsCountingDown(false);
      setCountdown(3);
    }

    return () => {
      if (countdownInterval) {
        clearInterval(countdownInterval);
      }
    };
  }, [isCountingDown, countdown]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" }, // Request front camera
      });
      videoRef.current.srcObject = stream;

      const video = videoRef.current;
      video.onloadedmetadata = () => {
        canvasRef.current.width = video.videoWidth;
        canvasRef.current.height = video.videoHeight;
      };
    } catch (error) {
      console.error("Error accessing the camera:", error);
    }
  };

  const startCountdown = () => {
    setIsCountingDown(true);
  };

  const onCapture = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext("2d");

    // Mirror the canvas to match the video preview
    context.scale(-1, 1);
    context.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
    context.scale(-1, 1); // Reset the scale

    canvas.toBlob((blob) => {
      setCapturedPhoto(blob);
      localStorage.setItem("capturedPhoto", URL.createObjectURL(blob));
    }, "image/jpeg");

    setIsVideoVisible(false);
  };

  const handleSwapFace = async (sourceImageBlob) => {
    const templateUrl = localStorage.getItem("selectedTemplate");
    const sourceFile = new File([sourceImageBlob], "source.jpg", {
      type: "image/jpeg",
    });

    setIsLoading(true);

    try {
      const swappedImageUrl = await swapFace(templateUrl, sourceFile);
      if (swappedImageUrl) {
        setCapturedPhoto(swappedImageUrl);
        localStorage.setItem("swappedPhoto", swappedImageUrl);
      }
    } catch (error) {
      console.error("Error swapping face:", error);
    } finally {
      setIsLoading(false);
      goTo();
    }
  };

  const handleCancel = () => {
    setCapturedPhoto(null);
    setIsVideoVisible(true);
    startCamera();
  };

  return (
    <div className="flex flex-col items-center justify-center">
      {isLoading && (
        <div className="z-10 absolute inset-0 grid mb-[5em]">
          <img src="/loading.gif" alt="loading" className="m-auto w-2/5" />
        </div>
      )}

      <div className="relative">
        <div className="w-[966px] h-[1526px] bg-black rounded-3xl flex items-center justify-center overflow-hidden">
          {isVideoVisible ? (
            <>
              <video
                ref={videoRef}
                autoPlay
                className="w-full h-full object-cover rounded-3xl transform scale-x-[-1]"
              />
              {isCountingDown && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="flex items-center justify-center w-40 h-40 bg-black bg-opacity-50 rounded-full">
                    <span className="text-white text-[8em] font-bold animate-pulse">
                      {countdown}
                    </span>
                  </div>
                </div>
              )}
            </>
          ) : (
            capturedPhoto && (
              <img
                src={
                  typeof capturedPhoto === "string"
                    ? capturedPhoto
                    : URL.createObjectURL(capturedPhoto)
                }
                alt="Captured"
                className="w-full h-full object-cover rounded-3xl"
              />
            )
          )}
        </div>
        <canvas ref={canvasRef} className="hidden" />
      </div>

      <div className="flex mt-16 gap-x-[67px]">
        {isVideoVisible ? (
          <>
            <button
              onClick={goBack}
              className="w-[418px] h-[126px] rounded-3xl border-4 border-[#002448] text-[3.25em] font-semibold"
              disabled={isCountingDown}
            >
              <span className="">Back</span>
            </button>
            <button
              onClick={startCountdown}
              className="w-[418px] h-[126px] border-4 rounded-3xl main-button"
              disabled={isCountingDown}
            >
              <span className="">Capture</span>
            </button>
          </>
        ) : (
          <>
            <button
              onClick={handleCancel}
              className="w-[418px] h-[126px] rounded-3xl border-4 border-[#002448] text-[3.25em] font-semibold"
            >
              <span className="">Retake</span>
            </button>
            <button
              onClick={() => handleSwapFace(capturedPhoto)}
              className="w-[418px] h-[126px] border-4 rounded-3xl main-button"
            >
              <span className="">Process</span>
            </button>
          </>
        )}
      </div>
    </div>
  );
}
