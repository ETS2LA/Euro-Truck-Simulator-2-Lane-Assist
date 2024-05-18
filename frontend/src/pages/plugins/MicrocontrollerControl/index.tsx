import { Card} from "@/components/ui/card"
import { Button } from "@/components/ui/button";
import { GetSettingsJSON } from "@/pages/settings"
import { PluginFunctionCall } from "@/pages/backend";
import { toast } from "sonner";
import useSWR from "swr";

export default function MicrocontrollerControl({ ip }: { ip: string }) {
    const {data, error, isLoading} = useSWR("MicrocontrollerControl", () => GetSettingsJSON("MicrocontrollerControl", ip));

    if (isLoading) return <p>Loading...</p>
    if (error) return <p className='p-4'>Lost connection to server - {error.message}</p>

    function PrintHi() {
        toast.promise(PluginFunctionCall("MicrocontrollerControl", "printhi", [], {}, ip), {
            loading: "Printing, please wait...",
            success: "Printed message successfully",
            error: "Failed to print message"
        });
    }

    return (
        <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-72px)] overflow-auto">
            <Button onClick={() => PrintHi()}>Print "Hi"</Button>
        </Card>
    )
}