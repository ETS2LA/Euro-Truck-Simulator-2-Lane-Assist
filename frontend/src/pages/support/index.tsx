import { Textarea } from '@/components/ui/textarea';
import { ResizablePanel, ResizablePanelGroup, ResizableHandle } from '@/components/ui/resizable';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Forward } from 'lucide-react';
import { toast, Toaster} from 'sonner';
import { useState, useEffect, useRef } from 'react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

class Message {
  id: number;
  username: string;
  text: string;
  side: 'left' | 'right';
  reference?: number;

  constructor(
    id: number,
    username: string,
    text: string,
    side: 'left' | 'right',
    reference?: number
  ) {
    this.id = id;
    this.username = username;
    this.text = text;
    this.side = side;
    this.reference = reference;
  }
}


class ConversationEvent {
    id: number;
    event: "create" | "join" | "tag_add" | "tag_remove" | "change_name" | "leave" | "fixing" | "closed" | "reopened";
    data: any;
    text: string | null;

    private eventTextGenerators: Record<string, () => string> = {
        "create": () => `${this.data[0]} created the conversation with tag(s): ${this.data[1]}`,
        "join": () => `${this.data[0]} joined the conversation`,
        "tag_add": () => `${this.data[0]} added the following tag(s): ${this.data[1]}`,
        "tag_remove": () => `${this.data[0]} removed the following tag(s): ${this.data[1]}`,
        "change_name": () => `${this.data[0]} changed the conversation name to ${this.data[1]}`,
        "fixing": () => `${this.data[0]} is fixing the issue`,
        "leave": () => `${this.data[0]} left the conversation`,
        "closed": () => `${this.data[0]} closed the conversation`,
        "reopened": () => `${this.data[0]} reopened the conversation`,
    };

    constructor(id: number, event: "create" | "join" | "tag_add" | "tag_remove" | "change_name" | "fixing" | "leave" | "closed" | "reopened", data: any) {
        this.id = id;
        this.event = event;
        this.data = data;
        this.text = this.eventTextGenerators[event]?.() ?? `Unknown event was triggered with: ${JSON.stringify(data)}`;
    }
}
class Conversation {
    name: string;
    id: number;
    members: string[];
    messages: any;
    tags: string[];
    constructor(name: string, id : number, members: string[], messages: any, tags: string[]) {
        this.name = name
        this.id = id
        this.members = members
        this.messages = messages;
        this.tags = tags
    }
}

const conv1_messages = [
  new ConversationEvent(1, 'create', ['You', ['Bug']]),
  new ConversationEvent(2, 'join', ['Developer']),
  new Message(3, 'Developer', 'Hello! How can I help you?', 'left'),
  new Message(4, 'You', "Hi! The steering won't work in ETS2LA.", 'right'),
  new Message(5, 'Developer', 'Did you do the First Time Setup?', 'left'),
  new Message(6, 'You', 'No, let me try that out.', 'right'),
  new Message(7, 'You', 'I did it now', 'right', 3),
  new Message(8, 'Developer', 'And is it working now?', 'left', 6),
  new Message(9, 'You', "Yes, it's working now", 'right'),
  new Message(10, 'Developer', 'Ok good!', 'left'),
  new Message(11, 'Developer', 'Have a nice day!', 'left'),
  new Message(12, 'You', 'Goodbye!', 'right'),
  new ConversationEvent(13, 'closed', ['You']),
];

const conv2_messages = [
  new ConversationEvent(1, 'create', ['You', ['Feature']]),
  new Message(2, 'You', 'Hello! I would like to suggest you a feature. Would it be possible to make a button that would allow us to upload images to this support chat?', 'right'),
  new Message(3, 'Developer', 'Great suggestion!', 'left'),
  new Message(4, 'Developer', "I'll get to work on adding this.", 'left'),
  new ConversationEvent(5, 'fixing', ['Developer']),
  new Message(6, 'You', 'Ok. Thank you.', 'right'),
  new Message(7, 'Developer', 'This has been added.', 'left'),
  new Message(8, 'You', 'Nice!', 'right'),
  new ConversationEvent(9, 'closed', ['You']),
];

