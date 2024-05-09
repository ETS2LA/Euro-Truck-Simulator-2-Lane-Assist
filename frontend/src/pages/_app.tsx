import type { AppProps } from 'next/app'
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider"
import { ETS2LAMenubar } from "@/components/ets2la_menubar";
import { ETS2LACommandMenu } from '@/components/ets2la_command_menu';
import { GetIP } from "./server";
import { Toaster } from "@/components/ui/sonner"
import { Badge } from '@/components/ui/badge';
import { Unplug, Ellipsis } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import useSWR from 'swr';
import Loader from '@/components/ets2la_loader';
import Head from 'next/head';
import {
  ContextMenu,
  ContextMenuCheckboxItem,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuLabel,
  ContextMenuRadioGroup,
  ContextMenuRadioItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
  ContextMenuSub,
  ContextMenuSubContent,
  ContextMenuSubTrigger,
  ContextMenuTrigger,
} from "@/components/ui/context-menu"
import { useRouter } from 'next/navigation';
import { useRouter as routerUseRouter } from 'next/router';
import { token, setToken } from './server';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ETS2LA - Euro Truck Simulator 2 Lane Assist",
  description: "",
  icons: ["favicon.ico"],
};
import { useState, useRef, useEffect } from 'react';
import { Authentication } from '@/components/ets2la_authentication';
import { toast } from 'sonner';

export default function MyApp({ Component, pageProps }: AppProps) {
  const [inputValue, setInputValue] = useState("localhost");
  const ipRef = useRef("localhost");

  const [showButton, setShowButton] = useState(false);
  const [status, setStatus] = useState("loading");

  const [Token, SetToken] = useState("");
  // Try and get the token from local storage
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setToken(token);
      SetToken(token);
      toast.success("Welcome back!", {duration: 1000});
    }
  }, []);

  // Save the token to local storage whenever it changes
  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      SetToken(token);
    }
  }, [token]);

  const handleIpChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
    setShowButton(event.target.value.length > 0);
  };

  const { data, error, isLoading, mutate } = useSWR(ipRef.current, () => GetIP(ipRef.current as string));

  useEffect(() => {
    if (isLoading && !error) {
      setStatus("isLoading");
      setShowButton(false);
    } else if (!isLoading && error) {
      setStatus("error");
    } else if (!isLoading && !error) {
      setStatus("success");
    }
  }, [isLoading, error]);

  const router = useRouter();

  const retry = () => {
    setShowButton(false);
    ipRef.current = inputValue;
    mutate(ipRef.current);
  };

  const reloadPage = () => {
    window.location.reload();
  };

  if (status == "isLoading") return <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
    <div className='p-3'>
    <Card className="flex flex-col content-center text-center space-y-5 pb-0 h-[calc(100vh-27px)] overflow-auto rounded-t-md">
      <div className='flex flex-col space-y-5'>
        <div className='flex flex-col items-center space-y-5 justify-center h-[calc(100vh-100px)]'>
          <h1>ETS2LA</h1>
          <Loader className='w-6 h-6 animate-spin' />
        </div>
      </div>
    </Card>
    </div>
  </ThemeProvider>

  if (status == "error") return <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
    <div className='p-3'>
    <Card className="flex flex-col content-center text-center space-y-5 pb-0 h-[calc(100vh-27px)] overflow-auto rounded-t-md">
      <div className='flex flex-col space-y-5'>
        <Badge variant={"destructive"} className='gap-1 rounded-b-none'><Unplug className='w-5 h-5' /> Lost connection to the server.</Badge>
        <div className='flex flex-col items-center space-y-5 justify-center h-[calc(100vh-180px)]'>
          <h1>ETS2LA</h1>
          <div className="flex flex-col sm:flex-row w-full max-w-sm items-center space-y-2 sm:space-y-0 sm:space-x-2">
            <Input type="text" onChange={handleIpChange} placeholder="Local IP address of ETS2LA" className='w-[60vw] sm:w-full' />
            {showButton && <Button onClick={retry}>Connect</Button>}
          </div>
        </div>
      </div>
    </Card>
    </div>
  </ThemeProvider>
  
  let ip = ipRef.current;

  console.log(ip);

  // Add the ip to the pageProps
  const newPageProps = { ...pageProps, ip };

  if(Token == "") {
    return <div className='overflow-hidden p-3'>
      <Head>
        <link rel="icon" href="https://wiki.tumppi066.fi/assets/favicon.ico" />
      </Head>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        <ETS2LAMenubar ip={ip} onLogout={() =>{
          localStorage.setItem('token', token);
          setToken("")
          SetToken("")
        }} />
        <div className='py-3 '>
          <ContextMenu>
            <ContextMenuTrigger className="h-full">
              <Authentication onLogin={(gotToken) => {
                SetToken(gotToken)
                setToken(gotToken)
                }} />
            </ContextMenuTrigger>
            <ContextMenuContent className="w-64">
              <ContextMenuItem onClick={router.back}>
                Back
                <ContextMenuShortcut>⌘B</ContextMenuShortcut>
              </ContextMenuItem>
              <ContextMenuItem onClick={router.forward}>
                  Forward
                <ContextMenuShortcut>⌘F</ContextMenuShortcut>
              </ContextMenuItem>
              <ContextMenuItem onClick={reloadPage}>
                  Reload
                  <ContextMenuShortcut>⌘R</ContextMenuShortcut>
              </ContextMenuItem>
            </ContextMenuContent>
          </ContextMenu>
        </div>
        <ETS2LACommandMenu ip={ip} />
        <Toaster position='bottom-center'/>
      </ThemeProvider>
    </div>
  }

  return (
    <div className='overflow-hidden p-3'>
      <Head>
        <link rel="icon" href="https://wiki.tumppi066.fi/assets/favicon.ico" />
      </Head>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        <ETS2LAMenubar ip={ip} onLogout={() =>{
          toast.success("Logged out")
          localStorage.setItem('token', "");
          SetToken("")
          setToken("")
        }} />
        <div className='py-3 '>
          <ContextMenu>
            <ContextMenuTrigger className="h-full">
              <Component {...newPageProps} />
            </ContextMenuTrigger>
            <ContextMenuContent className="w-64">
              <ContextMenuItem onClick={router.back}>
                Back
                <ContextMenuShortcut>⌘B</ContextMenuShortcut>
              </ContextMenuItem>
              <ContextMenuItem onClick={router.forward}>
                  Forward
                <ContextMenuShortcut>⌘F</ContextMenuShortcut>
              </ContextMenuItem>
              <ContextMenuItem onClick={reloadPage}>
                  Reload
                  <ContextMenuShortcut>⌘R</ContextMenuShortcut>
              </ContextMenuItem>
            </ContextMenuContent>
          </ContextMenu>
        </div>
        <ETS2LACommandMenu ip={ip} />
        <Toaster position='bottom-center'/>
      </ThemeProvider>
    </div>
  );
}