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
import { use, useState } from "react"
import { Button } from "@/components/ui/button"
import { useTheme } from "next-themes"
import { useEffect } from 'react'
import { set } from 'date-fns'
import { useRef } from 'react'
import CustomMarker from './custom_marker'
import pako from 'pako';
import maplibregl from 'maplibre-gl';

// Import maplibre css
import 'maplibre-gl/dist/maplibre-gl.css';
// Import leaflet css
// import 'leaflet/dist/leaflet.css'

function game_coord_to_coordinates(xx: number, yy: number): [number, number] {
    // Values from TileMapInfo.json - the bounds of your game world in game coordinates
    const x1 = -94621.8047;
    const x2 = 79370.13;
    const y1 = -80209.1641;
    const y2 = 93782.77;

    // The target lat/lon bounds that the game world corresponds to
    const latMin = -90; // Replace with the correct bounds for your map region
    const latMax = 90;  // Replace with the correct bounds for your map region
    const lonMin = -180;         // Replace with the correct bounds for your map region
    const lonMax = 180;          // Replace with the correct bounds for your map region

    // Convert the game coordinates to relative positions
    let xrel = (xx - x1) / (x2 - x1);  // Relative X position
    let yrel = (yy - y1) / (y2 - y1);  // Relative Y position

    // Map the relative positions to the latitude and longitude bounds
    const lon = lonMin + xrel * (lonMax - lonMin);
    const lat = latMin + yrel * (latMax - latMin);

    return [lon, -(lat)]; // Return the calculated coordinates
}

// Component to update the map's view
const UpdateMapView = ({ position, map }: { position: any, map: any }) => {
    if (!map) return null; // If the map is not ready yet, do not render anything

    position = game_coord_to_coordinates(position[0], position[1]); // Convert the game coordinates to normal map coordinates (lat, lng)
    //console.log("Position:", position);
    useEffect(() => {
        map.flyTo({ center: position, zoom: 7.9 });
    }, [position, map]);
  
    return null; // This component does not render anything
};

function game_coord_to_image(xx:number, yy:number) {
    var MAX_X = 512; //padding in ts-map 384px
    var MAX_Y = 512; //padding in ts-map 384px
    
    // Values from TileMapInfo.json
    const x1 = -94621.8047;
    const x2 = 79370.13;
    const y1 = -80209.1641;
    const y2 = 93782.77;

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
    const [position, setPosition] = useState([0, 0])
    const [rotation, setRotation] = useState(0)
    const markerRef = useRef<L.Marker>(null);
    const mapContainer = useRef<any>(null);
    const map = useRef<any>(null);
    const zoom = 7;

    useEffect(() => {
        if (map.current) return; // stops map from intializing more than once
        console.log("Initializing map")
        map.current = new maplibregl.Map({
          container: mapContainer.current,
          style: ip === "localhost" ? 'http://localhost:37520/api/map/style' : `http://${ip}:37520/api/map/style`,
          center: [0, 0],
          zoom: zoom
        });
        console.log("Map initialized")
    }, [zoom]);

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
            try {
                if (socket)
                    socket.send("ok");
                let data = event.data;
                if (data instanceof Blob) {
                    // Use the Blob.arrayBuffer() method to read the Blob's content
                    const arrayBuffer = data.arrayBuffer().then(buffer => {
                        data = new Uint8Array(buffer);
                        //console.log("Received message:", data);
                        const message = pako.ungzip(data, { windowBits: 28, to: 'string' });
                        const indices = message.split(";");
                        // Find X and Z
                        let X = 0;
                        let Z = 0;
                        let RX = 0;
                        indices.forEach((index: any) => {
                            if (index.startsWith("x")) {
                                X = parseFloat(index.split("x")[1].replace(":", ""));
                            } else if (index.startsWith("z")) {
                                Z = parseFloat(index.split("z")[1].replace(":", ""));
                            } else if (index.startsWith("rx")) {
                                RX = parseFloat(index.split("rx")[1].replace(":", ""));
                                setRotation(RX);
                            }
                        });
                        if (!isNaN(X) && !isNaN(Z)) {
                            //[X, Z] = game_coord_to_image(X, Z);
                            setPosition([X, Z]);
                        }
                    });
                }
                else{
                    //console.log("Received message:", data);
                    const message = pako.ungzip(data, { windowBits: 28, to: 'string' });
                    const indices = message.split(";");
                    // Find X and Z
                    let X = 0;
                    let Z = 0;
                    let RX = 0;
                    indices.forEach((index: any) => {
                        if (index.startsWith("x")) {
                            X = parseFloat(index.split("x")[1].replace(":", ""));
                        } else if (index.startsWith("z")) {
                            Z = parseFloat(index.split("z")[1].replace(":", ""));
                        } else if (index.startsWith("rx")) {
                            RX = parseFloat(index.split("rx")[1].replace(":", ""));
                            setRotation(RX);
                        }
                    });
                    if (!isNaN(X) && !isNaN(Z)) {
                        //[X, Z] = game_coord_to_image(X, Z);
                        setPosition([X, Z]);
                    }
                }

            } catch (error) {
                console.error("Decompression error:", error);
            }
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
            toast.error("Map disconnected from the backend!", {
                description: "" + event
            })
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
    // <CustomMarker position={position} rotation={rotation} />
    // <MapContainer center={position} zoom={7} style={{height: "100%", width: "100%", backgroundColor: "#1b1b1b"}} zoomControl={false} bounds={bounds} crs={CRS.Simple}>
    //    <TileLayer
    //    attribution='&copy; ETS2LA Team'
    //    url="https://raw.githubusercontent.com/ETS2LA/tilemap/master/tilemap/Tiles/{z}/{x}/{y}.png"
    //    minNativeZoom={2}
    //    maxNativeZoom={8}
    //    zIndex={-999}
    //    tileSize={512}
    //    />
    //    <CustomMarker position={position} rotation={rotation} />
    //    <UpdateMapView position={position} />
    //</MapContainer>
    return (
        <div className='w-full h-full'>
            <div ref={mapContainer} className='w-full h-full' style={{backgroundColor: "#1b1b1b"}}>
                <UpdateMapView position={position} map={map.current} />
            </div>
            <div className='border absolute w-2 h-2 top-[calc(50vh-0.5rem)] left-[calc(35vw-1.5rem)] border-white' />
        </div>
    )
}