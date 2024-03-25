"use client"
import { use } from "react";
import {toast} from "sonner"
import useSWR from "swr";
import { GetIP } from "@/app/server";

let socket: WebSocket;

export function ETS2LAImmediateServer({ip}: {ip: string}) {

    // Listen for events from the backend
    if (!socket){
        socket = new WebSocket(`ws://${ip}:37521`);
    }

    // Connection opened
    socket.addEventListener("open", function (event) {
        socket.send("Hello Server!");
        toast.success("Connected to the ETS2LA backend!")
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
    });

    // Error
    socket.addEventListener("error", function (event) {
        console.error("WebSocket error observed:", event);
    });

    return null
}