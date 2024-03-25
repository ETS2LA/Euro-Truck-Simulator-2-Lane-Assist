import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"

export default function TrafficLightDetection() {
    return (
        <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-75px)] overflow-auto">
            <div style={{ position: 'absolute', top: '75px', left: '25px' }}>
                <Switch />
                <label style={{ position: 'absolute', top: '-2px', left: '35px', width: '100px' }}>its a switch</label>
            </div>
            <div style={{ position: 'absolute', top: '90px', left: '25px' }}>
                <Button>Button</Button>
            </div>
            <div style={{ position: 'absolute', top: '130px', left: '25px' }}>
                <Input placeholder="Input" />
            </div>
        </Card>
    )
}