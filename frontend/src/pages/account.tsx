import { title } from "process";
import { token } from "./backend";
import { useState } from "react";
import { toast } from "sonner";

export async function CheckConnection() {
    try {
        let response = await fetch("https://api.tumppi066.fi/heartbeat", {
            method: "GET",
            headers: {
                'Content-Type': 'application/json'
            },
        })
        if(response.ok) {
            return true
        }
        throw new Error(response.statusText)
    } catch(error) {
        toast.error(error, 
            {
                description: "The server is most likely down, please use a guest account for now. We will notify you when the login system is back up and running!",  
                duration: 5000
            } 
        )
        return false
    }
}