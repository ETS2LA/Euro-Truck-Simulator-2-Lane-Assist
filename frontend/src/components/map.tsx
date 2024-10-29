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
import * as maptalks from "maptalks";

// Import maptalks styles
import "maptalks/dist/maptalks.css";

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

const baseOptions = {
    attribution: false,
    zoom: 8,
    minZoom: 0,
    maxZoom: 8,
    control: false,
    center: [0,0],
    spatialReference: {
        projection: "identity",
        resolutions: [1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128, 1/256, 1/512],
    }
};

const layers = {
    base: {
        urlTemplate: "https://raw.githubusercontent.com/ETS2LA/tilemap/master/tilemap/Tiles/{z}/{x}/{y}.png",
        tileSize: 512,
        debug: false,
        renderer: "gl",
        spacialReference: {
            projection: "identity",
            resolutions: [1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128, 1/256, 1/512],
        },
    },
};

let socket: WebSocket | null = null;
export default function ETS2LAMap({ip} : {ip: string}) {
    const {theme, setTheme} = useTheme()
    const [connected, setConnected] = useState(false)
    const [position, setPosition] = useState([0, 0])
    const [speed, setSpeed] = useState(0)
    const [rotation, setRotation] = useState(0)
    const [instructions, setInstructions] = useState<string[]>([])
    const markerRef = useRef<L.Marker>(null);
    const [tilt, setTilt] = useState(0)
    const [yOffset, setyOffset] = useState(-90)
    const [map, setMap] = useState<maptalks.Map | null>(null);
    const [mapLayer, setMapLayer] = useState<maptalks.TileLayer | null>(null);
    const [overlayLayer, setOverlayLayer] = useState<maptalks.VectorLayer | null>(null);
    const [marker, setMarker] = useState<maptalks.Marker | null>(null);

    useEffect(() => {
        if(map) return;
        try {
            console.log("Creating map");
            const newMap = new maptalks.Map('map', {
                ...baseOptions
            });
            setMap(newMap);
            let tileLayer = new maptalks.TileLayer('base', layers.base);
            setMapLayer(tileLayer);
            newMap.addLayer(tileLayer);
        }
        catch (e) {
            console.error("Error creating map", e);
        }
    }, []);

    useEffect(() => {
        if (!map) return;
        if (marker) {
            marker.setCoordinates(position);
        } else {
            const newMarker = new maptalks.Marker(position, {
                symbol: {
                    markerType: 'ellipse',
                    markerWidth: 10,
                    markerHeight: 10,
                    markerFill: '#f70',
                    markerLineColor: '#fff',
                    markerLineWidth: 2
                }
            });
            setMarker(newMarker);
            let overlay = new maptalks.VectorLayer('overlay', newMarker);
            overlay.addTo(map);
            setOverlayLayer(overlay);
        }
    }, [position, rotation, map]);

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
                            setPosition([X, -Z]);
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
                        setPosition([X, -Z]);
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
        //console.log(rotation)
        let newRotation = -rotation;
        if (newRotation < -180) {
            newRotation += 360;
        }
        if (newRotation > 180) {
            newRotation -= 360;
        }
        map?.setBearing(newRotation);
    }, [rotation]); // This effect depends on the rotation state 
    
    useEffect(() => {
        if (map) {
            //map.setZoom(8, { animation: false });
            map.setCenter(position);
            map.setPitch(tilt);
        }
    }, [position]);
    
    useEffect(() => {
        if (speed*3.6 > 5) {
            // From 0 tilt at 10kph to 55 tilt at 80kph
            setTilt(Math.min((speed*3.6 - 5) / 70 * 60, 60));
            // From -90 offset at 10kph to -60 offset at 80kph
            setyOffset((speed*3.6 - 5) / 70 * 5 - 90);
        }
        else {
            setyOffset(-95);
            setTilt(0);
        }
    })
    return (
        <div style={{height: "100%", width: "100%", position: "relative"}}>
            <div id="map" style={{height: "100%", width: "100%"}}></div>
        </div>
    )
}