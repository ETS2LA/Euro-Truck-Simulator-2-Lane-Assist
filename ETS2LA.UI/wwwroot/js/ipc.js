window.sendIPCMessage = function (msg) {
    if (window.external && window.external.sendMessage) {
        window.external.sendMessage(msg);
    }
};