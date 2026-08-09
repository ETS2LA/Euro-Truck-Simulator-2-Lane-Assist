<script>
  import SidebarTitle from '../../components/SidebarTitle.svelte';
  import SidebarButton from '../../components/SidebarButton.svelte';

  let { children } = $props();
</script>

<div class="flex h-full w-full gap-0">
    <div class="w-[230px] pl-4 pt-4 pr-4 pt-2.5 flex gap-6.5 flex-col h-full">
        <div class="flex flex-col gap-0">
            <SidebarTitle title="Driving" />
            <SidebarButton name="Assistant" path="/settings/assistant" />
            <SidebarButton name="Data Parsing" path="/settings/data" />
        </div>
    
        <div class="flex flex-col gap-0">
            <SidebarTitle title="General" />
            <SidebarButton name="Display" path="/settings/display" />
            <SidebarButton name="Audio" path="/settings/audio" />
            <SidebarButton name="Controls" path="/settings/controls" />
        </div>
    
        <div class="flex flex-col gap-0">
            <SidebarTitle title="Additional" />
            <SidebarButton name="Game SDK" path="/settings/sdk" />
            <SidebarButton name="Experiments" path="/settings/experiments" />
        </div>
    
        <div class="flex flex-col gap-0">
            <SidebarTitle title="Networking" />
            <SidebarButton name="Account" path="/settings/account" />
            <SidebarButton name="Telemetry" path="/settings/telemetry" />
        </div>
    
        <div class="flex flex-col w-58 gap-0 bottom-6 absolute">
            <SidebarButton name="Check For Updates" path="/settings/updates" />
        </div>
    </div>

    <div class="mt-3 mb-3 bg-control-bg w-0.5 rounded-md"></div>
    
    <div class="w-full h-full overflow-y-auto">
        {@render children()}
    </div>
</div>