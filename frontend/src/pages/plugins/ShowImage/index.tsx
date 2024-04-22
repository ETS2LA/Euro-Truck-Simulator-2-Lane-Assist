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

export default function Home({ ip }: { ip: string }) {

    const defaultWindowScale = "1.0";

    const {data, error, isLoading} = useSWR("ShowImage", () => GetSettingsJSON("ShowImage", ip));

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
        let newWindowScale = (e.target as HTMLInputElement).value;
        let valid = !isNaN(parseFloat(newWindowScale));
        if (valid) { if (parseFloat(newWindowScale) < 0.1) { newWindowScale = "0.1"; } if (parseFloat(newWindowScale) > 5.0) { newWindowScale = "5.0"; } }
        toast.promise(SetSettingByKey("ShowImage", "WindowScale", valid ? parseFloat(newWindowScale) : defaultWindowScale, ip), {
            loading: "Saving...",
            success: "Set value to " + parseFloat(newWindowScale),
            error: "Failed to save"
        });
        setWindowScale(newWindowScale);
    };

    return (
        <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-75px)] overflow-auto">

            <Popover>
                <PopoverTrigger asChild>
                    <CardHeader style={{ position: 'absolute', top: '43px', left: '-6px', width: '273px' }}>
                        <Button variant="secondary" style={{ fontWeight: 'bold' }}>ShowImage</Button>
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

            <Tabs defaultValue="general" style={{ position: 'absolute', top: '47px', left: '248px', right: '13.5pt' }}>
                <TabsList className="grid w-full grid-cols-1">
                    <TabsTrigger value="general">General</TabsTrigger>
                </TabsList>
                <TabsContent value="general">

                    <div style={{ position: 'absolute', left: '-227px', right: '12pt' }}>

                        <div className="flex flex-row" style={{ position: 'relative', top: '26px', left: '0px' }}>
                            <Label>
                                The settings below will only take effect when the plugin is currently running.
                            </Label>
                        </div>

                        <div className="flex flex-row" style={{ position: 'relative', top: '35px', left: '0px' }}>
                            <Button variant={'outline'} onClick={() => {setResetSymbolSaveWindowPosition(true); setTimeout(() => {setResetSymbolSaveWindowPosition(false);}, 1000); SaveWindowPosition();}}>
                                Save window position
                            </Button>
                            {ResetSymbolSaveWindowPosition && (
                                <div style={{ position: 'relative', top: '6px', left: '5px' }} className="h-6 w-6 animate-spin rounded-full border-4 border-t-transparent border-primary"></div>
                            )}
                        </div>

                        <div className="flex flex-row" style={{ position: 'relative', top: '43px', left: '0px' }}>
                            <Button variant={'outline'} onClick={() => {setResetSymbolResetWindow(true); setTimeout(() => {setResetSymbolResetWindow(false);}, 1000); ResetWindow();}}>
                                Set to window to default aspect ratio, apply scale and save position
                            </Button>
                            {ResetSymbolResetWindow && (
                                <div style={{ position: 'relative', top: '6px', left: '5px' }} className="h-6 w-6 animate-spin rounded-full border-4 border-t-transparent border-primary"></div>
                            )}
                        </div>
                        
                        {WindowScale !== undefined && (
                        <div className="flex flex-row" style={{ position: 'relative', top: '51px', left: '0px' }}>
                            <Input placeholder={String(defaultWindowScale)} id="windowscale" value={!isNaN(parseFloat(WindowScale)) ? WindowScale : ''}  onChangeCapture={(e) => UpdateWindowScale(e)} style={{ height: '26px', width: '50px', textAlign: 'center' }} />
                            <Label htmlFor="windowscale" style={{ position: 'relative', top: '6px', left: '8px' }}>
                                Window Scale
                            </Label>
                        </div>
                        )}

                    </div>

                </TabsContent>
            </Tabs>

        </Card>
    )
}