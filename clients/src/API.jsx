const API_BASE_URL = "http://127.0.0.1:5000/api";

export const fetchTemplates = async (gender) => {
  try {
    const response = await fetch(`${API_BASE_URL}/templates?folder=${gender}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const filenames = await response.json();

    return filenames.map((filename) => ({
      filename,
      imageUrl: `${API_BASE_URL}/template?filepath=${gender}/${encodeURIComponent(
        filename
      )}`,
    }));
  } catch (error) {
    console.error("Error fetching templates:", error);
    throw error;
  }
};

export const swapFace = async (templateUrl, sourceImage) => {
  const formData = new FormData();

  try {
    // Fetch the template file from the URL
    const response = await fetch(templateUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch template: ${response.status}`);
    }

    const templateBlob = await response.blob();
    const templateFile = new File([templateBlob], "template.jpg", {
      type: templateBlob.type,
    });

    // Append the template file
    formData.append("template", templateFile);

    // Append the source image file
    formData.append("source", sourceImage, "source.jpg");

    // Send the POST request
    const result = await fetch(`${API_BASE_URL}/swap`, {
      method: "POST",
      body: formData,
    });

    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    const data = await result.json();

    if (data.image) {
      const swappedImageUrl = `data:image/jpeg;base64,${data.image}`;
      return swappedImageUrl;
    } else {
      console.error("Error: No image returned");
      return null;
    }
  } catch (error) {
    console.error("Error in swapFace:", error);
    return null;
  }
};

export const saveUserData = async (userData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/save-user-data`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });

    if (response.ok) {
      console.log("User data saved sucessfully!");
      return await response.json();
    }
  } catch (error) {
    console.error("Error in saveUserData:", error);
    return null;
  }
};

export const exportTableToCSV = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/export`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Get the blob data
    const blob = await response.blob();

    // Create a downloadable link for the file
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "user_table.csv");
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);

    // Clean up the URL object
    window.URL.revokeObjectURL(url);

    return { success: true };
  } catch (error) {
    console.error("Error exporting table:", error);
    return { success: false, error };
  }
};

export const fetchPrinters = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/printer/config`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching printers:", error);
    throw error;
  }
};

export const updatePrinterConfig = async (config) => {
  try {
    const response = await fetch(`${API_BASE_URL}/printer/config`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(config),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error updating printer config:", error);
    throw error;
  }
};

export const printImage = async (imageBlob) => {
  const formData = new FormData();
  formData.append("image", imageBlob, "image.jpg");

  try {
    const response = await fetch(`${API_BASE_URL}/printer/print`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error printing image:", error);
    throw error;
  }
};
