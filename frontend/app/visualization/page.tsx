"use client";
import { motion } from "framer-motion";

export default function Visualization() {
    return (
        <motion.iframe className="w-full h-full rounded-md" 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6 }}
            src="http://localhost:60407/ETS2LA Visualisation.html"
        />
    )
}