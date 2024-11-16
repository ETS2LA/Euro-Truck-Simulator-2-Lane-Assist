"use client"
import { useEffect } from "react";
import { useState, useRef } from "react";
import {toast} from "sonner"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "./ui/button";
import { useRouter } from "next/navigation";
import { translate } from "@/apis/translation";
import ValueDialog from "./value-dialog";
import { ip } from "@/apis/backend";

let socket: WebSocket | null = null;
export function Popups() {
    const [dialogOpen, setDialogOpen] = useState(false);
    const [dialogObject, setDialogObject] = useState({__html: ""});
    const [dialogOptions, setDialogOptions] = useState<string[]>([]);
    const [dialogDescription, setDialogDescription] = useState("");
    const [valueDialogOpen, setValueDialogOpen] = useState(true);
    const [valueDialogJson, setValueDialogJson] = useState("");
    const [returnValue, setReturnValue] = useState(null)
    const returnValueRef = useRef(returnValue);
    const { push } = useRouter();
    let lastMessage:any = null;

    useEffect(() => { 
        returnValueRef.current = returnValue;
    }, [returnValue]);

    useEffect(() => {
        // Initialize the WebSocket connection
        socket = new WebSocket(`ws://${ip}:37521`);

        // Connection opened
        socket.addEventListener("open", function (event) {
            toast.success(translate("frontend.immediate.connected"))
        });

        // Listen for messages
        socket.addEventListener("message", function (event) {
            const message = JSON.parse(event.data)
            if (lastMessage === message) return;
            lastMessage = message;
            if ("ask" in message) {
                const text = message["ask"]["text"]
                const options = message["ask"]["options"]
                const description = message["ask"]["description"]
                setDialogObject({__html: "<div>" + text + "</div>"})
                setDialogOptions(options)
                setDialogDescription(description)
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
            else if ("dialog" in message) {
                const jsonData = message["dialog"]["json"]
                setValueDialogJson(jsonData)
                setValueDialogOpen(true)
                setReturnValue(null)
                // Wait for the return value to be set
                const listener = setInterval(() => {
                    if (returnValueRef.current !== null) { // Use the ref here
                        if (socket !== null) {
                            socket.send(JSON.stringify(returnValueRef.current)); // Use the ref here
                        }
                        setReturnValue(null)
                        clearInterval(listener)
                    }
                }, 200);
            }
            else if ("page" in message) {
                push(message["page"])
            }
            else {
                const toastType = message["type"]
                const toastMessage = message["text"]
                if (toastType === "error") {
                    toast.error(toastMessage)
                } else if (toastType === "success") {
                    toast.success(toastMessage)
                } else if (toastType == "info") {
                    toast.info(toastMessage)
                } else if (toastType == "warning") {
                    toast.warning(toastMessage)
                } else {
                    toast(toastMessage)
                }
            }
        });

        
        // Connection closed
        socket.addEventListener("close", function (event) {
            toast.error(translate("frontend.immediate.disconnected"))
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

    const handleReturnValue = (value: any) => {
        console.log(value)
        setValueDialogOpen(false)
        setReturnValue(value)
    }

    return <div className={"absolute gap-2 flex"}>
        <Dialog open={dialogOpen} >
            <DialogTrigger>
                <div>

                </div>
            </DialogTrigger>
            <DialogContent className="bg-sidebarbg font-geist">
                <DialogHeader>
                    <DialogTitle>
                        <div dangerouslySetInnerHTML={dialogObject} />
                    </DialogTitle>
                </DialogHeader>
                <DialogDescription>
                    {dialogDescription}
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

        <ValueDialog open={valueDialogOpen} onClose={handleReturnValue} json={valueDialogJson} />
    </div>
}