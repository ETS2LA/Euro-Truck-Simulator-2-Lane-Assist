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

import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"

import { toast } from "sonner"
import useSWR from "swr"
import { GetFrametimes, GetPerformance } from "../server"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { useRouter } from "next/router"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Label } from "recharts"
import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import { useState } from "react"
import simplify from "simplify-js"
import { X } from "lucide-react"
  

export default function Home({ ip }: { ip: string }) {
    const [ selected, setSelected ] = useState("")
    const { push } = useRouter()
    const { data, error, isLoading } = useSWR("performance", () => GetPerformance(ip), { refreshInterval: 500 })
    if (isLoading) return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-75px)] overflow-auto"><p className="absolute left-5 font-semibold text-xs text-stone-400">Loading...</p></Card>
    if (error){
        toast.error("Error fetching plugins from " + ip, {description: error.message})
        return <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-75px)] overflow-auto"><p className="absolute left-5 font-semibold text-xs text-stone-400">{error.message}</p></Card>
    } 

    function movingAverage(array:any, sampleSize:any) {
        let result = [];
        for (let i = 0; i < array.length - sampleSize + 1; i++) {
            let window = array.slice(i, i + sampleSize);
            let average = window.reduce((total:any, value:any) => total + value, 0) / window.length;
            result.push(average);
        }
        return result;
    }

    function downsample(array:any, size:any) {
        // Input is [{cpu, mem, disk}]
        // Output is [{cpu, mem, disk}] but downsampled
        let result:any[] = [];

        let cpuPoints = array.map((point:any) => point.data.cpu);
        let memPoints = array.map((point:any) => point.data.mem);
        let diskPoints = array.map((point:any) => point.data.disk);
        let fps = array.map((point:any) => 1/point.data.frametime*2);

        let cpuSimplified = movingAverage(cpuPoints, size);
        let memSimplified = movingAverage(memPoints, size);
        let diskSimplified = movingAverage(diskPoints, size);
        let fpsSimplified = movingAverage(fps, size);

        for (let i = 0; i < cpuSimplified.length; i++) {
            result.push({
                cpu: cpuSimplified[i],
                mem: memSimplified[i],
                disk: diskSimplified[i],
                fps: fpsSimplified[i]
            })
        }

        return result;
    }

    return (
        <div className="flex space-x-3 h-[calc(100vh-75px)]">
            <ResizablePanelGroup direction="horizontal"  className="flex flex-col w-full h-full gap-4">
                <ResizablePanel className="flex flex-col w-full border h-full rounded-lg" defaultSize={15}>
                    <div className="flex flex-col gap-2 items-center justify-between p-4">
                        {data && Object.keys(data).map((key) => (
                            <Button key={data[key]["name"]} onClick={() => setSelected(key)} className="w-full" variant={selected == key && "outline" || "ghost"}>{data[key]["name"]}</Button>
                        ))}
                    </div>
                </ResizablePanel>
                <ResizableHandle className="w-0" withHandle />
                <ResizablePanel className="flex flex-col w-full border h-full rounded-lg" defaultSize={85}>
                    {selected != "" && selected in data && (
                        <ResponsiveContainer>
                            <LineChart
                                data={downsample(data[selected]["data"], 5)}
                                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                            >
                                <Tooltip itemStyle={{background: "transparent"}} contentStyle={{background: "transparent", border: "none"}} />
                                <Legend />
                                <YAxis domain={[0, 100]} width={18} ticks={[0, 50, 100]} axisLine={false} tickSize={0} />
                                <YAxis width={18} orientation="right" yAxisId="right" axisLine={false} tickSize={4} />
                                <XAxis axisLine={false} ticks={[0, data[selected]["data"].length]}/>
                                <Line type="monotone" dataKey="cpu" stroke="#8884d8" dot={false} isAnimationActive={true} name="cpu" />
                                <Line type="monotone" dataKey="mem" stroke="#82ca9d" dot={false} isAnimationActive={true} name="mem" />
                                <Line type="monotone" dataKey="fps" stroke="#ff0000" dot={false} isAnimationActive={true} name="fps" yAxisId="right" />
                            </LineChart>
                        </ResponsiveContainer>
                    )}
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    )
}