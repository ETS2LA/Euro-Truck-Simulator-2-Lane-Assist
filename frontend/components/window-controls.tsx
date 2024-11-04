import { CloseBackend, MinimizeBackend, SetStayOnTop } from "@/apis/backend";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip"

import { useState, useEffect } from "react"
import { toast } from "sonner";

export default function WindowControls({ isCollapsed }: { isCollapsed: boolean }) {
    const [lastMousePosition, setLastMousePosition] = useState({ x: 0, y: 0 });
    const [windowPosition, setWindowPosition] = useState({ x: 0, y: 0 });
    const [isMouseInDragArea, setIsMouseInDragArea] = useState(false)
    const [stayOnTop, setStayOnTop] = useState(false);
    const [dragging, setDragging] = useState(false);

    useEffect(() => {
        const initialWindowPosition = { x: window.screenX, y: window.screenY };
        setWindowPosition(initialWindowPosition);
    }, []);

    const handleMouseCallback = (event: MouseEvent) => {
        // Check if the Y position is within 40px from the top
        if (event.clientY <= 40) {
            console.log("Mouse is in drag area")
            setIsMouseInDragArea(true)
        } else {
            setIsMouseInDragArea(false)
        }
    }

    useEffect(() => {
        window.addEventListener('mousemove', handleMouseCallback);
        return () => {
            window.removeEventListener('mousemove', handleMouseCallback);
        };
    }, []);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (dragging) {
                const newX = windowPosition.x + (e.screenX - lastMousePosition.x);
                const newY = windowPosition.y + (e.screenY - lastMousePosition.y);
                setWindowPosition({ x: newX, y: newY });
                // @ts-ignore
                window.pywebview._bridge.call('pywebviewMoveWindow', [newX, newY], "move");
                setLastMousePosition({ x: e.screenX, y: e.screenY });
            }
        };

        const handleMouseUp = () => {
            setDragging(false);
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };

        if (dragging) {
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        }

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [dragging, windowPosition, lastMousePosition]);

    const handleMouseDown = (e: React.MouseEvent) => {
        if (e.target instanceof HTMLElement) {
            e.preventDefault();
            setDragging(true);
            setLastMousePosition({ x: e.screenX, y: e.screenY });
        }
    };

    const containerClassName = "flex gap-1 absolute h-6 w-[59px] rounded-bl-lg top-0 right-0 items-center justify-center p-0 z-50 bg-sidebar transition-all pywebview-drag-region";

    return (
        <>
            <div className={containerClassName} onMouseDown={handleMouseDown}>
                {isCollapsed && (
                    <div className={`absolute right-0 top-0 h-6 flex items-center pl-2.5 pr-12 transition-all bg-sidebar rounded-bl-lg z-[-10] duration-150 ${isMouseInDragArea ? 'w-96 opacity-100' : 'w-0 opacity-0'}`}>
                        <div
                            className="flex-grow h-1 bg-repeat bg-center text-muted font-geist-mono text-[12px] text-center"
                            style={{
                                backgroundImage: "radial-gradient(circle, currentColor 1px, transparent 1px)",
                                backgroundSize: "10px 10px"
                            }}
                        >
                            <p className="bg-sidebar w-16 justify-self-center -my-1.5 pointer-events-none">
                                move
                            </p>
                        </div>
                    </div>
                )}
                <TooltipProvider>
                    <Tooltip delayDuration={250}>
                        <TooltipTrigger onClick={() => {
                            setStayOnTop(!stayOnTop)
                            SetStayOnTop(stayOnTop).then(() => {
                                toast.success(`${stayOnTop ? "Window is now on top" : "Window is no longer on top"}`)
                            })
                        }}>
                            <div className="w-2.5 h-2.5 bg-green-500 rounded-full flex items-center justify-center" />
                        </TooltipTrigger>
                        <TooltipContent className="bg-sidebar border text-white">
                            <p>Stay on top</p>
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
                <TooltipProvider>
                    <Tooltip delayDuration={250}>
                        <TooltipTrigger onClick={() => {
                            MinimizeBackend()
                        }}>
                            <div className="w-2.5 h-2.5 bg-yellow-500 rounded-full flex items-center justify-center" />
                        </TooltipTrigger>
                        <TooltipContent className="bg-sidebar border text-white">
                            <p>Minimize</p>
                        </TooltipContent>
                    </Tooltip>
                    <Tooltip delayDuration={250}>
                        <TooltipTrigger onClick={() => {
                            CloseBackend()
                        }}>
                            <div className="w-2.5 h-2.5 bg-red-500 rounded-full flex items-center justify-center" />
                        </TooltipTrigger>
                        <TooltipContent className="bg-sidebar border text-white">
                            <p>Close</p>
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            </div>
            {!isCollapsed && (
                <>
                    <div className="absolute top-0 right-0 left-0 h-6 z-40" onMouseDown={handleMouseDown} />
                    {/* Bottom side outer rounding */}
                    <div className="top-0 right-0 absolute z-50 w-4 h-4 my-[16px] mx-[-0.5px]">
                        <svg viewBox="4 -4 8 8" xmlns="http://www.w3.org/2000/svg">
                            <defs>
                                <mask id="hole">
                                    <rect x="0" y="0" width="8" height="8" fill="white" />
                                    <circle cx="4" cy="4" r="4" fill="black" />
                                </mask>
                            </defs>
                            <rect x="0" y="0" width="8" height="8" fill="#18181b" mask="url(#hole)" />
                        </svg>
                    </div>
                    {/* Left side outer rounding */}
                    <div className="top-0 right-0 absolute z-50 w-4 h-4 my-[0px] mx-[51px]">
                        <svg viewBox="4 -4 8 8" xmlns="http://www.w3.org/2000/svg">
                            <defs>
                                <mask id="hole">
                                    <rect x="0" y="0" width="8" height="8" fill="white" />
                                    <circle cx="4" cy="4" r="4" fill="black" />
                                </mask>
                            </defs>
                            <rect x="0" y="0" width="8" height="8" fill="#18181b" mask="url(#hole)" />
                        </svg>
                    </div>
                </>
            )}
        </>
    )
}