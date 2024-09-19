import { title } from "process";
import { token } from "./backend";
import { useState } from "react";
import { toast } from "sonner";
import { GetSettingByKey } from "./settingsServer";

async function GetCredentials() {
    return {
        user_id: await GetSettingByKey("global", "user_id"),
        token: await GetSettingByKey("global", "token")
    }
}

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

export async function DeleteUser() {
    const credentials = await GetCredentials()
    console.log(credentials)
    let response = await fetch("https://api.ets2la.com/delete/" + credentials.user_id, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${credentials.token}`
        },
    })
    if(response.ok) {
        toast.success("Your account has been deleted!")
        return true
    }
    throw new Error(response.statusText)
}

export async function ValidateUser() {
    const credentials = await GetCredentials()
    let response = await fetch("https://api.ets2la.com/user/" + credentials.user_id, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${credentials.token}`
        },
    })
    if(response.status == 200) {
        return true
    }
    return false
}

export async function GetUserData() {
    const credentials = await GetCredentials()
    let response = await fetch("https://api.ets2la.com/user/" + credentials.user_id, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${credentials.token}`
        },
    })
    if(response.ok) {
        return response.json()
    }
    throw new Error(response.statusText)
}