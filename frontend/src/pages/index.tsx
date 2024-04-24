import PluginList from "@/components/plugin_list"
import { Card } from "@/components/ui/card"
import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import VersionHistory from "@/components/version_history"


export default function Home({ip} : {ip: string}) {
    return (
        <div className="w-full h-[calc(100vh-75px)]">
            <ResizablePanelGroup direction="horizontal" className="border rounded-lg overflow-auto text-center">
                <ResizablePanel defaultSize={20}>
                    <PluginList ip={ip} />
                </ResizablePanel>
                <ResizableHandle />
                <ResizablePanel defaultSize={60} className="content-center">
                    <div>
                        <p className="text-stone-600">You can open the command palette with the escape key.</p>
                    </div>
                </ResizablePanel>
                <ResizableHandle />
                <ResizablePanel defaultSize={20}>
                    <VersionHistory ip={ip} />
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    )
}