
import { ResizablePanel, ResizablePanelGroup, ResizableHandle } from '@/components/ui/resizable';

export default function Home() {
    return (
        <div className="flex flex-col w-full h-[calc(100vh-76px)] overflow-auto rounded-t-md justify-center items-center">
        <ResizablePanelGroup direction="horizontal" className="rounded-lg border">
            <ResizablePanel defaultSize={30}>
                <div className="flex flex-col mt-4 h-full w-full space-y-3 overflow-y-auto overflow-x-hidden max-h-full">
            
                </div>
            </ResizablePanel>
            <ResizableHandle withHandle />
            <ResizablePanel defaultSize={70}>
                    <div className="flex flex-col space-y-2 h-full items-center justify-center text-center">

                    </div>
            </ResizablePanel>
        </ResizablePanelGroup>
    </div>
    )
}