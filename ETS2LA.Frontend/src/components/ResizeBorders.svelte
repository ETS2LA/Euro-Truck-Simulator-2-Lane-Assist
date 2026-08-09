<script>
  let isResizing = false;
  let startX = 0;
  let startY = 0;
  let startWidth = 0;
  let startHeight = 0;
  let currentDirection = '';

  /**
     * @param {MouseEvent & { currentTarget: EventTarget & HTMLDivElement; }} event
     * @param {string} direction
     */
  function startResize(event, direction) {
    isResizing = true;
    currentDirection = direction;
    startX = event.screenX;
    startY = event.screenY;
    startWidth = window.innerWidth;
    startHeight = window.innerHeight;

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', stopResize);
  }

  /**
     * @param {{ screenX: number; screenY: number; }} event
     */
  function handleMouseMove(event) {
    if (!isResizing) return;

    let newWidth = startWidth;
    let newHeight = startHeight;

    const deltaX = event.screenX - startX;
    const deltaY = event.screenY - startY;

    if (currentDirection.includes('e')) newWidth = startWidth + deltaX;
    if (currentDirection.includes('s')) newHeight = startHeight + deltaY;

    // Send updated dimensions to C#
    window.external.sendMessage(`window:setSize:${Math.max(800, newWidth)},${Math.max(500, newHeight)}`);
  }

  function stopResize() {
    isResizing = false;
    window.removeEventListener('mousemove', handleMouseMove);
    window.removeEventListener('mouseup', stopResize);
  }
</script>

<div class="resize-handle e" onmousedown={(e) => startResize(e, 'e')}></div>
<div class="resize-handle s" onmousedown={(e) => startResize(e, 's')}></div>
<div class="resize-handle se" onmousedown={(e) => startResize(e, 'se')}></div>

<style>
  .resize-handle {
    position: fixed;
    z-index: 9999;
    -webkit-app-region: no-drag;
  }

  .e {
    top: 36px;
    right: 0;
    width: 6px;
    height: 100%;
    cursor: e-resize;
  }

  .s {
    bottom: 0;
    left: 0;
    width: 100%;
    height: 6px;
    cursor: s-resize;
  }

  .se {
    bottom: 0;
    right: 0;
    width: 12px;
    height: 12px;
    cursor: se-resize;
  }
</style>