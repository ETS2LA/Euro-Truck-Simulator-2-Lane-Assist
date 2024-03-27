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
