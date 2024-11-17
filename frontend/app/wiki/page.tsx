"use client"

import { motion } from "framer-motion"

export default function Wiki() {
    return (
        <motion.iframe 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6 }}
            className="absolute w-full h-full rounded-md" 
            src="https://ets2la.github.io/documentation/"
            style={{ // clear header
                transform: 'translateY(-80px)',
                height: 'calc(100% + 80px)'
            }}
        />
    )
}