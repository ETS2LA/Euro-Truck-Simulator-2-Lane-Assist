"use client"

import * as React from "react"
import { GetFrametimes } from "@/app/server"



export async function Frametimes() {
    const frametimes = await GetFrametimes()
    
}