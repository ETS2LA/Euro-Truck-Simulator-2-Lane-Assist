"use client"
import { useEffect } from "react";
import { useState } from "react";
import {toast} from "sonner"
import { Badge } from "./ui/badge"
import { Plug, Unplug } from "lucide-react";

let socket: WebSocket;
export function ETS2LAImmediateServer({ip}: {ip: string}) {
    const [connected, setConnected] = useState(false);
    const [promiseMessages, setPromiseMessages] = useState<string[]>([]);
    let lastMessage:any = null;

    useEffect(() => {
        if(ip == "") ip = "localhost";

        // Initialize the WebSocket connection
        socket = new WebSocket(`ws://${ip}:37521`);

        // Connection opened
        socket.addEventListener("open", function (event) {
            socket.send("Hello Server!");
            toast.success("Connected to the ETS2LA backend!")
            setConnected(true);
        });

        // Listen for messages
        socket.addEventListener("message", function (event) {
            const message = JSON.parse(event.data)
            if (lastMessage === message) return;
            lastMessage = message;
            console.log("Message from server ", message);
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
        });

        
        // Connection closed
        socket.addEventListener("close", function (event) {
            toast.error("Disconnected from the ETS2LA backend!")
            setConnected(false);
        });
        
        // Error
        socket.addEventListener("error", function (event) {
            console.error("WebSocket error observed:", event);
        });
        
        // Cleanup function to close the socket when the component unmounts
        return () => {
            socket.close();
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
                    socket.addEventListener("message", listener);

                    // Add a cleanup function to remove the event listener when the promise is resolved
                    cleanupFunctions.push(() => {
                        socket.removeEventListener("message", listener);
                    });
                }),
                {
                    loading: promiseMessage,
                    success: 'Success!',
                    error: 'Error!'
                }
            );
        });

        // Return a cleanup function to remove all event listeners when the component unmounts
        return () => {
            cleanupFunctions.forEach(cleanupFunction => cleanupFunction());
        };
    }, [promiseMessages]); // Dependency array to run the effect when the promise messages change

    return <div className="absolute right-[17px] top-[17px]">
        <Badge variant={connected ? "default" : "destructive"} className="gap-1 pl-1 rounded-sm">{connected ? <Plug className="w-5 h-5" /> : <Unplug className="w-5 h-5" />}{connected ? "Connected" : "Disconnected, please refresh."}</Badge>
    </div>
}