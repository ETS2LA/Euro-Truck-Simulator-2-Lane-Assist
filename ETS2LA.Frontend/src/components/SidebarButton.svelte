<script lang="ts">
  import { page } from '$app/state';
  let { name, path } = $props();
</script>

<a
  href={path}
  
  class={"px-3 py-1 flex hover:bg-control-bg rounded-md transition-colors" + 
    (page.url.pathname == path ? ' bg-control-bg text-[#ffffff]' 
    : (path != "/" && page.url.pathname.startsWith(path)) ? ' bg-control-bg text-[#ffffff]' 
    : '')}
>
  <span>
    {name}
  </span>
</a>