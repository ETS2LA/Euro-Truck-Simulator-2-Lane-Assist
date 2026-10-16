// Enter -> Send, Shift+Enter -> New line
// Blazor can't conditionally preventDefault,
// so this needs to be in JS.
window.chatInput = {
    attach: function (element, dotNetRef) {
        if (!element || element.__chatInputAttached) {
            return;
        }

        element.__chatInputAttached = true;
        element.__chatInputHandler = function (event) {
            if (event.key !== "Enter" || event.shiftKey || event.isComposing) {
                return;
            }

            event.preventDefault();
            dotNetRef.invokeMethodAsync("OnEnterPressed");
        };

        element.addEventListener("keydown", element.__chatInputHandler);
    },

    detach: function (element) {
        if (!element || !element.__chatInputHandler) {
            return;
        }

        element.removeEventListener("keydown", element.__chatInputHandler);
        element.__chatInputHandler = null;
        element.__chatInputAttached = false;
    }
};
