import { Card, CardContent, CardDescription, CardFooter, 
    CardHeader, CardTitle } from "@/components/ui/card"
import { Popover, PopoverContent, 
    PopoverTrigger } from "@/components/ui/popover"
import { Tabs, TabsList, TabsTrigger, 
    TabsContent } from "@/components/ui/tabs"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"

import { GetSettingsJSON } from "@/pages/settingsServer"
import { PluginFunctionCall } from "@/pages/backend";

import useSWR from "swr";
import { useState } from "react";

export default function ObjectDetection({ ip }: { ip: string }) {
    const {data, error, isLoading} = useSWR("ObjectDetection", () => GetSettingsJSON("ObjectDetection", ip));

    // Lane Changing Model Enabled
    const [laneChangingModelEnabled, setLaneChangingModelEnabled] = useState<boolean>(false);
    const handleLaneChangingModelChange = (value: boolean) => {
        if (value) {
            setLaneChangingModelEnabled(true);
        } else {
            setLaneChangingModelEnabled(false);
        }
        console.log("Lane Changing Model Enabled was changed to: " + value + " This feature has not been added yet.");
    };

    // Vehicle Classification Model Enabled
    const [vehicleClassificationModelEnabled, setVehicleClassificationModelEnabled] = useState<boolean>(false);
    const handleVehicleClassificationModelChange = (value: boolean) => {
        if (value) {
            setVehicleClassificationModelEnabled(true);
        } else {
            setVehicleClassificationModelEnabled(false);
        }
        console.log("Vehicle Classification Model Enabled was changed to: " + value + " This feature has not been added yet.");
    };

    // Model Confidence Slider
    const [modelConfSlider, setModelConfSlider] = useState<number>(0.70);
    const handleSliderChange = (value: number[]) => {
        if (value.length > 0) {
            setModelConfSlider(value[0]);
            console.log("Model Confidence Slider Value was changed to: " + value[0] + " This feature has not been added yet.");
        }
    };

    return (
        <Card className="flex flex-col items-center text-center space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto relative">
            <div className="flex flex-row w-[calc(100vw-44px)] gap-3 m-2">
                <Popover>
                    <PopoverTrigger asChild>
                        <Button variant="secondary" className="font-bold w-52">
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
                                <h4>Vehicle Detection Settings:</h4>
                                <div className="flex flex-col pt-2">
                                    <div className="flex flex-row items-center text-left gap-2 pt-2">
                                        <Switch id="lanechanginemodelenabled" checked={laneChangingModelEnabled} onCheckedChange={handleLaneChangingModelChange} />
                                        <Label htmlFor="lanechanginemodelenabled">
                                            <span className="font-bold">Lame Changing Assist Model</span><br />
                                            If enabled, Vehicle Detection will use the Lame Changing Assist Model to check for vehicles before changing lanes.
                                        </Label>
                                    </div>
                                    <div className="flex flex-row items-center text-left gap-2 pt-2">
                                        <Switch id="classificationmodelenabled" checked={vehicleClassificationModelEnabled} onCheckedChange={handleVehicleClassificationModelChange} />
                                        <Label htmlFor="classificationmodelenabled">
                                            <span className="font-bold">Vehicle Classification Model</span><br/>
                                            If enabled, Vehicle Detection will use the Vehicle Classification Model to get details about vehicles for GoDot visualization.
                                        </Label>
                                    </div>
                                </div>
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
                                    <TabsList defaultValue="detection" className="grid grid-cols-2">
                                        <TabsTrigger value="detection">Detection</TabsTrigger>
                                        <TabsTrigger value="colors">Colors</TabsTrigger>
                                    </TabsList>
                                    <TabsContent value="detection">
                                        <div className="pb-2">
                                            <Badge variant={"destructive"}>
                                                You shouldnt not mess with these settings unless you know what you are doing. 
                                                These settings can be used to fine tune Vehicle Detection for your PC. 
                                                If used inccorectly, it can have negative impacts. 
                                                Normally, default settings are best.
                                            </Badge>
                                        </div>
                                        <div className="grid-flow-col">
                                            <p>Model Confidence Limit</p>
                                            <Slider defaultValue={[modelConfSlider]} max={1} step={0.01} onValueChange={handleSliderChange}></Slider>                         
                                        </div>
                                    </TabsContent>
                                    <TabsContent value="colors">
                                        <div className="grid grid-cols-3 grid-rows-3">
                                            <div className="flex flex-row">
                                                <p>Car R</p>
                                                <Input placeholder="Car Red Value"></Input>
                                            </div>
                                        </div>
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