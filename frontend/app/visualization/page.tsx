"use client";
import { motion } from "framer-motion";
import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"

export default function Visualization() {
    return (
        <motion.div className="flex w-full h-full">
            <ResizablePanelGroup direction="horizontal" className="w-full h-full">
                <ResizablePanel className="h-full" defaultSize={40}>
                    <motion.iframe className="w-full h-full" 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.6 }}
                        src="http://localhost:60407/ETS2LA Visualisation.html"
                    />
                </ResizablePanel>
                <ResizableHandle withHandle className="bg-transparent" />
                <ResizablePanel className="h-full w-0" defaultSize={0}>
                    <motion.iframe className="w-full h-full" 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.6 }}
                        src="https://truckermudgeon.github.io#12.69/52.44/12.97/43.2/60"
                    />
                </ResizablePanel>
            </ResizablePanelGroup>
        </motion.div>
    )
}