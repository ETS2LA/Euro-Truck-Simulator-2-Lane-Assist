import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button";
import useSWR from "swr";
import {toast} from "sonner";
import {useEffect, useState} from "react";
import { PluginFunctionCall } from "@/pages/backend";

export default function Home({ ip }: { ip: string }) {


    return (
        <Card className="w-[150px]">
            <CardHeader>
                <CardTitle>Test</CardTitle>
                <CardDescription>Test</CardDescription>
            </CardHeader>
            <CardContent>
                <Button onClick={() => {
                    toast.promise(PluginFunctionCall("Test", "SendNotification", [], {}), {
                        loading: "Loading...",
                        success: "Success",
                        error: "Error"
                    });
                }}>Test</Button>
            </CardContent>
        </Card>
    )
}