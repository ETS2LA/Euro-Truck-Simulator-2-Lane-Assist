import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button";
import useSWR from "swr";
import {toast} from "sonner";
import {useEffect, useState} from "react";
import { GetStates } from "@/pages/backend";
import { PluginFunctionCall } from "@/pages/backend";
import { RelievePlugin } from "@/pages/backend";

export default function Home({ ip }: { ip: string }) {
    const { data, error } = useSWR("states", () => GetStates(ip), { refreshInterval: 1000, refreshWhenHidden: true })

    if (error) {
        console.error(error);
    }

    useEffect(() => {
        if (data) {
            if("Test" in data) {
                console.log(data["Test"]);
                if("data" in data["Test"]) {
                    if ("text" in data["Test"]["data"])
                        {
                        toast.success(data["Test"]["data"]["text"]);
                        // After 2s call relieve
                        setTimeout(() => {
                            RelievePlugin("Test", {ok: "ok"}, ip);
                            toast.success("Relieved plugin");
                        }, 2000);
                    }
                }
            }
        }
    }, [data]);

    return (
        <p>nothing here innit'</p>
    )
}