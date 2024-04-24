"use client"
import { useState } from "react";
import {toast} from "sonner"
import { Badge } from "./ui/badge"
import { Plug, Unplug } from "lucide-react";

let socket: WebSocket;
export function ETS2LAImmediateServer({ip}: {ip: string}) {
    const [connected, setConnected] = useState(false);

    if(ip == "") ip = "localhost";

    // Listen for events from the backend
    if (!socket){
        socket = new WebSocket(`ws://${ip}:37521`);
    }

    // Connection opened
    socket.addEventListener("open", function (event) {
        socket.send("Hello Server!");
        toast.success("Connected to the ETS2LA backend!")
        setConnected(true);
    });

    // Listen for messages
    socket.addEventListener("message", function (event) {
        const message = JSON.parse(event.data)
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

    return <div className="absolute right-[17px] top-[17px]">
        <Badge variant={connected ? "default" : "destructive"} className="gap-1 pl-1 rounded-sm">{connected ? <Plug className="w-5 h-5" /> : <Unplug className="w-5 h-5" />}{connected ? "Connected" : "Disconnected, please refresh."}</Badge>
    </div>
}