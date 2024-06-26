import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"  

import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"

import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip"

import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"

import { toast } from "sonner"
import useSWR from "swr"
import { mutate } from "swr"
import { GetSettingsJSON, SetSettingByKey } from "@/pages/settings"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { useRouter } from "next/router"
import React, { useState, useEffect } from 'react';
import { Gauge, LineChart } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export default function Home({ ip }: { ip: string }) {
    const { push } = useRouter()
    
    const {data, error, isLoading} = useSWR("globals", () => GetSettingsJSON("global", ip));

    if (isLoading) return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto"><p className="font-semibold text-xs text-stone-400">Loading...</p></Card>
    if (error){
        toast.error("Error fetching settings from " + ip, {description: error.message})
        return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto"><p className="font-semibold text-xs text-red-400">{error.message}</p></Card>
    }

    const keys:string[] = [];
    const types:string[] = [];
    for (const key in data) {
        keys.push(key)
    }
    for (const key in data) {
        types.push(typeof data[key])
    }

    const PrettyPrintKey = (key:string) => {
        let words = key.split("_")
        let pretty = ""
        words.forEach((word) => {
            pretty += word.charAt(0).toUpperCase() + word.slice(1) + " "
        })
        return pretty
    }

    // Replace your input handlers with something like this
    const handleStringChange = (key:string, value:string) => {
        SetSettingByKey("global", key, value, ip)
        mutate("globals", {...data, [key]: value}, false) // Update the local state
    };

    const handleNumberChange = (key:string, value:number) => {
        SetSettingByKey("global", key, value, ip)
        mutate("globals", {...data, [key]: value}, false) // Update the local state
    }

    const handleBooleanChange = (key:string, value:boolean) => {
        SetSettingByKey("global", key, value, ip)
        mutate("globals", {...data, [key]: value}, false) // Update the local state
    }

    return (
        <div className="flex space-x-3">
            <Card className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 p-4 h-[calc(100vh-72px)] overflow-auto auto-rows-min w-full">
                {keys.map((key:any) => {
                    return (
                        <Card key={key} className="flex flex-col">
                            <CardHeader>
                                <CardTitle>{PrettyPrintKey(key)}</CardTitle>
                            </CardHeader>
                            <CardContent className="flex flex-col gap-4">
                                <CardDescription className="flex gap-2 content-center text-center items-center">
                                    {types[keys.indexOf(key)]}
                                    {types[keys.indexOf(key)] === "boolean" ?
                                        <Checkbox
                                            checked={data[key]}
                                            onClick={(e) => {
                                                handleBooleanChange(key, !data[key])
                                            }}
                                            className="w-5 h-5"
                                        /> : types[keys.indexOf(key)] === "string" ? 
                                        <Input
                                            type="text"
                                            value={data[key]}
                                            onChange={(e) => {
                                                handleStringChange(key, e.target.value)
                                            }}
                                        />
                                        : types[keys.indexOf(key)] === "number" ?
                                        <Input
                                            type="number"
                                            value={data[key]}
                                            onChange={(e) => {
                                                handleNumberChange(key, parseInt(e.target.value))
                                            }}
                                        />
                                        :   types[keys.indexOf(key)] === "object" && data[key] !== null ?
                                        <>
                                        <TooltipProvider>
                                            <Tooltip>
                                            <TooltipTrigger>
                                                <Badge>{Object.keys(data[key]).length} keys</Badge>
                                            </TooltipTrigger>
                                            <TooltipContent className="bg-background border">
                                                <Card className="flex flex-col gap-2 w-20 text-start border-transparent p-0">
                                                    <p>[</p>
                                                    {Object.keys(data[key]).map((subkey) => {
                                                        return (
                                                            <p key={subkey} className="text-xs pl-2">{data[key][subkey]},</p>
                                                        )
                                                    })}
                                                    <p>]</p>
                                                </Card>
                                            </TooltipContent>
                                            </Tooltip>
                                        </TooltipProvider>
                                        </>
                                        : null
                                    }
                                </CardDescription>
                            </CardContent>
                        </Card>
                    )
                })}
            </Card>
        </div>
    )
}