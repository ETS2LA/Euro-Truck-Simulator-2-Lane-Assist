import { Textarea } from '@/components/ui/textarea';
import { ResizablePanel, ResizablePanelGroup, ResizableHandle } from '@/components/ui/resizable';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Forward } from 'lucide-react';
import { toast, Toaster} from 'sonner';
import { useState } from 'react';

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

class Tag {
  name: string;
  color: string; // hex color
  constructor(name: string, color: string) {
    this.name = name;
    this.color = color;
  }
}

class Conversation {
    name: string;
    id: number;
    members: string[];
    messages: Message[];
    tags: Tag[];
    constructor(name: string, id : number, members: string[], messages: Message[], tags: Tag[]) {
        this.name = name
        this.id = id
        this.members = members
        this.messages = messages;
        this.tags = tags
    }
}

const tags = {
    'bug': new Tag('Bug', '#ef4444'),
    'feature': new Tag('Feature', '#2563eb'),
    'other': new Tag('Other', '#3f3f46'),
    'closed': new Tag('Closed', '#15803d'),
    'open': new Tag('Open', '#a16207'),
}

const conv1_messages: Message[] = [
  new Message(1, 'Developer', 'Hello! How can I help you?', 'left'),
  new Message(2, 'You', "Hi! The steering won't work in ETS2LA.", 'right'),
  new Message(3, 'Developer', 'Did you do the First Time Setup?', 'left'),
  new Message(4, 'You', 'No, let me try that out.', 'right'),
  new Message(6, 'You', 'I did it now', 'right', 3),
  new Message(7, 'Developer', 'And is it working now?', 'left', 6),
  new Message(9, 'You', "Yes, it's working now", 'right'),
  new Message(10, 'Developer', 'Ok good!', 'left'),
  new Message(11, 'Developer', 'Have a nice day!', 'left'),
  new Message(12, 'You', 'Goodbye!', 'right'),
];

const conv2_messages: Message[] = [
  new Message(1, 'You', 'Hello! I would like to suggest you a feature. Would it be possible to make a button that would allow us to upload images to this support chat?', 'right'),
  new Message(2, 'Developer', 'Great suggestion!', 'left'),
  new Message(3, 'Developer', "I'll get to work on adding this.", 'left'),
  new Message(4, 'You', 'Ok. Thank you.', 'right'),
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

    const messageContentClass = `px-4 py-2 rounded-lg ${
        isRight ? 'rounded-br-none' : 'rounded-bl-none'
    } bg-gray-200 text-black dark:bg-[#303030] dark:text-foreground`;

    return (
        <div className={messageContainerClass}>
            <div
                className={`flex-col gap-1 flex max-w-96 ${
                    isRight ? 'items-end' : 'items-start'
                }`}
            >
                <div className={messageContentClass}>
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

export default function Home() {
    const [conversations, setConversations] = useState<Conversation[]>([
        new Conversation('Broken Steering', 1, ['You', 'Developer'], conv1_messages, [tags['bug'], tags['closed']]),
        new Conversation('Uploading Images', 2, ['You', 'Developer'], conv2_messages, [tags['feature'], tags['open']]),
    ]);
    const [conversation_index, setConversationIndex] = useState(0);
    const [textbox_text, setTextboxText] = useState('');

    function ChangeConversation(index: number) {
        setConversationIndex(index);
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
        setConversations(updatedConversations);
        setTextboxText(''); // Clear the textbox
    }

    const conversation_data = conversations[conversation_index];

    return (
        <div className="flex flex-col w-full h-full overflow-auto rounded-t-md justify-center items-center">
        <ResizablePanelGroup direction="horizontal" className="rounded-lg border">
            {/* Left panel content */}
            <ResizablePanel defaultSize={30}>
                <div className="flex flex-col h-full w-full space-y-3 overflow-y-auto overflow-x-hidden max-h-full">
                    <div className="flex flex-col">
                        {conversations.map((conversation, index) => (
                            <div key={index}>
                                <Button className="flex flex-col justify-items-start w-full h-22 gap-1 rounded-none" variant={"ghost"} onClick={() => ChangeConversation(index)}>
                                    <h1 className='text-lg'>{conversation.name}</h1>
                                    <p className='text-sm text-zinc-600'>{conversation.members.join(', ')}</p>
                                    <div className="flex flex-row gap-2">
                                        {conversation.tags.map((tag) => (
                                            <Badge key={tag.name} style={{ backgroundColor: tag.color, color: 'white' }}>{tag.name}</Badge>
                                        ))}
                                    </div>
                                </Button>
                                <Separator orientation="horizontal" />
                            </div>
                        ))}
                    </div>
                </div>
            </ResizablePanel>
            <ResizableHandle withHandle />
            <ResizablePanel defaultSize={70}>
                <div className="w-full pb-2 h-full flex flex-col justify-between relative">
                    {/* Top gradient */}
                    <div className="absolute top-0 left-0 w-full h-16 bg-gradient-to-b from-background to-transparent pointer-events-none z-50"></div>

                    <ScrollArea className="flex flex-col gap-1 relative z-0">
                        <div className="flex flex-col text-center mt-6 mb-2 items-center">
                        <h1 className="text-2xl font-bold">{conversation_data.name}</h1>
                        <p className="text-sm text-zinc-500">{conversation_data.members.join(', ')}</p>
                        <p className="text-sm text-zinc-500">{conversation_data.messages.length} messages</p>
                        <div className="flex flex-row gap-2 mt-2">
                            {conversation_data.tags.map((tag) => (
                            <Badge key={tag.name} style={{ backgroundColor: tag.color, color: 'white' }}>{tag.name}</Badge>
                            ))}
                        </div>
                        </div>
                        <Separator className="translate-y-4 mb-8" />
                        <div className="flex flex-col mx-4">
                        {conversation_data.messages.map((message, index) => (
                            <ChatMessage key={message.id} message_index={index} messages={conversation_data.messages} />
                        ))}
                        </div>
                    </ScrollArea>

                    {/* Gradient behind the text area */}
                    <div className="absolute bottom-0 left-0 w-full h-40 bg-gradient-to-t from-background to-transparent pointer-events-none z-0"></div>

                    {/* Input area */}
                    <div className="relative z-10 flex flex-row">
                        <Textarea
                        className="p-2 ml-4 border rounded-lg w-11/12 bg-white text-black dark:bg-zinc-900 dark:text-foreground resize-none h-18"
                        placeholder="Type a message"
                        value={textbox_text}
                        onChange={(e) => setTextboxText(e.target.value)}
                        />
                        <Button className="w-1/12 mx-2 h-18 mr-4" onClick={() => SendMessage(textbox_text)}><Forward className='w-8 h-8' /></Button>
                    </div>
                </div>
            </ResizablePanel>
        </ResizablePanelGroup>
        </div>
    );
}
