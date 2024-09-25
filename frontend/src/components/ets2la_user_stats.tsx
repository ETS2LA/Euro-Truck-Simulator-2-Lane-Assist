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
            }
            catch (error) {
                toast.error("An error occurred while fetching your job data", {description: "Are you logged in? Have you done jobs?"})
            }
        })
    }, )

    function formatValue(value: number) {
        if (!value) {
            return "0"
        }
        let string = value.toString()
        // Add a space every 3 digits
        // if (string.length <= 4) {
        //     return string
        // }
        return string.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1 ')
    }

    return(
        <div className="w-full h-full grid grid-rows-3 grid-cols-2 gap-4">
            <Card className="flex flex-col gap-0 justify-center">
                <CardHeader className="pb-1">
                    <CardTitle className="text-sm font-medium">
                        You've driven a total of
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatValue(totalDistance)}km</div>
                    <p className="text-xs text-muted-foreground">
                        while using ETS2LA
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
                        Average job distance
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatValue(Math.round(totalDistance/jobCount))}km</div>
                    <p className="text-xs text-muted-foreground">
                        calculated using the data above
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
                        while using ETS2LA
                    </p>
                </CardContent>
            </Card>
            <Card className="flex flex-col gap-0 justify-center">
                <CardHeader className="pb-1">
                    <CardTitle className="text-sm font-medium">
                        Average revenue per kilometer
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatValue(Math.round(totalRevenue/totalDistance))}€/km</div>
                    <p className="text-xs text-muted-foreground">
                        calculated using the data above
                    </p>
                </CardContent>
            </Card>
            <Card className="flex flex-col gap-0 justify-center">
                <CardHeader className="pb-1">
                    <CardTitle className="text-sm font-medium">
                        Average revenue per job
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{formatValue(Math.round(totalRevenue/jobCount))}€</div>
                    <p className="text-xs text-muted-foreground">
                        calculated using the data above
                    </p>
                </CardContent>
            </Card>
        </div>
    )
}