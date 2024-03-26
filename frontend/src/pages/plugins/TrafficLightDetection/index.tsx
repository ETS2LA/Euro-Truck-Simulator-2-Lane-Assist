import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"

export default function TrafficLightDetection() {
    return (
        <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-75px)] overflow-auto">

            <div style={{ position: 'absolute', top: '75px', left: '25px' }}>
                <Button>Button</Button>
            </div>

            <div style={{ position: 'absolute', top: '100px', left: '25px' }}>
                <Switch />
                <label style={{ position: 'absolute', top: '-2px', left: '35px', width: '100px' }}>its a switch</label>
            </div>

            <div style={{ position: 'absolute', top: '130px', left: '25px', width: '200px' }}>
                <Input placeholder="Input" />
            </div>

            <div style={{ position: 'absolute', top: '180px', left: '25px', width: '200px' }}>
                <Slider defaultValue={[50]} min={0} max={100} step={1} />
            </div>

            <div style={{ position: 'absolute', top: '200px', left: '25px', width: '200px' }}>
                <Select>
                    <SelectTrigger>
                        <SelectValue placeholder="Select a YOLO model" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectGroup>
                        <SelectLabel>Select a YOLO model</SelectLabel>
                        <SelectItem value="apple">YOLOv5n</SelectItem>
                        <SelectItem value="banana">YOLOv5s</SelectItem>
                        <SelectItem value="grape">YOLOv5m</SelectItem>
                        <SelectItem value="orange">YOLOv5l</SelectItem>
                        <SelectItem value="pineapple">YOLOv5x</SelectItem>
                        </SelectGroup>
                    </SelectContent>
                </Select>
            </div>

        </Card>
    )
}