<script>
    let { className = '', orientation = 'horizontal', label = '' } = $props();
</script>

<div class={`flex ${orientation === 'horizontal' ? 'flex-row' : 'flex-col'} items-center ${className}`}>
    <div class="flex-1 border-t border-description/50"></div>
    {#if label}
        <span class="px-2 description">{label}</span>
    {/if}
    <div class="flex-1 border-t border-description/50"></div>
</div>