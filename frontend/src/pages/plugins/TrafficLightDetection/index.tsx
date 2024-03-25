import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function TrafficLightDetection() {
    return (
        <div>
            <div style={{ position: 'absolute', top: '100px', left: '25px', transform: 'translate(0px, -50%)' }}>
                <Switch />
            </div>
            <div style={{ position: 'absolute', top: '100px', left: '75px', transform: 'translate(0px, -50%)' }}>
                <label htmlFor="traffic-light-detection-switch">Something...</label>
            </div>
            <div style={{ position: 'absolute', top: '150px', left: '25px', transform: 'translate(0px, -50%)' }}>
                <Button variant="default">Something...</Button>
            </div>
            <div style={{ position: 'absolute', top: '200px', left: '25px', transform: 'translate(0px, -50%)' }}>
                <Input placeholder="Something..." />
            </div>
        </div>
    )
}