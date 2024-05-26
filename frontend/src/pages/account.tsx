import { title } from "process";
import { token } from "./backend";
import { useState } from "react";
import { toast } from "sonner";

export async function CheckConnection() {
    try {
        let response = await fetch("https://api.tumppi066.fi/", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
        })
        if(response.ok) {
            return true
        }
        throw new Error("Failed to connect to ETS2LA Backend Server")
    } catch(error) {
        toast.error("Failed to connect to ETS2LA Backend Server", 
            {
                description: "The server is most likely down, please use a guest account for now. We will notify you when the login system is back up and running!",  
                duration: 10000
            } 
        )
        return false
    }
}

export async function CheckUsernameAvailability(username:string) {
    if (await CheckConnection() === false) {
        console.error("Failed to connect to backend at https://api.tumppi066.fi/!")
        return false
    }
    let response = await fetch("https://api.tumppi066.fi/account/username/check", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username: username})
    })
    let data = await response.json()
    if(data.status == "ok") {
        return true
    }
    return false
}

export async function Register(username:string, password:string) {
    if (await CheckConnection() === false) {
        console.error("Failed to connect to backend at https://api.tumppi066.fi/!")
        return null
    }
    let response = await fetch("https://api.tumppi066.fi/account/register", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username: username, password: password})
    })
    let data = await response.json()
    if(data.status == "ok") {
        return data.message
    }
    return null
}

export async function Login(username:string, password:string) {
    await CheckConnection().then((result) => {
        console.log(result)
        if (result === false) {
            console.error("Failed to connect to backend at https://api.tumppi066.fi/!")
            return null
        }
    })
        
    let response = await fetch("https://api.tumppi066.fi/account/login", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username: username, password: password})
    })
    let data = await response.json()
    if(data.status == "ok") {
        return data.message
    }
    return null
}