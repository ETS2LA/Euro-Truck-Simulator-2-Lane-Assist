<script lang="ts">
    interface SwitchProps {
        title: string;
        description: string;
        value?: boolean;
        onToggle?: (value: boolean) => void;
    }

    let { 
        title, 
        description, 
        value = false, 
        onToggle 
    }: SwitchProps = $props();
</script>

<div class="flex flex-col gap-1">
    <div class="flex justify-between">
        <p>{title}</p>
        <!-- svelte-ignore a11y_consider_explicit_label -->
        <button class={"cursor-pointer w-12 bg-control h-6 rounded-full" + (value ? ' bg-accent-border!' : '')} onclick={() => {
            onToggle?.(!value);
            value = !value;
        }}>
            <div class={"ml-1 size-[15px] bg-text-l/80 rounded-full transition-all duration-200" + (value ? ' translate-x-[19px] bg-text-l!' : '')}></div>
        </button>
    </div>
    <p class="description">{description}</p>
</div>