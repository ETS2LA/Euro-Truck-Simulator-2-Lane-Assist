import PluginList from "@/components/plugin_list"
import { Card } from "@/components/ui/card"
import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import VersionHistory from "@/components/version_history"
import {
    ContextMenu,
    ContextMenuCheckboxItem,
    ContextMenuContent,
    ContextMenuItem,
    ContextMenuLabel,
    ContextMenuRadioGroup,
    ContextMenuRadioItem,
    ContextMenuSeparator,
    ContextMenuShortcut,
    ContextMenuSub,
    ContextMenuSubContent,
    ContextMenuSubTrigger,
    ContextMenuTrigger,
} from "@/components/ui/context-menu"
import { toast } from "sonner"
import { useRouter } from "next/router"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ETS2LAMenubar } from "@/components/ets2la_menubar"
  

export default function Home({ip} : {ip: string}) {
    const [visualisation, setVisualisation] = useState(false);
    const push = useRouter().push;
    return (
        <div className="w-full h-screen">
            <ResizablePanelGroup direction="horizontal" className="overflow-auto text-center gap-0">
                <ResizablePanel defaultSize={35}>
                    <iframe 
                        src={`http://localhost:60407/ETS2LA Visualisation.html`} 
                        className="w-full h-full" 
                        sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                    />
                </ResizablePanel>
                <ResizableHandle withHandle />
                <ResizablePanel defaultSize={65} className="content-center rounded-md gap-1.5 flex flex-col">
                    <div className="h-full">

                    </div>
                    <ETS2LAMenubar ip={ip} onLogout={() =>{

                    }} />
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    )
}