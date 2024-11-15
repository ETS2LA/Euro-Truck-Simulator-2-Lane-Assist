"use client";
import { toast } from "sonner"
import useSWR from "swr"
import { mutate } from "swr"
import { GetSettingsJSON, SetSettingByKey } from "@/apis/settings"
import { GetPlugins } from "@/apis/backend"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { useRouter } from "next/navigation"
import React, { useState, useEffect } from 'react';
import { Gauge, LineChart } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import {
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ETS2LAPage } from "@/components/page/page"
import { translate } from "@/apis/translation"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import RenderPage from "@/components/page/render_page"

export default function Home({ ip }: { ip: string }) {
    const { push } = useRouter()
    const { data, error, isLoading } = useSWR("plugin_ui_plugins", () => GetPlugins())
    const [selectedPlugin, setSelectedPlugin] = useState("Global")
    const [scrolledDown, setScrolledDown] = useState(false)


    const plugins:string[] = [];
    for (const key in data) {
        // Check if the key is a number
        if (isNaN(parseInt(key))){
            plugins.push(key)
        }
    }

    const renderPluginPage = () => {
        if (selectedPlugin === "Global") {
            return <RenderPage url="/settings/global" />;
        } else if (selectedPlugin === "Controls") {
            return null
            //return <ControlsPage ip={ip} />;
            // @ts-ignore
        } else if (data && data[selectedPlugin] && data[selectedPlugin].settings) {
            // Ensure data is correctly passed to ETS2LASettingsPage
            // @ts-ignore
            return <ETS2LAPage plugin={selectedPlugin} data={data[selectedPlugin]["settings"]} enabled={data[selectedPlugin]["enabled"]} />;
        } else {
            return <p className="text-xs text-muted-foreground text-start pl-4">{translate("frontend.settings.data_missing")}</p>;
        }
    };

    return (
        <div className="h-full font-geist rounded-lg bg-background p-4">
            <div className="flex flex-col gap-2 p-5 pt-[10px]">
                <h2 className="text-lg font-bold">{translate("frontend.settings")}</h2>
                <Separator className="translate-y-4" />
            </div>
            <div className="h-full pt-0 p-1 overflow-auto">
                <TooltipProvider>
                    <ResizablePanelGroup direction="horizontal" className="text-center gap-4 pr-4 h-full">
                        <ResizablePanel defaultSize={25}>
                            <ScrollArea className="h-full pt-4 relative" type="hover">
                                <div className="absolute bottom-0 z-10 right-0 top-0 w-12 bg-gradient-to-l from-background pointer-events-none" />
                                <div className="flex flex-col gap-2 text-start relative">
                                    <Button key={"Global"} className="items-center justify-start text-sm rounded-r-none" variant={selectedPlugin == "Global" && "secondary" || "ghost"} onClick={() => setSelectedPlugin("Global")}>
                                        {translate("frontend.settings.global")}
                                    </Button>
                                    <Button key={"Controls"} className="items-center justify-start text-sm rounded-r-none" variant={selectedPlugin == "Controls" && "secondary" || "ghost"} onClick={() => setSelectedPlugin("Controls")}>
                                        {translate("frontend.settings.controls")}
                                    </Button>
                                    <br />
                                    {plugins.map((plugin:any, index) => (
                                        plugin == "Separator" ? <br key={index} /> : 
                                        plugin == "Global" ? null : // @ts-ignore
                                        data && data[plugin] && data[plugin].settings ?
                                        <div className="items-center justify-start text-sm">
                                            <Tooltip>
                                                <TooltipTrigger className="items-center justify-start text-sm w-full">
                                                    <Button key={index} className="items-center justify-start text-sm w-full rounded-r-none" variant={selectedPlugin == plugin && "secondary" || "ghost"} onClick={() => setSelectedPlugin(plugin)}>
                                                        {// @ts-ignore
                                                            translate(data[plugin].description.name)
                                                        }
                                                    </Button>
                                                </TooltipTrigger>
                                                <TooltipContent>
                                                    <div className="flex flex-col gap-2 text-start">
                                                        <p className="text-xs text-start">
                                                            {// @ts-ignore
                                                                translate(data[plugin].description.name)
                                                            }
                                                        </p>
                                                    </div>
                                                </TooltipContent>
                                            </Tooltip> 
                                        </div> : null
                                    ))}
                                    <br />
                                    <p className="text-xs text-muted-foreground text-start pl-4">
                                        {translate("frontend.settings.global_info")}
                                    </p>
                                </div>
                            </ScrollArea>
                        </ResizablePanel>
                        <ResizablePanel defaultSize={75} className="h-full w-full relative">
                            <ScrollArea className="h-full" type="hover">
                                <div className="h-4" />
                                {renderPluginPage()}
                            </ScrollArea>
                            <div className="absolute h-4 top-0 left-0 right-0 bg-gradient-to-b from-background pointer-events-none" />
                        </ResizablePanel>
                    </ResizablePanelGroup>
                </TooltipProvider>
                <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-background pointer-events-none" />
            </div>
        </div>
    )
}