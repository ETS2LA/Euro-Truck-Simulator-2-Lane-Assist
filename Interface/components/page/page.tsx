// Utils
// @ts-expect-error
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
// @ts-expect-error
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import React, { Component, useEffect, useState } from "react"
import { Check, X } from "lucide-react"
import Markdown from "react-markdown"
import useSWR, { mutate } from "swr"

// UI
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { TooltipProvider, Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Slider from "@/components/page/slider_renderer"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { Progress } from "@/components/ui/progress"
import { Toggle } from "@/components/ui/toggle"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"

// ETS2LA
import { GetSettingsJSON, SetSettingByKey } from "@/apis/settings"
import { PluginFunctionCall, EnablePlugin } from "@/apis/backend"
import { translate } from "@/apis/translation"

interface LabelProps {
	text: string;
	classname: string;
	url: string;
}

interface MarkdownProps {
	text: string;
}

interface ButtonProps {
	text: string;
	classname: string;
	variant: "default" | "link" | "outline" | "destructive" | "secondary" | "ghost";
	target: string;
	args: any[];
}

interface SpaceProps {
	height: number;
}

interface InputProps {
	name: string;
	input_type: "string" | "number" | "password";
	setting_key: string;
	setting_default: any;
	classname: string;
	description: string;
	requires_restart: boolean;
}

// Separator has no props

interface SwitchProps {
	name: string;
	setting_key: string;
	setting_default: boolean;
	classname: string;
	description: string;
	requires_restart: boolean;
}

interface ToggleProps {
	name: string;
	setting_key: string;
	setting_default: boolean;
	variant: 'default' | 'outline';
	classname: string;
	description: string;
	requires_restart: boolean;
}

interface SliderProps {
	name: string;
	setting_key: string;
	setting_default: number;
	setting_min: number;
	setting_max: number;
	setting_step: number;
	classname: string;
	description: string;
	requires_restart: boolean;
}

interface SelectorProps {
	name: string;
	setting_key: string;
	setting_default: any;
	setting_options: any[];
	description: string;
	requires_restart: boolean;
}

interface TabViewProps {
	components: any[];
}

interface TabProps {
	components: any[];
}

interface GroupProps {
	classname: string;
	components: any[];
}

interface TooltipProps {
	text: string;
	classname: string;
	components: any[];
}

interface PaddingProps {
	padding: number
	components: any[]
}

interface GeistProps {
	components: any[]
}

// Form is not implimented
// Refresh rate is not implimented

interface ProgressBarProps {
	value: number;
	min: number;
	max: number;
	classname: string;
	description: string;
	id: number
}

interface EnabledLockProps {
	components: any[]
}

export function ETS2LAPage({ data, plugin, enabled, className }: { data: any, plugin: string, enabled?: boolean, className?: string }) {
	const { data: pluginSettings, error: pluginSettingsError, isLoading: pluginSettingsLoading } = useSWR(plugin + "settings", () => GetSettingsJSON(plugin))
	const [needsRestart, setNeedsRestart] = useState(false)

	// Update the settings when the plugin changes
	useEffect(() => {
		setNeedsRestart(false)
		mutate(plugin + "settings")
	}, [plugin])

	useEffect(() => {
		try{
			let interval = null;
			if(enabled){
				const item = data[0]
				if(item["refresh_rate"] == undefined){
					item["refresh_rate"] = 2
				}
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

	const LabelRenderer = (data: LabelProps) => {
		if (data.url === "") {
			return <p className={data.classname}>{translate(data.text)}</p>
		} else {
			return <a href={data.url} className={data.classname} target="_blank">{translate(data.text)}</a>
		}
	}

	function MarkdownRenderer(data: MarkdownProps, no_padding?: boolean) {
	  return (
		<Markdown
		  components={{
			// @ts-expect-error
			code({node, inline, className, children, ...props}) {
				const hasLineBreaks = String(children).includes('\n');
				const match = /language-(\w+)/.exec(className || '');
				const lang = match ? match[1] : 'json';
			  
				// For inline code (no line breaks)
				if (!hasLineBreaks) {
					return (
					<code
						className="rounded-md bg-zinc-800 p-1 font-geist-mono text-xs"
						{...props}
					>
						{children}
					</code>
					);
				}
			
				// For code blocks (has line breaks)
				return (
				  <SyntaxHighlighter
					language={lang}
					style={vscDarkPlus}
					customStyle={{
					  margin: (no_padding ? '0 0' : '1rem 0'),
					  padding: '1rem',
					  borderRadius: '0.5rem',
					  fontSize: '0.75rem',
					  fontFamily: 'var(--font-geist-mono)'
					}}
				  >
					{String(children).replace(/\n$/, '')}
				  </SyntaxHighlighter>
				);
			}
		}}>
		  {data.text}
		</Markdown>
	  );
	}

	const ButtonRenderer = (data: ButtonProps) => {
		return (
			<Button variant={data.variant} onClick={() => {
				PluginFunctionCall(plugin, data.target, data.args, {}).then(() => {
					toast.success(translate("Success"), {
						duration: 500
					})
				})
			}} className={`w-full ${data.classname}`}>{translate(data.text)}</Button>
		)
	}

	const SpaceRenderer = (data: SpaceProps) => {
		if (data.height) {
			return <div style={{ height: data.height + "px" }}></div>
		}
		return <div className="h-4"></div>
	}

	const InputRenderer = (data: InputProps) => {
		if(pluginSettings[data.setting_key] == undefined){
			if(data.setting_default != undefined) {
				console.log("Setting default value for", data.setting_key)
				pluginSettings[data.setting_key] = data.setting_default
			} else {
				pluginSettings[data.setting_key] = data.input_type
			}
		}

		if (data.input_type == "string" || data.input_type == "password") {
			const type = data.input_type == "password" ? "password" : "text"
			let placeholder = ""
			if (type == "password") {
				placeholder = "•".repeat(pluginSettings[data.setting_key].length)
			}
			else {
				placeholder = pluginSettings[data.setting_key]
			}
			return ( 
				<div className="flex flex-col gap-2 w-full">
					<h4>{translate(data.name)}</h4>
					<Input type={type} placeholder={placeholder} className={data.classname} onChange={(e) => {
						SetSettingByKey(plugin, data.setting_key, e.target.value).then(() => {
							if (data.requires_restart)
								setNeedsRestart(true)
							mutate(plugin + "settings")
							toast.success(translate("frontend.settings.string.updated"), {
								duration: 500
							})
						})
					}} />
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
			)
		}

		if (data.input_type == "number") {
			return (
				<div className="flex flex-col gap-2 w-full">
					<h4>{translate(data.name)}</h4>	
					<Input type="number" placeholder={pluginSettings[data.setting_key]} className={`font-customMono ${data.classname}`} onChange={(e) => {
						SetSettingByKey(plugin, data.setting_key, parseFloat(e.target.value)).then(() => {
							if (data.requires_restart)
								setNeedsRestart(true)
							mutate(plugin + "settings");
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

	const SeparatorRenderer = (data : {}) => {
		return <>
			<Separator />
		</>
	}

	const SwitchRenderer = (data: SwitchProps) => {
		const checked = pluginSettings[data.setting_key]
		if (checked == null || typeof checked != "boolean") {
			if (data.setting_default != undefined) {
				console.log("Setting default value for", data.setting_key)
				pluginSettings[data.setting_key] = data.setting_default
			}
			else {
				pluginSettings[data.setting_key] = false
			}
		}
		return (
			<div className={"flex justify-between p-0 items-center"}>
				<div className="flex flex-col gap-1 pr-12">
					<h4 className="font-semibold">{translate(data.name)}</h4>
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
				<Switch checked={checked} className={data.classname} onCheckedChange={(bool) => {
					SetSettingByKey(plugin, data.setting_key, bool).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
						mutate(plugin + "settings")
						toast.success(translate("frontend.settings.boolean.updated"), {
							duration: 500
						})
					})
				}} />
			</div>
		)
	}

	const ToggleRenderer = (data: ToggleProps) => {
		return (
			<div className="flex gap-4 w-full items-center">
				<Toggle pressed={pluginSettings[data.setting_key] && pluginSettings[data.setting_key] || false} onPressedChange={(bool) => {
					SetSettingByKey(plugin, data.setting_key, bool).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
						mutate(plugin + "settings")
						toast.success(translate("frontend.settings.boolean.updated"), {
							duration: 500
						})
					})
				}} className={`w-8 h-8 p-[7px] data-[state=on]:bg-background data-[state=on]:hover:bg-white/10 ${data.classname}`} variant={data.variant}>
					{pluginSettings[data.setting_key] && pluginSettings[data.setting_key] ? <Check /> : <X />}
				</Toggle>
				<Separator orientation="vertical" />
				<div>
					<h4>{translate(data.name)}</h4>
					<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
				</div>
			</div>
		)
	}

	const SliderRenderer = (data: SliderProps) => {
		return <Slider pluginSettings={pluginSettings} data={data} plugin={plugin} setNeedsRestart={setNeedsRestart} mutate={mutate} toast={toast} translate={translate} default={data.setting_default}/>
	}

	const SelectorRenderer = (data: SelectorProps) => {
		if (pluginSettings[data.setting_key] == undefined) {
			if (data.setting_default != undefined) {
				console.log("Setting default value for", data.setting_key)
				pluginSettings[data.setting_key] = data.setting_default
			}
			else {
				pluginSettings[data.setting_key] = data.setting_options[0]
			}
		}
		return (
			<div className="flex flex-col gap-2">
				<h4>{translate(data.name)}</h4>
				<Select defaultValue={pluginSettings[data.setting_key]} onValueChange={(value) => {
					SetSettingByKey(plugin, data.setting_key, value).then(() => {
						if (data.requires_restart)
							setNeedsRestart(true)
						mutate(plugin + "settings")
						toast.success(translate("frontend.settings.enum.updated"), {
							duration: 500
						})
					})
				}} >
					<SelectTrigger>
						<SelectValue placeholder={pluginSettings[data.setting_key]}>{pluginSettings[data.setting_key]}</SelectValue>
					</SelectTrigger>
					<SelectContent className="bg-background font-geist">
						{data.setting_options.map((value:any) => (
							<SelectItem key={value} value={value}>{value}</SelectItem>
						))}
					</SelectContent>
				</Select>
				<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
			</div>
		)
	}

	const TabViewRenderer = (data: TabViewProps) => {
		return (
			<Tabs className="w-full" defaultValue={data.components[0].tab.name}>
				<TabsList className="w-full bg-transparent border">
					{data.components.map((tab:any, index:number) => (
						<TabsTrigger key={index} value={tab.tab.name}>{translate(tab.tab.name)}</TabsTrigger>
					))}
				</TabsList>
				{data.components.map((tab:any, index:number) => (
					<TabsContent key={index} value={tab.tab.name} className="w-full rounded-md p-2 flex gap-6 flex-col data-[state=inactive]:hidden">
						{PageRenderer(tab)}
					</TabsContent>
				))}
			</Tabs>
		)
	}

	// @ts-ignore
	const TabRenderer = (data : TabProps) => {
		return PageRenderer(data.components)
	}

	const GroupRenderer = (data: GroupProps) => {
		return (
			<div className={data.classname}>
				{PageRenderer(data.components)}
			</div>
		)
	}

	const TooltipRenderer = (data: TooltipProps) => {
		const md_data = {"text": data.text}
		return (
			<Tooltip>
				<TooltipTrigger>
					{PageRenderer(data.components)}
				</TooltipTrigger>
				<TooltipContent className={data.classname} style={{whiteSpace: "pre-wrap"}}>
					{MarkdownRenderer(md_data, true)}
				</TooltipContent>
			</Tooltip>
		)
	}

	const PaddingRenderer = (data: PaddingProps) => {
		return (
			<div style={{padding: data.padding}}>
				{PageRenderer(data.components)}
			</div>
		)
	}

	const GeistRenderer = (data: GeistProps) => {
		return (
			<div className="font-geist">
				{PageRenderer(data.components)}
			</div>
		)
	}

	const ProgressBarRenderer = (data: ProgressBarProps) => {
		const value = data.value;
		const min = data.min;
		const max = data.max;
		const progress = (value - min) / (max - min) * 100;
		return (
			<div className="flex flex-col gap-2 w-full">
				<Progress value={progress} />
				<p className="text-xs text-muted-foreground">{translate(data.description)}</p>
			</div>
		)
	}

	// @ts-ignore
	const EnabledLockRenderer = (data: EnabledLockProps) => {
		if(!enabled){
			return (
				<div className="w-full relative">
					<div className="absolute inset-0 flex items-center justify-center z-10 w-full">
						<div className="flex justify-between p-4 items-center border rounded-md backdrop-blur-md gap-10">
							<div>
								<h4>Please enable the plugin.</h4>
								<p className="text-xs text-muted-foreground">{"This plugin is disabled. Enable it to access the rest of this plugin's settings."}</p>
							</div>
							<Button variant={"outline"} onClick={() => {
								EnablePlugin(plugin).then(() => {
									toast.success("Plugin enabled", {
										duration: 500
									})
								})
							}} className="min-w-32">Enable {plugin}</Button>
						</div>
					</div>
					<div className="p-3 opacity-50 blur-sm">
						{PageRenderer(data.components)}
					</div>
				</div>
			);
		}
		else{
			return PageRenderer(data.components)
		}
	}

    // @ts-ignore
	const PageRenderer = (data: any) => {
		if (!Array.isArray(data)) {
			data = [data]
		}
		const result = [];
		for (const item of data) {
			const key = Object.keys(item)[0];
			const key_data = item[key];

			if (key === "label") {
				result.push(LabelRenderer(key_data));
			} else if (key === "markdown") {
				result.push(MarkdownRenderer(key_data));
			} else if (key === "button") {
				result.push(ButtonRenderer(key_data));
			} else if (key === "separator") {
				result.push(SeparatorRenderer(key_data));
			} else if (key === "space") {
				result.push(SpaceRenderer(key_data));
			} else if (key === "input") {
				result.push(InputRenderer(key_data));
			} else if (key === "switch") {
				result.push(SwitchRenderer(key_data));
			} else if (key === "toggle") {
				result.push(ToggleRenderer(key_data));
			} else if (key === "slider") {
				result.push(SliderRenderer(key_data));
			} else if (key === "selector") {
				result.push(SelectorRenderer(key_data));
			} else if (key === "tabview") {
				result.push(TabViewRenderer(key_data));
			} else if (key === "tab") {
				result.push(TabRenderer(key_data));
			} else if (key === "group") {
				result.push(GroupRenderer(key_data));
			} else if (key === "tooltip") {
				result.push(TooltipRenderer(key_data));
			} else if (key === "padding") {
				result.push(PaddingRenderer(key_data));
			} else if (key === "geist") {
				result.push(GeistRenderer(key_data));
			} else if (key === "progressbar") {
				result.push(ProgressBarRenderer(key_data));
			} else if (key === "enabled_lock") {
				result.push(EnabledLockRenderer(key_data));
			} else {
				console.log("Unknown key", key)
			}
		};

		return result;
	};

	return (
		<TooltipProvider delayDuration={0}>
			<div className={"text-left flex flex-col w-full max-w-[calc(60vw-64px)] gap-6 relative " + className}>
				{PageRenderer(settings)}
				<div className="h-12"></div>
			</div>
		</TooltipProvider>
	)
}
