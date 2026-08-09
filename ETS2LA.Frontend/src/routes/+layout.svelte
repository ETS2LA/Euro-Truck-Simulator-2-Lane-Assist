<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap" rel="stylesheet">

<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	
	import Titlebar from '../components/Titlebar.svelte'
	import ResizeBorders from '../components/ResizeBorders.svelte'
	import SidebarTitle from '../components/SidebarTitle.svelte'
	import SidebarButton from '../components/SidebarButton.svelte'

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<main class="flex h-screen w-screen flex-col border border-border rounded-md bg-bg">
  <ResizeBorders />
  <Titlebar/>
  <div class="flex p-1.5 h-full w-full">
    <!-- Sidebar -->
    <div class="w-[230px] pl-1 pr-3 pt-2.5 flex gap-6.5 flex-col h-full">
      <div class="flex pl-3 flex-col">
        <div class="flex items-end gap-[2px]">
          <p class="font-bold">ETS2LA</p>
          <p class="text-[12px] mb-[1px]">Development</p>
        </div>
        <p class="description text-[11px] font-medium -my-0.5">v2026.8.3.4079</p>
      </div>

      <div class="flex flex-col gap-0">
        <SidebarTitle title="Main" />
        <SidebarButton name="Dashboard" path="/" />
        <SidebarButton name="Visualization" path="/visualization" />
      </div>

      <div class="flex flex-col gap-0">
        <SidebarTitle title="Plugins" />
        <SidebarButton name="Manager" path="/plugins/manager" />
        <SidebarButton name="Catalogue" path="/plugins/catalogue" />
        <SidebarButton name="Adjustments" path="/plugins/adjustments" />
      </div>

      <div class="flex flex-col gap-0">
        <SidebarTitle title="Help" />
        <SidebarButton name="Wiki / FAQ" path="/help/wiki" />
        <SidebarButton name="Contact Us" path="/help/contact" />
      </div>

      <div class="flex flex-col w-52 gap-0 bottom-4 absolute">
        <SidebarButton name="Settings" path="/settings" />
        <SidebarButton name="Anonymous" path="/settings/user" />
      </div>

    </div>

    <!-- Content -->
    <div class="w-full h-full bg-bg-dark rounded-md rounded-l-lg overflow-y-auto">
		  {@render children()}      
    </div>
  </div>
</main>


