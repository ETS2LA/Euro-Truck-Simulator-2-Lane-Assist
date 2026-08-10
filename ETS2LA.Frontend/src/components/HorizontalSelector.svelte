<script lang="ts">
    interface HorizontalSelectorProps {
        title: string;
        description: string;
        options?: string[];
        selectedIndex?: number;
        disabled?: boolean;
        onSelect?: (index: number) => void;
    }

    let { 
        title, 
        description, 
        options = [], 
        selectedIndex = 0, 
        onSelect
    }: HorizontalSelectorProps = $props();
</script>

<div class="flex flex-col">
    <div>
        <p>{title}</p>
        <p class="description">{description}</p>
    </div>
    <div class="flex gap-4 mt-2">
        {#each options as option, index}
            <button
                class={"px-4 py-2 cursor-pointer rounded-sm bg-control-bg-dark description hover:bg-control/50 hover:text-text text-[14px] transition-colors" + (index === selectedIndex ? ' text-text bg-accent-dark!' : '')}
                onclick={() => {
                    onSelect?.(index);
                    selectedIndex = index;
                }}
            >
                {option}
            </button>
        {/each}
    </div>
</div>