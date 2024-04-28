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
  

export default function Home({ip} : {ip: string}) {
    return (
        <div className="w-full h-[calc(100vh-72px)]">
            <ResizablePanelGroup direction="horizontal" className="overflow-auto text-center gap-1.5">
                <ResizablePanel defaultSize={20}>
                    <div className="border rounded-lg h-full">
                        <PluginList ip={ip} />
                    </div>
                </ResizablePanel>
                <ResizableHandle className="bg-transparent" />
                <ResizablePanel defaultSize={60} className="content-center">
                    <ContextMenu>
                        <ContextMenuTrigger className="flex h-full w-full items-center justify-center rounded-md border border-dashed text-sm text-stone-600">
                            Right Click
                        </ContextMenuTrigger>
                        <ContextMenuContent className="w-64">
                            <ContextMenuItem onClick={() => toast.info("Not yet implemented.")}>
                                User interface guide
                            </ContextMenuItem>
                        </ContextMenuContent>
                    </ContextMenu>
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