const ChatMessage = ({ message_index, messages }: { message_index: number, messages: Message[] }) => {
    const message = messages[message_index];
    const isRight = message.side === 'right';
    const nextMessage = messages[message_index + 1];
    const isSameSideNext = nextMessage?.side === message.side;

    // Remove bottom padding if there's a next message on the same side
    const messageContainerClass = `flex ${
        isRight ? 'justify-end' : 'justify-start'
    } font-customSans text-sm ${isSameSideNext ? 'pb-2' : 'pb-4'}`;

    const messageContentClass = `p-3 rounded-lg ${
        isRight ? !isSameSideNext ? 'rounded-br-none' : "" : !isSameSideNext ? 'rounded-bl-none' : ""
    } bg-gray-200 text-black dark:bg-[#303030] dark:text-foreground`;

    return (
        <div className={messageContainerClass}>
            <div
                className={`flex-col gap-1 flex max-w-96 ${
                    isRight ? 'items-end' : 'items-start'
                }`}
            >
                <div className={messageContentClass + " flex flex-col gap-1"}>
                    {message.reference && (
                        <div className={`p-2 border-l-4 border-gray-400 dark:border-gray-600`}>
                            {/* Display the referenced message text */}
                            <p className="text-xs text-gray-600 dark:text-gray-300">
                                {messages.find((msg) => msg.id === message.reference)?.text}
                            </p>
                        </div>
                    )}
                    <p>{message.text}</p>
                </div>
                {/* Hide the username if there's a next message from the same side */}
                {!isSameSideNext && (
                    <p className={`text-xs text-muted-foreground ${isRight ? 'text-end' : ''}`}>
                        {message.username} {message.reference && 'replied'}
                    </p>
                )}
            </div>
        </div>
    );
};

const ChatEvent = ({ event } : { event: ConversationEvent }) => {
    return (
        <div style={{ width: '100%', textAlign: 'center', margin: '20px 0', position: 'relative' }}>
            <Separator orientation="horizontal" style={{ width: '100%', position: 'relative' }}>
                <span
                    style={{
                        position: 'absolute',
                        top: '-0.75em', // Adjust as needed to position text
                        left: '50%',
                        transform: 'translateX(-50%)',
                        backgroundColor: '#09090b', // Ensure text is readable on separator
                        padding: '0 10px',
                        whiteSpace: 'nowrap', // Prevent text wrapping
                    }}
                >
                    {event.text}
                </span>
            </Separator>
        </div>
    );
};


