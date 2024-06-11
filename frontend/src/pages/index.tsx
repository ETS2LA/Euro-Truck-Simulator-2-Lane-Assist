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
  

export default function Home({ip} : {ip: string}) {
    const push = useRouter().push;
    return (
        <div className="w-full h-[calc(100vh-72px)]">
            <ResizablePanelGroup direction="horizontal" className="overflow-auto text-center gap-1.5">
                <ResizablePanel defaultSize={20}>
                    <div className="border rounded-lg h-full">
                        <PluginList ip={ip} />
                    </div>
                </ResizablePanel>
                <ResizableHandle className="bg-transparent" />
                <ResizablePanel defaultSize={60} className="content-center rounded-md">
                    <iframe 
                        src={`http://127.0.0.1:60407/ETS2LA Visualisation.html`} 
                        className="w-full h-full" 
                        frameBorder="0" 
                        title="Plugin" 
                    />
                </ResizablePanel>
                <ResizableHandle className="bg-transparent"/>
                <ResizablePanel defaultSize={20}>
                    <div className="border rounded-lg h-full">
                        <VersionHistory ip={ip} />
                    </div>
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    )
}