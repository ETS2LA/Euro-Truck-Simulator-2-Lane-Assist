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
import * as React from "react"

export default function Basic({ip} : {ip: string}) {
    const [collapsed, setCollapsed] = useState(false);
    const [cursorPosition, setCursorPosition] = useState({x: 0, y: 0});
    const [isInTop20Percent, setIsInTop20Percent] = useState(false);
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

    function handleMouseMove(e: React.MouseEvent) {
        setCursorPosition({x: e.clientX, y: e.clientY});
        console.log(e.clientY / window.innerHeight);
        if (e.clientY / window.innerHeight < 0.2) {
            setIsInTop20Percent(true);
        } else {
            setIsInTop20Percent(false);
        }
    }

    function getMenubarClassname() {
        if (isInTop20Percent) {
            return "absolute top-0 left-0 right-0 h-screen transition-all";
        }
        else {
            return "absolute top-0 left-0 right-0 h-screen transition-all opacity-0";
        }
    }

    return (
        <div className="w-full h-screen" onMouseMove={handleMouseMove}>
            <ResizablePanelGroup direction="horizontal" className="overflow-auto text-center gap-0">
                <ResizablePanel defaultSize={35}>
                    <iframe 
                        src={`http://${ip}:60407/ETS2LA Visualisation.html`} 
                        className="w-full h-full" 
                        sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                    />
                    {!collapsed && <div className="absolute bottom-0 left-[calc(35vw-0.25rem)] h-[100vh] w-1 bg-gradient-to-r from-transparent to-[#1b1b1b] pointer-events-none" />}
                </ResizablePanel>
                <ResizableHandle withHandle className="w-0" />
                <ResizablePanel defaultSize={65} className={collapsed ? "content-center gap-1.5 flex flex-col rounded-none" : "content-center gap-1.5 flex flex-col relative rounded-none"}
                    collapsedSize={0}
                    collapsible
                    maxSize={100}
                    minSize={50}
                    onCollapse={() => setCollapsed(true)}
                    onExpand={() => setCollapsed(false)}
                >
                    <div className="bg-[#1b1b1b] h-full">
                        <div className="h-full z-[-9999] bg-[#1b1b1b]">
                            <React.StrictMode>
                                <ETS2LAMap ip={ip} />
                            </React.StrictMode>
                        </div>
                    </div>
                    {!collapsed && <div className="absolute bottom-0 left-0 h-[100vh] w-16 bg-gradient-to-l from-transparent to-[#1b1b1b] pointer-events-none" />}
                    <div className={getMenubarClassname()}>
                        <ETS2LAMenubar ip={ip} onLogout={() =>{}} isCollapsed={collapsed} />
                    </div>
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    )
}