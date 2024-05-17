export async function SendCrashReport(type:string, message:string, additional:string){
    let add = {
        "version": "Frontend",
        "os": "web",
        "language": "typescript",
        "custom": additional
    }
    let json = {
        "type": type,
        "message": message,
        "additional": add
    }
    let url = "https://crash.tumppi066.fi/crash"
    let response = await fetch(url, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(json)
    })
    let data = await response.json()
    return data
}