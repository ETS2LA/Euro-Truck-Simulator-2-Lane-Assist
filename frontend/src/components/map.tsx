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
import pako from 'pako';
import { MdForkRight, MdStraight  } from "react-icons/md";
import { json } from 'stream/consumers'
import { Card, CardContent } from './ui/card'
import "leaflet-rotate"

// Import leaflet css
import 'leaflet/dist/leaflet.css'

// Component to update the map's view
const UpdateMapView = ({ position, speed, rx }: { position: LatLngTuple, speed: number, rx: number }) => {
    const map = useMap(); // Access the map instance
    useEffect(() => {
        let zoom = 8;
        map.flyTo(position, zoom, {
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
    const [position, setPosition] = useState<LatLngTuple>([0, 0])
    const [speed, setSpeed] = useState(0)
    const [rotation, setRotation] = useState(0)
    const [instructions, setInstructions] = useState<string[]>([])
    const markerRef = useRef<L.Marker>(null);
    const [tilt, setTilt] = useState(0)
    const [yOffset, setyOffset] = useState(-90)

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
                        const message = pako.ungzip(data, { windowBits: 28, to: 'string' });
                        const indices = message.split(";");
                        // Find X and Z
                        let X = 0;
                        let Z = 0;
                        let RX = 0;
                        let Speed = 0;
                        indices.forEach((index: any) => {
                            if (index.startsWith("x")) {
                                X = parseFloat(index.split("x")[1].replace(":", ""));
                            } else if (index.startsWith("z")) {
                                Z = parseFloat(index.split("z")[1].replace(":", ""));
                            } else if (index.startsWith("rx")) {
                                RX = parseFloat(index.split("rx")[1].replace(":", ""));
                                setRotation(RX);
                            } else if (index.startsWith("speed") && !index.startsWith("speedLimit")) {
                                Speed = parseFloat(index.split("speed")[1].replace(":", ""));
                                setSpeed(Speed);
                            } else if (index.startsWith("instruct")) {
                                let instruct = index.split("instruct")[1].replace(":", "");
                                instruct = JSON.parse(instruct);
                                if (instruct.length > 1) {
                                    setInstructions(instruct);
                                }
                            }
                        });
                        if (!isNaN(X) && !isNaN(Z)) {
                            [X, Z] = game_coord_to_image(X, Z);
                            setPosition([-Z, X]);
                        }
                    });
                }
                else{
                    const message = pako.ungzip(data, { windowBits: 28, to: 'string' });
                    const indices = message.split(";");
                    // Find X and Z
                    let X = 0;
                    let Z = 0;
                    let RX = 0;
                    let Speed = 0;
                    indices.forEach((index: any) => {
                        if (index.startsWith("x")) {
                            X = parseFloat(index.split("x")[1].replace(":", ""));
                        } else if (index.startsWith("z")) {
                            Z = parseFloat(index.split("z")[1].replace(":", ""));
                        } else if (index.startsWith("rx")) {
                            RX = parseFloat(index.split("rx")[1].replace(":", ""));
                            setRotation(RX);
                        } else if (index.startsWith("speed") && !index.startsWith("speedLimit")) {
                            Speed = parseFloat(index.split("speed")[1].replace(":", ""));
                            setSpeed(Speed);
                        } else if (index.startsWith("instruct")) {
                            let instruct = index.split("instruct")[1].replace(":", "");
                            instruct = JSON.parse(instruct);
                            setInstructions(instruct);
                        }
                    });
                    if (!isNaN(X) && !isNaN(Z)) {
                        [X, Z] = game_coord_to_image(X, Z);
                        setPosition([-Z, X]);
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
    
    useEffect(() => {
        if (speed*3.6 > 5) {
            // From 0 tilt at 10kph to 55 tilt at 80kph
            setTilt(Math.min((speed*3.6 - 5) / 80 * 55, 55));
            // From -90 offset at 10kph to -60 offset at 80kph
            setyOffset(Math.min((speed*3.6 - 5) / 60 * 10 - 90, -60));
        }
        else {
            setyOffset(-90);
            setTilt(0);
        }
    })

    let corner1 = latLng(0, 165168)
    let corner2 = latLng(148512, 0)
    let bounds = latLngBounds(corner1, corner2)
    // <CustomMarker position={position} rotation={rotation} />
    return (
        <div style={{height: "100%", width: "100%", position: "relative", perspective: "800px"}}>
            {instructions[0] && Number.isFinite(instructions[instructions.length - 1].totalDistance) &&
                <Card style={{position: "absolute", top: "58px", right: "12px", zIndex: 1000}} className="bg-transparent border-none backdrop-blur-xl backdrop-brightness-50 h-24 w-48">
                    <CardContent className='p-0 h-full pb-1'>
                        <div className='flex flex-col h-full gap-0 p-0 font-customSans justify-center'>
                            <div className='flex items-center h-full pr-6 gap-0'>
                                {instructions[0].distance < 10 &&
                                    <MdForkRight className='w-16 h-16 justify-center' />
                                    ||
                                    <MdStraight className='w-16 h-16 justify-center' />
                                }
                                <div className="flex flex-col gap-0 text-left pl-0 overflow-hidden">
                                    {instructions[0].distance > 10 &&
                                        <p className='font-bold'>In {Math.round(instructions[0].distance/100)/10} km</p>
                                    }
                                    <h3>{instructions[0].direction && "Prefab"}</h3>
                                    <p className='text-[10px] pt-1'>{Math.round(instructions[instructions.length - 1].totalDistance/100)/10} km left</p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            }
            <div style={{height: "100%", width: "100%", backgroundColor: "#1b1b1b", position: "absolute", transformStyle: "preserve-3d", transform: `rotateX(${tilt}deg) translate(-33vw, ${yOffset}vh)`}}>
                <MapContainer center={position} zoom={7} style={{height: "300%", width: "200%", backgroundColor: "#1b1b1b", transformStyle: "preserve-3d", WebkitTransformStyle: "preserve-3d"}} zoomControl={false} bounds={bounds} crs={CRS.Simple} rotate={true} zoomSnap={0}>
                    <TileLayer
                        attribution='&copy; ETS2LA Team'
                        url="https://raw.githubusercontent.com/ETS2LA/tilemap/master/tilemap/Tiles/{z}/{x}/{y}.png"
                        minNativeZoom={2}
                        maxNativeZoom={8}
                        zIndex={-999}
                        tileSize={512}
                    />
                    <CustomMarker position={position} rotation={rotation} />
                    <UpdateMapView position={position} speed={speed} rx={rotation} />
                </MapContainer>
            </div>
        </div>
    )
}