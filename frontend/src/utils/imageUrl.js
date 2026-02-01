/**
 * Get the full URL for a product image
 * @param {string} imagePath - The image path from the API (e.g., "/uploads/products/image.jpg")
 * @returns {string} Full image URL or placeholder
 */
export const getImageUrl = (imagePath) => {
  if (!imagePath) {
    return 'https://via.placeholder.com/300x200?text=No+Image';
  }

  // If it's already a full URL, return as is
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }

  // Build full URL from API base URL
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';
  const baseUrl = API_BASE_URL.replace('/api', ''); // Remove /api suffix

  return `${baseUrl}${imagePath}`;
};

export default getImageUrl;
