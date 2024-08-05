import React, { useEffect, useRef } from 'react';
import { Marker, useMap } from 'react-leaflet';
import { LatLngTuple, divIcon } from 'leaflet';

let modifiedSVG = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="white" stroke="orange" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-navigation-2"><polygon points="12 2 19 21 12 17 5 21 12 2"/></svg>';
let iconSVGRed = `data:image/svg+xml;base64,${btoa(modifiedSVG)}`;

const CustomMarker = ({ position, rotation}: { position: LatLngTuple, rotation: number }) => {
  const markerRef = useRef(null);
  const map = useMap();

  useEffect(() => {
    if (markerRef.current) {
      const newIcon = divIcon({
        className: 'custom-marker-icon',
        html: `<div style="transform: rotate(${-rotation}deg);">${modifiedSVG}</div>`, // Example with emoji, replace with your SVG or icon
        iconSize: [30, 30],
        iconAnchor: [15, 18],
      });
      markerRef.current.setIcon(newIcon);
    }
  }, [rotation]);

  return <Marker position={position} ref={markerRef} />;
};

export default CustomMarker;