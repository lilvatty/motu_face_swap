import React, { useEffect, useState } from "react";
import { fetchTemplates } from "../API";

const Template = () => {
  const [templates, setTemplates] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0); // Track the center image index

  useEffect(() => {
    const gender = localStorage.getItem("gender");
    const loadTemplates = async () => {
      try {
        const fetchedTemplates = await fetchTemplates(gender);
        setTemplates(fetchedTemplates);
      } catch (error) {
        setTemplates([]);
        console.error("Fetching templates error: ", error);
      }
    };

    loadTemplates();
  }, []);

  // Handle image click to center that image
  const handleImageClick = (index) => {
    setCurrentIndex(index);
    localStorage.setItem("selectedTemplate", templates[index].imageUrl);
  };

  // Get the images to display (center + side images)
  const getDisplayImages = () => {
    if (templates.length === 0) return [];

    const displayImages = [];
    const totalImages = templates.length;

    // Show up to 3 images (left, center, right)
    for (let i = -1; i <= 1; i++) {
      const index = (currentIndex + i + totalImages) % totalImages;
      displayImages.push({
        template: templates[index],
        originalIndex: index,
        position: i, // -1 for left, 0 for center, 1 for right
      });
    }

    return displayImages;
  };

  const displayImages = getDisplayImages();

  return (
    <div className="px-4">
      {templates.length > 0 ? (
        <div className="text-center">
          <h1 className="main-text text-[5em] font-bold">
            Choose Your Template
          </h1>
          <div className="flex items-center justify-center gap-x-8 py-10">
            {displayImages.map(
              ({ template, originalIndex, position }, index) => (
                <img
                  key={originalIndex}
                  src={template.imageUrl}
                  alt="templates"
                  className={`
                  object-cover cursor-pointer transition-all duration-300 ease-in-out rounded-3xl
                  ${
                    position === 0
                      ? "w-[430px] h-[639px] z-10 border-[4px] border-[#002448]"
                      : "w-[206px] h-[381px] opacity-70 hover:opacity-90"
                  }
                `}
                  onClick={() => handleImageClick(originalIndex)}
                />
              )
            )}
          </div>
        </div>
      ) : (
        <h1 className="text-white text-center">No templates available.</h1>
      )}
    </div>
  );
};

export default Template;
