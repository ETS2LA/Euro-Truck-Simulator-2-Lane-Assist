"use client"

import { GetSettingsJSON } from "./settings";
import { useAuth } from "@/apis/auth";
import { useEffect } from "react";
import useSWR from "swr";

export let login_token = '';
export let username = '';
export let user_id = '';
export let icon = '';

export async function open_login_window() {
    const discord_url_getter = "https://api.ets2la.com/auth/discord"
    let discord_url = await fetch(discord_url_getter)
    let url = await discord_url.json()

    window.open(url, "_blank")
}

async function get_user_data(setUsername: any) {
    const user_data_getter = `https://api.ets2la.com/user/${user_id}`
    let user_data = await fetch(user_data_getter, {
        headers: {
            "Authorization": `Bearer ${login_token}`
        }
    })
    let data = await user_data.json()
    if (data.error || data.data == null) {
        login_token = ''
        user_id = ''
        return null
    }
    username = data.data.username
    setUsername(username)
    return data
}

export default function AccountHandler() {
    const { setToken, setUsername } = useAuth()
    const { data: settings } = useSWR("global", GetSettingsJSON, { refreshInterval: 1000 });

    // Use useEffect to handle side effects
    useEffect(() => {
        if (!settings) return;

        if (!settings.token || !settings.user_id) {
            login_token = ''
            user_id = ''
            setToken('')
            return
        }

        login_token = settings.token
        user_id = settings.user_id
        setToken(login_token)

        // Get user data
        get_user_data(setUsername)
    }, [settings, setToken, setUsername])

    return null
}