import { ScrollArea } from "./ui/scroll-area"
import { GetPlugins } from "@/pages/backend"
import useSWR from "swr"
import { useRouter } from "next/router"
import { SkeletonCard } from "./skeleton_card"
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion"
import { Separator } from "./ui/separator"
import { Button } from "./ui/button"
import { EnablePlugin, DisablePlugin } from "@/pages/backend"
import { toast } from "sonner"
import { Badge } from "./ui/badge"
import { translate } from "@/pages/translation"

export default function PluginList({ ip }: { ip: string }) {
    const { push } = useRouter()
    const { data, error, isLoading } = useSWR("plugins", () => GetPlugins(ip), { refreshInterval: 1000 })
    
    let plugins:string[] = [];
    let enabledPlugins:string[] = [];
    let disabledPlugins:string[] = [];

    if (isLoading) return <SkeletonCard />
    if (error) return (
        <div className="w-full">
            <Badge variant="destructive" className="w-full">{translate("frontend.pluginlist.failed_to_fetch")}</Badge>
            <p>{error.message}</p>
        </div>
    )

    for (const key in data) {
        if(key == "Global" || key == "global_json")
            continue
        plugins.push(key)
        if ((data as any)[key]["enabled"] == false) {
            disabledPlugins.push(key)
        } else {
            enabledPlugins.push(key)
        }
    }

    return (
        // Hide scrollbar too
        <ScrollArea className="h-full pt-3 text-start" type="scroll">
            <h4 className="pb-3 pl-3 font-medium flex gap-1">{translate("frontend.pluginlist.name")} {translate("frontend.pluginlist.small_text") != "" && <p className="text-xs text-stone-600">{translate("frontend.pluginlist.small_text")}</p> || null} </h4>
            <Separator />
            <Accordion type="single" collapsible>
                {enabledPlugins.map((plugin, index) => (
                    <AccordionItem value={plugin}>
                        <AccordionTrigger className="pl-3 pr-2 decoration-transparent">
                            <p className="flex gap-3 font-semibold">
                                <p className="text-stone-600 text-xs content-center">{data ? (data as any)[plugin]["frametimes"][(data as any)[plugin]["frametimes"].length - 1] ? Math.round(1/(data as any)[plugin]["frametimes"][(data as any)[plugin]["frametimes"].length - 1]["frametime"]) : translate("unknown") : translate("unknown")} fps</p> 
                                {plugin}
                            </p>
                        </AccordionTrigger>
                        <AccordionContent className="pl-2 flex gap-2 w-full pr-2">
                            <div className="w-full justify-between flex gap-2">
                                {(data as any)[plugin]["enabled"] ? (
                                    <Button className="w-full" onClick={() => toast.promise(DisablePlugin(plugin, ip), { loading: "Disabling...", success: "Disabled", error: "Failed to disable" })} variant={"outline"}>{translate("frontend.pluginlist.plugin.disable")}</Button>
                                ) : (
                                    <Button className="w-full" onClick={() => toast.promise(EnablePlugin(plugin, ip), { loading: "Enabling...", success: "Enabled", error: "Failed to enable" })} variant={"outline"}>{translate("frontend.pluginlist.plugin.enable")}</Button>
                                )}
                                <Button onClick={() => push(`/plugins/${plugin}`)} variant={"outline"}>{translate("frontend.pluginlist.plugin.view")}</Button>
                            </div>
                        </AccordionContent>
                    </AccordionItem>
                ))}
                {disabledPlugins.map((plugin, index) => (
                    <AccordionItem value={plugin} className="group">
                        <AccordionTrigger className="pl-3 pr-2 decoration-transparent group">
                            <p className="flex gap-3 opacity-50 group-hover:opacity-100 transition-all"><p className="text-stone-600">{index+1}. </p> {plugin}</p>
                        </AccordionTrigger>
                        <AccordionContent className="pl-2 flex gap-2 w-full pr-2">
                            <div className="w-full justify-between flex gap-2">
                                {(data as any)[plugin]["enabled"] ? (
                                    <Button className="w-full" onClick={() => toast.promise(DisablePlugin(plugin, ip), { loading: "Disabling...", success: "Disabled", error: "Failed to disable" })} variant={"outline"}>{translate("frontend.pluginlist.plugin.disable")}</Button>
                                ) : (
                                    <Button className="w-full" onClick={() => toast.promise(EnablePlugin(plugin, ip), { loading: "Enabling...", success: "Enabled", error: "Failed to enable" })} variant={"outline"}>{translate("frontend.pluginlist.plugin.enable")}</Button>
                                )}
                                <Button onClick={() => push(`/plugins/${plugin}`)} variant={"outline"}>{translate("frontend.pluginlist.plugin.view")}</Button>
                            </div>
                        </AccordionContent>
                    </AccordionItem>
                ))}
            </Accordion>
        </ScrollArea>
    )
}