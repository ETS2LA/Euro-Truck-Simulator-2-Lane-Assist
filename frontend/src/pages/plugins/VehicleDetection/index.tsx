import { Card, CardContent, CardDescription, CardFooter, 
    CardHeader, CardTitle } from "@/components/ui/card"
import { Popover, PopoverContent, 
    PopoverTrigger } from "@/components/ui/popover"
import { Tabs, TabsList, TabsTrigger, 
    TabsContent } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogFooter, 
    DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button"
import { toast } from "sonner";

import { GetSettingsJSON } from "@/pages/settings"
import { PluginFunctionCall } from "@/pages/backend";

import useSWR from "swr";
import { useState } from "react";

export default function VehicleDetection({ ip }: { ip: string }) {
    const {data, error, isLoading} = useSWR("VehicleDetection", () => GetSettingsJSON("VehicleDetection", ip));
    
    // Setup Variables
    const [setup_page, setSetupPage] = useState(0);
    const [setup_open, setSetupOpen] = useState(false);

    return (
        <Card className="flex flex-col items-center text-center space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto relative">
            <div className="flex flex-row w-[calc(100vw-44px)] gap-3 m-2">
                <Popover>
                    <PopoverTrigger asChild>
                        <Button variant="secondary" className="font-bold w-42">
                            Vehicle Detection
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-48 h-auto">
                        <h2 className="text-base">Created by</h2>
                        <Separator className="my-2" />
                        <div className="flex pt-2">
                            <Avatar className="w-8 h-8">
                                <AvatarImage src="https://avatars.githubusercontent.com/u/110776467?v=4" />
                            </Avatar>
                            <h2 className="ml-2 text-base">Dyldev</h2>
                        </div>
                    </PopoverContent>
                </Popover>
                <Tabs defaultValue="general" className="w-full">
                    <TabsList className="grid grid-cols-3 w-full">
                        <TabsTrigger value="general">General</TabsTrigger>
                        <TabsTrigger value="setup">Setup</TabsTrigger>
                        <TabsTrigger value="advanced">Advanced</TabsTrigger>
                    </TabsList>
                    <TabsContent value="general">
                        <CardContent>
                            <div className="flex flex-col justify-start pt-2 self-start -ml-56 md:-ml-68">
                                
                            </div>
                        </CardContent>
                    </TabsContent>
                    <TabsContent value="setup">
                        <CardContent>
                            <div className="flex flex-col justify-start pt-2 self-start -ml-56 md:-ml-68">
                                
                            </div>
                        </CardContent>
                    </TabsContent>
                    <TabsContent value="advanced">
                        <CardContent>
                            <div className="flex flex-col justify-start pt-2 self-start -ml-40 md:-ml-68">
                                <Tabs className="w-full">
                                    <TabsList defaultValue="detection" className="grid grid-cols-2 w-full">
                                        <TabsTrigger value="detection">Detection</TabsTrigger>
                                        <TabsTrigger value="colors">Colors</TabsTrigger>
                                    </TabsList>
                                    <TabsContent value="detection">
                                        <Badge variant={"destructive"}>
                                            You shouldnt not mess with these settings unless you know what you are doing. 
                                            These settings can be used to fine tune Vehicle Detection for your PC. 
                                            If used inccorectly, it can have negative impacts. 
                                            Normally, default settings are best.</Badge>
                                    </TabsContent>
                                    <TabsContent value="colors">
                                        <p>Colors</p>
                                    </TabsContent>
                                </Tabs>
                            </div>
                        </CardContent>
                    </TabsContent>
                </Tabs>
            </div>
        </Card>
    );
}