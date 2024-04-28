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
        <div className="w-full h-[calc(100vh-72px)]">
            <ResizablePanelGroup direction="horizontal" className="overflow-auto text-center">
                <ResizablePanel defaultSize={20}>
                    <div className="border rounded-lg h-full">
                        <PluginList ip={ip} />
                    </div>
                </ResizablePanel>
                <ResizableHandle className="bg-transparent" />
                <ResizablePanel defaultSize={60} className="content-center">
                    <div>
                        <p className="text-stone-700">You can open the command palette with the escape key.</p>
                    </div>
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