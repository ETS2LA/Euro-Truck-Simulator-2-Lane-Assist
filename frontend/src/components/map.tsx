import { 
    MapContainer, 
    TileLayer, 
    useMap,
    Marker,
    Popup,
} from 'react-leaflet'
import { LatLngTuple, CRS } from 'leaflet'
import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import { toast } from "sonner"
import { useRouter } from "next/router"
import { useState } from "react"
import { Button } from "@/components/ui/button"
// Import leaflet css
import 'leaflet/dist/leaflet.css'

export default function ETS2LAMap({ip} : {ip: string}) {
    const position: LatLngTuple = [0, 0]
    return (
        <MapContainer center={position} zoom={8} style={{height: "100%", width: "100%"}}>
            <TileLayer
                url="https://ets2.online/map/ets2map_150/{z}/{x}/{y}.png"
                minZoom={2}
                maxZoom={8}
                zIndex={-999}
            />
        </MapContainer>
    )
}