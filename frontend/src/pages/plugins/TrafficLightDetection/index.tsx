import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"

export default function TrafficLightDetection() {
    return (
        <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-75px)] overflow-auto">
            <div className="flex space-x-3 w-10">
                <Switch />
                <p className="w-[100px]">Something...</p>
            </div>
            <Button variant="default" className="w-[100px]">Something...</Button>
            <Input className="w-[100px]" placeholder="Something..." />
        </Card>
    )
}