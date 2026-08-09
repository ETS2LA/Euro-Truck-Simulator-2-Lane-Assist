function triggerEvent(eventName: string, data?: string) {
    window.external.sendMessage(`event:${eventName}:${data ?? ''}`);
}

export { triggerEvent };