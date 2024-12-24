"use client"

import RenderPage from "@/components/page/render_page";

export default function Updater() {
    return (
        <div className="w-full h-full overflow-auto">
            <RenderPage url="/about" className="pl-20 max-w-full pr-20 w-full" />
        </div>
    )
}