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
    const response = await fetch(`http://${ip}:37520/api/plugins/${plugin}/settings/${key}/${value}`);
    return await response.json();
}
