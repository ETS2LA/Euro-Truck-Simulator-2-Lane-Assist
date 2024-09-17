import { Textarea } from '@/components/ui/textarea';
import { Avatar } from '@/components/ui/avatar';
import { ResizablePanel, ResizablePanelGroup, ResizableHandle } from '@/components/ui/resizable';

const messages = [
    { id: 1, username: "Developer", text: "Hello! How can I help you?", side: 'left' },
    { id: 2, username: "User", text: "Hi! The steering won't work in ETS2LA.", side: 'right' },
    { id: 3, username: "Developer", text: "Did you do First Time Setup?", side: 'left' },
    { id: 4, username: "User", text: "No, let me try that out.", side: 'right' },
  ];

const ChatMessage = ({ message }: { message: {id : number, username : string, text : string, side : "left" | "right" }}) => {
    return (
      <div className={`flex ${message.side === 'right' ? 'justify-end' : 'justify-start'} mb-2`}>
        <div className='flex-col'>
            <p className="text-sm text-zinc-500 mb-1">{message.username}</p>
            <div className={`px-4 py-2 rounded-lg ${message.side === 'right' ? 'bg-white text-black' : ' text-white border-2 border-white'}`}>{message.text}</div>
        </div>
      </div>
    );
  };

export default function Home() {
    return (
        <div className="flex flex-col w-full h-[calc(100vh-76px)] overflow-auto rounded-t-md justify-center items-center">
        <ResizablePanelGroup direction="horizontal" className="rounded-lg border">
            <ResizablePanel defaultSize={30}>
                <div className="flex flex-col mt-4 h-full w-full space-y-3 overflow-y-auto overflow-x-hidden max-h-full">
            
                </div>
            </ResizablePanel>
            <ResizableHandle withHandle />
            <ResizablePanel defaultSize={70}>
                <div className="w-full h-full">
                    <div className="overflow-auto h-5/6 p-4">
                        {messages.map((msg : any) => (
                            <ChatMessage key={msg.id} message={msg} />
                        ))}
                    </div>
                    <Textarea className="p-2 my-4 border rounded-lg w-full" placeholder="Type a message..." />
                </div>
            </ResizablePanel>
        </ResizablePanelGroup>
    </div>
    )
}