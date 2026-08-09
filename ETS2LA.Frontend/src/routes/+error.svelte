<script lang="ts">
	import { page } from '$app/state';
    let message = page.error?.message || 'Unknown error';

    const httpDescriptions: Record<number, string> = {
        400: "The server could not understand the request due to invalid syntax or corrupted request data.",
        401: "Authentication is required. The client must authenticate itself to get the requested response.",
        403: "You do not have permission to access this resource. The server understood the request but refuses to authorize it.",
        404: "The server cannot find the requested resource. The URL may be misspelled, or the resource has been removed.",
        405: "The request method is recognized by the server but is not supported by the target resource.",
        408: "The server timed out waiting for the request from the client.",
        429: "Too many requests. You have sent too many requests in a given amount of time.",
        500: "Internal server error. The server encountered an unexpected condition that prevented it from fulfilling the request.",
        502: "Bad gateway. The server, while acting as a gateway or proxy, received an invalid response from an inbound server.",
        503: "Service unavailable. The server is currently unable to handle the request due to temporary overloading or maintenance.",
        504: "Gateway timeout. The server was acting as a gateway or proxy and did not receive a timely response from the upstream server."
    };
</script>

<div class="flex flex-col p-6 w-lg">
    {#if message == "Not Found"}
        <img class="rounded-md" src="https://static2.klipy.com/ii/c3a19a0b747a76e98651f2b9a3cca5ff/4d/87/oyStUROc.gif" alt="Kermit is lost, he's looking at a map and around him." />
        <br/>
        <p>You took a wrong turn!</p>
        <p class="description">
            How did you get here? What were you even thinking?<br/>
            Do tell us in the <a href="https://discord.gg/ets2la" target="_blank" class="text-text-l hover:underline">
            Discord server</a> or on <a href="https://github.com/ETS2LA" target="_blank" class="text-text-l hover:underline">
            GitHub</a>.
        </p>
    {:else}
        <img class="rounded-md" src="https://http.cat/{page.status}" alt="Cat that's hiding under paper looking for something. Didn't find it. That's a 404 error!" />
        <br/>
        <p>{page.status} - {message}</p>
        <p class="description">
            {httpDescriptions[page.status] || ''} <br/><br/>
            Do tell us how you got here in the <a href="https://discord.gg/ets2la" target="_blank" class="text-text-l hover:underline">
            Discord server</a> or on <a href="https://github.com/ETS2LA" target="_blank" class="text-text-l hover:underline">
            GitHub</a>.
        </p>
    {/if}
</div>