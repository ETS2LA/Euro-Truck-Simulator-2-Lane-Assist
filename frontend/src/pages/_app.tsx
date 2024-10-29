import type { AppProps } from 'next/app'
import type { Metadata } from "next";
import "@/pages/translation";
import { translate, changeLanguage, currentLanguage } from '@/pages/translation';
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider"
import { ETS2LAMenubar } from "@/components/ets2la_menubar";
import { ETS2LACommandMenu } from '@/components/ets2la_command_menu';
import { ETS2LAStates } from '@/components/ets2la_states';
import { GetIP } from "./backend";
import { Toaster } from "@/components/ui/sonner"
import { Badge } from '@/components/ui/badge';
import { Unplug, Ellipsis } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import useSWR from 'swr';
import Loader from '@/components/ets2la_loader';
import Head from 'next/head';
import { GeistSans } from 'geist/font/sans';
import { GeistMono } from 'geist/font/mono';
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
import { token, setToken, PlaySound, GetCurrentLanguage } from './backend';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ETS2LA - Euro Truck Simulator 2 Lane Assist",
  description: "",
  icons: ["favicon.ico"],
};
import { useState, useRef, useEffect } from 'react';
import { Authentication } from '@/components/ets2la_authentication';
import { toast } from 'sonner';
import { SetSettingByKey } from './settingsServer';
import { ValidateUser } from './account';
import DisclaimerDialog from '@/components/ets2la_disclaimer_dialog';
import { GetPages } from './backend';
import { ETS2LAPage } from '@/components/ets2la_page';

export default function MyApp({ Component, pageProps }: AppProps) {
  const [inputValue, setInputValue] = useState("localhost");
  const ipRef = useRef("localhost");

  const [showButton, setShowButton] = useState(false);
  const [disclaimerOpen, setDisclaimerOpen] = useState(true);
  const [status, setStatus] = useState("loading");

  const [Token, SetToken] = useState("");

  useEffect(() => {
    try {
      if (!PlaySound(ipRef.current, "boot")) {console.log("Not running on the local machine")}
    }
    catch (e) {
      console.log("Not running on the local machine")
    }
  }, [])

  // Try and get the token from local storage
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setToken(token);
      SetToken(token);
      ValidateUser().then((valid) => {
        if(valid == true){
          console.log("Token is valid")
          toast.success("Welcome back!", {duration: 1000});
        }
        else {
          console.log("Token is invalid")
          toast.error("Your token is invalid, please log in again", {duration: 1000});
          localStorage.setItem('token', "");
          setToken("");
          SetToken("");
        }
      })
    }
  }, []);

  // Save the token to local storage whenever it changes
  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      SetToken(token);
    }
  }, [token]);

  // Try and validate the current token

  const handleIpChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
    setShowButton(event.target.value.trim() !== '');
  };

  const { data, error, isLoading, mutate } = useSWR(ipRef.current, () => GetIP(ipRef.current as string));
  const { data: language, error: languageError, isLoading: languageIsLoading } = useSWR("language", () => GetCurrentLanguage(ipRef.current as string), { refreshInterval: 1000 });

  useEffect(() => {
    if (language) {
      changeLanguage(language);
    }
  }, [language]);


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

  const {data: pages, error: pagesError, isLoading: pagesIsLoading} = useSWR("pages", () => GetPages(ipRef.current as string), {refreshInterval: 10000});

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
        <Badge variant={"destructive"} className='gap-2 rounded-b-none'><Unplug className='w-5 h-5' />{translate("frontend.app.lost_connection")}</Badge>
        <div className='flex flex-col items-center space-y-5 justify-center h-[calc(100vh-180px)]'>
          <h1>ETS2LA</h1>
          <div className="flex flex-col sm:flex-row w-full max-w-sm items-center space-y-2 sm:space-y-0 sm:space-x-2">
            <Input type="text" onChange={handleIpChange} placeholder={translate("frontend.app.local_ip_placeholder")} className='w-[60vw] sm:w-full' />
            {showButton && <Button onClick={retry}>{translate("frontend.app.connect")}</Button>}
          </div>
        </div>
      </div>
    </Card>
    </div>
  </ThemeProvider>
  
  let ip = ipRef.current;

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
                }} ip={ip} />
            </ContextMenuTrigger>
            <ContextMenuContent className="w-64">
              <ContextMenuItem onClick={router.back}>
                {translate("frontend.context.back")}
              <ContextMenuShortcut>⌘B</ContextMenuShortcut>
              </ContextMenuItem>
              <ContextMenuItem onClick={router.forward}>
                {translate("frontend.context.forward")}
              <ContextMenuShortcut>⌘F</ContextMenuShortcut>
              </ContextMenuItem>
              <ContextMenuItem onClick={reloadPage}>
                {translate("frontend.context.reload")}
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

  console.log(pages)
  const page = routerUseRouter().pathname;
  console.log(page)
  const isInBasicMode = page.includes("basic");
  const isCustomPage = pages && page in pages;
  return (
    <main className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <div className={isInBasicMode ? "overflow-hidden" : "overflow-hidden p-3 h-[calc(100vh)]"}>
        <Head>
          <link rel="icon" href="https://wiki.tumppi066.fi/assets/favicon.ico" />
        </Head>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          {disclaimerOpen? 
            <DisclaimerDialog onClose={() => setDisclaimerOpen(false)} open={disclaimerOpen} /> : null
          }
          {
            !isInBasicMode ? <ETS2LAMenubar ip={ip} onLogout={() =>{
              toast.success(translate("frontend.logged_out"))
              SetSettingByKey("global", "token", null, ip)
              localStorage.setItem('token', "");
              SetToken("") // Having two setTokens
              setToken("")
            }} /> : null
          }
          <div className={isInBasicMode ? "" : "pt-3 pb-9 h-full"}>
            <ContextMenu>
              <ContextMenuTrigger className="h-full">
                  {isCustomPage ? <ETS2LAPage ip={ip} data={pages[page]} plugin={pages[page][0]["settings"]} /> : <Component {...newPageProps} />}
              </ContextMenuTrigger>
              <ContextMenuContent className="w-64">
                <ContextMenuItem onClick={router.back}>
                  {translate("frontend.context.back")}
                <ContextMenuShortcut>⌘B</ContextMenuShortcut>
                </ContextMenuItem>
                <ContextMenuItem onClick={router.forward}>
                  {translate("frontend.context.forward")}
                <ContextMenuShortcut>⌘F</ContextMenuShortcut>
                </ContextMenuItem>
                <ContextMenuItem onClick={reloadPage}>
                  {translate("frontend.context.reload")}
                  <ContextMenuShortcut>⌘R</ContextMenuShortcut>
                </ContextMenuItem>
                {isInBasicMode ? 
                  <ContextMenuItem onClick={() => router.push("/")}>
                      {translate("frontend.context.return_to_normal")}
                  </ContextMenuItem> :
                  <ContextMenuItem onClick={() => router.push("/basic")}>
                      {translate("frontend.context.return_to_basic")}
                  </ContextMenuItem>
                }
              </ContextMenuContent>
            </ContextMenu>
          </div>
          <ETS2LAStates ip={ip} />
          <ETS2LACommandMenu ip={ip} />
          <Toaster position={!isInBasicMode ? 'bottom-center' : 'bottom-left'}/>
        </ThemeProvider>
      </div>
    </main>
  );
}