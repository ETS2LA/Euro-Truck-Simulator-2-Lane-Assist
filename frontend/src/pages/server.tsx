import { time } from "console"
import { randomInt } from "crypto"
import { toast } from "sonner"
const sleep = (delay:number) => new Promise((resolve) => setTimeout(resolve, delay))

let token = '';

async function setToken(newToken: string){
    token = newToken;
}

// Communicate with the ETS2LA backend web server on 37520
async function GetVersion(ip="localhost") {
    console.log("Getting version")
    const response = await fetch("http://" + ip + ":37520/")
    const data = await response.json()
}

async function CloseBackend(ip="localhost") {
    console.log("Closing backend")
    const response = await fetch("http://" + ip + ":37520/api/quit")
    const data = await response.json()
}

async function RestartBackend(ip="localhost") {
    console.log("Restarting backend")
    const response = await fetch("http://" + ip + ":37520/api/restart")
    const data = await response.json()
}

async function GetFrametimes(ip="localhost") {
    console.log("Getting frametimes")
    const response = await fetch("http://" + ip + ":37520/api/frametimes")
    const data = await response.json()
    return data
}

async function GetPlugins(ip="localhost"): Promise<string[]> {
    const response = await fetch("http://" + ip + ":37520/api/plugins")
    const data = await response.json()
    return data
}

async function DisablePlugin(plugin: string, ip="localhost") {
    console.log("Disabling plugin")
    const response = await fetch("http://" + ip + `:37520/api/plugins/${plugin}/disable`)
    const data = await response.json()
}

async function EnablePlugin(plugin: string, ip="localhost") {
    console.log("Enabling plugin")
    const response = await fetch("http://" + ip + `:37520/api/plugins/${plugin}/enable`)
    const data = await response.json()
}

async function GetIP(ip="localhost"): Promise<string> {
    const response = await fetch(`http://${ip}:37520/api/server/ip`)
    const data = await response.json()
    await sleep(Math.floor(Math.random() * 1000) + 1000)
    return data
}

async function PluginFunctionCall(plugin:string, method:string, args:any, kwargs:any, ip="localhost") {
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

async function GetGitHistory(ip="localhost") {
    const response = await fetch(`http://${ip}:37520/api/git/history`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json'
        
        }
    })
    const data = await response.json()
    return data
}

async function GetPerformance(ip="localhost") {
    const response = await fetch(`http://${ip}:37520/api/plugins/performance`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json'
        }
    })
    const data = await response.json()
    return data
}

async function ColorTitleBar(ip="localhost", theme="dark") {
    const response = await fetch(`http://${ip}:37520/api/ui/theme/${theme}`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json'
        }
    })
    const data = await response.json()
    return data
}

export { ColorTitleBar, GetPerformance, GetVersion, CloseBackend, GetFrametimes, GetPlugins, DisablePlugin, EnablePlugin, GetIP, RestartBackend, PluginFunctionCall, GetGitHistory, token, setToken }