import { Progress } from "@/components/ui/progress";
import Loader from "../loader";

export function ProgressState({ state, plugin_name, state_progress_percent }: { state: string, plugin_name: string, state_progress_percent: number })
{
    return (
        <div className="h-min w-[354px] rounded-lg text-sm flex flex-col gap-2 font-semibold">
            <div className="flex justify-between text-start items-center">
                <p style={{whiteSpace: "pre-wrap"}}>{state}</p>
                <p className="text-[10px] text-muted-foreground p-0">{plugin_name}</p>
            </div>
            <Progress value={state_progress_percent} className="pb-0" />
        </div>
    )
}

export function IndeterminateState({ state, plugin_name }: { state: string, plugin_name: string })
{
    return (
        <div className="h-min w-[354px] rounded-lg text-sm flex flex-col gap-2 font-semibold">
            <div className="flex justify-between text-start items-center">
                <div className="flex text-center content-center items-center gap-2">
                    <Loader className={""} /> 
                    <p style={{whiteSpace: "pre-wrap"}}>{state}</p>
                </div>
                <p className="text-[10px] text-muted-foreground p-0">{plugin_name}</p>
            </div>
        </div>
    )
}