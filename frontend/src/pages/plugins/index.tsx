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
import { GetPlugins, EnablePlugin, DisablePlugin } from "../server"
import { Button } from "@/components/ui/button"

export default function Home({ ip }: { ip: string }) {
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
        <Card className="grid grid-cols-3 gap-4 p-4 h-[calc(100vh-75px)] overflow-auto auto-rows-min">
            {plugins.map((plugin) => (
                <Card key={plugin} id={plugin}>
                    <CardHeader>
                        <CardTitle>{plugin}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <CardDescription>
                            <p>Exercitation qui irure incididunt eiusmod nisi qui dolore eiusmod cillum consequat excepteur commodo deserunt.</p>
                        </CardDescription>
                    </CardContent>
                    <CardFooter className="gap-3">
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
                        <Button variant={"outline"}>Open Interface</Button>
                    </CardFooter>
                </Card>
            ))}
        </Card>
    )
}