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

    const [YellowLightDetection, setYellowLightDetection] = useState<boolean | undefined>(undefined);
    const [PerformanceMode, setPerformanceMode] = useState<boolean | undefined>(undefined);
    const [AdvancedSettings, setAdvancedSettings] = useState<boolean | undefined>(undefined);
    const [FOV, setFOV] = useState<number | undefined>(undefined);

    const [ConfirmDetectedTrafficLightswithAI, setConfirmDetectedTrafficLightswithAI] = useState<boolean | undefined>(undefined);
    const [ShowUnconfirmedTrafficLights, setShowUnconfirmedTrafficLights] = useState<boolean | undefined>(undefined);
    const [YOLOModel, setYOLOModel] = useState<string | undefined>(undefined);

    useEffect(() => {
        if (data) {

            if (data.YellowLightDetection !== undefined) { setYellowLightDetection(data.YellowLightDetection); } else { setYellowLightDetection(false); }
            if (data.PerformanceMode !== undefined) { setPerformanceMode(data.PerformanceMode); } else { setPerformanceMode(true); }
            if (data.AdvancedSettings !== undefined) { setAdvancedSettings(data.AdvancedSettings); } else { setAdvancedSettings(false); }
            if (data.FOV !== undefined) { setFOV(data.FOV); } else { setFOV(80); }

            if (data.ConfirmDetectedTrafficLightswithAI !== undefined) { setConfirmDetectedTrafficLightswithAI(data.ConfirmDetectedTrafficLightswithAI); } else { setConfirmDetectedTrafficLightswithAI(true); }
            if (data.ShowUnconfirmedTrafficLights !== undefined) { setShowUnconfirmedTrafficLights(data.ShowUnconfirmedTrafficLights); } else { setShowUnconfirmedTrafficLights(false); }
            if (data.YOLOModel !== undefined) { setYOLOModel(data.YOLOModel); } else { setYOLOModel("yolov5n"); }
            
        }
    }, [data]);

    if (isLoading) return <p>Loading...</p>
    if (error) return <p className='p-4'>Lost connection to server - {error.message}</p>


    const UpdateYellowLightDetection = async () => {
        let newYellowLightDetection = !YellowLightDetection;
        toast.promise(SetSettingByKey("TrafficLightDetection", "YellowLightDetection", newYellowLightDetection, ip), {
            loading: "Saving...",
            success: "Set value to " + newYellowLightDetection,
            error: "Failed to save"
        });
        setYellowLightDetection(newYellowLightDetection);
    };

    const UpdatePerformanceMode = async () => {
        let newPerformanceMode = !PerformanceMode;
        toast.promise(SetSettingByKey("TrafficLightDetection", "PerformanceMode", newPerformanceMode, ip), {
            loading: "Saving...",
            success: "Set value to " + newPerformanceMode,
            error: "Failed to save"
        });
        setPerformanceMode(newPerformanceMode);
    };

    const UpdateAdvancedSettings = async () => {
        let newAdvancedSettings = !AdvancedSettings;
        toast.promise(SetSettingByKey("TrafficLightDetection", "AdvancedSettings", newAdvancedSettings, ip), {
            loading: "Saving...",
            success: "Set value to " + newAdvancedSettings,
            error: "Failed to save"
        });
        setAdvancedSettings(newAdvancedSettings);
    };

    const UpdateFOV = async (e:any) => {
        let newFOV = parseInt((e.target as HTMLInputElement).value);
        toast.promise(SetSettingByKey("TrafficLightDetection", "FOV", newFOV, ip), {
            loading: "Saving...",
            success: "Set value to " + newFOV,
            error: "Failed to save"
        });
        setFOV(newFOV);
    };

    const UpdateConfirmDetectedTrafficLightswithAI = async () => {
        let newConfirmDetectedTrafficLightswithAI = !ConfirmDetectedTrafficLightswithAI;
        toast.promise(SetSettingByKey("TrafficLightDetection", "ConfirmDetectedTrafficLightswithAI", newConfirmDetectedTrafficLightswithAI, ip), {
            loading: "Saving...",
            success: "Set value to " + newConfirmDetectedTrafficLightswithAI,
            error: "Failed to save"
        });
        setConfirmDetectedTrafficLightswithAI(newConfirmDetectedTrafficLightswithAI);
    };

    const UpdateShowUnconfirmedTrafficLights = async () => {
        let newShowUnconfirmedTrafficLights = !ShowUnconfirmedTrafficLights;
        toast.promise(SetSettingByKey("TrafficLightDetection", "ShowUnconfirmedTrafficLights", newShowUnconfirmedTrafficLights, ip), {
            loading: "Saving...",
            success: "Set value to " + newShowUnconfirmedTrafficLights,
            error: "Failed to save"
        });
        setShowUnconfirmedTrafficLights(newShowUnconfirmedTrafficLights);
    };

    const UpdateYOLOModel = async (e:any) => {
        let allowedValues = ["yolov5n", "yolov5s", "yolov5m", "yolov5l", "yolov5x"];
        let newYOLOModel = (e.target as HTMLInputElement).value;
        if (!allowedValues.includes(newYOLOModel)) {
            newYOLOModel = "yolov5n";
        }
        toast.promise(SetSettingByKey("TrafficLightDetection", "YOLOModel", newYOLOModel, ip), {
            loading: "Saving...",
            success: "Set value to " + newYOLOModel,
            error: "Failed to save"
        });
        setYOLOModel(newYOLOModel);
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

                        <div style={{ position: 'absolute', top: '62px' }}>
                            <Switch id="switch" />
                            <Label htmlFor="switch" style={{ position: 'relative', top: '-2px', left: '5px', width: '800px', textAlign: 'left' }}>This is a label which is connected to the switch. (you can click on the label to change the switch state)</Label>
                        </div>

                        <div style={{ position: 'absolute', top: '90px' }}>
                            <Checkbox id="checkbox" />
                            <Label htmlFor="checkbox" style={{ position: 'relative', top: '-2px', left: '5px', width: '800px', textAlign: 'left' }}>This is a label which is connected to the checkbox. (you can click on the label to change the checkbox state)</Label>
                        </div>

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

                    <div className="flex flex-col gap-4 justify-start pt-2" style={{ position: 'absolute', left: '-194px', right: '12pt' }}>

                        {YellowLightDetection !== undefined && (
                        <div className="flex flex-row" style={{ position: 'relative',top: '20px' }}>
                            <Switch id="yellowlightdetection" checked={YellowLightDetection} onCheckedChange={UpdateYellowLightDetection} />
                            <div className="flex flex-col items-start pl-2 text-left gap-2">
                                <Label htmlFor="yellowlightdetection" className="font-bold">
                                    Yellow Light Detection (not recommended)
                                </Label>
                                <Label htmlFor="yellowlightdetection">
                                    If enabled, the traffic light detection tries to detect yellow traffic lights, but it is not recommended because it causes more wrong detected traffic lights.
                                </Label>    
                            </div>
                        </div>
                        )}

                        {PerformanceMode !== undefined && (
                        <div className="flex flex-row" style={{ position: 'relative', top: '30px' }}>
                            <Switch id="performancemode" checked={PerformanceMode} onCheckedChange={UpdatePerformanceMode} />
                            <div className="flex flex-col items-start pl-2 text-left gap-2">
                                <Label htmlFor="performancemode" className="font-bold">
                                    Performance Mode (recommended)
                                </Label>
                                <Label htmlFor="performancemode">
                                    If enabled, the traffic light detection only detects red traffic lights, which increases performance, but does not reduce detection accuracy.
                                </Label>    
                            </div>
                        </div>
                        )}

                        {AdvancedSettings !== undefined && (
                        <div className="flex flex-row" style={{ position: 'relative', top: '40px' }}>
                            <Switch id="advancedsettings" checked={AdvancedSettings} onCheckedChange={UpdateAdvancedSettings} />
                            <div className="flex flex-col items-start pl-2 text-left gap-2">
                                <Label htmlFor="advancedsettings" className="font-bold">
                                    Advanced Settings
                                </Label>
                                <Label htmlFor="advancedsettings">
                                    If enabled, the traffic light detection uses the settings you set in the Advanced tab. (could have a bad impact on performance)
                                </Label>    
                            </div>
                        </div>
                        )}
                        <div className="flex flex-row" style={{ position: 'relative', top: '34px', left: '44px' }}>
                            <Button variant={'destructive'}>
                                Reset Advanced Settings to Default
                            </Button>
                        </div>

                        {FOV !== undefined && (
                        <div className="flex flex-row" style={{ position: 'relative', top: '46px' }}>
                            <Input placeholder={FOV as unknown as string} onChangeCapture={(e) => UpdateFOV(e)} style={{ width: '50px', textAlign: 'center' }} />
                            <div className="flex flex-col items-start pl-2 text-left gap-2">
                                <Label htmlFor="fov" className="font-bold">
                                    FOV
                                </Label>
                                <Label htmlFor="fov">
                                    You need to set the field of view for the position estimation to work. You can find the FOV in the game by pressing F4, then selecting "Adjust seats."
                                </Label>    
                            </div>
                        </div>
                        )}

                    </div>

                </TabsContent>
                <TabsContent value="screencapture">

                </TabsContent>
                <TabsContent value="outputwindow">

                </TabsContent>
                <TabsContent value="trackerai">

                    <div className="flex flex-col gap-4 justify-start pt-2" style={{ position: 'absolute', left: '-194px', right: '12pt' }}>

                        {ConfirmDetectedTrafficLightswithAI !== undefined && (
                        <div className="flex flex-row" style={{ position: 'relative',top: '20px' }}>
                            <Switch id="confirmdetectedtrafficlightswithai" checked={ConfirmDetectedTrafficLightswithAI} onCheckedChange={UpdateConfirmDetectedTrafficLightswithAI} />
                            <div className="flex flex-col items-start pl-2 text-left gap-2">
                                <Label htmlFor="confirmdetectedtrafficlightswithai" className="font-bold">
                                    Confirmed Detected Traffic Lights with AI
                                </Label>
                                <Label htmlFor="confirmdetectedtrafficlightswithai">
                                    If enabled, the app tracks the detected traffic lights and confirms them with the YOLO object detection. This reduces false detections and increases accuracy.
                                </Label>    
                            </div>
                        </div>
                        )}

                        {ShowUnconfirmedTrafficLights !== undefined && (
                        <div className="flex flex-row" style={{ position: 'relative', top: '30px' }}>
                            <Switch id="showunconfirmedtrafficlights" checked={ShowUnconfirmedTrafficLights} onCheckedChange={UpdateShowUnconfirmedTrafficLights} />
                            <div className="flex flex-col items-start pl-2 text-left gap-2">
                                <Label htmlFor="showunconfirmedtrafficlights" className="font-bold">
                                    Show Unconfirmed Traffic Lights
                                </Label>
                                <Label htmlFor="showunconfirmedtrafficlights">
                                    If enabled, the app will show unconfirmed or wrongly detected traffic lights in gray in the output window.
                                </Label>
                            </div>
                        </div>
                        )}

                        {YOLOModel !== undefined && (
                        <div className="flex flex-row" style={{ position: 'relative', top: '40px', left: '-8px' }}>
                            <div className="flex flex-col items-start pl-2 text-left gap-2">
                                <Label className="font-bold">
                                    YOLO Model
                                </Label>
                                <Label>
                                    Choose a YOLO model for the confirmation, YOLOv5n is the recommended model.
                                </Label>
                                <Select value={YOLOModel} onValueChange={(e) => UpdateYOLOModel(e)}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select a YOLO model" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectGroup>
                                        <SelectLabel>Select a YOLO model</SelectLabel>
                                        <SelectItem value="yolov5n">YOLOv5n (fastest, lowest accuracy)</SelectItem>
                                        <SelectItem value="yolov5s">YOLOv5s (fast, low accuracy)</SelectItem>
                                        <SelectItem value="yolov5m">YOLOv5m (slow, medium accuracy)</SelectItem>
                                        <SelectItem value="yolov5l">YOLOv5l (slow, high accuracy)</SelectItem>
                                        <SelectItem value="yolov5x">YOLOv5x (slowest, highest accuracy)</SelectItem>
                                        </SelectGroup>
                                    </SelectContent>
                                </Select>
                                <Button variant={"destructive"} style={{ height: '100%', textAlign: 'left' }}>
                                    Delete all downloaded models and redownload the model you are currently using.<br />This could fix faulty model files and other issues.
                                </Button>
                            </div>
                        </div>
                        )}

                    </div>

                </TabsContent>
                <TabsContent value="advanced">

                </TabsContent>
            </Tabs>

        </Card>
    )
}