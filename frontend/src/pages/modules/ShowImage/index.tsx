"use client"

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
import { useSearchParams } from "next/navigation";


import { GetSettingsJSON, SetSettingByKey, SetSettingByKeys } from "@/pages/settings"
import { useEffect, useState } from "react";
import { toast } from "sonner";
import useSWR from "swr";

export default function ShowImage({ ip, plugin }: { ip: string, plugin: string}) {

    if (plugin == null) {
        return <div>
            Please provide a plugin name in the URL.
        </div>
    }

    const defaultWindowScale = "1.0";

    const {data, error, isLoading} = useSWR(plugin, () => GetSettingsJSON(plugin, ip));

    const [ResetSymbolSaveWindowPosition, setResetSymbolSaveWindowPosition] = useState<boolean>(false);
    const [ResetSymbolResetWindow, setResetSymbolResetWindow] = useState<boolean>(false);
    const [WindowScale, setWindowScale] = useState<string | undefined>(undefined);

    useEffect(() => {
        if (data) {

            if (data.WindowScale !== undefined) { setWindowScale(data.WindowScale); } else { setWindowScale(defaultWindowScale); }

        }
    }, [data]);

    if (isLoading) return <p>Loading...</p>
    if (error) return <p className='p-4'>Lost connection to server - {error.message}</p>

    const SaveWindowPosition = async () => {
        
    };

    const ResetWindow = async () => {
        
    };

    const UpdateWindowScale = async (e:any) => {
        let newWindowScale = String(e).replace(/\./g, ".");
        if (newWindowScale.includes(".") && newWindowScale.substring(newWindowScale.indexOf(".") + 1).length > 1) { return; }
        let valid = !isNaN(parseFloat(newWindowScale));
        if (valid) { if (parseFloat(newWindowScale) < 0.1) { newWindowScale = "0.1"; } if (parseFloat(newWindowScale) > 5) { newWindowScale = "5"; } }
        toast.promise(SetSettingByKeys(plugin, ["ShowImage", "WindowScale"], valid ? parseFloat(newWindowScale) : defaultWindowScale, ip), {
            loading: "Saving...",
            success: "Set value to " + parseFloat(newWindowScale),
            error: "Failed to save"
        });
        setWindowScale(newWindowScale);
    };

    return (
        <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-129px)] overflow-auto" style={{ position: 'relative', left: '-3px', top: '-3px' }}>
            
            <Popover>
                <PopoverTrigger asChild>
                    <CardHeader style={{ position: 'absolute', top: '-19px', left: '-19px', width: '273px' }}>
                        <Button variant="secondary">ShowImage<p className="pl-2 text-xs text-stone-500">{plugin}</p></Button>
                    </CardHeader>
                </PopoverTrigger>
                <PopoverContent style={{ position: 'relative', top: '-23px', left: '0px', height: '91px', width: '225px' }}>
                    <Label style={{ position: 'absolute', top: '12px', left: '10px', fontSize: '16px' }}>Created by</Label>
                    <Separator style={{ position: 'absolute', top: '40px', left: "0px" }}/>
                    <Label style={{ position: 'absolute', top: '57px', left: '46px', fontSize: '16px' }}>Tumppi066</Label>
                    <Avatar style={{ position: 'absolute', top: '49px', left: '8px', width: '32px', height: '32px' }}>
                        <AvatarImage src="https://avatars.githubusercontent.com/u/83072683?v=4"/>
                    </Avatar>
                </PopoverContent>
            </Popover>

            <Tabs defaultValue="general" style={{ position: 'absolute', top: '-15px', left: '235px', right: '3pt' }}>
                <TabsList className="grid w-full grid-cols-1">
                    <TabsTrigger value="general">General</TabsTrigger>
                </TabsList>
                <TabsContent value="general">
                    
                    <div className="flex flex-col gap-3 justify-start pt-2" style={{ position: 'absolute', top: '50px', left: '-227px', right: '2.5pt', textAlign: 'left' }}>

                        <div className="flex flex-row">
                            <Label>
                                The settings below will only take effect when the plugin is currently running.
                            </Label>
                        </div>

                        <div className="flex flex-row">
                            <Button variant={'outline'} onClick={() => {setResetSymbolSaveWindowPosition(true); setTimeout(() => {setResetSymbolSaveWindowPosition(false);}, 1000); SaveWindowPosition();}}>
                                Save window position
                            </Button>
                            {ResetSymbolSaveWindowPosition && (
                                <div className="h-6 w-6 animate-spin rounded-full border-4 border-t-transparent border-primary"></div>
                            )}
                        </div>

                        <div className="flex flex-row">
                            <Button variant={'outline'} onClick={() => {setResetSymbolResetWindow(true); setTimeout(() => {setResetSymbolResetWindow(false);}, 1000); ResetWindow();}}>
                                Set to window to default aspect ratio, apply scale and save position
                            </Button>
                            {ResetSymbolResetWindow && (
                                <div className="h-6 w-6 animate-spin rounded-full border-4 border-t-transparent border-primary"></div>
                            )}
                        </div>
                        
                        {WindowScale !== undefined && (
                        <div>
                            <div className="flex flex-row items-center text-left gap-2">
                            <Input placeholder={String(defaultWindowScale)} id="windowscale" type="number" step="0.1" value={!isNaN(parseFloat(WindowScale)) ? WindowScale : ''}  onChangeCapture={(e) => UpdateWindowScale((e.target as HTMLInputElement).value)} style={{ width: '75px' }}/>
                                <Label htmlFor="windowscale">
                                    <span className="font-bold">Window Scale</span><br />
                                    Sets the scale of the window to the given value.
                                </Label>
                            </div>
                        </div>
                        )}

                    </div>

                </TabsContent>
            </Tabs>

        </Card>
    )
}