export default function Home() {
    const [conversations, setConversations] = useState<Conversation[]>([
        new Conversation('Broken Steering', 1, ['You', 'Developer'], conv1_messages, ["Bugs", "Closed"]),
        new Conversation('Uploading Images', 2, ['You', 'Developer'], conv2_messages, ["Feedback", "Open"]),
    ]);
    const [conversation_index, setConversationIndex] = useState(0);
    const [textbox_text, setTextboxText] = useState('');
    const conversation_data = conversations[conversation_index];
    const scrollAreaRef = useRef<HTMLDivElement>(null); // Ref for the scroll area

    const handleKeyDown = (event: any) => {
        if (event.key === "Enter") {
            SendMessage(textbox_text);
        }
    };

    function ChangeConversation(index: number) {
        setConversationIndex(index);
        if (scrollAreaRef.current) {
            scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
        }
    }

    function SendMessage(text: string) {
        if (text.trim() === '') {toast.error('Message cannot be empty!'); return} // Prevent sending empty messages

        // Create a new array for messages
        const updatedMessages = [...conversations[conversation_index].messages, new Message(conversations[conversation_index].messages.length + 1, 'You', text, 'right')];

        // Update the conversation
        const updatedConversation = {
            ...conversations[conversation_index],
            messages: updatedMessages,
        };

        // Create a new conversations array with the updated conversation
        const updatedConversations = [...conversations];
        updatedConversations[conversation_index] = updatedConversation;

        // Update the state
        scrollToBottom()
        setConversations(updatedConversations);
        const conversation_data = conversations[conversation_index];
        setTextboxText(''); // Clear the textbox
    }

    function HandleNewConversation() {
        const new_conversation = new Conversation('New Conversation', conversations.length + 1, ['You', 'Developer'], [], ["New"]);
        setConversations([...conversations, new_conversation]);
        setConversationIndex(conversations.length);
    }

    function scrollToBottom() {
        if (scrollAreaRef.current) {
            let scrollHeight = scrollAreaRef.current.scrollHeight;
            let clientHeight = scrollAreaRef.current.clientHeight;
            let difference = scrollHeight - clientHeight;
            console.log("Scroll Height: " + scrollHeight + " Client Height: " + clientHeight + " Difference: " + difference);
    
            if (difference > 0) {
                const scrollDown = () => {
                    let scrollTop = scrollAreaRef.current.scrollTop;
                    let remainingDistance = difference - scrollTop;
    
                    // Adjusted speed factor for smoother scroll
                    let speedFactor = Math.pow(remainingDistance / difference, 5);
                    let scrollStep = Math.max(1, Math.min(20, (1 - speedFactor) * 200));
                    let interval = Math.max(5, speedFactor * 10);
    
                    if (scrollTop < difference - 1) {
                        scrollAreaRef.current.scrollTop += scrollStep;
                        console.log("Current Position: " + scrollAreaRef.current.scrollTop);
                        setTimeout(scrollDown, interval);
                    } else {
                        // Set scrollTop to scrollHeight - clientHeight for the exact bottom position
                        scrollAreaRef.current.scrollTop = scrollHeight - clientHeight;
                        console.log("Snapped to bottom at position: " + scrollAreaRef.current.scrollTop);
                    }
                };
    
                scrollDown();
            }
        }
    }
    
    

    return (
        <div className="flex flex-col w-full h-full overflow-auto rounded-t-md justify-center items-center">
            <div className="absolute bottom-0 left-[212px] top-[50px] w-12 bg-gradient-to-l from-background pointer-events-none" />
            <ResizablePanelGroup direction="horizontal" className="">
                {/* Left panel content */}
                <ResizablePanel defaultSize={20}>
                    <div className="flex flex-col h-full w-full space-y-3 overflow-y-auto overflow-x-hidden max-h-full">
                        <div className="flex flex-col gap-2">
                            <TooltipProvider>
                                <Button variant="secondary" className="items-center justify-start text-sm w-full rounded-r-none" onClick={HandleNewConversation}>
                                    Create a new conversation
                                </Button>
                                <br />
                                {conversations.map((conversation, index) => (
                                    <div className="items-center justify-start text-sm">
                                        <Tooltip delayDuration={0} disableHoverableContent={true}>
                                            <TooltipTrigger className="items-center justify-start text-sm w-full">
                                                <Button key={index} variant={ conversation_index == index ? "secondary" : "ghost"} className="items-center justify-start text-sm w-full rounded-r-none" onClick={() => ChangeConversation(index)}>
                                                    {conversation.name}
                                                </Button>
                                            </TooltipTrigger>
                                            <TooltipContent className='bg-transparent'>
                                                <div className="flex gap-2 text-start p-2 rounded-lg backdrop-blur-md backdrop-brightness-75">
                                                    {conversation.tags.map((tag, index) => (
                                                        <Badge key={index} variant="default" className="text-xs">{tag}</Badge>
                                                    ))}
                                                </div>
                                            </TooltipContent>
                                        </Tooltip> 
                                    </div>
                                ))}
                                <p className='p-4 text-muted-foreground text-xs'>Please note that nothing on this page is real, and you cannot yet use it.</p>
                            </TooltipProvider>
                        </div>
                    </div>
                </ResizablePanel>
                <ResizablePanel defaultSize={80}>
                    <div className="w-full pb-2 h-full flex flex-col justify-between relative">
                        {/* Top gradient */}
                        <div className="absolute top-0 left-0 w-full h-16 bg-gradient-to-b from-background to-transparent pointer-events-none z-50"></div>
                        <div ref={scrollAreaRef} className="flex flex-col gap-1 relative z-0 overflow-y-auto custom-scrollbar">
                            <div className="flex flex-col gap-1 p-2">
                                <br />
                                {conversation_data.messages.map((message, index) => {
                                    if (message instanceof Message) {
                                        return <ChatMessage key={message.id} message_index={index} messages={conversation_data.messages} />;
                                    } else if (message instanceof ConversationEvent) {
                                        return <ChatEvent key={message.id} event={message} />;
                                    }
                                    return null;
                                })}
                            </div>
                        </div>

                        {/* Input area */}
                        <div className="relative z-10 flex flex-row">
                            <Textarea
                                className="p-2 ml-4 border rounded-lg w-11/12 bg-white text-black dark:bg-zinc-900 dark:text-foreground resize-none h-14"
                                placeholder="Type a message"
                                value={textbox_text}
                                onChange={(e) => setTextboxText(e.target.value)}
                                onKeyDown={handleKeyDown}
                            />
                            <Button className="w-1/12 h-15 mr-4 ml-2" onClick={() => SendMessage(textbox_text)}><Forward className='w-6 h-6' /></Button>
                        </div>
                    </div>
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    );
}