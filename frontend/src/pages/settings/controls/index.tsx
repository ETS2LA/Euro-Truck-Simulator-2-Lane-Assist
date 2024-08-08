import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"  

import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"

import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip"

import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"

import { toast } from "sonner"
import useSWR from "swr"
import { mutate } from "swr"
import { GetSettingsJSON, TriggerControlChange, UnbindControl } from "@/pages/settingsServer"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { useRouter } from "next/router"
import { Gauge, LineChart } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export default function ControlsPage({ ip }: { ip: string }) {
    const { push } = useRouter()
    const {data, error, isLoading} = useSWR("controls", () => GetSettingsJSON("ETS2LA%5Cbackend%5Csettings%5Ccontrols.json", ip));
    if (isLoading) return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto"><p className="font-semibold text-xs text-stone-400">Loading...</p></Card>
    if (error){
        toast.error("Error fetching settings from " + ip, {description: error.message})
        return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto"><p className="absolute left-5 font-semibold text-xs text-stone-400">{error.message}</p></Card>
    } 

    console.log(data)
    const controls:string[] = [];
    for (const key in data) {
        controls.push(key)
    }

    return (
        <div className="flex space-x-3 font-sans max-w-[calc(60vw-64px)]">
            <div className="flex flex-col gap-4 h-full overflow-auto auto-rows-min w-full">
                {controls.map((control:any) => (
                    <div key={control} id={control} className="flex w-full h-full justify-between border rounded-md p-4 text-left content-center items-center">
                        <div className="flex flex-col gap-2 w-96">
                            <h3>{control}</h3>
                            <p className="pt-3 text-sm text-muted-foreground">{data[control]["description"] == "" && "No description provided" || data[control].description}</p>
                        </div>
                        <div className="flex flex-col gap-2">
                            <div className="">
                                <Badge className="rounded-r-none">Device: </Badge>
                                <Badge className="rounded-l-none" variant={"secondary"}>{data[control]["deviceGUID"] == 1 && "Keyboard" || data[control]["deviceGUID"] == -1 && "Unbound" || data[control]["deviceGUID"]}</Badge>
                            </div>
                            <div>
                                <Badge className="rounded-r-none">{data[control]["deviceGUID"] == "1" && "Key: " || "Button: "}</Badge>
                                <Badge className="rounded-l-none" variant={"secondary"}>{data[control]["buttonIndex"] == -1 && "Unbound" || data[control]["buttonIndex"]}</Badge>
                            </div>
                            
                        </div>
                        <div className="flex flex-col gap-2">
                            <Button onClick={() => {
                                toast.promise(TriggerControlChange(control, ip), {
                                    loading: "Changing keybind...",
                                    success: "Keybind changed successfully!",
                                    error: "Failed to change keybind.",
                                    description: "Remember click the window that popped up.",
                                    duration: 1000,
                                    onAutoClose: () => mutate("controls"),
                                    onDismiss: () => mutate("controls")
                                })
                            }}>Change</Button>
                            <Button variant={"secondary"} onClick={() => {
                                toast.promise(UnbindControl(control, ip), {
                                    loading: "Unbinding keybind...",
                                    success: "Keybind unbound successfully!",
                                    error: "Failed to unbind keybind.",
                                    duration: 1000,
                                    onAutoClose: () => mutate("controls"),
                                    onDismiss: () => mutate("controls")
                                })
                            }}>Unbind</Button>
                        </div>
                    </div>
                ))}
                <div className="h-12" />
            </div>
        </div>
    )
}