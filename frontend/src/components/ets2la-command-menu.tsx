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
import { GetPlugins } from "@/pages/server";
import useSWR from "swr";
import { useRouter } from "next/router";

export function ETS2LACommandMenu({ip}: {ip: string}) {
    const [open, setOpen] = React.useState(false)
    const { push } = useRouter()
    const { data, error, isLoading } = useSWR("plugins", () => GetPlugins(ip), { refreshInterval: 1000 })
    
    let plugins:string[] = [];
    let enabledPlugins:string[] = [];
    let disabledPlugins:string[] = [];
    if (open) {
        if (isLoading) return null
        if (error) return null
        for (const key in data) {
            plugins.push(key)
            if (data[key]) {
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
                <CommandEmpty>No results found.</CommandEmpty>
                <CommandGroup heading="Settings">
                    {plugins.map((plugin) => (
                        <CommandItem key={plugin} onClick={() => push("/plugins/" + plugin)}>
                            Open {plugin} settings
                        </CommandItem>
                    ))}
                </CommandGroup>
                <CommandSeparator />
                {disabledPlugins.length > 0 ? (
                    <CommandGroup heading="Enable plugins">
                        {disabledPlugins.map((plugin) => (
                            <CommandItem key={plugin}>
                                Enable {plugin}
                            </CommandItem>
                        ))}
                    </CommandGroup>
                ) : null}
                <CommandSeparator />
                {enabledPlugins.length > 0 ? (
                    <CommandGroup heading="Disable plugins">
                        {enabledPlugins.map((plugin) => (
                            <CommandItem key={plugin}>
                                Disable {plugin}
                            </CommandItem>
                        ))}
                    </CommandGroup>
                ) : null}
            </CommandList>
        </CommandDialog>
    )
  }