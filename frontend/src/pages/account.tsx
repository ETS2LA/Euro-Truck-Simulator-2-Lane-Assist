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
        let response = await fetch("https://api.ets2la.com/heartbeat", {
            method: "GET",
            headers: {
                'Content-Type': 'application/json'
            },
        });
        if (response.ok) {
            return true;
        }
        throw new Error(response.statusText);
    } catch (error) {
        toast.error("The ETS2LA server is currently unavailable!");
        return false;
    }
}

export async function DeleteUser() {
    const credentials = await GetCredentials();
    const isConnected = await CheckConnection();

    if (!isConnected) {
        toast.error("Cannot delete user, the ETS2LA server is unavailable!");
        return false;
    }

    try {
        let response = await fetch("https://api.ets2la.com/delete/" + credentials.user_id, {
            method: "GET",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${credentials.token}`
            },
        });
        if (response.ok) {
            toast.success("Your account has been deleted!");
            return true;
        }
        throw new Error(response.statusText);
    } catch (error) {
        toast.error("Failed to delete account!");
        return false;
    }
}

export async function ValidateUser() {
    const credentials = await GetCredentials();
    const isConnected = await CheckConnection();

    if (!isConnected) {
        toast.error("Cannot validate user, the ETS2LA server is unavailable!");
        return false;
    }

    try {
        let response = await fetch("https://api.ets2la.com/user/" + credentials.user_id, {
            method: "GET",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${credentials.token}`
            },
        });
        let data = await response.json();
        if (data["status"] == 200) {
            return true;
        } else {
            toast.error("Your token is invalid, please log in again");
            return false;
        }
    } catch (error) {
        toast.error("Failed to validate user!");
        return false;
    }
}

export async function GetUserData() {
    const credentials = await GetCredentials();
    const isConnected = await CheckConnection();

    if (!isConnected) {
        toast.error("Cannot fetch user data, the ETS2LA server is unavailable!");
        return null;
    }

    try {
        let response = await fetch("https://api.ets2la.com/user/" + credentials.user_id, {
            method: "GET",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${credentials.token}`
            },
        });
        if (response.ok) {
            const data = await response.json();
            return data["data"];
        }
        throw new Error(response.statusText);
    } catch (error) {
        toast.error("Failed to fetch user data!");
        return null;
    }
}

export async function GetJobs() {
    const credentials = await GetCredentials();
    const isConnected = await CheckConnection();

    if (!isConnected) {
        toast.error("Cannot fetch jobs, the ETS2LA server is unavailable!");
        return [];
    }

    try {
        let response = await fetch("https://api.ets2la.com/user/" + credentials.user_id + "/jobs", {
            method: "GET",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${credentials.token}`
            },
        });
        if (response.ok) {
            const data = await response.json();
            return data["data"];
        }
        throw new Error(response.statusText);
    } catch (error) {
        toast.error("Failed to fetch jobs!");
        return [];
    }
}
