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

import * as React from "react"  
import { GetPlugins, EnablePlugin, DisablePlugin } from "@/pages/server";
import useSWR from "swr";
import { useRouter } from "next/router";
import { toast } from "sonner";

export function ETS2LACommandMenu({ip}: {ip: string}) {
    const [open, setOpen] = React.useState(false)
    const { push } = useRouter()
    const { data, error, isLoading } = useSWR("plugins", () => GetPlugins(ip), { refreshInterval: 1000 })
    
    let plugins:string[] = [];
    let enabledPlugins:string[] = [];
    let disabledPlugins:string[] = [];
    if (open) {
        console.log(data)
        if (isLoading) return null
        if (error) return null
        for (const key in data) {
            plugins.push(key)
            if (data[key]["enabled"] == false) {
                disabledPlugins.push(key)
            } else {
                enabledPlugins.push(key)
            }
        }
    }
    
    React.useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault()
                setOpen((open) => !open)
            }
        }
        document.addEventListener("keydown", down)
        return () => document.removeEventListener("keydown", down)
    }, [])
   
    return (
        <CommandDialog open={open} onOpenChange={setOpen}>
            <CommandInput placeholder="Type a command or search..." />
            <CommandList>
                <CommandEmpty>No results, please try again.</CommandEmpty>
                <CommandGroup heading="Actions">
                    <CommandItem onSelect={() => {push("/"); setOpen(false)}}>
                        Return to the Main Menu
                    </CommandItem>
                </CommandGroup>
                <CommandGroup heading="Settings">
                    {plugins.map((plugin) => (
                        <CommandItem key={plugin} onSelect={() => {push("/plugins/" + plugin); setOpen(false)}}>
                            Open {plugin} settings
                        </CommandItem>
                    ))}
                </CommandGroup>
                <CommandSeparator />
                {disabledPlugins.length > 0 ? (
                    <CommandGroup heading="Enable plugins">
                        {disabledPlugins.map((plugin) => (
                            <CommandItem key={plugin} onSelect={() => {
                                    setOpen(false)
                                    toast.promise(EnablePlugin(plugin, ip=ip), {
                                        loading: "Enabling " + plugin,
                                        success: "Enabled " + plugin,
                                        error: "Error enabling " + plugin
                                    }) 
                                }}>
                                Enable {plugin}
                            </CommandItem>
                        ))}
                    </CommandGroup>
                ) : null}
                <CommandSeparator />
                {enabledPlugins.length > 0 ? (
                    <CommandGroup heading="Disable plugins">
                        {enabledPlugins.map((plugin) => (
                            <CommandItem key={plugin} onSelect={() => {
                                    setOpen(false)
                                    toast.promise(DisablePlugin(plugin, ip=ip), {
                                        loading: "Disabling " + plugin,
                                        success: "Disabled " + plugin,
                                        error: "Error disabling " + plugin
                                    })
                                }}>
                                Disable {plugin}
                            </CommandItem>
                        ))}
                    </CommandGroup>
                ) : null}
            </CommandList>
        </CommandDialog>
    )
  }