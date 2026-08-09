<script lang="ts">
  import { browser } from '$app/environment';
  import Tooltip from './Tooltip.svelte';

  let isDragging = $state(false);
  let isHovering = $state(false);
  
  let startX = 0;
  let startY = 0;

  function sendMessage(msg: string) {
    if (browser && window.external?.sendMessage) {
      window.external.sendMessage(msg);
    }
  }

  function startDrag(event: MouseEvent) {
    if (event.button !== 0 || !browser) return;

    isDragging = true;
    startX = event.screenX;
    startY = event.screenY;

    window.addEventListener('mousemove', handleDrag);
    window.addEventListener('mouseup', stopDrag);
    sendMessage('window:focus');
  }

  function handleDrag(event: MouseEvent) {
    if (!isDragging) return;

    const dx = event.screenX - startX;
    const dy = event.screenY - startY;

    if (dx !== 0 || dy !== 0) {
      startX = event.screenX;
      startY = event.screenY;
      sendMessage(`window:moveBy:${dx},${dy}`);
    }
  }

  function stopDrag() {
    if (!browser) return;
    isDragging = false;
    window.removeEventListener('mousemove', handleDrag);
    window.removeEventListener('mouseup', stopDrag);
  }

  function minimize() { sendMessage('window:minimize'); }
  function maximize() { sendMessage('window:maximize'); }
  function close() { sendMessage('window:close'); }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<header 
  class="titlebar" 
  onmousedown={startDrag} 
  onmouseenter={() => isHovering = true} 
  onmouseleave={() => isHovering = false} 
  style:cursor={isDragging ? 'grabbing' : 'grab'}
>
  <br/>

  <div 
    class="absolute left-1.25 right-0 top-0 h-1 rounded-md transition-colors" 
    style:background-color={
      isDragging ? 'var(--description)' : 
      isHovering ? 'var(--control)' : 'transparent'
    }
  ></div>

  <div class="absolute top-0.75 right-0.75 size-1 bg-description rounded-md z-40"></div>

  <div 
    class="group z-50 flex h-full bg-bg opacity-0 hover:opacity-100 transition-opacity rounded-bl-md border-r border-border rounded-tr-md p-1 items-center"
    onmouseenter={() => isHovering = false} 
    onmouseleave={() => isHovering = true}
  >
    <Tooltip content="Minimize" timeout={1000}>
      <button onclick={minimize} class="w-5 p-0.5 text-description hover:text-text transition-colors flex items-center cursor-pointer" title="Minimize" aria-label="Minimize">
        <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24">
          <path d="M0 0h24v24H0z" fill="none" />
          <path fill="currentColor" d="M7 19h10c.55 0 1 .45 1 1s-.45 1-1 1H7c-.55 0-1-.45-1-1s.45-1 1-1" />
        </svg>
      </button>
    </Tooltip>
    
    <Tooltip content="Maximize" timeout={1000}>
      <button onclick={maximize} class="w-5 p-0.5 text-description hover:text-text transition-colors flex items-center cursor-pointer" title="Maximize" aria-label="Maximize">
        <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24">
          <path d="M0 0h24v24H0z" fill="none" />
          <path fill="currentColor" d="M19 3H5c-1.11 0-2 .89-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2m0 2v14H5V5z" />
        </svg>
      </button>
    </Tooltip>
    
    <Tooltip content="Close" timeout={1000}>
      <button onclick={close} class="w-5 p-0.5 text-description hover:text-text transition-colors flex items-center cursor-pointer" title="Close" aria-label="Close">
        <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24">
          <path d="M0 0h24v24H0z" fill="none" />
          <path fill="currentColor" d="m12 13.4l-4.9 4.9q-.275.275-.7.275t-.7-.275t-.275-.7t.275-.7l4.9-4.9l-4.9-4.9q-.275-.275-.275-.7t.275-.7t.7-.275t.7.275l4.9 4.9l4.9-4.9q.275-.275.7-.275t.7.275t.275.7t-.275.7L13.4 12l4.9 4.9q.275.275.275.7t-.275.7t-.7.275t-.7-.275z" />
        </svg>
      </button>
    </Tooltip>
  </div>
</header>

<style>
  .titlebar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 20px;
    user-select: none;
    left: 200px;
    margin-left: auto;
    position: absolute;
    right: 0;
  }
</style>