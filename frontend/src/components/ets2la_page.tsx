import { Skeleton } from "@/components/ui/skeleton"
import useSWR, { mutate } from "swr"
import { GetPlugins, PluginFunctionCall } from "@/pages/backend"
import { Separator } from "./ui/separator"
import { set } from "date-fns"
import { Input } from "./ui/input"
import { GetSettingsJSON, SetSettingByKey, SetSettingByKeys } from "@/pages/settingsServer"
import { DisablePlugin, EnablePlugin } from "@/pages/backend"
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select"
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@/components/ui/tooltip"
import { Toggle } from "@/components/ui/toggle"
import { Switch } from "./ui/switch"
import { Button } from "./ui/button"
import { toast } from "sonner"
import { useEffect } from "react"
import { Slider } from "./ui/slider"
import { useState } from "react"
import { translate } from "@/pages/translation"
import React, { Component } from 'react';
import { SkeletonItem } from "./skeleton_item"
import {
	Check,
	X
} from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "./ui/progress"

interface SliderComponentProps {
    pluginSettings: Record<string, any>;
    data: {
        key: string;
        name: string;
        description: string;
		requires_restart?: boolean;
		type: string;
        options: {
            min: number;
            max: number;
            step?: number;
            suffix?: string;
        };
    };
    plugin: string;
    ip: string;
    setNeedsRestart: (needsRestart: boolean) => void;
    mutate: (key: string) => void;
    translate: (key: string) => string;
}

interface SliderComponentState {
    curSliderValue: number;
    tempSliderValue: number | null;
}

class SliderComponent extends Component<SliderComponentProps, SliderComponentState> {
    constructor(props: SliderComponentProps) {
        super(props);
        const value = props.pluginSettings[props.data.key] ? parseFloat(props.pluginSettings[props.data.key]) : 0;
        this.state = {
            curSliderValue: value,
            tempSliderValue: null
        };
    }

    handleValueChange = (value: number[]) => {
        this.setState({ tempSliderValue: value[0] });
    }

    handleValueCommit = (value: number[]) => {
        const { plugin, data, ip, setNeedsRestart, mutate, translate } = this.props;
        SetSettingByKey(plugin, data.key, value[0], ip).then(() => {
            if (data.requires_restart)
                setNeedsRestart(true);
            mutate("settings");
            toast.success(translate("frontend.settings.number.updated"), {
                duration: 500
            });
            this.setState({ curSliderValue: value[0], tempSliderValue: null });
        });
    }

    render() {
        const { data, translate, pluginSettings } = this.props;
        const { curSliderValue, tempSliderValue } = this.state;
        const value = pluginSettings[data.key] ? parseFloat(pluginSettings[data.key]) : 0;
        const step = data.options.step || 1;
        const suffix = data.options.suffix || "";

        return (
            <div className="flex flex-col gap-2">
                <h4>{translate(data.name)}  —  {value}{suffix}{tempSliderValue !== null ? tempSliderValue != value ? ` → ${tempSliderValue}${suffix}` : `` : ``}</h4>
                <Slider min={data.options.min} max={data.options.max} defaultValue={[value]} step={step} onValueChange={this.handleValueChange} onValueCommit={this.handleValueCommit} />
                <p className="text-xs text-muted-foreground">{translate(data.description)}</p>
            </div>
        );
    }
}

