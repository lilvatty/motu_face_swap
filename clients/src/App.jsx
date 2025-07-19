import { useEffect, useState } from "react";

// Pages
import UserForm from "./components/UserForm";
import Gender from "./components/Gender";
import Template from "./components/Template";
import Capture from "./components/Capture";
import Result from "./components/Result";

import { saveUserData } from "./API";

import StartButton from "./components/ui/StartButton";
import SaveButton from "./components/ui/SaveButton";
import SmallButtons from "./components/ui/SmallButtons";

function App() {
  const [step, setStep] = useState(0);
  const [started, setStarted] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [animationDirection, setAnimationDirection] = useState("forward");

  // State for UserForm Component
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");

  const handleUserData = async () => {
    const userData = {
      name: name.trim(),
      phone: phone.trim(),
    };
    const result = await saveUserData(userData);

    if (result) {
      console.log("User data saved successfully!");
    } else {
      console.error("Error saving user data");
    }
  };

  const start = () => {
    setStarted(true);
  };

  const nextStep = () => {
    if (isTransitioning) return; // Prevent multiple clicks during transition

    setIsTransitioning(true);
    setAnimationDirection("forward");

    setTimeout(() => {
      if (step === 0) {
        handleUserData();
      }
      setStep((prevStep) =>
        prevStep < steps.length ? prevStep + 1 : prevStep
      );

      setTimeout(() => {
        setIsTransitioning(false);
      }, 300); // Half of the total transition time
    }, 300);
  };

  const backStep = () => {
    if (isTransitioning) return; // Prevent multiple clicks during transition

    setIsTransitioning(true);
    setAnimationDirection("backward");

    setTimeout(() => {
      setStep((prevStep) => (prevStep > 0 ? prevStep - 1 : prevStep));

      setTimeout(() => {
        setIsTransitioning(false);
      }, 10);
    }, 10);
  };

  // Disable Next button if any field in UserForm is empty
  const isNextDisabled = step === 0 && (!name.trim() || !phone.trim());

  const backgroundImage = ["/ui/1.png", "/ui/3.png", "/ui/4.png", "/ui/5.png"];

  const steps = [
    <UserForm
      key={1}
      onNext={nextStep}
      name={name}
      setName={setName}
      phone={phone}
      setPhone={setPhone}
    />,
    <Gender key={2} />,
    <Template key={3} />,
    <Capture key={4} goTo={nextStep} goBack={backStep} />,
    <Result key={5} />,
  ];

  return (
    <div
      className="h-screen m-0 p-0 flex flex-col justify-evenly relative overflow-hidden"
      style={{
        backgroundImage: `url(${backgroundImage[step]})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        transition: "background-image 0.6s ease-in-out",
      }}
    >
      <div
        className={`flex flex-col items-center justify-center h-full ${
          started ? "hidden" : "block"
        }`}
      >
        <img src="/logo.png" alt="logo" className="w-1/2 mb-10" />
        <StartButton text="Tap to Start" onClick={start} />
      </div>

      {started && (
        <div>
          {/* Render Pages with transition effects */}
          <div
            className={`transition-all duration-600 ease-in-out ${
              isTransitioning
                ? animationDirection === "forward"
                  ? "transform -translate-x-full opacity-0"
                  : "transform translate-x-full opacity-0"
                : "transform translate-x-0 opacity-100"
            }`}
            style={{
              transitionProperty: "transform, opacity",
              transitionDuration: "0.6s",
              transitionTimingFunction: "cubic-bezier(0.4, 0, 0.2, 1)",
            }}
          >
            {steps[step]}
          </div>

          {/* Buttons */}
          {step < 2 && (
            <div className="flex justify-center items-center">
              <SaveButton
                text={step === 0 ? "Save & Next" : "Next"}
                onClick={nextStep}
                isDisabled={isNextDisabled}
              />
            </div>
          )}
          {step > 1 && step < 3 && (
            <div className="flex justify-center items-center">
              <SmallButtons back={backStep} next={nextStep} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
