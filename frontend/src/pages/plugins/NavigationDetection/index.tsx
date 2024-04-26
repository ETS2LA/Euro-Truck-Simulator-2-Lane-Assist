import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { Card, CardHeader } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
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

    const defaultFOV = 80;
    const defaultWindowScale = "0.5";
    const defaultPositionEstimationWindowScale = "0.5";
    const defaultFiltersMinimalTrafficLightSize = 8;
    const defaultFiltersMaximalTrafficLightSize = 300;

    const {data, error, isLoading} = useSWR("TrafficLightDetection", () => GetSettingsJSON("TrafficLightDetection", ip));

    const [ResetSymbol, setResetSymbol] = useState<boolean>(false);

    const [YellowLightDetection, setYellowLightDetection] = useState<boolean | undefined>(undefined);
    const [PerformanceMode, setPerformanceMode] = useState<boolean | undefined>(undefined);
    const [AdvancedSettings, setAdvancedSettings] = useState<boolean | undefined>(undefined);
    const [FOV, setFOV] = useState<number | undefined>(undefined);

    const [FinalWindow, setFinalWindow] = useState<boolean | undefined>(undefined);
    const [GrayscaleWindow, setGrayscaleWindow] = useState<boolean | undefined>(undefined);
    const [WindowScale, setWindowScale] = useState<string | undefined>(undefined);
    const [PositionEstimationWindow, setPositionEstimationWindow] = useState<boolean | undefined>(undefined);
    const [PositionEstimationWindowScale, setPositionEstimationWindowScale] = useState<string | undefined>(undefined);

    const [ConfirmDetectedTrafficLightswithAI, setConfirmDetectedTrafficLightswithAI] = useState<boolean | undefined>(undefined);
    const [ShowUnconfirmedTrafficLights, setShowUnconfirmedTrafficLights] = useState<boolean | undefined>(undefined);
    const [YOLOModel, setYOLOModel] = useState<string | undefined>(undefined);

    const [FiltersContourSizeFilter, setFiltersContourSizeFilter] = useState<boolean | undefined>(undefined);
    const [FiltersWidthHeightRatioFilter, setFiltersWidthHeightRatioFilter] = useState<boolean | undefined>(undefined);
    const [FiltersPixelPercentageFilter, setFiltersPixelPercentageFilter] = useState<boolean | undefined>(undefined);
    const [FiltersOtherLightsFilter, setFiltersOtherLightsFilter] = useState<boolean | undefined>(undefined);
    const [FiltersMinimalTrafficLightSize, setFiltersMinimalTrafficLightSize] = useState<number | undefined>(undefined);
    const [FiltersMaximalTrafficLightSize, setFiltersMaximalTrafficLightSize] = useState<number | undefined>(undefined);

    useEffect(() => {
        if (data) {

            if (data.YellowLightDetection !== undefined) { setYellowLightDetection(data.YellowLightDetection); } else { setYellowLightDetection(false); }
            if (data.PerformanceMode !== undefined) { setPerformanceMode(data.PerformanceMode); } else { setPerformanceMode(true); }
            if (data.AdvancedSettings !== undefined) { setAdvancedSettings(data.AdvancedSettings); } else { setAdvancedSettings(false); }
            if (data.FOV !== undefined) { setFOV(data.FOV); } else { setFOV(defaultFOV); }

            if (data.FinalWindow !== undefined) { setFinalWindow(data.FinalWindow); } else { setFinalWindow(true); }
            if (data.GrayscaleWindow !== undefined) { setGrayscaleWindow(data.GrayscaleWindow); } else { setGrayscaleWindow(false); }
            if (data.WindowScale !== undefined) { setWindowScale(data.WindowScale); } else { setWindowScale(defaultWindowScale); }
            if (data.PositionEstimationWindow !== undefined) { setPositionEstimationWindow(data.PositionEstimationWindow); } else { setPositionEstimationWindow(false); }
            if (data.PositionEstimationWindowScale !== undefined) { setPositionEstimationWindowScale(data.PositionEstimationWindowScale); } else { setPositionEstimationWindowScale(defaultPositionEstimationWindowScale); }

            if (data.ConfirmDetectedTrafficLightswithAI !== undefined) { setConfirmDetectedTrafficLightswithAI(data.ConfirmDetectedTrafficLightswithAI); } else { setConfirmDetectedTrafficLightswithAI(true); }
            if (data.ShowUnconfirmedTrafficLights !== undefined) { setShowUnconfirmedTrafficLights(data.ShowUnconfirmedTrafficLights); } else { setShowUnconfirmedTrafficLights(false); }
            if (data.YOLOModel !== undefined) { setYOLOModel(data.YOLOModel); } else { setYOLOModel("YOLOv5n"); }

            if (data.FiltersContourSizeFilter !== undefined) { setFiltersContourSizeFilter(data.FiltersContourSizeFilter); } else { setFiltersContourSizeFilter(true); }
            if (data.FiltersWidthHeightRatioFilter !== undefined) { setFiltersWidthHeightRatioFilter(data.FiltersWidthHeightRatioFilter); } else { setFiltersWidthHeightRatioFilter(true); }
            if (data.FiltersPixelPercentageFilter !== undefined) { setFiltersPixelPercentageFilter(data.FiltersPixelPercentageFilter); } else { setFiltersPixelPercentageFilter(true); }
            if (data.FiltersOtherLightsFilter !== undefined) { setFiltersOtherLightsFilter(data.FiltersOtherLightsFilter); } else { setFiltersOtherLightsFilter(true); }
            if (data.FiltersMinimalTrafficLightSize !== undefined) { setFiltersMinimalTrafficLightSize(data.FiltersMinimalTrafficLightSize); } else { setFiltersMinimalTrafficLightSize(defaultFiltersMinimalTrafficLightSize); }
            if (data.FiltersMaximalTrafficLightSize !== undefined) { setFiltersMaximalTrafficLightSize(data.FiltersMaximalTrafficLightSize); } else { setFiltersMaximalTrafficLightSize(defaultFiltersMaximalTrafficLightSize); }

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
        let valid = !isNaN(newFOV);
        if (valid) { if (newFOV < 0) { newFOV = 0; } if (newFOV > 999) { newFOV = 999; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "FOV", valid ? newFOV : defaultFOV, ip), {
            loading: "Saving...",
            success: "Set value to " + newFOV,
            error: "Failed to save"
        });
        setFOV(newFOV);
    };

    const UpdateFinalWindow = async () => {
        let newFinalWindow = !FinalWindow;
        toast.promise(SetSettingByKey("TrafficLightDetection", "FinalWindow", newFinalWindow, ip), {
            loading: "Saving...",
            success: "Set value to " + newFinalWindow,
            error: "Failed to save"
        });
        setFinalWindow(newFinalWindow);
    };

    const UpdateGrayscaleWindow = async () => {
        let newGrayscaleWindow = !GrayscaleWindow;
        toast.promise(SetSettingByKey("TrafficLightDetection", "GrayscaleWindow", newGrayscaleWindow, ip), {
            loading: "Saving...",
            success: "Set value to " + newGrayscaleWindow,
            error: "Failed to save"
        });
        setGrayscaleWindow(newGrayscaleWindow);
    };

    const UpdateWindowScale = async (e:any) => {
        let newWindowScale = (e.target as HTMLInputElement).value;
        let valid = !isNaN(parseFloat(newWindowScale));
        if (valid) { if (parseFloat(newWindowScale) < 0.1) { newWindowScale = "0.1"; } if (parseFloat(newWindowScale) > 9.9) { newWindowScale = "9.9"; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "WindowScale", valid ? parseFloat(newWindowScale) : defaultWindowScale, ip), {
            loading: "Saving...",
            success: "Set value to " + parseFloat(newWindowScale),
            error: "Failed to save"
        });
        setWindowScale(newWindowScale);
    };

    const UpdatePositionEstimationWindow = async () => {
        let newPositionEstimationWindow = !PositionEstimationWindow;
        toast.promise(SetSettingByKey("TrafficLightDetection", "PositionEstimationWindow", newPositionEstimationWindow, ip), {
            loading: "Saving...",
            success: "Set value to " + newPositionEstimationWindow,
            error: "Failed to save"
        });
        setPositionEstimationWindow(newPositionEstimationWindow);
    };

    const UpdatePositionEstimationWindowScale = async (e:any) => {
        let newPositionEstimationWindowScale = (e.target as HTMLInputElement).value;
        let valid = !isNaN(parseFloat(newPositionEstimationWindowScale));
        if (valid) { if (parseFloat(newPositionEstimationWindowScale) < 0.1) { newPositionEstimationWindowScale = "0.1"; } if (parseFloat(newPositionEstimationWindowScale) > 9.9) { newPositionEstimationWindowScale = "9.9"; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "PositionEstimationWindowScale", valid ? parseFloat(newPositionEstimationWindowScale) : defaultPositionEstimationWindowScale, ip), {
            loading: "Saving...",
            success: "Set value to " + parseFloat(newPositionEstimationWindowScale),
            error: "Failed to save"
        });
        setPositionEstimationWindowScale(newPositionEstimationWindowScale);
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
        let newYOLOModel = e;
        if (!["YOLOv5n", "YOLOv5s", "YOLOv5m", "YOLOv5l", "YOLOv5x"].includes(newYOLOModel)) {
            newYOLOModel = "YOLOv5n";
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
                    <CardHeader style={{ position: 'absolute', top: '43px', left: '-6px', width: '273px' }}>
                        <Button variant="secondary" style={{ fontWeight: 'bold' }}>NavigationDetection</Button>
                    </CardHeader>
                </PopoverTrigger>
                <PopoverContent style={{ position: 'relative', top: '-23px', left: '0px', height: '91px', width: '225px' }}>
                    <Label style={{ position: 'absolute', top: '12px', left: '10px', fontSize: '16px' }}>Created by</Label>
                    <Separator style={{ position: 'absolute', top: '40px', left: "0px" }}/>
                    <Label style={{ position: 'absolute', top: '57px', left: '46px', fontSize: '16px' }}>Glas42</Label>
                    <Avatar style={{ position: 'absolute', top: '49px', left: '8px', width: '32px', height: '32px' }}>
                        <AvatarImage src="https://avatars.githubusercontent.com/u/145870870?v=4"/>
                    </Avatar>
                </PopoverContent>
            </Popover>

            <Tabs defaultValue="general" style={{ position: 'absolute', top: '47px', left: '248px', right: '13.5pt' }}>
                <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="general">General</TabsTrigger>
                    <TabsTrigger value="setup">Setup</TabsTrigger>
                    <TabsTrigger value="navigationdetectionai">NavigationDetectionAI</TabsTrigger>
                </TabsList>
                <TabsContent value="general">

                    <div className="flex flex-col gap-4 justify-start pt-2" style={{ position: 'absolute', left: '-227px', right: '2.5pt' }}>

                        {YellowLightDetection !== undefined && (
                        <div className="flex flex-row" style={{ position: 'relative',top: '20px' }}>
                            <Switch id="yellowlightdetection" checked={YellowLightDetection} onCheckedChange={UpdateYellowLightDetection} />
                            <div className="flex flex-col items-start pl-2 text-left gap-2" style={{ position: 'relative', top: '-2px' }}>
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
                            <div className="flex flex-col items-start pl-2 text-left gap-2" style={{ position: 'relative', top: '-2px' }}>
                                <Label htmlFor="performancemode" className="font-bold">
                                    Performance Mode (recommended)
                                </Label>
                                <Label htmlFor="performancemode">
                                    If enabled, the traffic light detection only detects red traffic lights, which increases performance, but does not reduce detection accuracy.
                                </Label>
                            </div>
                        </div>
                        )}

                        {FOV !== undefined && (
                        <div className="flex flex-row" style={{ position: 'relative', top: '46px' }}>
                            <Input placeholder={String(defaultFOV)} id="fov" value={!isNaN(FOV) ? FOV : ''}  onChangeCapture={(e) => UpdateFOV(e)} style={{ height: '26px', width: '50px', textAlign: 'center' }} />
                            <div className="flex flex-col items-start pl-2 text-left gap-2" style={{ position: 'relative', top: '-2px' }}>
                                <Label htmlFor="fov" className="font-bold">
                                    FOV
                                </Label>
                                <Label htmlFor="fov">
                                    You need to set the field of view for the position estimation to work. You can find the FOV in the game by pressing F4, then selecting "Adjust seats".
                                </Label>
                            </div>
                        </div>
                        )}

                    </div>

                </TabsContent>
                <TabsContent value="setup">

                <div className="flex flex-col gap-4 justify-start pt-2" style={{ position: 'absolute', left: '-227px', right: '2.5pt' }}>

                    {FinalWindow !== undefined && (
                    <div className="flex flex-row" style={{ position: 'relative', top: '20px' }}>
                        <Switch id="finalwindow" checked={FinalWindow} onCheckedChange={UpdateFinalWindow} />
                        <div className="flex flex-col items-start pl-2 text-left gap-2" style={{ position: 'relative', top: '-2px' }}>
                            <Label htmlFor="finalwindow" className="font-bold">
                                Final Window
                            </Label>
                            <Label htmlFor="finalwindow">
                                If enabled, the app creates a window with the result of the traffic light detection.
                            </Label>
                        </div>
                    </div>
                    )}

                    {GrayscaleWindow !== undefined && (
                    <div className="flex flex-row" style={{ position: 'relative', top: '30px' }}>
                        <Switch id="grayscalewindow" checked={GrayscaleWindow} onCheckedChange={UpdateGrayscaleWindow} />
                        <div className="flex flex-col items-start pl-2 text-left gap-2" style={{ position: 'relative', top: '-2px' }}>
                            <Label htmlFor="grayscalewindow" className="font-bold">
                                Grayscale Window
                            </Label>
                            <Label htmlFor="grayscalewindow">
                                If enabled, the app creates a window with the color masks combined in a grayscaled frame.
                            </Label>
                        </div>
                    </div>
                    )}

                    {WindowScale !== undefined && (
                    <div className="flex flex-row" style={{ position: 'relative', top: '40px' }}>
                        <Input placeholder={String(defaultWindowScale)} id="windowscale" value={!isNaN(parseFloat(WindowScale)) ? WindowScale : ''}  onChangeCapture={(e) => UpdateWindowScale(e)} style={{ height: '26px', width: '50px', textAlign: 'center' }} />
                        <div className="flex flex-col items-start pl-2 text-left gap-2" style={{ position: 'relative', top: '-2px' }}>
                            <Label htmlFor="windowscale" className="font-bold">
                                Window Scale
                            </Label>
                            <Label htmlFor="windowscale">
                                Sets the size of the output windows.
                            </Label>
                        </div>
                    </div>
                    )}

                    {PositionEstimationWindow !== undefined && (
                    <div className="flex flex-row" style={{ position: 'relative', top: '50px' }}>
                        <Switch id="positionestimationwindow" checked={PositionEstimationWindow} onCheckedChange={UpdatePositionEstimationWindow} />
                        <div className="flex flex-col items-start pl-2 text-left gap-2" style={{ position: 'relative', top: '-2px' }}>
                            <Label htmlFor="positionestimationwindow" className="font-bold">
                                Position Estimation Window
                            </Label>
                            <Label htmlFor="positionestimationwindow">
                                If enabled, the app creates a window which shows the estimated position of the traffic light.
                            </Label>
                        </div>
                    </div>
                    )}

                    {PositionEstimationWindowScale !== undefined && (
                    <div className="flex flex-row" style={{ position: 'relative', top: '60px' }}>
                        <Input placeholder={String(defaultPositionEstimationWindowScale)} id="windowscale" value={!isNaN(parseFloat(PositionEstimationWindowScale)) ? PositionEstimationWindowScale : ''}  onChangeCapture={(e) => UpdatePositionEstimationWindowScale(e)} style={{ height: '26px', width: '50px', textAlign: 'center' }} />
                        <div className="flex flex-col items-start pl-2 text-left gap-2" style={{ position: 'relative', top: '-2px' }}>
                            <Label htmlFor="windowscale" className="font-bold">
                                Position Estimation Window Scale
                            </Label>
                            <Label htmlFor="windowscale">
                                Sets the size of the position estimation window.
                            </Label>
                        </div>
                    </div>
                    )}

                </div>

                </TabsContent>
                <TabsContent value="navigationdetectionai">

                    <div className="flex flex-col gap-4 justify-start pt-2" style={{ position: 'absolute', left: '-227px', right: '2.5pt' }}>

                        {ConfirmDetectedTrafficLightswithAI !== undefined && (
                        <div className="flex flex-row" style={{ position: 'relative',top: '20px' }}>
                            <Switch id="confirmdetectedtrafficlightswithai" checked={ConfirmDetectedTrafficLightswithAI} onCheckedChange={UpdateConfirmDetectedTrafficLightswithAI} />
                            <div className="flex flex-col items-start pl-2 text-left gap-2" style={{ position: 'relative', top: '-2px' }}>
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
                            <div className="flex flex-col items-start pl-2 text-left gap-2" style={{ position: 'relative', top: '-2px' }}>
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
                        <div className="flex flex-row" style={{ position: 'relative', top: '38px', left: '-8px' }}>
                            <div className="flex flex-col items-start pl-2 text-left gap-2">
                                <Label className="font-bold">
                                    YOLO Model
                                </Label>
                                <Label>
                                    Choose a YOLO model for the confirmation, YOLOv5n is the recommended model.
                                </Label>
                                <Select value={ YOLOModel } onValueChange={(e) => UpdateYOLOModel(e)}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select a YOLO model" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectGroup>
                                        <SelectLabel>Select a YOLO model</SelectLabel>
                                        <SelectItem value="YOLOv5n">YOLOv5n (fastest, lowest accuracy)</SelectItem>
                                        <SelectItem value="YOLOv5s">YOLOv5s (fast, low accuracy)</SelectItem>
                                        <SelectItem value="YOLOv5m">YOLOv5m (slow, medium accuracy)</SelectItem>
                                        <SelectItem value="YOLOv5l">YOLOv5l (slow, high accuracy)</SelectItem>
                                        <SelectItem value="YOLOv5x">YOLOv5x (slowest, highest accuracy)</SelectItem>
                                        </SelectGroup>
                                    </SelectContent>
                                </Select>
                                <Button variant={"destructive"} style={{ position: 'relative', top: '2px', height: '100%', textAlign: 'left' }}>
                                    Delete all downloaded models and redownload the model you are currently using.<br />This could fix faulty model files and other issues.
                                </Button>
                            </div>
                        </div>
                        )}

                    </div>

                </TabsContent>

            </Tabs>

        </Card>
    )
}