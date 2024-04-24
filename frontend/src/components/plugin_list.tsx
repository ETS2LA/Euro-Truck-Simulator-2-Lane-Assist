import { ScrollArea } from "./ui/scroll-area"
import { GetPlugins } from "@/pages/server"
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
import { EnablePlugin, DisablePlugin } from "@/pages/server"
import { toast } from "sonner"
import { Badge } from "./ui/badge"

export default function PluginList({ ip }: { ip: string }) {
    const { push } = useRouter()
    const { data, error, isLoading } = useSWR("plugins", () => GetPlugins(ip), { refreshInterval: 1000 })

    if (isLoading) return <SkeletonCard />
    if (error) return <div className="w-full">
            <Badge variant="destructive" className="w-full">Failed to fetch plugins</Badge>
            <p>{error.message}</p>
        </div>

    return (
        <ScrollArea className="h-full pt-3 text-start">
            <h4 className="pb-3 pl-3 font-medium flex gap-1"> Plugin QuickAccess™ <p className="text-xs text-stone-600">(not really)</p> </h4>
            <Separator />
            <Accordion type="single" collapsible>
                {Object.keys(data as any).map((plugin, index) => (
                    <AccordionItem value={plugin}>
                        <AccordionTrigger className="pl-3 pr-2">
                            <p className="flex gap-3"><p className="text-stone-600">{index+1}. </p> {plugin}</p>
                        </AccordionTrigger>
                        <AccordionContent className="pl-2 flex gap-2 w-full pr-2">
                            <div className="w-full justify-between flex gap-2">
                                {(data as any)[plugin]["enabled"] ? (
                                    <Button className="w-full" onClick={() => toast.promise(DisablePlugin(plugin, ip), { loading: "Disabling...", success: "Disabled", error: "Failed to disable" })} variant={"outline"}>Disable</Button>
                                ) : (
                                    <Button className="w-full" onClick={() => toast.promise(EnablePlugin(plugin, ip), { loading: "Enabling...", success: "Enabled", error: "Failed to enable" })} variant={"outline"}>Enable</Button>
                                )}
                                <Button onClick={() => push(`/plugins/${plugin}`)} variant={"outline"}>View</Button>
                            </div>
                        </AccordionContent>
                    </AccordionItem>
                ))}
            </Accordion>
        </ScrollArea>
    )
}