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
import { GetStates } from "@/pages/backend";
import { mutate } from "swr";
import useSWR from "swr";
import { useRouter } from "next/router";
import { toast } from "sonner";
import { useEffect } from "react";
import { useState } from "react";
import { Progress } from "@/components/ui/progress";

export function ETS2LAStates({ip}: {ip: string}) {
    const { data, error } = useSWR("states", () => GetStates(ip), { refreshInterval: 1000, refreshWhenHidden: true })
    const [toasts, setToasts] = useState<any[]>([]);
    const [toastNames, setToastNames] = useState<string[]>([]);

    if (error) {
        console.error(error);
    }

    useEffect(() => {
        /*
        
        data = {
            "pluginName": {
                "state": "enabled",
                "state_progress": 0.5,
            }
        }

        */
        if (data) {
            console.log("Data has changed:", data);
            let indexesToNotRemove: number[] = [];
            // Loop through the plugins
            for (const plugin in data) {
                const state = data[plugin].state;
                const state_progress = data[plugin].progress;
                const state_progress_percent = Math.floor(state_progress * 100);  
                if(toastNames.includes(plugin) && state_progress != -1)
                {
                    let index = toastNames.indexOf(plugin);
                    indexesToNotRemove.push(index);

                    // Update the toast
                    const toastID = toasts[index];
                    toast.custom((t) => (
                        <div className="h-min w-[354px] border border-zinc-800 rounded-md p-4 text-sm flex flex-col gap-2 font-semibold">
                            <p>{state}</p>
                            <Progress value={state_progress_percent} />
                        </div>
                    ), {
                        duration: Infinity,
                        id: toastID
                    })

                }
                else if (state_progress != -1)
                {
                    const toastID = toast.custom((t) => (
                        <div className="h-min w-[354px] border border-zinc-800 rounded-md p-4 text-sm flex flex-col gap-2 font-semibold">
                            <p>{state}</p>
                            <Progress value={state_progress_percent} />
                        </div>
                    ), {
                        duration: Infinity,
                    })
                    setToasts([...toasts, toastID]);
                    setToastNames([...toastNames, plugin]);
                    indexesToNotRemove.push(toastNames.length);
                }
            }
            for (let i = 0; i < toasts.length; i++)
            {
                if (!indexesToNotRemove.includes(i))
                {
                    toast.dismiss(toasts[i]);
                    toasts.splice(i, 1);
                    toastNames.splice(i, 1);
                    toast.success("Done!", { duration: 1000 });
                }
            }
        }
    }, [data]);


    return null;
}