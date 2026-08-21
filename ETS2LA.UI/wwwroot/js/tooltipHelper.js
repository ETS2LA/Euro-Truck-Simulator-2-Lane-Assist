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