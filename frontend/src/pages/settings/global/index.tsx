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

    return (
        <div className="flex space-x-3">
            <Card className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 p-4 h-[calc(100vh-72px)] overflow-auto auto-rows-min w-full">
            </Card>
        </div>
    )
}