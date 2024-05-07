import { token } from "./server";

export async function CheckUsernameAvailability(username:string) {
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