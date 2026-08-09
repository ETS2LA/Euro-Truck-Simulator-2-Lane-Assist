<script lang="ts">
    interface VerticalSelectorProps {
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
        selectedIndex = $bindable(0), 
        onSelect 
    }: VerticalSelectorProps = $props();

    let isOpen = $state(false);
</script>

<div class="flex flex-col gap-2">
    <div class="flex flex-col">
        <p>{title}</p>
        <p class="description">{description}</p>
    </div>

    <div class="relative w-full">
        <button 
            class={"w-full h-11 border border-control-bg bg-control-bg rounded-md items-center flex px-4 justify-between" + (isOpen ? ' border-accent-dark!' : '')}
            onclick={() => isOpen = !isOpen}
        >
            <p>{options[selectedIndex]}</p>
            <svg class={"description transition-transform duration-200" + (isOpen ? " rotate-180" : "")} xmlns="http://www.w3.org/2000/svg" width="1.5em" height="1.5em" viewBox="0 0 24 24">
                <path d="M0 0h24v24H0z" fill="none" />
                <path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m6 9l6 6l6-6" />
            </svg>
        </button>

        {#if isOpen}
            <div class="absolute top-full left-0 mt-1 w-full max-h-48 bg-control-bg-dark rounded-md z-50 overflow-y-auto flex flex-col shadow-lg">
                {#each options as option, index}
                    <button
                        class={"w-full px-4 py-2 text-left description hover:bg-control/50 hover:text-text text-[14px] transition-colors" + (index === selectedIndex ? ' text-text bg-accent-dark!' : '')}
                        onclick={() => {
                            onSelect?.(index);
                            selectedIndex = index;
                            isOpen = false;
                        }}>
                        {option}
                    </button>
                {/each}
            </div>
        {/if}
    </div>
</div>