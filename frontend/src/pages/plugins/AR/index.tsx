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

import { GetSettingsJSON, SetSettingByKey } from "@/pages/settingsServer"
import { useEffect, useState } from "react";
import { toast } from "sonner";
import useSWR from "swr";

export default function AR({ ip }: { ip: string }) {

    const defaultFOV = "80";

    const {data, error, isLoading} = useSWR("AR", () => GetSettingsJSON("AR", ip));

    const [FOV, setFOV] = useState<string | undefined>(undefined);

    useEffect(() => {
        if (data) {

            if (data.FOV !== undefined) { setFOV(data.FOV); } else { setFOV(defaultFOV); }

        }
    }, [data]);

    if (isLoading) return <p>Loading...</p>
    if (error) return <p className='p-4'>Lost connection to server - {error.message}</p>

    const UpdateFOV = async (e:any) => {
        let newFOV = String(e).replace(/\./g, ".");
        if (newFOV.includes(".") && newFOV.substring(newFOV.indexOf(".") + 1).length > 1) { return; }
        let valid = !isNaN(parseFloat(newFOV));
        if (valid) { if (parseFloat(newFOV) < 10) { newFOV = "10"; } if (parseFloat(newFOV) > 180) { newFOV = "180"; } }
        toast.promise(SetSettingByKey("AR", "FOV", valid ? parseFloat(newFOV) : parseFloat(defaultFOV), ip), {
            loading: "Saving...",
            success: "Set value to " + parseFloat(newFOV),
            error: "Failed to save"
        });
        setFOV(newFOV);
    };

    return (
        <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto">

            <Popover>
                <PopoverTrigger asChild>
                    <CardHeader style={{ position: 'absolute', top: '43px', left: '-6px', width: '273px' }}>
                        <Button variant="secondary" style={{ fontWeight: 'bold' }}>AR (Augmented Reality)</Button>
                    </CardHeader>
                </PopoverTrigger>
                <PopoverContent style={{ position: 'relative', top: '-23px', left: '0px', height: '131px', width: '225px' }}>
                    <Label style={{ position: 'absolute', top: '12px', left: '10px', fontSize: '16px' }}>Created by</Label>
                    <Separator style={{ position: 'absolute', top: '40px', left: "0px" }}/>

                    <Label style={{ position: 'absolute', top: '57px', left: '46px', fontSize: '16px' }}>Glas42</Label>
                    <Avatar style={{ position: 'absolute', top: '49px', left: '8px', width: '32px', height: '32px' }}>
                        <AvatarImage src="https://avatars.githubusercontent.com/u/145870870?v=4"/>
                    </Avatar>
                    
                    <Label style={{ position: 'absolute', top: '97px', left: '46px', fontSize: '16px' }}>Tumppi066</Label>
                    <Avatar style={{ position: 'absolute', top: '89px', left: '8px', width: '32px', height: '32px' }}>
                        <AvatarImage src="https://avatars.githubusercontent.com/u/83072683?v=4"/>
                    </Avatar>
                </PopoverContent>
            </Popover>

            <Tabs defaultValue="general" style={{ position: 'absolute', top: '47px', left: '248px', right: '13.5pt' }}>
                <TabsList className="grid w-full grid-cols-1">
                    <TabsTrigger value="general">General</TabsTrigger>
                </TabsList>
                <TabsContent value="general">

                    <div className="flex flex-col gap-4 justify-start pt-2" style={{ position: 'absolute', left: '-227px', right: '2.5pt' }}>

                        {FOV !== undefined && (
                        <div>
                            <div className="flex flex-row items-center text-left gap-2 pt-2">
                            <Input placeholder={String(defaultFOV)} id="fov" type="number" step="1" value={!isNaN(parseFloat(FOV)) ? FOV : ''}  onChangeCapture={(e) => UpdateFOV((e.target as HTMLInputElement).value)} style={{ width: '75px' }}/>
                                <Label htmlFor="fov">
                                    <span className="font-bold">FOV</span><br />
                                    You need to set the field of view for the AR. You can find the FOV in the game by pressing F4, then selecting "Adjust seats".
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