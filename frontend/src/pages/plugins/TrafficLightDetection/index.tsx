import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Checkbox } from "@/components/ui/checkbox"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"

export default function TrafficLightDetection() {
    return (
        <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-75px)] overflow-auto">

            <div style={{ position: 'absolute', top: '75px', left: '25px' }}>
                <Button>Primary Button</Button>
                <Button variant='secondary' style={{ marginLeft: '10px' }}>Secondary Button</Button>
                <Button variant='destructive' style={{ marginLeft: '10px' }}>Destructive Button</Button>
                <Button variant="outline" style={{ marginLeft: '10px' }}>Outline Button</Button>
                <Button variant="ghost" style={{ marginLeft: '10px' }}>Ghost Button</Button>
                <Button variant="link">Link Button</Button>
            </div>

            <div style={{ position: 'absolute', top: '102px', left: '25px' }}>
                <Switch id="switch" />
                <Label htmlFor="switch" style={{ position: 'relative', top: '-2px', left: '5px', width: '800px', textAlign: 'left' }}>This is a label which is connected to the switch. (you can click on the label to change the switch state)</Label>
            </div>

            <div style={{ position: 'absolute', top: '130px', left: '25px' }}>
                <Checkbox id="checkbox" />
                <Label htmlFor="checkbox" style={{ position: 'relative', top: '-2px', left: '5px', width: '800px', textAlign: 'left' }}>This is a label which is connected to the checkbox. (you can click on the label to change the checkbox state)</Label>
            </div>

            <div style={{ position: 'absolute', top: '161px', left: '25px', width: '200px' }}>
                <RadioGroup defaultValue="option1">
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value="option1" id="r1"/>
                        <Label htmlFor="r1">Option 1</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value="option2" id="r2"/>
                        <Label htmlFor="r2">Option 2</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value="option3" id="r3"/>
                        <Label htmlFor="r3">Option 3</Label>
                    </div>
                </RadioGroup>
            </div>

            <div style={{ position: 'absolute', top: '238px', left: '25px', width: '200px' }}>
                <Slider defaultValue={[50]} min={0} max={100} step={1} />
            </div>

            <div style={{ position: 'absolute', top: '255px', left: '25px', width: '200px' }}>
                <Input placeholder="Input" />
            </div>

            <div style={{ position: 'absolute', top: '300px', left: '25px', width: '200px' }}>
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