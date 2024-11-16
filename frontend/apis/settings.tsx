import { ip } from "./backend";
// Communicate with the ETS2LA backend to get and set settings

export async function GetSettingsJSON(plugin:string) {
    const response = await fetch(`http://${ip}:37520/backend/plugins/${plugin}/settings`);
    return await response.json();
}

export async function GetSettingByKey(plugin: string, key: string) {
    try {
        const response = await fetch(`http://${ip}:37520/backend/plugins/${plugin}/settings/${key}`);
        
        if (!response.ok) {
            console.error(`Failed to fetch: HTTP status ${response.status}`);
            return null;
        }

        try {
            return await response.json();
        } catch (jsonError) {
            console.error("Failed to parse JSON response:", jsonError);
            return null;
        }
    } catch (error) {
        console.error("An error occurred while getting the setting by key:", error);
        return null;
    }
}
export async function SetSettingByKey(plugin:string, key:string, value:any) {
    try {
        const response = await fetch(`http://${ip}:37520/backend/plugins/${plugin}/settings/${key}/set`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({value})
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error("An error occurred while setting the setting by key:", error);
    }
}

// Set setting multiple keys deep.
export async function SetSettingByKeys(plugin:string, keys:string[], setting:any) {
    try {
        const response = await fetch(`http://${ip}:37520/backend/plugins/${plugin}/settings/set`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "keys": keys, 
                "setting": setting
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error("An error occurred while setting the settings by keys:", error);
    }
}

export async function TriggerControlChange(control:string) {
    try {
        const response = await fetch(`http://${ip}:37520/api/controls/${control}/change`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error("An error occurred while triggering the keybind change:", error);
    }
}

export async function UnbindControl(control:string) {
    try {
        const response = await fetch(`http://${ip}:37520/api/controls/${control}/unbind`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error("An error occurred while unbinding the keybind:", error);
    }
}