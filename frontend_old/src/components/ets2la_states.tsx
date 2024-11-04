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
import Loader from "./ets2la_loader";

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
                "status": "enabled",
                "progress": 0.5,
            }
        }

        */
        if (data) {
            let indexesToNotRemove: number[] = [];
            // Loop through the plugins
            console.log(data);
            for (const plugin in data) {
                const plugin_name = plugin;
                const state = data[plugin].status;
                const state_progress = data[plugin].progress;
                const state_progress_percent = Math.floor(state_progress * 100);  
                if(toastNames.includes(plugin_name) && state_progress != -1)
                {
                    let index = toastNames.indexOf(plugin_name);
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
                    setToastNames([...toastNames, plugin_name]);
                    indexesToNotRemove.push(toastNames.length);
                }
                else if(toastNames.includes(plugin_name) && state != "")
                {
                    let index = toastNames.indexOf(plugin_name);
                    indexesToNotRemove.push(index);

                    // Update the toast
                    const toastID = toasts[index];
                    toast.custom((t) => (
                        <div className="h-min w-[354px] border border-zinc-800 rounded-lg p-4 text-sm flex flex-col gap-2 font-semibold">
                            <div className="flex justify-between text-start items-center">
                                <div className="flex text-center content-center items-center gap-2">
                                    <Loader className={""} /> 
                                    <p>{state}</p>
                                </div>
                                <p className="text-[10px] text-muted-foreground p-0">{plugin_name}</p>
                            </div>
                        </div>
                    ), {
                        duration: Infinity,
                        id: toastID
                    })

                }
                else if (state != "") 
                { // Indeterminate
                    const toastID = toast.custom((t) => (
                        <div className="h-min w-[354px] border border-zinc-800 rounded-lg p-4 text-sm flex flex-col gap-2 font-semibold">
                            <div className="flex justify-between text-start items-center">
                                <div className="flex text-center content-center items-center gap-2">
                                    <Loader className={""} /> 
                                    <p>{state}</p>
                                </div>
                                <p className="text-[10px] text-muted-foreground p-0">{plugin_name}</p>
                            </div>
                        </div>
                    ), {
                        duration: Infinity,
                    })
                    setToasts([...toasts, toastID]);
                    setToastNames([...toastNames, plugin_name]);
                    indexesToNotRemove.push(toastNames.length);
                }
            }
            for (let i = 0; i < toasts.length; i++)
            {
                console.log(i);
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