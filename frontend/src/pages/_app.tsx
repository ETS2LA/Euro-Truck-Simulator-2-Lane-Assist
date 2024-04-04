import type { AppProps } from 'next/app'
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider"
import { ETS2LAMenubar } from "@/components/ets2la-menubar";
import { ETS2LACommandMenu } from '@/components/ets2la-command-menu';
import { GetIP } from "./server";
import { Toaster } from "@/components/ui/sonner"
import { Badge } from '@/components/ui/badge';
import { Unplug, Ellipsis } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import useSWR from 'swr';
import Loader from '@/components/ets2la-loader';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ETS2LA - Euro Truck Simulator 2 Lane Assist",
  description: "",
  icons: ["favicon.ico"],
};
import { useState, useRef } from 'react';

export default function MyApp({ Component, pageProps }: AppProps) {
  const [inputValue, setInputValue] = useState("localhost");
  const ipRef = useRef("localhost");
  const port = 37520;

  const handleIpChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  };

  const handlePortChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  };

  const { data, error, isLoading, mutate } = useSWR(ipRef.current, () => GetIP(ipRef.current as string));

  const retry = () => {
    ipRef.current = inputValue;
    mutate(ipRef.current);
  };

  if (isLoading) return <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
    <div className='p-3'>
    <Card className="flex flex-col content-center text-center space-y-5 pb-0 h-[calc(100vh-27px)] overflow-auto rounded-t-md">
      <div className='flex flex-col space-y-5'>
        <div className='flex flex-col items-center space-y-5 justify-center h-[calc(100vh-100px)]'>
          <h1>Euro Truck Simulator 2 Lane Assist</h1>
          <Loader className='w-8 h-8 animate-spin' />
          <h3>Connecting to backend at {ipRef.current}:{port}...</h3>
        </div>
      </div>
    </Card>
    </div>
  </ThemeProvider>

  if (error) return <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
    <div className='p-3'>
    <Card className="flex flex-col content-center text-center space-y-5 pb-0 h-[calc(100vh-27px)] overflow-auto rounded-t-md">
      <div className='flex flex-col space-y-5'>
        <Badge variant={"destructive"} className='gap-1 rounded-b-none'><Unplug className='w-5 h-5' /> Lost connection to the server.</Badge>
        <div className='grid grid-cols-1 place-items-center space-y-3 justify-center h-[calc(100vh-180px)]'>
          <h1>ETS2 Lane Assist</h1>
          <div className="grid grid-rows-2 grid-cols-1 space-y-1">
            <div className="flex gap-2 w-[45vw]">
              <Input type="text" onChange={handleIpChange} value={inputValue} placeholder="Local IP address of ETS2LA" className='w-3/4'/>
              <Input type="text" onChange={handlePortChange} value={port} placeholder="Port (Default: 37520)" className='w-1/4'/>
            </div>
            <div className='flex w-[45vw]'>
              <Button onClick={retry} className='w-full'>Connect</Button>
            </div>
          </div>
        </div>
      </div>
    </Card>
    </div>
  </ThemeProvider>
  
  let ip = ipRef.current;

  console.log(ip + ":" + port);

  // Add the ip to the pageProps
  const newPageProps = { ...pageProps, ip };

  return (
    <div className='overflow-hidden p-3'>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        <ETS2LAMenubar ip={ip} />
        <div className='py-3'>
          <Component {...newPageProps} />
        </div>
        <ETS2LACommandMenu ip={ip} />
        <Toaster position='bottom-center'/>
      </ThemeProvider>
    </div>
  );
}