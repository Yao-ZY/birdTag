// src/utils/urlToBase64.js
export const urlToBase64 = async (url) => {
  try {
    if (url.startsWith('data:')) {
      return url;
    }

    const checkImage = new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve();
      img.onerror = (err) => reject(new Error(`File Load Fail: ${err.message}`));
      img.crossOrigin = 'anonymous'; 
      img.src = url;
    });

    await checkImage;

    const response = await fetch(url, {
      mode: 'cors', 
    });

    if (!response.ok) {
      throw new Error(`HTTP Error! Status Code: ${response.status}`);
    }

    const blob = await response.blob();
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  } catch (error) {
    console.error('File convert Fail:', error);
    return null;
  }
};