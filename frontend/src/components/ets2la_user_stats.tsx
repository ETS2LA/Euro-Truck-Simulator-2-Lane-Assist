import * as React from "react"  
import { GetStates } from "@/pages/backend";
import useSWR from "swr";
import { toast } from "sonner";
import { useEffect } from "react";
import { useState } from "react";
import { Progress } from "@/components/ui/progress";
import { translate } from "@/pages/translation";
import { GetJobs } from "@/pages/account";
import { Card, CardContent, CardDescription, CardFooter, 
    CardHeader, CardTitle } from "@/components/ui/card"

export default function ETS2LAUserStats() {
    const [jobs, setJobs] = useState<any[]>([]);
    const [jobCount, setJobCount] = useState(0);
    const [totalDistance, setTotalDistance] = useState(0);
    const [totalRevenue, setTotalRevenue] = useState(0);
    const [totalWeight, setTotalWeight] = useState(0);
    const [heaviestJob, setHeaviestJob] = useState(0);

    useState(() => {
        GetJobs().then((data) => {
            try {
                setJobs(data);
                setJobCount(data.length);
                let distance = 0;
                data.forEach((job:any) => {
                    distance += job["delivered_distance_km"];
                })
                setTotalDistance(distance);
                let revenue = 0;
                data.forEach((job:any) => {
                    revenue += job["delivered_revenue"];
                })
                setTotalRevenue(revenue);
                let totalWeight = 0;
                data.forEach((job:any) => {
                    let mass = job["unit_mass"];
                    let count = job["unit_count"];
                    totalWeight += mass * count;
                    if (mass * count > heaviestJob) {
                        setHeaviestJob(mass * count);
                    }
                })
                setTotalWeight(totalWeight/1000);
            }
            catch (error) {
                toast.error("An error occurred while fetching your job data", {description: "Are you logged in? Have you done jobs?"})
            }
        })
    }, )

    function formatValue(value: number, denominator?: string) {
        if (!value) {
            return "0"
        }
        let string = value.toString()
        // Add a space every 3 digits
        // if (string.length <= 4) {
        //     return string
        // }
        return string.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1' + (denominator ? denominator : ' '))
    }

    return(
        <div className="w-full h-[calc(100%-34px)] grid grid-rows-4 grid-cols-2 gap-3">
            <Card className="flex flex-col gap-0 justify-center">
                <CardHeader className="pb-1">
                    <CardTitle className="text-sm font-medium">
                        You've driven a total of
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatValue(totalDistance)}km</div>
                    <p className="text-xs text-muted-foreground">
                        in the US that's {formatValue(Math.round(totalDistance*0.621371), ",")} miles
                    </p>
                </CardContent>
            </Card>
            <Card className="flex flex-col gap-0 justify-center">
                <CardHeader className="pb-1">
                    <CardTitle className="text-sm font-medium">
                        You've completed
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatValue(jobCount)} jobs</div>
                    <p className="text-xs text-muted-foreground">
                        while using ETS2LA
                    </p>
                </CardContent>
            </Card>
            <Card className="flex flex-col gap-0 justify-center">
                <CardHeader className="pb-1">
                    <CardTitle className="text-sm font-medium">
                        On average your jobs were
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatValue(Math.round(totalDistance/jobCount))}km</div>
                    <p className="text-xs text-muted-foreground">
                        ({formatValue(Math.round(totalDistance/jobCount*0.621371), ",")} miles) long
                    </p>
                </CardContent>
            </Card>
            <Card className="flex flex-col gap-0 justify-center">
                <CardHeader className="pb-1">
                    <CardTitle className="text-sm font-medium">
                        You've earned a total of
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatValue(totalRevenue)}€</div>
                    <p className="text-xs text-muted-foreground">
                        or ${formatValue(Math.round(totalRevenue*1.18), ",")} (very rough estimate)
                    </p>
                </CardContent>
            </Card>
            <Card className="flex flex-col gap-0 justify-center">
                <CardHeader className="pb-1">
                    <CardTitle className="text-sm font-medium">
                        On average you earned
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatValue(Math.round(totalRevenue/totalDistance))}€/km</div>
                    <p className="text-xs text-muted-foreground">
                        or ${formatValue(Math.round((totalRevenue*1.18)/(totalDistance*0.621371)), ",")}/mile
                    </p>
                </CardContent>
            </Card>
            <Card className="flex flex-col gap-0 justify-center">
                <CardHeader className="pb-1">
                    <CardTitle className="text-sm font-medium">
                        On average your jobs have paid you
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatValue(Math.round(totalRevenue/jobCount))}€</div>
                    <p className="text-xs text-muted-foreground">
                        or ${formatValue(Math.round((totalRevenue*1.18)/jobCount), ",")} (again rough estimate)
                    </p>
                </CardContent>
            </Card>
            <Card className="flex flex-col gap-0 justify-center">
                <CardHeader className="pb-1">
                    <CardTitle className="text-sm font-medium">
                        You've also transported a total of
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatValue(Math.round(totalWeight))} tons</div>
                    <p className="text-xs text-muted-foreground">
                        or {formatValue(Math.round(totalWeight*1.10231), ",")} US tonnes
                    </p>
                </CardContent>
            </Card>
            <Card className="flex flex-col gap-0 justify-center">
                <CardHeader className="pb-1">
                    <CardTitle className="text-sm font-medium">
                        Your heaviest job was
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatValue(heaviestJob)}kg</div>
                    <p className="text-xs text-muted-foreground">
                        or {formatValue(Math.round(heaviestJob*2.20462), ",")}lbs
                    </p>
                </CardContent>
            </Card>
        </div>
    )
}