import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function Home() {
    return (
        <Card className="w-[150px]">
            <CardHeader>
                <CardTitle>Show Image</CardTitle>
                <CardDescription>Settings</CardDescription>
            </CardHeader>
            <CardContent>
                <Button>Click me!</Button>
            </CardContent>
        </Card>
    )
}