import { Textarea } from '@/components/ui/textarea';
import { Avatar } from '@/components/ui/avatar';
import { ResizablePanel, ResizablePanelGroup, ResizableHandle } from '@/components/ui/resizable';
import { ScrollArea } from '@/components/ui/scroll-area';

class Message {
    id: number;
    username: string;
    text: string;
    side: "left" | "right";
    reference?: number;

    constructor(id: number, username: string, text: string, side: "left" | "right", reference?: number) {
        this.id = id;
        this.username = username;
        this.text = text;
        this.side = side;
        this.reference = reference;
    }

}

const messages = [
    new Message(1, "Developer", "Hello! How can I help you?", "left"),
    new Message(2, "You", "Hi! The steering won't work in ETS2LA.", "right"),
    new Message(3, "Developer", "Did you do the First Time Setup?", "left"),
    new Message(4, "You", "No, let me try that out.", "right"),
    new Message(5, "You", "Quis pariatur eiusmod minim mollit quis. Ea dolor aute magna ipsum eu consectetur et labore veniam sunt non. Incididunt do officia eu excepteur enim veniam incididunt.", "right"),
    new Message(6, "You", "I did it now", "right", 3),
    new Message(7, "Developer", "And is it working now?", "left", 6),
    new Message(8, "Developer", "Also what the crap is this?", "left", 5),
    new Message(9, "You", "Yes, it's working now", "right"),
    new Message(10, "Developer", "Ok good!", "left"),
];

const ChatMessage = ({message, isReference} : {message:Message, isReference:boolean}) => {
    if (isReference) {
        return (
            <div className={`flex ${message.side === 'right' ? 'justify-end' : 'justify-start'} font-customSans text-xs`}>
                <div className='flex flex-col gap-1'>
                    <div className={`px-3 py-1.5 rounded-md ${message.side === 'right' ? 'bg-[#2d7ac4] text-foreground' : ' text-foreground bg-[#303030]'}`}>
                        {message.text}
                    </div>
                </div>
            </div>
        )
    }
    return (
      <div className={`flex ${message.side === 'right' ? 'justify-end' : 'justify-start'} font-customSans text-sm pb-4`}>
        <div className={`flex-col gap-1 flex max-w-96 ${message.side === "right" ? "place-items-end" : "place-items-start"}`}>
            {message.reference && (
                <ChatMessage key={message.reference} message={messages[message.reference - 1]} isReference={true} />
            )}
            <div className={`px-4 py-2 rounded-lg ${message.side === "right" ? "rounded-br-none" : "rounded-bl-none"} ${message.side === 'right' ? 'bg-[#2d7ac4] text-foreground' : ' text-foreground bg-[#303030]'}`}>
                {message.text}
            </div>
            {!isReference && (
                <p className={`text-xs text-muted-foreground ${message.side === "right" ? "text-end" : ""}`}>
                    {message.username} {message.reference && "replied"}
                </p>   
            )}
        </div>
      </div>
    );
  };

export default function Home() {
    return (
        <div className="flex flex-col w-full h-full overflow-auto rounded-t-md justify-center items-center">
            <ResizablePanelGroup direction="horizontal" className="rounded-lg border">
                <ResizablePanel defaultSize={20}>
                    <div className="flex flex-col mt-4 h-full w-full space-y-3 overflow-y-auto overflow-x-hidden max-h-full">
                
                    </div>
                </ResizablePanel>
                <ResizableHandle withHandle />
                <ResizablePanel defaultSize={80}>
                    <div className="w-full h-full p-4 flex flex-col justify-between">
                        <ScrollArea className='p-2 flex flex-col gap-1'>
                            {messages.map((message) => (
                                <ChatMessage key={message.id} message={message} isReference={false} />
                            ))}
                        </ScrollArea>
                        <Textarea className="p-2 border rounded-lg w-full" placeholder="Type a message..." />
                    </div>
                </ResizablePanel>
            </ResizablePanelGroup>
    </div>
    )
}