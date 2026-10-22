window.initTitlebarDrag = function (element) {
    let isDragging = false;
    let startX = 0;
    let startY = 0;

    element.addEventListener('mousedown', (e) => {
        if (e.button !== 0 || e.target.closest('.titlebar-no-drag')) return;

        isDragging = true;
        startX = e.screenX;
        startY = e.screenY;

        const handleMouseMove = (ev) => {
            if (!isDragging) return;
            const dx = ev.screenX - startX;
            const dy = ev.screenY - startY;

            if (dx !== 0 || dy !== 0) {
                startX = ev.screenX;
                startY = ev.screenY;
                if (window.external && window.external.sendMessage) {
                    window.external.sendMessage(`window:moveBy:${dx},${dy}`);
                }
            }
        };

        const handleMouseUp = () => {
            isDragging = false;
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
            window.sendIPCMessage('window:notopmost');
        };

        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mouseup', handleMouseUp);

        if (window.external && window.external.sendMessage) {
            window.external.sendMessage('window:topmost');
        }
    });
};

window.initResizing = function (element) {
    let isResizing = false;
    let startX = 0, startY = 0;
    let startWidth = 0, startHeight = 0;
    let currentDirection = '';

    const minContentHeight = 560;
    let lastPixelRatio = 0;

    function updateMinHeight() {
        if (window.devicePixelRatio === lastPixelRatio) return;
        lastPixelRatio = window.devicePixelRatio;

        // Take scaling into account
        const scale = window.outerHeight / window.innerHeight;
        window.sendIPCMessage(`window:setMinHeight:${Math.ceil(minContentHeight * scale)}`);
    }

    updateMinHeight();
    window.addEventListener('resize', updateMinHeight);

    window.startResize = function (event, direction) {
        if (event.button !== 0) return;
        isResizing = true;
        currentDirection = direction;
        startX = event.screenX;
        startY = event.screenY;
        startWidth = window.outerWidth;
        startHeight = window.outerHeight;

        window.addEventListener('mousemove', handleResizeMouseMove);
        window.addEventListener('mouseup', stopResize);
    };

    function handleResizeMouseMove(event) {
        if (!isResizing) return;

        let newWidth = startWidth;
        let newHeight = startHeight;

        const deltaX = event.screenX - startX;
        const deltaY = event.screenY - startY;

        if (currentDirection.includes('e')) newWidth = startWidth + deltaX;
        if (currentDirection.includes('s')) newHeight = startHeight + deltaY;

        if (window.external && window.external.sendMessage) {
            window.external.sendMessage(`window:setSize:${Math.max(800, newWidth)},${Math.max(500, newHeight)}`);
        }
    }

    function stopResize() {
        isResizing = false;
        window.removeEventListener('mousemove', handleResizeMouseMove);
        window.removeEventListener('mouseup', stopResize);
    }
}