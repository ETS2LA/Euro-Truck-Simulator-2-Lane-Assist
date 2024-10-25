import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"  

import { toast } from "sonner"
import useSWR from "swr"
import { GetPlugins, EnablePlugin, DisablePlugin } from "../backend"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { useRouter } from "next/router"
import { Gauge, LineChart } from "lucide-react"

import { translate } from "../translation"

export default function Home({ ip }: { ip: string }) {
    const { push } = useRouter()
    const { data, error, isLoading } = useSWR("plugins", () => GetPlugins(ip), { refreshInterval: 500 })
    if (isLoading) return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto"><p className="absolute left-5 font-semibold text-xs text-stone-400">{translate("loading")}</p></Card>
    if (error){
        toast.error(translate("frontend.menubar.error_fetching_plugins", ip), {description: error.message})
        return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto"><p className="absolute left-5 font-semibold text-xs text-stone-400">{error.message}</p></Card>
    } 

    const plugins:string[] = [];
    for (const key in data) {
        // Check if the key is a number
        if (isNaN(parseInt(key))){
            if(key == "Global" || key == "global_json")
                continue
            plugins.push(key)
        }
    }
    return (
        <div className="flex space-x-3 cursor-default">
            <Card className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-4 h-[calc(100vh-72px)] overflow-auto auto-rows-min w-full">
                {plugins.map((plugin) => (
                    <Card key={plugin} id={plugin} className="flex flex-col justify-between">
                        <CardHeader className="gap-1">
                            <CardTitle>
                                {data ? translate((data as any)[plugin]["description"]["name"]) : plugin}
                            </CardTitle>

                                <div className="flex gap-2">
                                    {data && (data as any)[plugin]["description"]["authors"] && typeof (data as any)[plugin]["description"]["authors"] == typeof [{}] ? (
                                        (data as any)[plugin]["description"]["authors"].map((author: any, index: number) => (
                                            <div className="flex items-center gap-1">
                                                <Avatar className="w-5 h-5">
                                                    <AvatarImage src={author["avatar"] || ""} />
                                                </Avatar>
                                                <a className="text-muted-foreground text-xs" href={author["url"] || "https://wiki.tumppi066.fi"} target="_blank">{author["name"] || "Unknown"}</a>
                                            </div>
                                        ))
                                    ) : null}
                                </div>

                                {data ? (data as any)[plugin]["enabled"] ? (
                                    <div className="flex flex-row gap-1 items-center">
                                        <Gauge color="#888888" className="w-5 h-5"/>
                                        <p className="text-muted-foreground text-xs">{translate("frontend.plugins.plugin_running", data ? (data as any)[plugin]["frametimes"][(data as any)[plugin]["frametimes"].length - 1] ? Math.round(1/(data as any)[plugin]["frametimes"][1]) : "Unknown" : "Unknown")}</p>
                                    </div>
                                ) : null : null}
                        </CardHeader>
                        <CardContent>
                            <CardDescription>
                                <p>{data ? translate((data as any)[plugin]["description"]["description"]) : translate("frontend.plugins.no_description")}</p>
                            </CardDescription>
                        </CardContent>
                        <CardFooter className="gap-3 flex flex-col">
                            <div className="gap-3 flex-row flex">
                                {data ? (data as any)[plugin]["enabled"] ? (
                                    <Button variant={"outline"} onClick={() => {
                                        toast.promise(DisablePlugin(plugin, ip), {
                                            loading: translate("frontend.command.disabling_plugin", data ? translate((data as any)[plugin]["description"]["name"]) : plugin),
                                            success: translate("frontend.command.disabled_plugin", data ? translate((data as any)[plugin]["description"]["name"]) : plugin),
                                            error: translate("frontend.command.error_disabling_plugin", data ? translate((data as any)[plugin]["description"]["name"]) : plugin),
                                            description: translate("frontend.plugins.button_may_take_second_to_update")
                                        })
                                    }}>{translate("frontend.menubar.plugins.plugin.disable")}</Button>) : (
                                    <Button onClick={() => {
                                        toast.promise(EnablePlugin(plugin, ip), {
                                            loading: translate("frontend.command.enabling_plugin", data ? translate((data as any)[plugin]["description"]["name"]) : plugin),
                                            success: translate("frontend.command.enabled_plugin", data ? translate((data as any)[plugin]["description"]["name"]) : plugin),
                                            error: translate("frontend.command.error_enabling_plugin", data ? translate((data as any)[plugin]["description"]["name"]) : plugin),
                                            description: translate("frontend.plugins.button_may_take_second_to_update")
                                        })
                                }}>{translate("frontend.menubar.plugins.plugin.enable")}</Button>): null} 
                                <Button variant={"outline"} onClick={() => push(`/plugins/${plugin}`)}>{translate("frontend.plugins.open_interface")}</Button>
                            </div>
                        </CardFooter>
                    </Card>
                ))}
            </Card>
        </div>
    )
}