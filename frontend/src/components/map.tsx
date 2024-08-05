import { 
    MapContainer, 
    TileLayer, 
    useMap,
    Marker,
    Popup,
} from 'react-leaflet'
import { LatLngTuple, CRS, latLng, latLngBounds, Icon } from 'leaflet'
import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import { toast } from "sonner"
import { useRouter } from "next/router"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { useTheme } from "next-themes"
import { useEffect } from 'react'
import { set } from 'date-fns'
import { useRef } from 'react'
import CustomMarker from './custom_marker'

// Import leaflet css
import 'leaflet/dist/leaflet.css'

// Component to update the map's view
const UpdateMapView = ({ position }: { position: LatLngTuple }) => {
    const map = useMap(); // Access the map instance
    useEffect(() => {
        map.flyTo(position, 8, {
            animate: false,
            duration: 0
        });
    }, [position, map]);
  
    return null; // This component does not render anything
};

function game_coord_to_image(xx:number, yy:number) {
    var MAX_X = 512; //padding in ts-map 384px
    var MAX_Y = 512; //padding in ts-map 384px
    
    // Values from TileMapInfo.json
    const x1 = -94505.8047;
    const x2 = 79254.13;
    const y1 = -80093.1641;
    const y2 = 93666.77;

    const xtot = x2 - x1; // Total X length
    const ytot = y2 - y1; // Total Y length

    const xrel = (xx - x1) / xtot; // The fraction where the X is (between 0 and 1, 0 being fully left, 1 being fully right)
    const yrel = (yy - y1) / ytot; // The fraction where the Y is

    return [
        xrel * MAX_X, // Where X actually is, so multiplied the actual width
        yrel * MAX_Y // Where Y actually is, only Y is inverted
    ];
}

let socket: WebSocket | null = null;
export default function ETS2LAMap({ip} : {ip: string}) {
    const {theme, setTheme} = useTheme()
    const [connected, setConnected] = useState(false)
    const [position, setPosition] = useState<LatLngTuple>([0, 0])
    const [rotation, setRotation] = useState(0)
    const markerRef = useRef<L.Marker>(null);

    useEffect(() => {

        if (ip === "") ip = "localhost";
    
        // Initialize the WebSocket connection
        socket = new WebSocket(`ws://${ip}:37522`);
    
        // Connection opened
        socket.addEventListener("open", function (event) {
            toast.success("Map is now connected to the backend!")
            setConnected(true);
        });
    
        // Listen for messages
        socket.addEventListener("message", function (event) {
            const message = event.data;
            const indices = message.split(";");
            // Find X and Z
            let X = 0;
            let Z = 0;
            let RX = 0;
            indices.forEach((index:any) => {
                if (index.startsWith("x")) {
                    X = parseFloat(index.split("x")[1].replace(":", ""));
                } else if (index.startsWith("z")) {
                    Z = parseFloat(index.split("z")[1].replace(":", ""));
                } else if (index.startsWith("rx")) {
                    RX = parseFloat(index.split("rx")[1].replace(":", ""));
                    setRotation(RX);
                }
            });
            if(!isNaN(X) && !isNaN(Z)){
                [X, Z] = game_coord_to_image(X, Z);
                //console.log(X, Z);
                setPosition([-Z, X]);
            }
            socket.send("ok");    
        });
    
        // Setup a heartbeat
        const heartbeat = setInterval(() => {
            
        }, 2000);
    
        // Connection closed
        socket.addEventListener("close", function (event) {
            toast.error("Map disconnected from the backend!")
            console.log(`WebSocket closed: Code=${event.code}, Reason=${event.reason}`);
            setConnected(false);
        });
        
        // Error
        socket.addEventListener("error", function (event) {
            console.error("WebSocket error observed:", event);
        });
        
        // Cleanup function to close the socket and clear the heartbeat interval when the component unmounts
        return () => {
            socket.close();
            clearInterval(heartbeat); // Clear the heartbeat interval
            // Clear the socket reference
            socket = null;
        };
    }, []); // Empty dependency array to run the effect only once on mount

    useEffect(() => {
        // Check if the marker exists
        if (markerRef.current) {
            const markerElement = markerRef.current.getElement(); // Get the DOM element of the marker
            if (markerElement && rotation && rotation !== 0) {
                markerElement.style.transformOrigin = 'center'; // Ensure rotation is around the center
                markerElement.style.transform += ` rotate(${-rotation}deg)`; // Apply rotation
            }
        }
    }, [rotation]); // This effect depends on the rotation state    

    let corner1 = latLng(0, 165168)
    let corner2 = latLng(148512, 0)
    let bounds = latLngBounds(corner1, corner2)

    return (
        <MapContainer center={position} zoom={7} style={{height: "100%", width: "100%", backgroundColor: "#1b1b1b"}} zoomControl={false} bounds={bounds} crs={CRS.Simple}>
            <TileLayer
                attribution='&copy; ETS2LA Team'
                url="https://raw.githubusercontent.com/ETS2LA/tilemap/master/tilemap/Tiles/{z}/{x}/{y}.png"
                minNativeZoom={2}
                maxNativeZoom={8}
                zIndex={-999}
                tileSize={512}
            />
            <CustomMarker position={position} rotation={rotation} />
            <UpdateMapView position={position} />
        </MapContainer>
    )
}