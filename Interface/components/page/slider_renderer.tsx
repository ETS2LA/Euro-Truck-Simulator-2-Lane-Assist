import { SetSettingByKey } from "@/apis/settings";
import { Slider as ShadCNSlider } from "@/components/ui/slider";
import { Component } from "react";
import { toast } from "sonner";

export interface SliderProps {
    pluginSettings: Record<string, any>;
	data: { name: string, description: string, setting_key: string, setting_default: number, setting_min: number, setting_max: number, setting_step: number, classname: string, requires_restart: boolean }
	default: number;
	toast: any;
    plugin: string;
    setNeedsRestart: (needsRestart: boolean) => void;
    mutate: (key: string) => void;
    translate: (key: string) => string;
}

interface SliderState {
    curSliderValue: number;
    tempSliderValue: number | null;
}

export default class Slider extends Component<SliderProps, SliderState> {
    constructor(props: SliderProps) {
        super(props);
        const value = props.pluginSettings[props.data.setting_key] ? parseFloat(props.pluginSettings[props.data.setting_key]) : props.default;
        this.state = {
            curSliderValue: value,
            tempSliderValue: null
        };
    }

    handleValueChange = (value: number[]) => {
        this.setState({ tempSliderValue: value[0] });
    }

    handleValueCommit = (value: number[]) => {
        const { plugin, data, setNeedsRestart, mutate, translate } = this.props;
        SetSettingByKey(plugin, data.setting_key, value[0]).then(() => {
            if (data.requires_restart)
                setNeedsRestart(true);
            mutate(plugin + "settings");
            toast.success(translate("frontend.settings.number.updated"), {
                duration: 500
            });
            this.setState({ curSliderValue: value[0], tempSliderValue: null });
        });
    }

    render() {
        const { data, translate, pluginSettings } = this.props;
        const { curSliderValue, tempSliderValue } = this.state;
        const value = pluginSettings[data.setting_key] ? parseFloat(pluginSettings[data.setting_key]) : curSliderValue;
        const step = data.setting_step || 1;

        return (
            <div className="flex flex-col gap-2 w-full">
                <h4>{translate(data.name)}  —  {value}{tempSliderValue !== null ? tempSliderValue != value ? ` → ${tempSliderValue}` : `` : ``}</h4>
                <ShadCNSlider min={data.setting_min} max={data.setting_max} defaultValue={[value]} step={step} onValueChange={this.handleValueChange} onValueCommit={this.handleValueCommit} />
                <p className="text-xs text-muted-foreground">{translate(data.description)}</p>
            </div>
        );
    }
}