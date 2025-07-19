import React, { useState } from "react";

// Images
// 1. Upload di folder public
// 2. E.G: import men from "/nama_file.png";
import Men from "../assets/men/ai_00075_.png";
import Women from "../assets/women/ai_00042_.png";

export default function Gender() {
  const [selectedGender, setSelectedGender] = useState("");

  const genders = [
    { key: "men", src: Men, alt: "Male" },
    { key: "women", src: Women, alt: "Female" },
  ];

  // Save gender selection to state and localStorage
  const saveGender = (selectedGender) => {
    setSelectedGender(selectedGender);
    localStorage.setItem("gender", selectedGender);
  };

  return (
    <div className="w-full text-center main-text">
      <h1>Choose Your Gender</h1>
      <div className="flex mx-auto justify-center items-center gap-6 mt-[38px]">
        {genders.map((gender) => (
          <div key={gender.key}>
            <div
              className={`w-[472px] h-[571px] bg-[#002448] rounded-3xl relative mb-[38px] ${selectedGender === gender.key ? "border-[12px] border-[#002448]" : ""}`}
            >
              <img
                key={gender.key}
                className="w-full h-full object-cover absolute inset-0"
                src={gender.src}
                alt={gender.alt}
                onClick={() => saveGender(gender.key)}
              />
            </div>
            <span>{gender.alt}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
