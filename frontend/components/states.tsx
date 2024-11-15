"use client"

import * as React from "react"  
import { GetStates } from "@/apis/backend";
import useSWR from "swr";
import { mutate } from "swr";
import { toast } from "sonner";
import { useEffect } from "react";
import { useState } from "react";
import { Progress } from "@/components/ui/progress";
import { translate } from "@/apis/translation";
import Loader from "./loader";
import { ProgressState, IndeterminateState } from "./states/states";

export function States() {
    const { data, error } = useSWR("states", () => GetStates())
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
            for (const plugin in data) {
                const plugin_name = plugin;
                const state = data[plugin].status;
                const state_progress = data[plugin].progress;
                let state_progress_percent = 0;
                if (state_progress <= 1){
                    state_progress_percent = Math.floor(state_progress * 100);  
                }
                else{
                    state_progress_percent = Math.floor(state_progress);
                }
                if(toastNames.includes(plugin_name) && state_progress != -1)
                {
                    let index = toastNames.indexOf(plugin_name);
                    indexesToNotRemove.push(index);

                    // Update the toast
                    const toastID = toasts[index];
                    toast.custom((t) => (
                        <ProgressState state={state} plugin_name={plugin_name} state_progress_percent={state_progress_percent} />
                    ), {
                        duration: Infinity,
                        id: toastID
                    })

                }
                else if (state_progress != -1)
                {
                    const toastID = toast.custom((t) => (
                        <ProgressState state={state} plugin_name={plugin_name} state_progress_percent={state_progress_percent} />
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
                        <IndeterminateState state={state} plugin_name={plugin_name} />
                    ), {
                        duration: Infinity,
                        id: toastID
                    })

                }
                else if (state != "") 
                { // Indeterminate
                    const toastID = toast.custom((t) => (
                        <IndeterminateState state={state} plugin_name={plugin_name} />
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