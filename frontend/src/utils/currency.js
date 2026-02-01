// Currency formatting utilities

/**
 * Formats a number as Indian Rupees
 * @param {number|string} amount - The amount to format
 * @param {boolean} showDecimals - Whether to show decimal places (default: true)
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount, showDecimals = true) => {
  const numAmount = parseFloat(amount);

  if (isNaN(numAmount)) {
    return '₹0.00';
  }

  if (showDecimals) {
    return `₹${numAmount.toFixed(2)}`;
  }

  return `₹${Math.round(numAmount)}`;
};

/**
 * Formats currency with Indian number system (lakhs, crores)
 * @param {number|string} amount - The amount to format
 * @returns {string} Formatted currency string with Indian numbering
 */
export const formatCurrencyIndian = (amount) => {
  const numAmount = parseFloat(amount);

  if (isNaN(numAmount)) {
    return '₹0.00';
  }

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numAmount);
};

export default formatCurrency;
