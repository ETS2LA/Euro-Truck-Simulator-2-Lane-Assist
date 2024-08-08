import { toast } from "sonner"
import useSWR from "swr"
import { mutate } from "swr"
import { GetSettingsJSON, SetSettingByKey } from "@/pages/settingsServer"
import { GetPlugins } from "@/pages/backend"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { useRouter } from "next/router"
import React, { useState, useEffect } from 'react';
import { Gauge, LineChart } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import {
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import ControlsPage from "./controls"
import { ETS2LASettingsPage } from "@/components/ets2la_settings_page"

export default function Home({ ip }: { ip: string }) {
    const { push } = useRouter()
    const { data, error, isLoading } = useSWR("plugins", () => GetPlugins(ip), { refreshInterval: 500 })
    const { data: global, error: globalsError, isLoading: globalsLoading } = useSWR("globals", () => GetSettingsJSON("global_json", ip));
    const [selectedPlugin, setSelectedPlugin] = useState("Global")
    const [scrolledDown, setScrolledDown] = useState(false)

    const plugins:string[] = [];
    for (const key in data) {
        // Check if the key is a number
        if (isNaN(parseInt(key))){
            console.log(key)
            plugins.push(key)
        }
    }

    const renderPluginPage = () => {
        if (selectedPlugin === "Global") {
            //return <GlobalPage ip={ip} />;
            return <ETS2LASettingsPage ip={ip} plugin={"Global"} />;
        } else if (selectedPlugin === "Controls") {
            return <ControlsPage ip={ip} />;
        } else if (data && data[selectedPlugin] && data[selectedPlugin].file && data[selectedPlugin].file.settings) {
            // Ensure data is correctly passed to ETS2LASettingsPage
            return <ETS2LASettingsPage ip={ip} plugin={selectedPlugin} />;
        } else {
            return <p className="text-xs text-muted-foreground text-start pl-4">Plugin data is not valid or missing.</p>;
        }
    };

    return (
        <div className="h-full font-customSans">
            <div className="flex flex-col gap-2 p-5 pt-[13px]">
                <h2>Settings</h2>
                <Separator className="translate-y-4" />
            </div>
            <div className="h-full pt-0 p-1 max-h-[calc(100vh-132px)]">
                <ResizablePanelGroup direction="horizontal" className="text-center gap-8 pr-4 h-full">
                    <ResizablePanel defaultSize={20}>
                        <ScrollArea className="h-full pt-4" type="hover">
                            <div className="flex flex-col gap-2 text-start">
                                <Button key={"Global"} className="items-center justify-start text-sm" variant={selectedPlugin == "Global" && "secondary" || "ghost"} onClick={() => setSelectedPlugin("Global")}>
                                    Global
                                </Button>
                                <Button key={"Controls"} className="items-center justify-start text-sm" variant={selectedPlugin == "Controls" && "secondary" || "ghost"} onClick={() => setSelectedPlugin("Controls")}>
                                Controls
                                </Button>
                                <br />
                                {plugins.map((plugin:any, index) => (
                                    plugin == "Separator" ? <br key={index} /> : 
                                    plugin == "Global" ? null :
                                    data && data[plugin] && data[plugin].file && data[plugin].file.settings ?
                                    <Button key={index} className="items-center justify-start text-sm" variant={selectedPlugin == plugin && "secondary" || "ghost"} onClick={() => setSelectedPlugin(plugin)}>
                                        {plugin}
                                    </Button> : null
                                ))}
                                <br />
                                <p className="text-xs text-muted-foreground text-start pl-4">This list only includes plugins that support the global settings file.</p>
                            </div>
                        </ScrollArea>
                    </ResizablePanel>
                    <ResizablePanel defaultSize={80} className="h-full w-full relative">
                        <ScrollArea className="h-full" type="hover">
                            <div className="h-4" />
                            {renderPluginPage()}
                        </ScrollArea>
                        <div className="absolute h-4 top-0 left-0 right-0 bg-gradient-to-b from-background pointer-events-none" />
                    </ResizablePanel>
                </ResizablePanelGroup>
                <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-background pointer-events-none" />
            </div>
        </div>
    )
}