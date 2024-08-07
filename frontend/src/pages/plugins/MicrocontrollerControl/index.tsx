import { Card, CardContent, CardDescription, CardFooter, 
    CardHeader, CardTitle } from "@/components/ui/card"
import { Popover, PopoverContent, 
    PopoverTrigger } from "@/components/ui/popover"
import { Tabs, TabsList, TabsTrigger, 
    TabsContent } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogFooter, 
    DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button"
import { toast } from "sonner";

import { GetSettingsJSON } from "@/pages/settingsServer"
import { PluginFunctionCall } from "@/pages/backend";

import useSWR from "swr";
import { useState } from "react";

export default function MicrocontrollerControl({ ip }: { ip: string }) {
    const {data, error, isLoading} = useSWR("MicrocontrollerControl", () => GetSettingsJSON("MicrocontrollerControl", ip));
    
    // Setup Variables
    const [setup_page, setSetupPage] = useState(0); // 0: Introduction 1: Board, 2: Ard Board Gen, 3. Pi Board Gen
    const [setup_open, setSetupOpen] = useState(false);

    return (
        <Card className="flex flex-col items-center text-center space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto relative">
            <div className="flex flex-row w-[calc(100vw-44px)] gap-3 m-2">
                <Popover>
                    <PopoverTrigger asChild>
                        <Button variant="secondary" className="font-bold w-42">
                            Microcontroller Control
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
                        <TabsTrigger value="boards">Boards</TabsTrigger>
                    </TabsList>
                    <TabsContent value="general">
                        <CardContent>
                            <div className="flex flex-col justify-start pt-2 self-start -ml-56 md:-ml-68">
                                <h3>General</h3>
                            </div>
                        </CardContent>
                    </TabsContent>
                    <TabsContent value="setup">
                        <CardContent>
                            <div className="flex flex-col justify-start pt-2 self-start -ml-56 md:-ml-68">
                                <div className="flex flex-row items-start justify-start text-left">
                                    <div className="ml-3 mt-2 font-bold">
                                        <p>In order to receive and send data to and from the microcntroller, we need to know how to communicate with it.</p>
                                        <p>This setup will guide you through the process of setting up your microcontroller.</p>
                                        <p>Please note that this will only work if you have an Arduino or Raspberry Pi board</p>
                                        <p>If you would like to request another board please let us know through the feedback section.</p>
                                        <div className="pt-3">
                                            <Button onClick={() => setSetupOpen(true)}>Launch Setup</Button>
                                        </div>
                                    </div>
                                    <Dialog open={setup_open} onOpenChange={setSetupOpen}>
                                        <DialogContent className="min-w-[600px]">
                                            {setup_page == 0 && <Page0 />}
                                            {setup_page == 1 && <Page1 />}
                                            {setup_page == 2 && <Page2 />}
                                        </DialogContent>
                                    </Dialog>
                                </div> 
                            </div>
                        </CardContent>
                    </TabsContent>
                    <TabsContent value="boards">
                        <CardContent>
                            <div className="flex flex-col justify-start pt-2 self-start -ml-56 md:-ml-68">
                                <h3>Boards</h3>
                            </div>
                        </CardContent>
                    </TabsContent>
                </Tabs>
            </div>
        </Card>
    );


    // Setup Pages

    // Welcome
    function Page0() {
        return (
            <div>
                <h1 className="font-bold">Welcome!</h1>
                <p className="text-md font-semibold mt-4">This wizard will guide you through setting up your microcontroller for use with ETS2LA.
                A series of questions will be asked to guide you through the process.
                Please keep in mind that this only works with an Arduino or Raspberry Pi.
                If you would like to request another board please let us know through the feedback section.</p>
                <div className="flex flex-row mt-6 space-x-3">
                    <Button onClick={() => setSetupOpen(false)}>Cancel</Button>
                    <Button onClick={() => setSetupPage(1)}>Next</Button>
                </div>
            </div>
        )
    }

    // Board
    function Page1() {
        const [boardType, setBoardType] = useState("arduino");
        return (
            <div>
                <h1 className="font-bold">Board Type</h1>
                <p className="text-md font-semibold mt-4">Here you should select the type of microcntroller that you would like to use.
                Choose from the options below and select continue.</p>
                <RadioGroup value={boardType} onValueChange={setBoardType}>
                    <div className="flex flex-col mt-4">
                        <div className="flex flex-row space-x-3">
                            <RadioGroupItem value={"arduino"} className="mt-1"></RadioGroupItem>
                            <p>Arduino</p>
                        </div>
                        <div className="flex flex-row space-x-3">
                            <RadioGroupItem value={"raspberry"} className="mt-1"></RadioGroupItem>
                            <p>Raspberry Pi</p>
                        </div>
                    </div>
                </RadioGroup>
                <div className="flex flex-row mt-6 space-x-3">
                    <Button onClick={() => setSetupPage(0)}>Back</Button>
                    <Button onClick={() => {if (boardType === "arduino") {setSetupPage(2);} else if (boardType === "raspberry") { setSetupPage(3); }}}>Next</Button>
                </div>
            </div>
        )
    }
    
    // Arduino Wifi
    function Page2() {
        const [wifiEnabled, setWifiEnabled] = useState("No");
        return (
            <div>
                <h1 className="font-bold">Wi-Fi Capabilities</h1>
                <p className="text-md font-semibold mt-4">Now that we hae verified that you have an Arduino, we need to get into more detail.
                Please select whether your Arduino is WIFI enabled or not.</p>
                <RadioGroup value={wifiEnabled} onValueChange={setWifiEnabled}>
                    <div className="flex flex-col mt-4">
                        <div className="flex flex-row space-x-3">
                            <RadioGroupItem value={"yes"} className="mt-1"></RadioGroupItem>
                            <p>My Arduino is Wi-Fi enabled.</p>
                        </div>
                        <div className="flex flex-row space-x-3">
                            <RadioGroupItem value={"no"} className="mt-1"></RadioGroupItem>
                            <p>My Arduino is not Wi-Fi enabled.</p>
                        </div>
                    </div>
                </RadioGroup>
                <div className="flex flex-row mt-6 space-x-3">
                    <Button onClick={() => setSetupPage(1)}>Back</Button>
                    <Button onClick={() => {if (wifiEnabled === "yes") {setSetupPage(2);} else if (wifiEnabled === "no") { setSetupPage(3); }}}>Next</Button>
                </div>
            </div>
        )
    }

    // Raspberry Wifi
    function Page3() {
        const [wifiEnabled, setWifiEnabled] = useState("No");
        return (
            <div>
                <h1 className="font-bold">What Model?</h1>
                <p className="text-md font-semibold mt-4">Now that we hae verified that you have an Raspberry Pi, we need to get into more detail.
                Please select the model of your Raspberry Pi.</p>
                <Select>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Select a fruit" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectGroup>
                        <SelectLabel>Fruits</SelectLabel>
                        <SelectItem value="apple">Apple</SelectItem>
                        <SelectItem value="banana">Banana</SelectItem>
                        <SelectItem value="blueberry">Blueberry</SelectItem>
                        <SelectItem value="grapes">Grapes</SelectItem>
                        <SelectItem value="pineapple">Pineapple</SelectItem>
                        </SelectGroup>
                    </SelectContent>
                    </Select>
                <div className="flex flex-row mt-6 space-x-3">
                    <Button onClick={() => setSetupPage(1)}>Back</Button>
                    <Button onClick={() => {if (wifiEnabled === "yes") {setSetupPage(2);} else if (wifiEnabled === "no") { setSetupPage(3); }}}>Next</Button>
                </div>
            </div> 
        )
    }
}