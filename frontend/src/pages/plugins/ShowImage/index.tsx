import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { GetSettingsJSON, SetSettingByKey, GetSettingByKey } from "@/pages/settings"
import useSWR from "swr";
import {toast} from "sonner";
import {useEffect, useState} from "react";

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
        <Card className="w-[150px]">
            <CardHeader>
                <CardTitle>Show Image</CardTitle>
                <CardDescription>Settings</CardDescription>
            </CardHeader>
            <CardContent>
                {enabled !== undefined && (
                    <div className="flex space-x-2">
                        <Checkbox checked={enabled} onCheckedChange={handleCheckboxChange}/>
                        <p>Enabled</p>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}