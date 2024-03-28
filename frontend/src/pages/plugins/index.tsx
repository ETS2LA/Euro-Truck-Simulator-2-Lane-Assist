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
import { GetPlugins, EnablePlugin, DisablePlugin } from "../server"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { useRouter } from "next/router"
import { HomeIcon } from "lucide-react"

export default function Home({ ip }: { ip: string }) {
    const { push } = useRouter()
    const { data, error, isLoading } = useSWR(ip, () => GetPlugins(ip), { refreshInterval: 1000 })
    if (isLoading) return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-75px)] overflow-auto"><p className="absolute left-5 font-semibold text-xs text-stone-400">Loading...</p></Card>
    if (error){
        toast.error("Error fetching plugins from " + ip, {description: error.message})
        return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-75px)] overflow-auto"><p className="absolute left-5 font-semibold text-xs text-stone-400">{error.message}</p></Card>
    } 

    const plugins:string[] = [];
    for (const key in data) {
        console.log(key)
        plugins.push(key)
    }
    return (
        <div className="flex space-x-3">
            <Card className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-4 h-[calc(100vh-75px)] overflow-auto auto-rows-min">
                {plugins.map((plugin) => (
                    <Card key={plugin} id={plugin} className="flex flex-col justify-between">
                        <CardHeader className="gap-2">
                            <CardTitle>{data ? (data as any)[plugin]["file"]["name"] : plugin}</CardTitle>
                            <div className="flex items-center gap-1">
                                {data ? (data as any)[plugin]["file"]["author"] != "Unknown" ? (
                                    <Avatar className="w-5 h-5">
                                        <AvatarImage src={data ? (data as any)[plugin]["file"]["author"]["avatar"] : ""} />
                                    </Avatar>
                                ) : null : null}
                                <p className="text-muted-foreground text-xs">{data ? (data as any)[plugin]["file"]["author"]["name"] : "Unknown"}</p>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <CardDescription>
                                <p>{data ? (data as any)[plugin]["file"]["description"] : "No description available"}</p>
                            </CardDescription>
                        </CardContent>
                        <CardFooter className="gap-3 flex flex-col">
                            <div className="gap-3 flex-row flex">
                                {data ? (data as any)[plugin]["enabled"] ? (
                                    <Button variant={"outline"} onClick={() => {
                                        toast.promise(DisablePlugin(plugin, ip), {
                                            loading: "Disabling " + plugin,
                                            success: "Disabled " + plugin,
                                            error: "Error disabling " + plugin
                                        })
                                    }}>Disable</Button>) : (
                                    <Button onClick={() => {
                                        toast.promise(EnablePlugin(plugin, ip), {
                                            loading: "Enabling " + plugin,
                                            success: "Enabled " + plugin,
                                            error: "Error enabling " + plugin
                                        })
                                }}>Enable</Button>): null} 
                                <Button variant={"outline"} onClick={() => push(`/plugins/${plugin}`)}>Open Interface</Button>
                            </div>
                        </CardFooter>
                    </Card>
                ))}
            </Card>
        </div>
    )
}