export function ETS2LAPage({ ip, data, plugin, enabled }: { ip: string, data: any, plugin: string, enabled?: boolean }) {
	const { data: pluginSettings, error: pluginSettingsError, isLoading: pluginSettingsLoading } = useSWR("settings", () => GetSettingsJSON(plugin, ip))
	const [needsRestart, setNeedsRestart] = useState(false)

	// Update the settings when the plugin changes
	useEffect(() => {
		setNeedsRestart(false)
		mutate("settings")
	}, [plugin])

	useEffect(() => {
		try{
			let interval = null;
			if(enabled){
				const item = data[0]
				interval = setInterval(() => {
					mutate("plugin_ui_plugins")
				}, item["refresh_rate"] * 1000)
			}
			else{
				interval = setInterval(() => {
					mutate("plugin_ui_plugins")
				}, 2000)
			}
			return () => clearInterval(interval)
		}
		catch{}
    }, [data, plugin, enabled]);

	if(enabled == undefined){
		enabled = true
	}

	if (pluginSettingsLoading) {
		return <Skeleton />
	}

	if (pluginSettingsError) {
		return <p className="text-xs text-muted-foreground">{translate("frontend.settings.error", pluginSettingsError)}</p>
	}

	if (!data || !pluginSettings) {
		return <p className="text-xs text-muted-foreground">{translate("frontend.settings.backend_no_data")}</p>
	}

	const settings = data

	const TitleRenderer = (data:string) => {
		return <h3 className="font-medium">{translate(data)}</h3>
	}

	const DescriptionRenderer = (data:string) => {
		return <p className="text-sm text-muted-foreground">{translate(data)}</p>
	}

	const LabelRenderer = (data:string) => {
		return <p>{translate(data)}</p>
	}

	const SeparatorRenderer = () => {
		return <>
			<Separator />
		</>
	}

	const SpaceRenderer = (data:number) => {
		if (data) {
			return <div>
				{Array(data).fill(0).map((_, index) => (
					<div key={index} className="h-1"></div>
				))}
			</div>
		}
		return <div className="h-4"></div>
	}

	const InputRenderer = (data:any) => {
		if(pluginSettings[data.key] == undefined){
			if(data.options.default != undefined){
				console.log("Setting default value for", data.key)
				pluginSettings[data.key] = data.options.default
			}
			else{
				pluginSettings[data.key] = data.options.type
			}
		}

		if (data.options.type == "string") {
			return <div className="flex flex-col gap-2 w-full">
				<h4>{translate(data.name)}</h4>
				<Input type="text" placeholder={pluginSettings[data.key]} onChange={(e) => {
					SetSettingByKey(plugin, data.key, e.target.value, ip).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
						mutate("settings")
						toast.success(translate("frontend.settings.string.updated"), {
							duration: 500
						})
					})
				}} />
				<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
			</div>
		}

		if (data.options.type == "number") {
			return (
				<div className="flex flex-col gap-2 w-full">
					<h4>{translate(data.name)}</h4>	
					<Input type="number" placeholder={pluginSettings[data.key]} className="font-customMono" onChange={(e) => {
						SetSettingByKey(plugin, data.key, parseFloat(e.target.value), ip).then(() => {
							if (data.requires_restart)
								setNeedsRestart(true)
							mutate("settings");
							toast.success(translate("frontend.settings.number.updated"), {
								duration: 500
							});
						});
					}} />
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
			)
		}
	}

	const SliderRenderer = (data:any) => {
		return ( // Add return statement here
			<SliderComponent
				pluginSettings={pluginSettings}
				data={data}
				plugin={plugin}
				ip={ip}
				setNeedsRestart={setNeedsRestart}
				mutate={mutate}
				toast={toast}
				translate={translate}
			/>
		);
	}

	const SwitchRenderer = (data:any) => {
		return <div className={"flex justify-between p-0 items-center" + GetBorderClassname(data.options.border)}>
				<div className="flex flex-col gap-1 pr-12">
					<h4 className="font-semibold">{translate(data.name)}</h4>
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
				<Switch checked={pluginSettings[data.key] && pluginSettings[data.key] || false} onCheckedChange={(bool) => {
					SetSettingByKey(plugin, data.key, bool, ip).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
						mutate("settings")
						toast.success(translate("frontend.settings.boolean.updated"), {
							duration: 500
						})
					})
				}} />
			</div>
	}

	const ToggleRenderer = (data:any) => {
		return <div className="flex gap-4 w-full items-center">
				<Toggle pressed={pluginSettings[data.key] && pluginSettings[data.key] || false} onPressedChange={(bool) => {
					SetSettingByKey(plugin, data.key, bool, ip).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
						mutate("settings")
						toast.success(translate("frontend.settings.boolean.updated"), {
							duration: 500
						})
					})
				}} className="w-8 h-8 p-[7px] data-[state=on]:bg-background data-[state=on]:hover:bg-white/10 " variant={"outline"}>
					{pluginSettings[data.key] && pluginSettings[data.key] ? <Check /> : <X />}
				</Toggle>
				{data.options.separator && <Separator orientation="vertical" />}
				<div>
					<h4>{translate(data.name)}</h4>
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
			</div>
	}

	const ButtonRenderer = (data:any) => {
		return <div className={"flex justify-between p-4 items-center" + GetBorderClassname(data.options.border)}>
				<div className="flex flex-col gap-1 pr-12">
					<h4 className="font-semibold">{translate(data.title)}</h4>
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
				<Button variant={"outline"} onClick={() => {
					PluginFunctionCall(plugin, data.options.target, [], {}, ip).then(() => {
						toast.success(translate(data.success), {
							duration: 500
						})
					})
				}} className="min-w-32">{translate(data.text)}</Button>
			</div>
	}

	const ProgressBarRenderer = (data:any) => {
		const value = data.value;
		const min = data.min;
		const max = data.max;
		const progress = (value - min) / (max - min) * 100;
		return <div className="flex flex-col gap-2 w-full">
			<Progress value={progress} />
			<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
		</div>
	}

	const EnabledLock = () => {
		return <div className="flex justify-between p-4 items-center border rounded-md backdrop-blur-md gap-10">
			<div>
				<h4>Please enable the plugin.</h4>
				<p className="text-xs text-muted-foreground">This plugin is disabled. Enable it to access the rest of this plugin's settings.</p>
			</div>
			<Button variant={"outline"} onClick={() => {
				EnablePlugin(plugin, ip).then(() => {
					toast.success("Plugin enabled", {
						duration: 500
					})
				})
			}} className="min-w-32">Enable {plugin}</Button>
		</div>
	}

	const GetBorderClassname = (border:boolean) => {
		if(border){
			return " p-4 border rounded-md"
		}
		return "p-4"
	}

	const PageRenderer = (data: any) => {
		if (!Array.isArray(data)) {
			data = [data]
		}
		const result = [];
		for (const item of data) {
			const key = Object.keys(item)[0];
			const key_data = item[key];

			if (key == "enabled_lock") {
				if(!enabled){
					result.push(
						<div className="w-full relative">
							<div className="absolute inset-0 flex items-center justify-center z-10 w-full">
								<EnabledLock />
							</div>
							<div className="p-3 opacity-50 blur-sm">
								{PageRenderer(key_data.components)}
							</div>
						</div>
					);
				}
				else{
					result.push(PageRenderer(key_data.components))
				}
			}

			// Page looks
			if(key == "title"){
				result.push(TitleRenderer(key_data.text))
			}
			if(key == "description"){
				result.push(DescriptionRenderer(key_data.text))
			}
			if (key == "label") {
				result.push(LabelRenderer(key_data.text))
			}
			if (key == "separator") {
				result.push(SeparatorRenderer())
			}
			if (key == "space") {
				result.push(SpaceRenderer(key_data.amount))
			}
			if (key == "group") {
				const direction = key_data.direction
				if(direction == "horizontal"){
					result.push(<div className={"flex gap-4 w-full rounded-md" + GetBorderClassname(key_data.border)}>
						{PageRenderer(key_data.components)}
					</div>)
				}
				else{
					result.push(<div className={"flex flex-col gap-4 w-full rounded-md" + GetBorderClassname(key_data.border)}>
						{PageRenderer(key_data.components)}
					</div>)
				}
			}
			if (key == "tabview") {
				result.push(<Tabs className="w-full" defaultValue={key_data.components[0].tab.name}>
					<TabsList className="w-full bg-transparent border">
						{key_data.components.map((tab:any, index:number) => (
							<TabsTrigger key={index} value={tab.tab.name}>{translate(tab.tab.name)}</TabsTrigger>
						))}
					</TabsList>
					{key_data.components.map((tab:any, index:number) => (
						<TabsContent key={index} value={tab.tab.name} className="w-full rounded-md p-2 flex gap-6 flex-col">
							{PageRenderer(tab)}
						</TabsContent>
					))}
				</Tabs>)
			}
			if (key == "tab"){
				result.push(PageRenderer(key_data.components))
			}

			// Live Data
			if (key == "progress_bar") {
				result.push(ProgressBarRenderer(key_data))
			}

			// Functions
			if (key == "button") {
				result.push(ButtonRenderer(key_data))
			}

			// Options
			if (key == "input") {
				result.push(InputRenderer(key_data))
			}
			if (key == "slider") {
				result.push(SliderRenderer(key_data))
			}
			if (key == "switch") {
				result.push(SwitchRenderer(key_data))
			}
			if (key == "toggle") {
				result.push(ToggleRenderer(key_data))
			}
		};

		return result;
	};

	console.log(settings)

	return (
		<TooltipProvider delayDuration={0}>
			<div className="text-left flex flex-col w-full max-w-[calc(60vw-64px)] gap-6 relative">
				{PageRenderer(settings)}
				<div className="h-12"></div>
			</div>
		</TooltipProvider>
	)
}
