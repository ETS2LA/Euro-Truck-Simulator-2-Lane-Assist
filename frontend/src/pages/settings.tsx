// Communicate with the ETS2LA backend to get and set settings

export async function GetSettingsJSON(plugin:string, ip="localhost") {
    const response = await fetch(`http://${ip}:37520/api/plugins/${plugin}/settings`);
    return await response.json();
}

export async function GetSettingByKey(plugin:string, key:string, ip="localhost") {
    const response = await fetch(`http://${ip}:37520/api/plugins/${plugin}/settings/${key}`);
    return await response.json();
}

export async function SetSettingByKey(plugin:string, key:string, value:any, ip="localhost") {
    try {
        const response = await fetch(`http://${ip}:37520/api/plugins/${plugin}/settings/${key}/set`, {
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
export async function SetSettingByKeys(plugin:string, keys:string[], setting:any, ip="localhost") {
    try {
        const response = await fetch(`http://${ip}:37520/api/plugins/${plugin}/settings/set`, {
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

export async function TriggerControlChange(control:string, ip="localhost") {
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
