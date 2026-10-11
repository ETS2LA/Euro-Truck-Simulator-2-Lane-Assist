window.initNotificationHover = function () {
    if (window.notificationHoverHandler) return;

    let hideTimeout;

    const setNotificationsVisible = (visible) => {
        document.querySelectorAll('[data-notification-hover-target]').forEach((target) => {
            target.style.opacity = visible ? '1' : '0';
            target.style.pointerEvents = visible ? 'auto' : 'none';
        });
    };

    const hideAfterInactivity = () => {
        clearTimeout(hideTimeout);
        hideTimeout = setTimeout(() => setNotificationsVisible(false), 600);
    };

    const updateOpacity = (event) => {
        const insideNotification = [...document.querySelectorAll('[data-notification-hover-target]')]
            .some((target) => {
                const rect = target.getBoundingClientRect();
                return event.clientX >= rect.left &&
                    event.clientX <= rect.right &&
                    event.clientY >= rect.top &&
                    event.clientY <= rect.bottom;
            });

        if (insideNotification) {
            hideAfterInactivity();
            return;
        }

        clearTimeout(hideTimeout);
        setNotificationsVisible(true);
    };

    document.addEventListener('pointermove', updateOpacity, {
        passive: true
    });

    window.notificationHoverHandler = updateOpacity;
};