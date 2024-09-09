"use client"
import { useEffect } from "react";
import { useState } from "react";
import {toast} from "sonner"
import { Badge } from "./ui/badge"
import { Plug, Unplug, Rss, ArrowDownToLine, Check, WifiOff, X, Minimize2, Pin, PinOff} from "lucide-react";
import { CheckForUpdate, Update, GetStayOnTop, SetStayOnTop, CloseBackend, MinimizeBackend } from "@/pages/backend";
import useSWR, { mutate } from "swr";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "./ui/button";
import { useRouter } from "next/router";
import { after } from "node:test";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import { translate } from "@/pages/translation";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "./ui/accordion"

let socket: WebSocket | null = null;
export function ETS2LAImmediateServer({ip, collapsed}: {ip: string, collapsed?: boolean}) {
    const { data, error, isLoading } = useSWR("updates", () => CheckForUpdate(ip), { refreshInterval: 60000 }) // Check for updates every minute
    const { data: onTopData, error: onTopError, isLoading: onTopLoading } = useSWR("onTop", () => GetStayOnTop(ip), { refreshInterval: 10000 })
    const [connected, setConnected] = useState(false);
    const [promiseMessages, setPromiseMessages] = useState<string[]>([]);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [dialogText, setDialogText] = useState("");
    const [dialogOptions, setDialogOptions] = useState<string[]>([]);
    const { push } = useRouter();
    let lastMessage:any = null;

    useEffect(() => {
        if (ip == "") ip = "localhost";

        // Initialize the WebSocket connection
        socket = new WebSocket(`ws://${ip}:37521`);

        // Connection opened
        socket.addEventListener("open", function (event) {
            toast.success(translate("frontend.immediate.connected"))
            setConnected(true);
        });

        // Listen for messages
        socket.addEventListener("message", function (event) {
            const message = JSON.parse(event.data)
            if (lastMessage === message) return;
            lastMessage = message;
            if ("ask" in message) {
                let text = message["ask"]["text"]
                let options = message["ask"]["options"]
                setDialogText(text)
                setDialogOptions(options)
                setDialogOpen(true)
                // Wait for the user to select an option
                const listener = function (event:any) {
                    const message = JSON.parse(event.data);
                    if ("response" in message) {
                        if (message["response"] === "dialog") {
                            // Send the selected option to the backend
                            if (socket !== null) {
                                socket.send(JSON.stringify({response: dialogOptions[message["option"]]}));
                                setDialogOpen(false);
                            }
                        }
                    }
                };
            }
            else if ("page" in message) {
                push(message["page"])
            }
            else {
                let toastType = message["type"]
                let toastMessage = message["text"]
                if (toastType === "error") {
                    toast.error(toastMessage)
                } else if (toastType === "success") {
                    toast.success(toastMessage)
                } else if (toastType == "info") {
                    toast.info(toastMessage)
                } else if (toastType == "warning") {
                    toast.warning(toastMessage)
                } else if (toastType == "promise") {
                    // Add the promise message to the state
                    setPromiseMessages(prevMessages => [...prevMessages, toastMessage]);
                } else {
                    toast(toastMessage)
                }
            }
        });

        
        // Connection closed
        socket.addEventListener("close", function (event) {
            toast.error(translate("frontend.immediate.disconnected"))
            setConnected(false);
        });
        
        // Error
        socket.addEventListener("error", function (event) {
            console.error("WebSocket error observed:", event);
        });
        
        // Cleanup function to close the socket when the component unmounts
        return () => {
            if (socket !== null) {
                socket.close();
            }
            socket = null;
        };
    }, []); // Empty dependency array to run the effect only once on mount
    
    // Add a function to remove a promise message
    const removePromiseMessage = (message: string) => {
        setPromiseMessages(prevMessages => prevMessages.filter(m => m !== message));
    };

    // Use an effect to handle promise messages
    useEffect(() => {
        // Create an array to store the cleanup functions for the event listeners
        const cleanupFunctions:any[] = [];

        promiseMessages.forEach(promiseMessage => {
            // Display a toast with the promise message
            toast.promise(
                new Promise((resolve) => {
                    // Wait for a message that resolves the promise
                    const listener = function (event:any) {
                        const message = JSON.parse(event.data);
                        if (message["promise"] === promiseMessage) {
                            resolve(promiseMessage);
                            // Remove the promise message when the promise is resolved
                            removePromiseMessage(promiseMessage);
                        }
                    };
                    if (socket !== null) {
                        socket.addEventListener("message", listener);

                        // Add a cleanup function to remove the event listener when the promise is resolved
                        cleanupFunctions.push(() => {
                            if (socket !== null) {
                                socket.removeEventListener("message", listener);
                            }
                        });
                    }
                }),
                {
                    loading: promiseMessage,
                    success: translate("success"),
                    error: translate("error"),
                }
            );
        });

        // Return a cleanup function to remove all event listeners when the component unmounts
        return () => {
            cleanupFunctions.forEach(cleanupFunction => cleanupFunction());
        };
    }, [promiseMessages]); // Dependency array to run the effect when the promise messages change

    return <div className={collapsed && "absolute right-[119px] top-[17px] gap-2 flex" || "absolute right-[19px] top-[17px] gap-2 flex"}>
        <Dialog open={dialogOpen}>
            <DialogTrigger>
                <div></div>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>{dialogText}</DialogTitle>
                </DialogHeader>
                <DialogDescription>
                </DialogDescription>
                <div className="flex gap-2">
                    {dialogOptions.map((option, index) => (
                        <Button key={index} variant={"outline"} onClick={() => {
                            if (socket !== null) {
                                socket.send(JSON.stringify({response: option}));
                            }
                            setDialogOpen(false);
                        }}>{option}</Button>
                    ))}
                </div>
            </DialogContent>
        </Dialog>
        { error && <Badge variant={"destructive"} className="gap-1 pl-1 rounded-sm"><WifiOff className="w-5 h-5" />{translate("frontend.immediate.update_check_error", error.message)}</Badge> }
        {   isLoading && 
                <Badge variant={"outline"} className="gap-1 pl-1 rounded-sm"><Rss className="w-5 h-5"/>{translate("frontend.immediate.checking_updates")}</Badge> 
            || data && 
                <TooltipProvider>
                    <Tooltip delayDuration={0}>
                        <TooltipTrigger>
                            <Badge variant="default" className="gap-1 pl-1 rounded-sm cursor-pointer" onClick={() => toast.promise(Update())}><ArrowDownToLine className="w-5 h-5" />{translate("frontend.immediate.update_available", data.length)}</Badge> 
                        </TooltipTrigger>
                        <TooltipContent className="bg-background border flex flex-col gap-3 w-64 max-h-64 overflow-auto p-0">
                            <Accordion type="multiple">
                                {data.map((update:any, index:any) => (
                                    <AccordionItem value={update.message} className="text-foreground">
                                        <AccordionTrigger className="text-xs font-semibold text-left p-2 no-underline">
                                            <p>{update.message}</p>
                                        </AccordionTrigger>
                                        <AccordionContent className="text-xs pl-2">
                                            {update.description !== "" && 
                                            <div className="pt-1 pb-0.5">
                                                <p className="">{update.description}</p>
                                            </div>
                                            }
                                            <p className="text-muted">by {update.author}</p>
                                        </AccordionContent>
                                    </AccordionItem>
                                ))}
                            </Accordion>
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            ||
            <TooltipProvider>
                <Tooltip delayDuration={0}>
                    <TooltipTrigger>
                    <Badge variant="secondary" className="gap-1 pl-1 rounded-sm" onClick={() => toast.promise(Update())}><Check className="w-5 h-5" />{translate("frontend.immediate.up_to_date")}</Badge>
                    </TooltipTrigger>
                    <TooltipContent className="bg-background border flex flex-col gap-3 w-44 h-8 overflow-auto p-0 text-center text-foreground text-bold justify-center">
                        {translate("frontend.immediate.no_updates")}
                    </TooltipContent>
                </Tooltip>
            </TooltipProvider>
        }
        <Badge variant={connected ? "default" : "destructive"} className="gap-1 pl-1 rounded-sm">{connected ? <Plug className="w-5 h-5" /> : <Unplug className="w-5 h-5" />}{connected ? translate("frontend.immediate.socket_connected") : translate("frontend.immediate.socket_disconnected")}</Badge>
        <div>
            <TooltipProvider>
                <Tooltip>
                    <TooltipTrigger>
                        <Button variant={"secondary"} className="h-[26px] w-5 rounded-r-none group" onClick={() => {
                            toast.promise(SetStayOnTop(ip, !onTopData), { 
                                loading: translate("setting"), 
                                success: translate("set"), 
                                error: translate("error"), 
                                onAutoClose: () => mutate("onTop"),
                                onDismiss: () => mutate("onTop"),
                                duration: 1000
                            });
                        }}>
                            {onTopData ? <Pin className="w-4 h-4 overflow-visible" /> : <PinOff className="w-4 h-4 overflow-visible" />}
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                        {onTopData ? translate("frontend.immediate.disable_stay_on_top") : translate("frontend.immediate.enable_stay_on_top")}
                    </TooltipContent>
                </Tooltip>
                <Tooltip>
                    <TooltipTrigger>
                        <Button variant={"secondary"} className="h-[26px] w-5 rounded-none group" onClick={() => MinimizeBackend()}>
                            <Minimize2 className="w-4 h-4 overflow-visible" />
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                        {translate("frontend.immediate.minimize")}
                    </TooltipContent>
                </Tooltip>
                <Tooltip>
                    <TooltipTrigger>
                        <Button variant={"secondary"} className="h-[26px] w-5 rounded-l-none group" onClick={() => CloseBackend()}>
                            <X className="w-4 h-4 overflow-visible" />
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                        {translate("frontend.immediate.close")}
                    </TooltipContent>
                </Tooltip>
            </TooltipProvider>
        </div>
    </div>
}