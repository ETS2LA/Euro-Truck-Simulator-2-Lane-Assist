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

    const defaultFOV = 80;
    const defaultWindowScale = "0.5";
    const defaultPositionEstimationWindowScale = "0.5";
    const defaultColorSettings_urr = 255;
    const defaultColorSettings_urg = 110;
    const defaultColorSettings_urb = 110;
    const defaultColorSettings_lrr = 200;
    const defaultColorSettings_lrg = 0;
    const defaultColorSettings_lrb = 0;
    const defaultColorSettings_uyr = 255;
    const defaultColorSettings_uyg = 240;
    const defaultColorSettings_uyb = 170;
    const defaultColorSettings_lyr = 200;
    const defaultColorSettings_lyg = 170;
    const defaultColorSettings_lyb = 50;
    const defaultColorSettings_ugr = 150;
    const defaultColorSettings_ugg = 255;
    const defaultColorSettings_ugb = 230;
    const defaultColorSettings_lgr = 0;
    const defaultColorSettings_lgg = 200;
    const defaultColorSettings_lgb = 0;
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

    const [ColorSettings_urr, setColorSettings_urr] = useState<number | undefined>(undefined);
    const [ColorSettings_urg, setColorSettings_urg] = useState<number | undefined>(undefined);
    const [ColorSettings_urb, setColorSettings_urb] = useState<number | undefined>(undefined);
    const [ColorSettings_lrr, setColorSettings_lrr] = useState<number | undefined>(undefined);
    const [ColorSettings_lrg, setColorSettings_lrg] = useState<number | undefined>(undefined);
    const [ColorSettings_lrb, setColorSettings_lrb] = useState<number | undefined>(undefined);
    const [ColorSettings_uyr, setColorSettings_uyr] = useState<number | undefined>(undefined);
    const [ColorSettings_uyg, setColorSettings_uyg] = useState<number | undefined>(undefined);
    const [ColorSettings_uyb, setColorSettings_uyb] = useState<number | undefined>(undefined);
    const [ColorSettings_lyr, setColorSettings_lyr] = useState<number | undefined>(undefined);
    const [ColorSettings_lyg, setColorSettings_lyg] = useState<number | undefined>(undefined);
    const [ColorSettings_lyb, setColorSettings_lyb] = useState<number | undefined>(undefined);
    const [ColorSettings_ugr, setColorSettings_ugr] = useState<number | undefined>(undefined);
    const [ColorSettings_ugg, setColorSettings_ugg] = useState<number | undefined>(undefined);
    const [ColorSettings_ugb, setColorSettings_ugb] = useState<number | undefined>(undefined);
    const [ColorSettings_lgr, setColorSettings_lgr] = useState<number | undefined>(undefined);
    const [ColorSettings_lgg, setColorSettings_lgg] = useState<number | undefined>(undefined);
    const [ColorSettings_lgb, setColorSettings_lgb] = useState<number | undefined>(undefined);

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

            if (data.ColorSettings_urr !== undefined) { setColorSettings_urr(data.ColorSettings_urr); } else { setColorSettings_urr(defaultColorSettings_urr); }
            if (data.ColorSettings_urg !== undefined) { setColorSettings_urg(data.ColorSettings_urg); } else { setColorSettings_urg(defaultColorSettings_urg); }
            if (data.ColorSettings_urb !== undefined) { setColorSettings_urb(data.ColorSettings_urb); } else { setColorSettings_urb(defaultColorSettings_urb); }
            if (data.ColorSettings_lrr !== undefined) { setColorSettings_lrr(data.ColorSettings_lrr); } else { setColorSettings_lrr(defaultColorSettings_lrr); }
            if (data.ColorSettings_lrg !== undefined) { setColorSettings_lrg(data.ColorSettings_lrg); } else { setColorSettings_lrg(defaultColorSettings_lrg); }
            if (data.ColorSettings_lrb !== undefined) { setColorSettings_lrb(data.ColorSettings_lrb); } else { setColorSettings_lrb(defaultColorSettings_lrb); }
            if (data.ColorSettings_uyr !== undefined) { setColorSettings_uyr(data.ColorSettings_uyr); } else { setColorSettings_uyr(defaultColorSettings_uyr); }
            if (data.ColorSettings_uyg !== undefined) { setColorSettings_uyg(data.ColorSettings_uyg); } else { setColorSettings_uyg(defaultColorSettings_uyg); }
            if (data.ColorSettings_uyb !== undefined) { setColorSettings_uyb(data.ColorSettings_uyb); } else { setColorSettings_uyb(defaultColorSettings_uyb); }
            if (data.ColorSettings_lyr !== undefined) { setColorSettings_lyr(data.ColorSettings_lyr); } else { setColorSettings_lyr(defaultColorSettings_lyr); }
            if (data.ColorSettings_lyg !== undefined) { setColorSettings_lyg(data.ColorSettings_lyg); } else { setColorSettings_lyg(defaultColorSettings_lyg); }
            if (data.ColorSettings_lyb !== undefined) { setColorSettings_lyb(data.ColorSettings_lyb); } else { setColorSettings_lyb(defaultColorSettings_lyb); }
            if (data.ColorSettings_ugr !== undefined) { setColorSettings_ugr(data.ColorSettings_ugr); } else { setColorSettings_ugr(defaultColorSettings_ugr); }
            if (data.ColorSettings_ugg !== undefined) { setColorSettings_ugg(data.ColorSettings_ugg); } else { setColorSettings_ugg(defaultColorSettings_ugg); }
            if (data.ColorSettings_ugb !== undefined) { setColorSettings_ugb(data.ColorSettings_ugb); } else { setColorSettings_ugb(defaultColorSettings_ugb); }
            if (data.ColorSettings_lgr !== undefined) { setColorSettings_lgr(data.ColorSettings_lgr); } else { setColorSettings_lgr(defaultColorSettings_lgr); }
            if (data.ColorSettings_lgg !== undefined) { setColorSettings_lgg(data.ColorSettings_lgg); } else { setColorSettings_lgg(defaultColorSettings_lgg); }
            if (data.ColorSettings_lgb !== undefined) { setColorSettings_lgb(data.ColorSettings_lgb); } else { setColorSettings_lgb(defaultColorSettings_lgb); }
            
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

    const UpdateColorSettings_urr = async (e:any) => {
        let newColorSettings_urr = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_urr);
        if (valid) { if (newColorSettings_urr < 0) { newColorSettings_urr = 0; } if (newColorSettings_urr > 255) { newColorSettings_urr = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_urr", valid ? newColorSettings_urr : defaultColorSettings_urr, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_urr,
            error: "Failed to save"
        });
        setColorSettings_urr(newColorSettings_urr);
    };

    const UpdateColorSettings_urg = async (e:any) => {
        let newColorSettings_urg = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_urg);
        if (valid) { if (newColorSettings_urg < 0) { newColorSettings_urg = 0; } if (newColorSettings_urg > 255) { newColorSettings_urg = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_urg", valid ? newColorSettings_urg : defaultColorSettings_urg, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_urg,
            error: "Failed to save"
        });
        setColorSettings_urg(newColorSettings_urg);
    };

    const UpdateColorSettings_urb = async (e:any) => {
        let newColorSettings_urb = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_urb);
        if (valid) { if (newColorSettings_urb < 0) { newColorSettings_urb = 0; } if (newColorSettings_urb > 255) { newColorSettings_urb = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_urb", valid ? newColorSettings_urb : defaultColorSettings_urb, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_urb,
            error: "Failed to save"
        });
        setColorSettings_urb(newColorSettings_urb);
    };

    const UpdateColorSettings_lrr = async (e:any) => {
        let newColorSettings_lrr = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_lrr);
        if (valid) { if (newColorSettings_lrr < 0) { newColorSettings_lrr = 0; } if (newColorSettings_lrr > 255) { newColorSettings_lrr = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lrr", valid ? newColorSettings_lrr : defaultColorSettings_lrr, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_lrr,
            error: "Failed to save"
        });
        setColorSettings_lrr(newColorSettings_lrr);
    };

    const UpdateColorSettings_lrg = async (e:any) => {
        let newColorSettings_lrg = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_lrg);
        if (valid) { if (newColorSettings_lrg < 0) { newColorSettings_lrg = 0; } if (newColorSettings_lrg > 255) { newColorSettings_lrg = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lrg", valid ? newColorSettings_lrg : defaultColorSettings_lrg, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_lrg,
            error: "Failed to save"
        });
        setColorSettings_lrg(newColorSettings_lrg);
    };

    const UpdateColorSettings_lrb = async (e:any) => {
        let newColorSettings_lrb = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_lrb);
        if (valid) { if (newColorSettings_lrb < 0) { newColorSettings_lrb = 0; } if (newColorSettings_lrb > 255) { newColorSettings_lrb = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lrb", valid ? newColorSettings_lrb : defaultColorSettings_lrb, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_lrb,
            error: "Failed to save"
        });
        setColorSettings_lrb(newColorSettings_lrb);
    };

    const UpdateColorSettings_uyr = async (e:any) => {
        let newColorSettings_uyr = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_uyr);
        if (valid) { if (newColorSettings_uyr < 0) { newColorSettings_uyr = 0; } if (newColorSettings_uyr > 255) { newColorSettings_uyr = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_uyr", valid ? newColorSettings_uyr : defaultColorSettings_uyr, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_uyr,
            error: "Failed to save"
        });
        setColorSettings_uyr(newColorSettings_uyr);
    };

    const UpdateColorSettings_uyg = async (e:any) => {
        let newColorSettings_uyg = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_uyg);
        if (valid) { if (newColorSettings_uyg < 0) { newColorSettings_uyg = 0; } if (newColorSettings_uyg > 255) { newColorSettings_uyg = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_uyg", valid ? newColorSettings_uyg : defaultColorSettings_uyg, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_uyg,
            error: "Failed to save"
        });
        setColorSettings_uyg(newColorSettings_uyg);
    };

    const UpdateColorSettings_uyb = async (e:any) => {
        let newColorSettings_uyb = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_uyb);
        if (valid) { if (newColorSettings_uyb < 0) { newColorSettings_uyb = 0; } if (newColorSettings_uyb > 255) { newColorSettings_uyb = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_uyb", valid ? newColorSettings_uyb : defaultColorSettings_uyb, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_uyb,
            error: "Failed to save"
        });
        setColorSettings_uyb(newColorSettings_uyb);
    };

    const UpdateColorSettings_lyr = async (e:any) => {
        let newColorSettings_lyr = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_lyr);
        if (valid) { if (newColorSettings_lyr < 0) { newColorSettings_lyr = 0; } if (newColorSettings_lyr > 255) { newColorSettings_lyr = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lyr", valid ? newColorSettings_lyr : defaultColorSettings_lyr, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_lyr,
            error: "Failed to save"
        });
        setColorSettings_lyr(newColorSettings_lyr);
    };

    const UpdateColorSettings_lyg = async (e:any) => {
        let newColorSettings_lyg = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_lyg);
        if (valid) { if (newColorSettings_lyg < 0) { newColorSettings_lyg = 0; } if (newColorSettings_lyg > 255) { newColorSettings_lyg = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lyg", valid ? newColorSettings_lyg : defaultColorSettings_lyg, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_lyg,
            error: "Failed to save"
        });
        setColorSettings_lyg(newColorSettings_lyg);
    };

    const UpdateColorSettings_lyb = async (e:any) => {
        let newColorSettings_lyb = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_lyb);
        if (valid) { if (newColorSettings_lyb < 0) { newColorSettings_lyb = 0; } if (newColorSettings_lyb > 255) { newColorSettings_lyb = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lyb", valid ? newColorSettings_lyb : defaultColorSettings_lyb, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_lyb,
            error: "Failed to save"
        });
        setColorSettings_lyb(newColorSettings_lyb);
    };

    const UpdateColorSettings_ugr = async (e:any) => {
        let newColorSettings_ugr = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_ugr);
        if (valid) { if (newColorSettings_ugr < 0) { newColorSettings_ugr = 0; } if (newColorSettings_ugr > 255) { newColorSettings_ugr = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_ugr", valid ? newColorSettings_ugr : defaultColorSettings_ugr, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_ugr,
            error: "Failed to save"
        });
        setColorSettings_ugr(newColorSettings_ugr);
    };

    const UpdateColorSettings_ugg = async (e:any) => {
        let newColorSettings_ugg = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_ugg);
        if (valid) { if (newColorSettings_ugg < 0) { newColorSettings_ugg = 0; } if (newColorSettings_ugg > 255) { newColorSettings_ugg = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_ugg", valid ? newColorSettings_ugg : defaultColorSettings_ugg, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_ugg,
            error: "Failed to save"
        });
        setColorSettings_ugg(newColorSettings_ugg);
    };

    const UpdateColorSettings_ugb = async (e:any) => {
        let newColorSettings_ugb = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_ugb);
        if (valid) { if (newColorSettings_ugb < 0) { newColorSettings_ugb = 0; } if (newColorSettings_ugb > 255) { newColorSettings_ugb = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_ugb", valid ? newColorSettings_ugb : defaultColorSettings_ugb, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_ugb,
            error: "Failed to save"
        });
        setColorSettings_ugb(newColorSettings_ugb);
    };

    const UpdateColorSettings_lgr = async (e:any) => {
        let newColorSettings_lgr = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_lgr);
        if (valid) { if (newColorSettings_lgr < 0) { newColorSettings_lgr = 0; } if (newColorSettings_lgr > 255) { newColorSettings_lgr = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lgr", valid ? newColorSettings_lgr : defaultColorSettings_lgr, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_lgr,
            error: "Failed to save"
        });
        setColorSettings_lgr(newColorSettings_lgr);
    };

    const UpdateColorSettings_lgg = async (e:any) => {
        let newColorSettings_lgg = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_lgg);
        if (valid) { if (newColorSettings_lgg < 0) { newColorSettings_lgg = 0; } if (newColorSettings_lgg > 255) { newColorSettings_lgg = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lgg", valid ? newColorSettings_lgg : defaultColorSettings_lgg, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_lgg,
            error: "Failed to save"
        });
        setColorSettings_lgg(newColorSettings_lgg);
    };

    const UpdateColorSettings_lgb = async (e:any) => {
        let newColorSettings_lgb = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newColorSettings_lgb);
        if (valid) { if (newColorSettings_lgb < 0) { newColorSettings_lgb = 0; } if (newColorSettings_lgb > 255) { newColorSettings_lgb = 255; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lgb", valid ? newColorSettings_lgb : defaultColorSettings_lgb, ip), {
            loading: "Saving...",
            success: "Set value to " + newColorSettings_lgb,
            error: "Failed to save"
        });
        setColorSettings_lgb(newColorSettings_lgb);
    };

    const UpdateFiltersContourSizeFilter = async () => {
        let newFiltersContourSizeFilter = !FiltersContourSizeFilter;
        toast.promise(SetSettingByKey("TrafficLightDetection", "FiltersContourSizeFilter", newFiltersContourSizeFilter, ip), {
            loading: "Saving...",
            success: "Set value to " + newFiltersContourSizeFilter,
            error: "Failed to save"
        });
        setFiltersContourSizeFilter(newFiltersContourSizeFilter);
    };

    const UpdateFiltersWidthHeightRatioFilter = async () => {
        let newFiltersWidthHeightRatioFilter = !FiltersWidthHeightRatioFilter;
        toast.promise(SetSettingByKey("TrafficLightDetection", "FiltersWidthHeightRatioFilter", newFiltersWidthHeightRatioFilter, ip), {
            loading: "Saving...",
            success: "Set value to " + newFiltersWidthHeightRatioFilter,
            error: "Failed to save"
        });
        setFiltersWidthHeightRatioFilter(newFiltersWidthHeightRatioFilter);
    }

    const UpdateFiltersPixelPercentageFilter = async () => {
        let newFiltersPixelPercentageFilter = !FiltersPixelPercentageFilter;
        toast.promise(SetSettingByKey("TrafficLightDetection", "FiltersPixelPercentageFilter", newFiltersPixelPercentageFilter, ip), {
            loading: "Saving...",
            success: "Set value to " + newFiltersPixelPercentageFilter,
            error: "Failed to save"
        });
        setFiltersPixelPercentageFilter(newFiltersPixelPercentageFilter);
    }

    const UpdateFiltersOtherLightsFilter = async () => {
        let newFiltersOtherLightsFilter = !FiltersOtherLightsFilter;
        toast.promise(SetSettingByKey("TrafficLightDetection", "FiltersOtherLightsFilter", newFiltersOtherLightsFilter, ip), {
            loading: "Saving...",
            success: "Set value to " + newFiltersOtherLightsFilter,
            error: "Failed to save"
        });
        setFiltersOtherLightsFilter(newFiltersOtherLightsFilter);
    }

    const UpdateFiltersMinimalTrafficLightSize = async (e:any) => {
        let newFiltersMinimalTrafficLightSize = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newFiltersMinimalTrafficLightSize);
        if (valid) { if (newFiltersMinimalTrafficLightSize < 1) { newFiltersMinimalTrafficLightSize = 1; } if (newFiltersMinimalTrafficLightSize > 999) { newFiltersMinimalTrafficLightSize = 999; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "FiltersMinimalTrafficLightSize", valid ? newFiltersMinimalTrafficLightSize : defaultFiltersMinimalTrafficLightSize, ip), {
            loading: "Saving...",
            success: "Set value to " + newFiltersMinimalTrafficLightSize,
            error: "Failed to save"
        });
        setFiltersMinimalTrafficLightSize(newFiltersMinimalTrafficLightSize);
    };

    const UpdateFiltersMaximalTrafficLightSize = async (e:any) => {
        let newFiltersMaximalTrafficLightSize = parseInt((e.target as HTMLInputElement).value);
        let valid = !isNaN(newFiltersMaximalTrafficLightSize);
        if (valid) { if (newFiltersMaximalTrafficLightSize < 1) { newFiltersMaximalTrafficLightSize = 1; } if (newFiltersMaximalTrafficLightSize > 999) { newFiltersMaximalTrafficLightSize = 999; } }
        toast.promise(SetSettingByKey("TrafficLightDetection", "FiltersMaximalTrafficLightSize", valid ? newFiltersMaximalTrafficLightSize : defaultFiltersMaximalTrafficLightSize, ip), {
            loading: "Saving...",
            success: "Set value to " + newFiltersMaximalTrafficLightSize,
            error: "Failed to save"
        });
        setFiltersMaximalTrafficLightSize(newFiltersMaximalTrafficLightSize);
    }

    const ResetColorsToDefault = async () => {
        setResetSymbol(true);
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_urr", defaultColorSettings_urr, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_urr, error: "Failed to save"}); setColorSettings_urr(defaultColorSettings_urr);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_urg", defaultColorSettings_urg, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_urg, error: "Failed to save"}); setColorSettings_urg(defaultColorSettings_urg);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_urb", defaultColorSettings_urb, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_urb, error: "Failed to save"}); setColorSettings_urb(defaultColorSettings_urb);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lrr", defaultColorSettings_lrr, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_lrr, error: "Failed to save"}); setColorSettings_lrr(defaultColorSettings_lrr);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lrg", defaultColorSettings_lrg, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_lrg, error: "Failed to save"}); setColorSettings_lrg(defaultColorSettings_lrg);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lrb", defaultColorSettings_lrb, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_lrb, error: "Failed to save"}); setColorSettings_lrb(defaultColorSettings_lrb);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_uyr", defaultColorSettings_uyr, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_uyr, error: "Failed to save"}); setColorSettings_uyr(defaultColorSettings_uyr);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_uyg", defaultColorSettings_uyg, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_uyg, error: "Failed to save"}); setColorSettings_uyg(defaultColorSettings_uyg);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_uyb", defaultColorSettings_uyb, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_uyb, error: "Failed to save"}); setColorSettings_uyb(defaultColorSettings_uyb);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lyr", defaultColorSettings_lyr, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_lyr, error: "Failed to save"}); setColorSettings_lyr(defaultColorSettings_lyr);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lyg", defaultColorSettings_lyg, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_lyg, error: "Failed to save"}); setColorSettings_lyg(defaultColorSettings_lyg);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lyb", defaultColorSettings_lyb, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_lyb, error: "Failed to save"}); setColorSettings_lyb(defaultColorSettings_lyb);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_ugr", defaultColorSettings_ugr, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_ugr, error: "Failed to save"}); setColorSettings_ugr(defaultColorSettings_ugr);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_ugg", defaultColorSettings_ugg, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_ugg, error: "Failed to save"}); setColorSettings_ugg(defaultColorSettings_ugg);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_ugb", defaultColorSettings_ugb, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_ugb, error: "Failed to save"}); setColorSettings_ugb(defaultColorSettings_ugb);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lgr", defaultColorSettings_lgr, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_lgr, error: "Failed to save"}); setColorSettings_lgr(defaultColorSettings_lgr);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lgg", defaultColorSettings_lgg, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_lgg, error: "Failed to save"}); setColorSettings_lgg(defaultColorSettings_lgg);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "ColorSettings_lgb", defaultColorSettings_lgb, ip), {loading: "Saving...", success: "Set value to " + defaultColorSettings_lgb, error: "Failed to save"}); setColorSettings_lgb(defaultColorSettings_lgb);
        setResetSymbol(false);
    };
    
    const ResetFiltersToDefault = async () => {
        setResetSymbol(true);
        toast.promise(SetSettingByKey("TrafficLightDetection", "FiltersContourSizeFilter", true, ip), {loading: "Saving...", success: "Set value to " + true, error: "Failed to save"}); setFiltersContourSizeFilter(true);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "FiltersWidthHeightRatioFilter", true, ip), {loading: "Saving...", success: "Set value to " + true, error: "Failed to save"}); setFiltersWidthHeightRatioFilter(true);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "FiltersPixelPercentageFilter", true, ip), {loading: "Saving...", success: "Set value to " + true, error: "Failed to save"}); setFiltersPixelPercentageFilter(true);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "FiltersOtherLightsFilter", true, ip), {loading: "Saving...", success: "Set value to " + true, error: "Failed to save"}); setFiltersOtherLightsFilter(true);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "FiltersMinimalTrafficLightSize", defaultFiltersMinimalTrafficLightSize, ip), {loading: "Saving...", success: "Set value to " + defaultFiltersMinimalTrafficLightSize, error: "Failed to save"}); setFiltersMinimalTrafficLightSize(defaultFiltersMinimalTrafficLightSize);
        await new Promise(resolve => setTimeout(resolve, 100));
        toast.promise(SetSettingByKey("TrafficLightDetection", "FiltersMaximalTrafficLightSize", defaultFiltersMaximalTrafficLightSize, ip), {loading: "Saving...", success: "Set value to " + defaultFiltersMaximalTrafficLightSize, error: "Failed to save"}); setFiltersMaximalTrafficLightSize(defaultFiltersMaximalTrafficLightSize);
        setResetSymbol(false);
    }

    const ResetAdvancedSettingsToDefault = async () => {
        await ResetColorsToDefault();
        setResetSymbol(true);
        await new Promise(resolve => setTimeout(resolve, 100));
        await ResetFiltersToDefault();
    }

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

            <Tabs defaultValue="general" style={{ position: 'absolute', top: '47px', left: '215px', right: '13.5pt' }}>
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

                        {AdvancedSettings !== undefined && (
                        <div className="flex flex-row" style={{ position: 'relative', top: '40px' }}>
                            <Switch id="advancedsettings" checked={AdvancedSettings} onCheckedChange={UpdateAdvancedSettings} />
                            <div className="flex flex-col items-start pl-2 text-left gap-2" style={{ position: 'relative', top: '-2px' }}>
                                <Label htmlFor="advancedsettings" className="font-bold">
                                    Advanced Settings
                                </Label>
                                <Label htmlFor="advancedsettings">
                                    If enabled, the traffic light detection uses the settings you set in the Advanced tab. (could have a bad impact on performance)
                                </Label>
                            </div>
                        </div>
                        )}
                        <div className="flex flex-row" style={{ position: 'relative', top: '32px', left: '44px' }}>
                            <Button variant={'destructive'} onClick={() => ResetAdvancedSettingsToDefault()}>
                                Reset Advanced Settings to Default
                            </Button>
                            {ResetSymbol && (
                                <div style={{ position: 'relative', top: '6px', left: '5px', filter: 'invert(1)' }} className="h-6 w-6 animate-spin rounded-full border-4 border-t-transparent border-currentColor-500"></div>
                            )}
                        </div>

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
                <TabsContent value="screencapture">

                </TabsContent>
                <TabsContent value="outputwindow">

                <div className="flex flex-col gap-4 justify-start pt-2" style={{ position: 'absolute', left: '-194px', right: '12pt' }}>

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
                <TabsContent value="trackerai">

                    <div className="flex flex-col gap-4 justify-start pt-2" style={{ position: 'absolute', left: '-194px', right: '12pt' }}>

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
                <TabsContent value="advanced">

                    <Tabs defaultValue="colorsettings" style={{ position: 'absolute', top: '42px', left: '-197px', right: '0pt' }}>
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="colorsettings">ColorSettings</TabsTrigger>
                        <TabsTrigger value="filters">Filters</TabsTrigger>
                    </TabsList>
                    <TabsContent value="colorsettings">
                        
                        <div className="flex flex-col gap-4 justify-start pt-2" style={{ position: 'absolute', left: '0px', right: '12pt' }}>

                            <div className="flex flex-row" style={{ position: 'relative', top: '20px', left: '-5px' }}>
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label>
                                        You can set your own RGB color thresholds for the detection of traffic lights here.<br />Don't forget to enable Advanced Settings in the General tab to use your own color thresholds.
                                    </Label>
                                </div>
                            </div>

                            {ColorSettings_urr !== undefined && ColorSettings_urg !== undefined && ColorSettings_urb !== undefined && (
                            <div className="flex flex-row" style={{ position: 'relative', top: '27px', left: '-5px' }}>
                                
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label style={{ position: 'relative' }}>
                                        Upper Thresholds for red traffic lights:
                                    </Label>
                                </div>

                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_urr" className="font-bold" style={{ fontSize: '15px', marginLeft: '29px' }}>
                                        R:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_urr)} id="ColorSettings_urr" value={!isNaN(ColorSettings_urr) ? ColorSettings_urr : ''}  onChangeCapture={(e) => UpdateColorSettings_urr(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                            
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_urg" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        G:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_urg)} id="ColorSettings_urg" value={!isNaN(ColorSettings_urg) ? ColorSettings_urg : ''}  onChangeCapture={(e) => UpdateColorSettings_urg(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                                
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_urb" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        B:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_urb)} id="ColorSettings_urb" value={!isNaN(ColorSettings_urb) ? ColorSettings_urb : ''}  onChangeCapture={(e) => UpdateColorSettings_urb(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                                
                            </div>
                            )}

                            {ColorSettings_lrr !== undefined && ColorSettings_lrg !== undefined && ColorSettings_lrb !== undefined && (
                            <div className="flex flex-row" style={{ position: 'relative', top: '17px', left: '-5px' }}>
                                
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label style={{ position: 'relative' }}>
                                        Lower Thresholds for red traffic lights:
                                    </Label>
                                </div>

                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_lrr" className="font-bold" style={{ fontSize: '15px', marginLeft: '30px' }}>
                                        R:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_lrr)} id="ColorSettings_lrr" value={!isNaN(ColorSettings_lrr) ? ColorSettings_lrr : ''}  onChangeCapture={(e) => UpdateColorSettings_lrr(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                            
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_lrg" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        G:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_lrg)} id="ColorSettings_lrg" value={!isNaN(ColorSettings_lrg) ? ColorSettings_lrg : ''}  onChangeCapture={(e) => UpdateColorSettings_lrg(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                                
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_lrb" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        B:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_lrb)} id="ColorSettings_lrb" value={!isNaN(ColorSettings_lrb) ? ColorSettings_lrb : ''}  onChangeCapture={(e) => UpdateColorSettings_lrb(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                            
                            </div>
                            )}

                            {ColorSettings_uyr !== undefined && ColorSettings_uyg !== undefined && ColorSettings_uyb !== undefined && (
                            <div className="flex flex-row" style={{ position: 'relative', top: '13px', left: '-5px' }}>
                                
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label style={{ position: 'relative' }}>
                                        Upper Thresholds for yellow traffic lights:
                                    </Label>
                                </div>

                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_uyr" className="font-bold" style={{ fontSize: '15px', marginLeft: '10px' }}>
                                        R:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_uyr)} id="ColorSettings_uyr" value={!isNaN(ColorSettings_uyr) ? ColorSettings_uyr : ''}  onChangeCapture={(e) => UpdateColorSettings_uyr(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                            
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_uyg" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        G:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_uyg)} id="ColorSettings_uyg" value={!isNaN(ColorSettings_uyg) ? ColorSettings_uyg : ''}  onChangeCapture={(e) => UpdateColorSettings_uyg(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                                
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_uyb" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        B:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_uyb)} id="ColorSettings_uyb" value={!isNaN(ColorSettings_uyb) ? ColorSettings_uyb : ''}  onChangeCapture={(e) => UpdateColorSettings_uyb(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                            
                            </div>
                            )}

                            {ColorSettings_lyr !== undefined && ColorSettings_lyg !== undefined && ColorSettings_lyb !== undefined && (
                            <div className="flex flex-row" style={{ position: 'relative', top: '3px', left: '-5px' }}>
                                
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label style={{ position: 'relative' }}>
                                        Lower Thresholds for yellow traffic lights:
                                    </Label>
                                </div>

                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_lyr" className="font-bold" style={{ fontSize: '15px', marginLeft: '11px' }}>
                                        R:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_lyr)} id="ColorSettings_lyr" value={!isNaN(ColorSettings_lyr) ? ColorSettings_lyr : ''}  onChangeCapture={(e) => UpdateColorSettings_lyr(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                            
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_lyg" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        G:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_lyg)} id="ColorSettings_lyg" value={!isNaN(ColorSettings_lyg) ? ColorSettings_lyg : ''}  onChangeCapture={(e) => UpdateColorSettings_lyg(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                                
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_lyb" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        B:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_lyb)} id="ColorSettings_lyb" value={!isNaN(ColorSettings_lyb) ? ColorSettings_lyb : ''}  onChangeCapture={(e) => UpdateColorSettings_lyb(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                            
                            </div>
                            )}

                            {ColorSettings_ugr !== undefined && ColorSettings_ugg !== undefined && ColorSettings_ugb !== undefined && (
                            <div className="flex flex-row" style={{ position: 'relative', top: '-1px', left: '-5px' }}>
                                
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label style={{ position: 'relative' }}>
                                        Lower Thresholds for green traffic lights:
                                    </Label>
                                </div>

                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_ugr" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        R:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_ugr)} id="ColorSettings_ugr" value={!isNaN(ColorSettings_ugr) ? ColorSettings_ugr : ''}  onChangeCapture={(e) => UpdateColorSettings_ugr(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                            
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_ugg" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        G:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_ugg)} id="ColorSettings_ugg" value={!isNaN(ColorSettings_ugg) ? ColorSettings_ugg : ''}  onChangeCapture={(e) => UpdateColorSettings_ugg(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                                
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_ugb" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        B:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_ugb)} id="ColorSettings_ugb" value={!isNaN(ColorSettings_ugb) ? ColorSettings_ugb : ''}  onChangeCapture={(e) => UpdateColorSettings_ugb(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                            
                            </div>
                            )}

                            {ColorSettings_lgr !== undefined && ColorSettings_lgg !== undefined && ColorSettings_lgb !== undefined && (
                            <div className="flex flex-row" style={{ position: 'relative', top: '-11px', left: '-5px' }}>
                                
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label style={{ position: 'relative' }}>
                                        Lower Thresholds for green traffic lights:
                                    </Label>
                                </div>

                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_lgr" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        R:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_lgr)} id="ColorSettings_lgr" value={!isNaN(ColorSettings_lgr) ? ColorSettings_lgr : ''}  onChangeCapture={(e) => UpdateColorSettings_lgr(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                            
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_lgg" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        G:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_lgg)} id="ColorSettings_lgg" value={!isNaN(ColorSettings_lgg) ? ColorSettings_lgg : ''}  onChangeCapture={(e) => UpdateColorSettings_lgg(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                                
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="ColorSettings_lgb" className="font-bold" style={{ fontSize: '15px', marginLeft: '15px' }}>
                                        B:
                                    </Label>
                                </div>
                                <Input placeholder={String(defaultColorSettings_lgb)} id="ColorSettings_lgb" value={!isNaN(ColorSettings_lgb) ? ColorSettings_lgb : ''}  onChangeCapture={(e) => UpdateColorSettings_lgb(e)} style={{ position: 'relative', top: '-5px', left: '4px', width: '50px', height: '25px', textAlign: 'center' }} />
                            
                            </div>
                            )}
                            
                            <div className="flex flex-row" style={{ position: 'relative', left: '3px', top: '-13px' }}>
                                <Button variant={"destructive"} style={{ height: '100%', textAlign: 'left' }} onClick={() => ResetColorsToDefault()}>
                                    Reset all values to default.
                                </Button>
                                {ResetSymbol && (
                                    <div style={{ position: 'relative', top: '6px', left: '5px', filter: 'invert(1)' }} className="h-6 w-6 animate-spin rounded-full border-4 border-t-transparent border-currentColor-500"></div>
                                )}
                            </div>

                        </div>

                    </TabsContent>
                    <TabsContent value="filters">

                        <div className="flex flex-col gap-4 justify-start pt-2" style={{ position: 'absolute', left: '0px', right: '12pt' }}>

                            <div className="flex flex-row" style={{ position: 'relative', top: '20px', left: '-5px' }}>
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label>
                                        You can enable or disable the filters the detection uses to detect traffic lights.<br />Don't forget to enable Advanced Settings in the General tab to use these settings.
                                    </Label>
                                </div>
                            </div>

                            {FiltersContourSizeFilter !== undefined && (
                            <div className="flex flex-row" style={{ position: 'relative', top: '30px', left: '3px' }}>
                                <Switch id="filterscontoursizefilter" checked={FiltersContourSizeFilter} onCheckedChange={UpdateFiltersContourSizeFilter} />
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="filterscontoursizefilter" className="font-bold" style={{ position: 'relative', top: '3px' }}>
                                        Contour Size Filter
                                    </Label>
                                </div>
                            </div>
                            )}

                            {FiltersWidthHeightRatioFilter !== undefined && (
                            <div className="flex flex-row" style={{ position: 'relative', top: '30px', left: '3px' }}>
                                <Switch id="filterswidthheightratiofilter" checked={FiltersWidthHeightRatioFilter} onCheckedChange={UpdateFiltersWidthHeightRatioFilter} />
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="filterswidthheightratiofilter" className="font-bold" style={{ position: 'relative', top: '3px' }}>
                                        Width/Height Ratio Filter
                                    </Label>
                                </div>
                            </div>
                            )}

                            {FiltersPixelPercentageFilter !== undefined && (
                            <div className="flex flex-row" style={{ position: 'relative', top: '30px', left: '3px' }}>
                                <Switch id="filterspixelpercentagefilter" checked={FiltersPixelPercentageFilter} onCheckedChange={UpdateFiltersPixelPercentageFilter} />
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="filterspixelpercentagefilter" className="font-bold" style={{ position: 'relative', top: '3px' }}>
                                        Pixel Percentage Filter
                                    </Label>
                                </div>
                            </div>
                            )}

                            {FiltersOtherLightsFilter !== undefined && (
                            <div className="flex flex-row" style={{ position: 'relative', top: '30px', left: '3px' }}>
                                <Switch id="filtersotherlightsfilter" checked={FiltersOtherLightsFilter} onCheckedChange={UpdateFiltersOtherLightsFilter} />
                                <div className="flex flex-col items-start pl-2 text-left gap-2">
                                    <Label htmlFor="filtersotherlightsfilter" className="font-bold" style={{ position: 'relative', top: '3px' }}>
                                        Other Lights Filter
                                    </Label>
                                </div>
                            </div>
                            )}

                            {FiltersMinimalTrafficLightSize !== undefined && (
                            <div className="flex flex-row" style={{ position: 'relative', top: '30px', left: '3px' }}>
                                <Input placeholder={String(defaultFiltersMinimalTrafficLightSize)} id="filtersminimaltrafficlightsize" value={!isNaN(FiltersMinimalTrafficLightSize) ? FiltersMinimalTrafficLightSize : ''}  onChangeCapture={(e) => UpdateFiltersMinimalTrafficLightSize(e)} style={{ width: '50px', height: '26px', textAlign: 'center' }} />
                                <div className="flex flex-col items-start pl-2 text-left gap-2" style={{ position: 'relative', top: '7px' }}>
                                    <Label htmlFor="filtersminimaltrafficlightsize" className="font-bold">
                                        Minimal Traffic Light Size
                                    </Label>   
                                </div>
                            </div>
                            )}

                            {FiltersMaximalTrafficLightSize !== undefined && (
                            <div className="flex flex-row" style={{ position: 'relative', top: '30px', left: '3px' }}>
                                <Input placeholder={String(defaultFiltersMaximalTrafficLightSize)} id="filtersmaximaltrafficlightsize" value={!isNaN(FiltersMaximalTrafficLightSize) ? FiltersMaximalTrafficLightSize : ''}  onChangeCapture={(e) => UpdateFiltersMaximalTrafficLightSize(e)} style={{ width: '50px', height: '26px', textAlign: 'center' }} />
                                <div className="flex flex-col items-start pl-2 text-left gap-2" style={{ position: 'relative', top: '7px' }}>
                                    <Label htmlFor="filtersmaximaltrafficlightsize" className="font-bold">
                                        Maximal Traffic Light Size
                                    </Label>   
                                </div>
                            </div>
                            )}
                            <div className="flex flex-row" style={{ position: 'relative', top: '42px', left: '3px' }}>
                                <Button variant={"destructive"} style={{ height: '100%', textAlign: 'left' }} onClick={() => ResetFiltersToDefault()}>
                                    Reset all values to default.
                                </Button>
                                {ResetSymbol && (
                                    <div style={{ position: 'relative', top: '6px', left: '5px', filter: 'invert(1)' }} className="h-6 w-6 animate-spin rounded-full border-4 border-t-transparent border-currentColor-500"></div>
                                )}
                            </div>

                        </div>

                    </TabsContent>
                    </Tabs>

                </TabsContent>
            </Tabs>

        </Card>
    )
}