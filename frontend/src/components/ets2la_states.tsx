"use client"

import * as React from "react"  
import { GetStates } from "@/pages/backend";
import useSWR from "swr";
import { mutate } from "swr";
import { toast } from "sonner";
import { useEffect } from "react";
import { useState } from "react";
import { Progress } from "@/components/ui/progress";
import { translate } from "@/pages/translation";

export function ETS2LAStates({ip}: {ip: string}) {
    const { data, error } = useSWR("states", () => GetStates(ip))
    const [toasts, setToasts] = useState<any[]>([]);
    const [toastNames, setToastNames] = useState<string[]>([]);

    useEffect(() => {
        let interval = setInterval(() => {
            mutate("states");
        }, 1000);
        return () => clearInterval(interval);
    }, []);

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
            let indexesToNotRemove: number[] = [];
            // Loop through the plugins
            for (const plugin in data) {
                const plugin_name = plugin;
                const state = data[plugin].status;
                const state_progress = data[plugin].progress;
                const state_progress_percent = Math.floor(state_progress * 100);  
                if(toastNames.includes(plugin) && state_progress != -1)
                {
                    let index = toastNames.indexOf(plugin);
                    indexesToNotRemove.push(index);

                    // Update the toast
                    const toastID = toasts[index];
                    toast.custom((t) => (
                        <div className="h-min w-[354px] border border-zinc-800 rounded-lg p-4 text-sm flex flex-col gap-2 font-semibold">
                            <div className="flex justify-between text-start items-center">
                                <p>{state}</p>
                                <p className="text-[10px] text-muted-foreground p-0">{plugin_name}</p>
                            </div>
                            <Progress value={state_progress_percent} className="pb-0" />
                        </div>
                    ), {
                        duration: Infinity,
                        id: toastID
                    })

                }
                else if (state_progress != -1)
                {
                    const toastID = toast.custom((t) => (
                        <div className="h-min w-[354px] border border-zinc-800 rounded-lg p-4 text-sm flex flex-col gap-2 font-semibold">
                            <div className="flex justify-between text-start items-center">
                                <p>{state}</p>
                                <p className="text-[10px] text-muted-foreground p-0">{plugin_name}</p>
                            </div>
                            <Progress value={state_progress_percent} className="pb-0" />
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
                    toast.success(translate("frontend.states.complete"), { duration: 1000 });
                }
            }
        }
    }, [data]);


    return null;
}