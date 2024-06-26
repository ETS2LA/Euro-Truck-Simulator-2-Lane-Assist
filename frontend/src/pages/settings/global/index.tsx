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
import { GetSettingsJSON, TriggerControlChange } from "@/pages/settings"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { useRouter } from "next/router"
import { Gauge, LineChart } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export default function Home({ ip }: { ip: string }) {
    const { push } = useRouter()

    const {data, error, isLoading} = useSWR("globals", () => GetSettingsJSON("ETS2LA%5Cbackend%5Csettings%5Cglobals.json", ip));

    if (!isLoading) return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto"><p className="font-semibold text-xs text-stone-400">Loading...</p></Card>
    if (error){
        toast.error("Error fetching settings from " + ip, {description: error.message})
        return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto"><p className="font-semibold text-xs text-red-400">{error.message}</p></Card>
    }

    return (
        <div className="flex space-x-3">
            <Card className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 p-4 h-[calc(100vh-72px)] overflow-auto auto-rows-min w-full">
            </Card>
        </div>
    )
}