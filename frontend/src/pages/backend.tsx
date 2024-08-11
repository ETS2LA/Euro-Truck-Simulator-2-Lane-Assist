import { time } from "console"
import { randomInt } from "crypto"
import { toast } from "sonner"
const sleep = (delay:number) => new Promise((resolve) => setTimeout(resolve, delay))

export let token = '';

export async function setToken(newToken: string){
    token = newToken;
}

// Communicate with the ETS2LA backend web server on 37520
export async function GetVersion(ip="localhost") {
    console.log("Getting version")
    const response = await fetch("http://" + ip + ":37520/")
    const data = await response.json()
}

export async function CheckForUpdate(ip="localhost") {
    console.log("Checking for update")
    const response = await fetch("http://" + ip + ":37520/api/check/updates")
    const data = await response.json()
    return data
}

export async function Update(ip="localhost") {
    console.log("Updating")
    const response = await fetch("http://" + ip + ":37520/api/update")
    const data = await response.json()
}

export async function CloseBackend(ip="localhost") {
    console.log("Closing backend")
    const response = await fetch("http://" + ip + ":37520/api/quit")
    const data = await response.json()
}

export async function RestartBackend(ip="localhost") {
    console.log("Restarting backend")
    const response = await fetch("http://" + ip + ":37520/api/restart")
    const data = await response.json()
}

export async function MinimizeBackend(ip="localhost") {
    console.log("Minimizing backend")
    const response = await fetch("http://" + ip + ":37520/api/minimize")
    const data = await response.json()
}

export async function GetFrametimes(ip="localhost") {
    console.log("Getting frametimes")
    const response = await fetch("http://" + ip + ":37520/api/frametimes")
    const data = await response.json()
    return data
}

export async function GetPlugins(ip="localhost"): Promise<string[]> {
    const response = await fetch("http://" + ip + ":37520/api/plugins")
    const data = await response.json()
    return data
}

export async function GetStates(ip="localhost") {
    const response = await fetch("http://" + ip + ":37520/api/plugins/states")
    const data = await response.json()
    return data
}

export async function DisablePlugin(plugin: string, ip="localhost") {
    console.log("Disabling plugin")
    const response = await fetch("http://" + ip + `:37520/api/plugins/${plugin}/disable`)
    const data = await response.json()
}

export async function EnablePlugin(plugin: string, ip="localhost") {
    console.log("Enabling plugin")
    const response = await fetch("http://" + ip + `:37520/api/plugins/${plugin}/enable`)
    const data = await response.json()
}

export async function GetIP(ip="localhost"): Promise<string> {
    const response = await fetch(`http://${ip}:37520/api/server/ip`)
    const data = await response.json()
    await sleep(Math.floor(Math.random() * 1000) + 1000)
    return data
}

export async function PluginFunctionCall(plugin:string, method:string, args:any, kwargs:any, ip="localhost") {
    const response = await fetch(`http://${ip}:37520/api/plugins/${plugin}/call/${method}`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({args: args, kwargs: kwargs})
    })
    const data = await response.json()
    return data
}

export async function RelievePlugin(plugin:string, relieveData:any, ip="localhost") {
    const response = await fetch(`http://${ip}:37520/api/plugins/${plugin}/relieve`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({data: relieveData})
    })
    const result = await response.json()
    return result
}

export async function GetGitHistory(ip="localhost") {
    const response = await fetch(`http://${ip}:37520/api/git/history`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json'
        }
    })
    const data = await response.json()
    return data
}

export async function GetPerformance(ip="localhost") {
    const response = await fetch(`http://${ip}:37520/api/plugins/performance`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json'
        }
    })
    const data = await response.json()
    return data
}

export async function ColorTitleBar(ip="localhost", theme="dark") {
    const response = await fetch(`http://${ip}:37520/api/ui/theme/${theme}`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json'
        }
    })
    const data = await response.json()
    return data
}

export async function PlaySound(ip="localhost", sound="boot") {
    const response = await fetch(`http://${ip}:37520/api/sounds/play/${sound}`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json'
        }
    })
    const data = await response.json()
    return data
}

export async function GetStayOnTop(ip="localhost") {
    const response = await fetch(`http://${ip}:37520/api/window/stay_on_top`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json'
        }
    })
    const data = await response.json()
    return data
}

export async function SetStayOnTop(ip="localhost", top=true) {
    const response = await fetch(`http://${ip}:37520/api/window/stay_on_top/${top}`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json'
        }
    })
    const data = await response.json()
    return data
}

export async function GetCurrentLanguage(ip="localhost") {
    const response = await fetch(`http://${ip}:37520/api/language`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json'
        }
    })
    const data = await response.json()
    return data
}