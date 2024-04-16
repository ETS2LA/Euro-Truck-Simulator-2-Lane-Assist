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

export default function Home({ ip }: { ip: string }) {
    const {data, error, isLoading} = useSWR("ShowImage", () => GetSettingsJSON("ShowImage", ip));
    const [enabled, setEnabled] = useState<boolean | undefined>(undefined);

    useEffect(() => {
        if (data) {
            if (data.enabled !== undefined) {
                setEnabled(data.enabled);
            } else {
                setEnabled(false);
            }
        }
    }, [data]);

    if (isLoading) return <p>Loading...</p>
    if (error) return <p className='p-4'>Lost connection to server - {error.message}</p>

    const handleCheckboxChange = async () => {
        const newValue = !enabled;
        await toast.promise(SetSettingByKey("ShowImage", "enabled", newValue, ip), {
            loading: "Saving...",
            success: "Set value to " + newValue,
            error: "Failed to save"
        });
        setEnabled(newValue);
    };

    return (
        <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-75px)] overflow-auto">

            <Popover>
                <PopoverTrigger asChild>
                    <CardHeader style={{ position: 'absolute', top: '43px', left: '-6px', width: '273px' }}>
                        <Button variant="secondary" style={{ fontWeight: 'bold' }}>ShowImage</Button>
                    </CardHeader>
                </PopoverTrigger>
                <PopoverContent style={{ position: 'relative', top: '-23px', left: '0px', height: '50px', width: '225px' }}>
                    <Label style={{ position: 'absolute', top: '15px', left: '10px', fontSize: '16px' }}>Created by Tumppi066</Label>
                    <Avatar style={{ position: 'absolute', top: '8px', right: '10px', width: '32px', height: '32px' }}>
                        <AvatarImage src="https://avatars.githubusercontent.com/u/83072683?v=4"/>
                    </Avatar>
                </PopoverContent>
            </Popover>

            <Tabs defaultValue="general" style={{ position: 'absolute', top: '47px', left: '248px', right: '13.5pt' }}>
                <TabsList className="grid w-full grid-cols-1">
                    <TabsTrigger value="general">General</TabsTrigger>
                </TabsList>
                <TabsContent value="general">


                    {/* code */}


                </TabsContent>
            </Tabs>

        </Card>
    )
}