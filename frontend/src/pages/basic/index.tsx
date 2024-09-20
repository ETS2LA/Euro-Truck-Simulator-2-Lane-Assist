import PluginList from "@/components/plugin_list"
import { Card } from "@/components/ui/card"
import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import { EnablePlugin, DisablePlugin } from "../backend"
import { toast } from "sonner"
import { useRouter } from "next/router"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ETS2LAMenubar } from "@/components/ets2la_menubar"
import ETS2LAMap from "@/components/map"
import { useEffect } from "react";
import { useRef } from "react"

export default function Basic({ip} : {ip: string}) {
    const [collapsed, setCollapsed] = useState(false);
    const push = useRouter().push;
    const isMounted = useRef(true); // Track if the component is mounted

    useEffect(() => {
        console.log("Enabling plugins with IP " + ip);
        //EnablePlugin("Sockets", ip).then(() => {
        //    EnablePlugin("ObjectDetection", ip).then(() => {
        //        EnablePlugin("Map", ip).then(() => {
        //        
        //        });
        //    });
        //});
        
        return () => {

        }
    }, []);

    return (
        <div className="w-full h-screen">
            <ResizablePanelGroup direction="horizontal" className="overflow-auto text-center gap-0">
                <ResizablePanel defaultSize={35}>
                    <iframe 
                        src={`http://localhost:60407/ETS2LA Visualisation.html`} 
                        className="w-full h-full" 
                        sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                    />
                    {!collapsed && <div className="absolute bottom-0 left-[calc(35vw-0.25rem)] h-[100vh] w-1 bg-gradient-to-r from-transparent to-[#1b1b1b] pointer-events-none" />}
                </ResizablePanel>
                <ResizableHandle withHandle className="w-0" />
                <ResizablePanel defaultSize={65} className={collapsed ? "content-center gap-1.5 flex flex-col rounded-none" : "content-center gap-1.5 flex flex-col relative rounded-none"}
                    collapsedSize={0}
                    collapsible
                    maxSize={65}
                    minSize={65}
                    onCollapse={() => setCollapsed(true)}
                    onExpand={() => setCollapsed(false)}
                >
                    <div className="bg-[#1b1b1b] h-full">
                        <div className="h-full z-[-9999] bg-[#1b1b1b]" style={{perspective: "1200px"}}>
                            <ETS2LAMap ip={ip} />
                        </div>
                    </div>
                    {!collapsed && <div className="absolute bottom-0 left-0 h-[100vh] w-16 bg-gradient-to-l from-transparent to-[#1b1b1b] pointer-events-none" />}
                    <div className="absolute top-0 left-0 right-0 h-screen">
                        <ETS2LAMenubar ip={ip} onLogout={() =>{}} isCollapsed={collapsed} />
                    </div>
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    )
}