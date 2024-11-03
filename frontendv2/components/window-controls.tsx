import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip"

export default function WindowControls() {
    return (
        <div className="flex gap-1 absolute top-1.5 right-1.5">
            <TooltipProvider>
                <Tooltip delayDuration={250}>
                    <TooltipTrigger>
                        <div className="w-3 h-3 bg-green-500 rounded-full flex items-center justify-center" />
                    </TooltipTrigger>
                    <TooltipContent className="bg-sidebar border text-white">
                        <p>Stay on top</p>
                    </TooltipContent>
                </Tooltip>
            </TooltipProvider>
            <TooltipProvider>
                <Tooltip delayDuration={250}>
                    <TooltipTrigger>
                        <div className="w-3 h-3 bg-yellow-500 rounded-full flex items-center justify-center" />
                    </TooltipTrigger>
                    <TooltipContent className="bg-sidebar border text-white">
                        <p>Minimize</p>
                    </TooltipContent>
                </Tooltip>
                <Tooltip delayDuration={250}>
                    <TooltipTrigger>
                        <div className="w-3 h-3 bg-red-500 rounded-full flex items-center justify-center" />
                    </TooltipTrigger>
                    <TooltipContent className="bg-sidebar border text-white">
                        <p>Close</p>
                    </TooltipContent>
                </Tooltip>
            </TooltipProvider>
        </div>
    )
}