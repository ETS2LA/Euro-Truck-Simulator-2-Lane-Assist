window.getTooltipAutoPosition = (element) => {
    if (!element) return "top";
    
    const rect = element.getBoundingClientRect();
    const viewportWidth = window.innerWidth || document.documentElement.clientWidth;
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;

    const spaceTop = rect.top;
    const spaceBottom = viewportHeight - rect.bottom;
    const spaceLeft = rect.left;
    const spaceRight = viewportWidth - rect.right;

    if (spaceTop >= 100) return "top";
    if (spaceBottom >= 100) return "bottom";
    
    return spaceRight > spaceLeft ? "right" : "left";
};

window.getSliderPointerPercentage = (element, clientX) => {
    if (!element) return 0;

    const rect = element.getBoundingClientRect();
    if (rect.width <= 0) return 0;

    const thumbWidth = 12;
    const travelWidth = Math.max(1, rect.width - thumbWidth);
    const thumbPosition = clientX - rect.left - (thumbWidth / 2);

    return Math.max(0, Math.min(100, (thumbPosition / travelWidth) * 100));
};

window.getSliderValuePosition = (element, valuePercentage) => {
    if (!element) return valuePercentage;

    const rect = element.getBoundingClientRect();
    if (rect.width <= 0) return valuePercentage;

    const thumbWidth = 12;
    const thumbCenter = (thumbWidth / 2) + (Math.max(0, Math.min(100, valuePercentage)) / 100) * (rect.width - thumbWidth);
    return (thumbCenter / rect.width) * 100;
};