import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { Card, CardHeader } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"

import { GetSettingsJSON, SetSettingByKey } from "@/pages/settings"
import { useEffect, useState } from "react";
import { toast } from "sonner";
import useSWR from "swr";

export default function TrafficLightDetection({ ip }: { ip: string }) {

    const {data, error, isLoading} = useSWR("TrafficLightDetection", () => GetSettingsJSON("TrafficLightDetection", ip));

    const [TestSwitch, setTestSwitch] = useState<boolean | undefined>(undefined);
    const [TestCheckbox, setTestCheckbox] = useState<boolean | undefined>();

    useEffect(() => {
        if (data) {

            if (data.TestSwitch !== undefined) { setTestSwitch(data.TestSwitch); } else { setTestSwitch(false); }
            if (data.TestCheckbox !== undefined) { setTestCheckbox(data.TestCheckbox); } else { setTestCheckbox(false); }
            
        }
    }, [data]);

    if (isLoading) return <p>Loading...</p>
    if (error) return <p className='p-4'>Lost connection to server - {error.message}</p>

    const UpdateTestSwitch = async () => {
        let newTestSwitch = !TestSwitch;
        toast.promise(SetSettingByKey("TrafficLightDetection", "TestSwitch", newTestSwitch, ip), {
            loading: "Saving...",
            success: "Set value to " + newTestSwitch,
            error: "Failed to save"
        });
        setTestSwitch(newTestSwitch);
    };

    const UpdateTestCheckbox = async () => {
        let newTestCheckbox = !TestCheckbox;
        toast.promise(SetSettingByKey("TrafficLightDetection", "TestCheckbox", newTestCheckbox, ip), {
            loading: "Saving...",
            success: "Set value to " + newTestCheckbox,
            error: "Failed to save"
        });
        setTestCheckbox(newTestCheckbox);
    };

    return (
        <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-75px)] overflow-auto">

            <Popover>
                <PopoverTrigger asChild>
                    <CardHeader style={{ position: 'absolute', top: '43px', left: '-6px', width: '240px' }}>
                        <Button variant="secondary" style={{ fontWeight: 'bold' }}>TrafficLightDetection</Button>
                    </CardHeader>
                </PopoverTrigger>
                <PopoverContent style={{ position: 'relative', top: '-23px', left: '0px', height: '50px', width: '192px' }}>
                    <Label style={{ position: 'absolute', top: '15px', left: '10px', fontSize: '16px' }}>Created by Glas42</Label>
                    <Avatar style={{ position: 'absolute', top: '8px', right: '10px', width: '32px', height: '32px' }}>
                        <AvatarImage src="https://avatars.githubusercontent.com/u/145870870?v=4"/>
                    </Avatar>
                </PopoverContent>
            </Popover>

            <Tabs defaultValue="general" style={{ position: 'absolute', top: '47px', left: '215px', right: '14pt' }}>
                <TabsList className="grid w-full grid-cols-6">
                    <TabsTrigger value="test">Test</TabsTrigger>
                    <TabsTrigger value="general">General</TabsTrigger>
                    <TabsTrigger value="screencapture">ScreenCapture</TabsTrigger>
                    <TabsTrigger value="outputwindow">OutputWindow</TabsTrigger>
                    <TabsTrigger value="trackerai">Tracker/AI</TabsTrigger>
                    <TabsTrigger value="advanced">Advanced</TabsTrigger>
                </TabsList>
                <TabsContent value="test">

                <div style={{ position: 'absolute', left: '-194px', right: '12pt' }}>

                    <div style={{ position: 'absolute', top: '15px' }}>
                        <Button>Primary Button</Button>
                        <Button variant='secondary' style={{ marginLeft: '10px' }}>Secondary Button</Button>
                        <Button variant='destructive' style={{ marginLeft: '10px' }}>Destructive Button</Button>
                        <Button variant="outline" style={{ marginLeft: '10px' }}>Outline Button</Button>
                        <Button variant="ghost" style={{ marginLeft: '10px' }}>Ghost Button</Button>
                        <Button variant="link">Link Button</Button>
                    </div>

                    {TestSwitch !== undefined && (
                    <div style={{ position: 'absolute', top: '62px' }}>
                        <Switch id="switch" checked={TestSwitch} onCheckedChange={UpdateTestSwitch} />
                        <Label htmlFor="switch" style={{ position: 'relative', top: '-2px', left: '5px', width: '800px', textAlign: 'left' }}>This is a label which is connected to the switch. (you can click on the label to change the switch state)</Label>
                    </div>
                    )}

                    {TestCheckbox !== undefined && (
                    <div style={{ position: 'absolute', top: '90px' }}>
                        <Checkbox id="checkbox" checked={TestCheckbox} onCheckedChange={UpdateTestCheckbox} />
                        <Label htmlFor="checkbox" style={{ position: 'relative', top: '-2px', left: '5px', width: '800px', textAlign: 'left' }}>This is a label which is connected to the checkbox. (you can click on the label to change the checkbox state)</Label>
                    </div>
                    )}

                    <div style={{ position: 'absolute', top: '120px', width: '200px' }}>
                        <RadioGroup defaultValue="option1">
                            <div className="flex items-center space-x-2">
                                <RadioGroupItem value="option1" id="r1"/>
                                <Label htmlFor="r1">Option 1</Label>
                            </div>
                            <div className="flex items-center space-x-2">
                                <RadioGroupItem value="option2" id="r2"/>
                                <Label htmlFor="r2">Option 2</Label>
                            </div>
                            <div className="flex items-center space-x-2">
                                <RadioGroupItem value="option3" id="r3"/>
                                <Label htmlFor="r3">Option 3</Label>
                            </div>
                        </RadioGroup>
                    </div>

                    <div style={{ position: 'absolute', top: '200px', width: '200px' }}>
                        <Slider defaultValue={[50]} min={0} max={100} step={1} />
                    </div>

                    <div style={{ position: 'absolute', top: '218px', width: '200px' }}>
                        <Input placeholder="Input" />
                    </div>

                    <div style={{ position: 'absolute', top: '260px', width: '200px' }}>
                        <Select>
                            <SelectTrigger>
                                <SelectValue placeholder="Select a YOLO model" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectGroup>
                                <SelectLabel>Select a YOLO model</SelectLabel>
                                <SelectItem value="yolov5n">YOLOv5n</SelectItem>
                                <SelectItem value="yolov5s">YOLOv5s</SelectItem>
                                <SelectItem value="yolov5m">YOLOv5m</SelectItem>
                                <SelectItem value="yolov5l">YOLOv5l</SelectItem>
                                <SelectItem value="yolov5x">YOLOv5x</SelectItem>
                                </SelectGroup>
                            </SelectContent>
                        </Select>
                    </div>

                    <div style={{ position: 'absolute', top: '285px' }}>
                        <div style={{ position: 'relative', top: '22px', left: '0px', filter: 'invert(1)' }} className="h-6 w-6 animate-spin rounded-full border-4 border-t-transparent border-currentColor-500"></div>
                        <Label style={{ position: 'relative', top: '-2px', left: '32px', width: '800px', textAlign: 'left' }}>Loading...</Label>
                    </div>

                </div>

                </TabsContent>
                <TabsContent value="general">

                </TabsContent>
                <TabsContent value="screencapture">

                </TabsContent>
                <TabsContent value="outputwindow">

                </TabsContent>
                <TabsContent value="trackerai">

                </TabsContent>
                <TabsContent value="advanced">

                </TabsContent>
            </Tabs>

        </Card>
    )
}