import { Card } from "@/components/ui/card"

export default function Home() {
    return (
        <Card className="flex flex-col content-center text-center pt-10 space-y-5 pb-0 h-[calc(100vh-75px)] overflow-auto">
            <p className="text-stone-600">You can open the command palette with the escape key.</p>
        </Card>
    )
}