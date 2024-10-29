import { Button } from "@/components/ui/button"
import {
  Card, CardContent, CardDescription, CardFooter, 
  CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogFooter,
    DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import React, { useState, useEffect } from 'react';
import { toast } from "sonner"

export default function Home() {
    return (
        <iframe src="https://kanboard.tumppi066.fi/public/board/f91d8a06534f358e3ba459f5c36bd622e0d5bda01de20eba38f64c96d9cc" className="h-[calc(100vh-72px)] w-full rounded-xl shadow-inner shadow-black"/>
        /*<Card className="flex flex-col content-center text-center pt-5 space-y-4 pb-0 h-[calc(100vh-72px)] overflow-auto">
            <h1>ETS2LA Developemt Home</h1>
            <Card className="flex flex-col content-center text-center pb-10 mx-10 my-10 h-[calc(100vh-72px)] overflow-auto">
                <Tabs defaultValue="Development Updates" className="w-full">
                    <TabsList className="w-full">
                        <TabsTrigger value="Developer Dashboard">Developer Dashboard</TabsTrigger>
                        <TabsTrigger value="Development Updates">Development Updates</TabsTrigger>
                        <TabsTrigger value="New Features">New Features</TabsTrigger>
                        <TabsTrigger value="Github">Github</TabsTrigger>
                        <TabsTrigger value="Polls">Polls</TabsTrigger>
                        <TabsTrigger value="Feedback and Feature Requests">Feedback and Feature Requests</TabsTrigger>
                    </TabsList>
                    <TabsContent value="Developer Dashboard"> 
                        <h2>Developer Dashboard</h2> 
                    </TabsContent>
                    <TabsContent value="Development Updates">
                        <p>Development Updates</p>
                    </TabsContent>
                    <TabsContent value="New Features">
                        <p>New Features</p>
                    </TabsContent>
                    <TabsContent value="Github">
                        <p>Github</p>
                    </TabsContent>
                    <TabsContent value="Polls">
                        <p>Polls</p>
                    </TabsContent>
                    <TabsContent value="Feedback and Feature Requests">
                        <p>Feedback and Feature Requests</p>
                    </TabsContent>
                </Tabs>
            </Card>
        </Card>
        */
    )
}

