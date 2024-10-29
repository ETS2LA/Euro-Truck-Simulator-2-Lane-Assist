"use client"

import {
    Command,
    CommandDialog,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
    CommandSeparator,
    CommandShortcut,
} from "@/components/ui/command"

import { usePathname } from "next/navigation";
import * as React from "react"  
import { GetPlugins, EnablePlugin, DisablePlugin } from "@/pages/backend";
import useSWR from "swr";
import { useRouter } from "next/router";
import { toast } from "sonner";
import { translate } from "@/pages/translation";

export function ETS2LACommandMenu({ip}: {ip: string}) {
    const [open, setOpen] = React.useState(false)
    const { push } = useRouter()
    const { data, error, isLoading } = useSWR("plugins", () => GetPlugins(ip), { refreshInterval: 1000 })
    
    let path = usePathname();
    let plugins:string[] = [];
    let enabledPlugins:string[] = [];
    let disabledPlugins:string[] = [];
    if (open) {
        console.log(data)
        if (isLoading) return null
        if (error) return null
        for (const key in data) {
            if(key != "Global" && key != "global_json"){
                plugins.push(key)
                if ((data as any)[key]["enabled"] == false) {
                    disabledPlugins.push(key)
                } else {
                    enabledPlugins.push(key)
                }
            }
        }
    }
    
    React.useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (((e.key === "k" || e.key === "Enter") && (e.metaKey || e.ctrlKey)) || e.key === "F1" || e.key === "Escape") {
                e.preventDefault()
                setOpen((open) => !open)
            }
        }
        document.addEventListener("keydown", down)
        return () => document.removeEventListener("keydown", down)
    }, [])
   
    return (
        <CommandDialog open={open} onOpenChange={setOpen}>
            <CommandInput placeholder={translate("frontend.command.typing_prompt")} />
            <CommandList>
                <CommandEmpty>{translate("frontend.command.no_results")}</CommandEmpty>
                <CommandGroup heading="Actions">
                    {path != "/" ? (
                        <CommandItem onSelect={() => {push("/"); setOpen(false)}}>
                            {translate("frontend.command.return_to_main_menu")}
                        </CommandItem>
                    ): null}
                    {path != "/plugins" ? (
                        <CommandItem onSelect={() => {push("/plugins"); setOpen(false)}}>
                            {translate("frontend.command.open_plugin_manager")}
                        </CommandItem>
                    ): null}
                </CommandGroup>
                <CommandGroup heading="Settings">
                    {plugins.map((plugin) => (
                        <CommandItem key={plugin} onSelect={() => {push("/plugins/" + plugin); setOpen(false)}}>
                            {translate("frontend.command.open_plugin", plugin)}
                        </CommandItem>
                    ))}
                </CommandGroup>
                <CommandSeparator />
                {disabledPlugins.length > 0 ? (
                    <CommandGroup heading={translate("frontend.command.enable_plugins_header")}>
                        {disabledPlugins.map((plugin) => (
                            <CommandItem key={plugin} onSelect={() => {
                                    setOpen(false)
                                    toast.promise(EnablePlugin(plugin, ip=ip), {
                                        loading: translate("frontend.command.enabling_plugin", plugin), //"Enabling " + plugin,
                                        success: translate("frontend.command.enabled_plugin", plugin), //"Enabled " + plugin,
                                        error: translate("frontend.command.error_enabling_plugin", plugin), //"Error enabling " + plugin
                                    }) 
                                }}>
                                {translate("frontend.command.enable_plugin", plugin)}
                            </CommandItem>
                        ))}
                    </CommandGroup>
                ) : null}
                <CommandSeparator />
                {enabledPlugins.length > 0 ? (
                    <CommandGroup heading={translate("frontend.command.disable_plugins_header")}>
                        {enabledPlugins.map((plugin) => (
                            <CommandItem key={plugin} onSelect={() => {
                                    setOpen(false)
                                    toast.promise(DisablePlugin(plugin, ip=ip), {
                                        loading: translate("frontend.command.disabling_plugin", plugin), //"Disabling " + plugin,
                                        success: translate("frontend.command.disabled_plugin", plugin), //"Disabled " + plugin,
                                        error: translate("frontend.command.error_disabling_plugin", plugin), //"Error disabling " + plugin
                                    })
                                }}>
                                {translate("frontend.command.disable_plugin", plugin)}
                            </CommandItem>
                        ))}
                    </CommandGroup>
                ) : null}
            </CommandList>
        </CommandDialog>
    )
  }