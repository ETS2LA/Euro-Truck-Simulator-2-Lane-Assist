"use client";

import {
    ChartConfig,
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
} from "@/components/ui/chart"
import { GetStatistics } from "@/apis/backend";
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { 
    Label, 
    Pie, 
    PieChart, 
    Bar, 
    BarChart,
    RadialBar,
    RadialBarChart,
    PolarGrid,
    PolarRadiusAxis,
} from "recharts"
import { useState } from "react";
import useSWR from "swr";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Button } from "@/components/ui/button";
import { Tooltip } from "@radix-ui/react-tooltip";
import { plugin } from "postcss";

const chartConfig = {
} satisfies ChartConfig;

export default function LoginPage() {
    const { data, isLoading, error } = useSWR("statistics", GetStatistics, { refreshInterval: 1000 });
    const [selected, setSelected] = useState<string>("Please select a plugin");

    if (error) {
        return (
            <div className="w-full h-full font-geist pl-28 pr-20 pt-20 flex flex-col gap-6 border">
                <div className="text-2xl font-bold">Error</div>
                <div className="text-lg">An error occurred while fetching the statistics.</div>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="w-full h-full font-geist pl-28 pr-20 pt-20 flex flex-col gap-6 border">
                <div className="text-2xl font-bold">Loading</div>
                <div className="text-lg">Fetching the statistics...</div>
            </div>
        );
    }

    const global = data?.global;
    const plugins = data?.plugins;

    const plugin_names = Object.keys(plugins);
    
    // Convert the dictionary to a list of dictionaries where each of their key is added as a new value called "name"
    let graph_data = Object.keys(plugins).map((key) => {
        return {
            name: key,
            memory: plugins[key].memory[plugins[key].memory.length - 1],
            cpu: plugins[key].cpu[plugins[key].cpu.length - 1],
            performance: plugins[key].performance[plugins[key].performance.length - 1],
        };
    });

    const backend_ram = global.ram.python - graph_data.reduce((acc, plugin) => acc + plugin.memory, 0);
    const backend_cpu = global.cpu.python
    const plugin_cpu_total = graph_data.reduce((acc, plugin) => acc + plugin.cpu, 0);
    graph_data = [
      { name: "Other", memory: global.ram.other, cpu: global.cpu.other, performance: 0 },
      { name: "Frontend", memory: global.ram.node, cpu: global.cpu.node, performance: 0 },
      { name: "Backend", memory: backend_ram, cpu: backend_cpu, performance: 0 },
      ...graph_data,
      { name: "Free", memory: global.ram.free, cpu: 100-plugin_cpu_total, performance: 0 }
    ];

    // Define a grayscale palette generator
    const getGrayscaleShade = (index: number, total: number) => {
        if (index == 0) {
            return "#6c757d"; // Other software
        }
        else if (index == 1) {
            return "#00b4d8 "; // Frontend
        }
        else if (index == 2) {
            return "#00b4d8 "; // Backend
        }
        else if (index == total - 1) {
            return "#50C878"; // Free
        }
        else{
            index -= 2;
            return `#FFA500`;
        }
    };

    // In your component
    const graph_data_with_colors = graph_data.map((item, index) => ({
        ...item,
        fill: getGrayscaleShade(index, graph_data.length)
    }));

    let selected_data = plugins[selected];
    if (selected_data != undefined) {
        selected_data = {
            ...selected_data,
            metrics: selected_data.memory.map((_:any, index:any) => ({
                time: index,
                ram: selected_data.memory[index] || 0,
                cpu: selected_data.cpu[index] || 0,
                fps: selected_data.performance && selected_data.performance.length > index && 1/selected_data.performance[index][1] || 0 || 0
            }))
        };
    }

    return (
        <div className="w-full h-full font-geist flex flex-col gap-6 p-10 relative">
            <ChartContainer config={chartConfig} className="absolute w-72 h-72 -my-8">
                <PieChart width={300} height={300}>
                    <Pie
                        data={graph_data_with_colors}
                        dataKey="memory"
                        nameKey="name"
                        innerRadius={90}
                        outerRadius={110}
                        paddingAngle={2}
                        cornerRadius={5}
                    >
                        <Label
                            content={({ viewBox }) => {
                                if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                                    return (
                                    <text
                                        x={viewBox.cx}
                                        y={viewBox.cy}
                                        textAnchor="middle"
                                        dominantBaseline="middle"
                                    >
                                        <tspan
                                            x={viewBox.cx}
                                            y={viewBox.cy}
                                            className="fill-foreground text-3xl font-bold"
                                        >
                                            {Math.round((100 - global.ram.free) * 10) / 10}%
                                        </tspan>
                                        <tspan
                                            x={viewBox.cx}
                                            y={(viewBox.cy || 0) + 24}
                                            className="fill-muted-foreground"
                                        >
                                            Total RAM %
                                        </tspan>
                                    </text>
                                    )
                                }
                            }}
                        />
                    </Pie>
                    <ChartTooltip content={
                        <ChartTooltipContent className="" indicator="line" />
                        // @ts-ignore
                    } formatter={(value, name) => `${name} - ${Math.round(value * 10) / 10 + "%"}`} />
                    <Tooltip />
                </PieChart>
            </ChartContainer>
            <ChartContainer config={chartConfig} className="absolute w-72 h-72 -my-8 right-12">
                <PieChart width={300} height={300}>
                    <Pie
                        data={graph_data_with_colors}
                        dataKey="cpu"
                        nameKey="name"
                        innerRadius={90}
                        outerRadius={110}
                        paddingAngle={2}
                        cornerRadius={5}
                    >
                        <Label
                            content={({ viewBox }) => {
                                if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                                    return (
                                    <text
                                        x={viewBox.cx}
                                        y={viewBox.cy}
                                        textAnchor="middle"
                                        dominantBaseline="middle"
                                    >
                                        <tspan
                                            x={viewBox.cx}
                                            y={viewBox.cy}
                                            className="fill-foreground text-3xl font-bold"
                                        >
                                            {Math.round((plugin_cpu_total) * 10) / 10}%
                                        </tspan>
                                        <tspan
                                            x={viewBox.cx}
                                            y={(viewBox.cy || 0) + 24}
                                            className="fill-muted-foreground"
                                            style={{ whiteSpace: "pre-line" }}
                                        >
                                            ~ ETS2LA CPU %
                                        </tspan>
                                    </text>
                                    )
                                }
                            }}
                        />
                    </Pie>
                    <ChartTooltip content={
                        <ChartTooltipContent className="" indicator="line" />
                        // @ts-ignore
                    } formatter={(value, name) => `${name} - ${Math.round(value * 10) / 10 + "%"}`} />
                    <Tooltip />
                </PieChart>
            </ChartContainer>
            <div className="w-full h-full flex flex-col gap-6 pt-64">
                <Select value={selected} onValueChange={setSelected}>
                    <SelectTrigger className="w-72">
                        <SelectValue>{selected || "Select a plugin"}</SelectValue>
                    </SelectTrigger>
                    <SelectContent className="bg-background font-geist">
                        {plugin_names.map((plugin_name) => (
                            <SelectItem key={plugin_name} value={plugin_name}>
                                {plugin_name}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
                {selected_data == undefined ? (
                    <div className="w-full h-96 border rounded-md">
                        <div className="w-full h-full flex items-center justify-center">
                            <div className="text-2xl font-bold">Select a plugin</div>
                        </div>
                    </div>
                ) : (            
                    <ChartContainer config={chartConfig} className="w-full h-80 border rounded-md">
                        <AreaChart data={selected_data.metrics} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                            <defs>
                                <linearGradient id="fillRAM" x1="0" y1="0" x2="0" y2="1">
                                    <stop
                                    offset="0%"
                                    stopColor="#8884d8"
                                    stopOpacity={0.8}
                                    />
                                    <stop
                                    offset="95%"
                                    stopColor="#8884d8"
                                    stopOpacity={0}
                                    />
                                </linearGradient>
                                <linearGradient id="fillCPU" x1="0" y1="0" x2="0" y2="1">
                                    <stop
                                    offset="5%"
                                    stopColor="#82ca9d"
                                    stopOpacity={0.8}
                                    />
                                    <stop
                                    offset="95%"
                                    stopColor="#82ca9d"
                                    stopOpacity={0}
                                    />
                                </linearGradient>
                                <linearGradient id="fillPerformance" x1="0" y1="0" x2="0" y2="1">
                                    <stop
                                    offset="5%"
                                    stopColor="#ff7300"
                                    stopOpacity={0.8}
                                    />
                                    <stop
                                    offset="95%"
                                    stopColor="#ff7300"
                                    stopOpacity={0}
                                    />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" />
                            
                            <XAxis dataKey="time" tickCount={6} />
                            <YAxis 
                                yAxisId="left"
                                label={{ 
                                    value: 'RAM/CPU %', 
                                    angle: -90, 
                                    position: 'insideLeft',
                                    offset: 0,
                                    style: {
                                        textAnchor: 'middle'
                                    },
                                    dx: 6
                                }}
                                width={40}
                            />
                            
                            <YAxis 
                                yAxisId="right" 
                                orientation="right"
                                label={{ 
                                    value: 'FPS', 
                                    angle: 90, 
                                    position: 'insideRight',
                                    offset: 0,
                                    style: {
                                        textAnchor: 'middle'
                                    },
                                    dx: -6
                                }}
                                width={40}
                            />

                            <Area type="monotone" dataKey="ram" stroke="#8884d8" fill="url(#fillRAM)" yAxisId={"left"} />
                            <Area type="monotone" dataKey="cpu" stroke="#82ca9d" fill="url(#fillCPU)" yAxisId={"left"} />
                            <Area type="monotone" dataKey="fps" stroke="#ff7300" fill="url(#fillPerformance)" yAxisId={"right"} />
                            <ChartTooltip content={
                                <ChartTooltipContent className="" indicator="line" />
                            } />
                        </AreaChart>
                    </ChartContainer>
                )}
            </div>
        </div>
    );
}