<script>
	let { content, timeout, className = '', children } = $props();

	let isHovered = $state(false);
    let firstHovered = $state(Date.now());
	let x = $state(0);
	let y = $state(0);
	
	/**
     * @param {{ pageX: number; pageY: number; }} event
     */
	function mouseOver(event) {
        if (!isHovered) {
            firstHovered = Date.now();
        } else if (Date.now() - firstHovered < timeout) {
            return;
        }
		isHovered = true;
		x = event.pageX + 5;
		y = event.pageY + 5;
	}
	/**
     * @param {{ pageX: number; pageY: number; }} event
     */
	function mouseMove(event) {
		x = event.pageX + 5;
		y = event.pageY + 5;
	}
	function mouseLeave() {
		isHovered = false;
	}
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_mouse_events_have_key_events -->
<div
    class={className}
	onmouseover={mouseOver}
    onmouseleave={mouseLeave}
	onmousemove={mouseMove}>
	{@render children()}
</div>

{#if isHovered && Date.now() - firstHovered >= timeout}
	<div style="top: {y}px; left: {x}px;" class="absolute p-1 rounded-sm bg-control-bg border border-border">{content}</div>
{/if}