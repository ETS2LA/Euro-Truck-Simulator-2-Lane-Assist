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
  

export default function Home({ip} : {ip: string}) {
    const [visualisation, setVisualisation] = useState(false);
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
                    {visualisation && (
                        <iframe 
                            src={`http://localhost:60407/ETS2LA Visualisation.html`} 
                            className="w-full h-full" 
                            sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                        />
                    )
                    ||
                    <Card className="flex flex-col justify-center items-center w-full h-full border-dashed gap-4">
                        <Button onClick={() => setVisualisation(true)} variant={"outline"} className="w-64">Start Visualisation</Button>
                        <Button onClick={() => open("http://localhost:60407/ETS2LA Visualisation.html", "_blank")} variant={"outline"} className="w-64">Open in browser</Button>
                        <Button onClick={() => push("/basic")} variant={"outline"} className="w-64">Enter Basic mode (recommended)</Button>
                    </Card>
                    }
                </ResizablePanel>
                <ResizableHandle className="bg-transparent" />
                <ResizablePanel defaultSize={20}>
                    <div className="border rounded-lg h-full">
                        <VersionHistory ip={ip} />
                    </div>
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    )
}