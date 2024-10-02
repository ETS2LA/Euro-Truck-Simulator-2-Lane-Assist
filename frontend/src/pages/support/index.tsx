import { useState, useEffect, useRef } from 'react';
import { useTheme } from 'next-themes';
import { Textarea } from '@/components/ui/textarea';
import { ResizablePanel, ResizablePanelGroup } from '@/components/ui/resizable';
import { Badge } from '@/components/ui/badge';
import { Forward, Reply, ChevronUp, ChevronDown } from 'lucide-react';
import { toast } from 'sonner';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Button } from '@/components/ui/button';

const convertMarkdownToHTML = (text: string) => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.*?)__/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/_(.*?)_/g, '<em>$1</em>')
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
    .replace(/\n/g, '<br/>');
};

const escapeRegExp = (string: string) => {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
};

const highlightText = (
  text = '',
  searchText = '',
  globalMatchIndex = 0,
  currentMatch = 0
) => {
  if (!searchText || !text) return text;

  const regex = new RegExp(escapeRegExp(searchText), 'gi');
  let matchCount = 0;

  return text.replace(regex, (match) => {
    const isCurrentMatch = globalMatchIndex + matchCount === currentMatch;
    matchCount++;

    return `<span style="background-color: ${
      isCurrentMatch ? 'orange' : 'yellow'
    }; color: black;">${match}</span>`;
  });
};

class Message {
  id: number;
  username: string;
  text: string;
  side: 'left' | 'right';
  reference?: string;

  constructor(
    id: number,
    username: string,
    text: string,
    side: 'left' | 'right',
    reference?: string
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
  event:
    | 'create'
    | 'join'
    | 'tag_add'
    | 'tag_remove'
    | 'change_name'
    | 'leave'
    | 'fixing'
    | 'closed'
    | 'reopened';
  data: any;
  text: string | null;

  private eventTextGenerators: Record<string, () => string> = {
    create: () => `${this.data[0]} started a new conversation`,
    join: () => `${this.data[0]} joined the conversation`,
    tag_add: () => `${this.data[0]} added the following tag(s): ${this.data[1]}`,
    tag_remove: () =>
      `${this.data[0]} removed the following tag(s): ${this.data[1]}`,
    change_name: () =>
      `${this.data[0]} changed the conversation name to ${this.data[1]}`,
    fixing: () => `${this.data[0]} is fixing the issue`,
    leave: () => `${this.data[0]} left the conversation`,
    closed: () => `${this.data[0]} closed the conversation`,
    reopened: () => `${this.data[0]} reopened the conversation`,
  };

  constructor(
    id: number,
    event:
      | 'create'
      | 'join'
      | 'tag_add'
      | 'tag_remove'
      | 'change_name'
      | 'fixing'
      | 'leave'
      | 'closed'
      | 'reopened',
    data: any
  ) {
    this.id = id;
    this.event = event;
    this.data = data;
    this.text =
      this.eventTextGenerators[event]?.() ??
      `Unknown event was triggered with: ${JSON.stringify(data)}`;
  }
}

class Conversation {
  name: string;
  id: number;
  members: string[];
  messages: any[];
  tags: string[];

  constructor(
    name: string,
    id: number,
    members: string[],
    messages: any[],
    tags: string[]
  ) {
    this.name = name;
    this.id = id;
    this.members = members;
    this.messages = messages;
    this.tags = tags;
  }
}

const conv1_messages = [
  new ConversationEvent(1, 'create', ['You', ['Bug']]),
  new ConversationEvent(2, 'join', ['Developer']),
  new Message(3, 'Developer', 'Hello! How can I help you?', 'left'),
  new Message(4, 'You', "Hi! The steering won't work in ETS2LA.", 'right'),
  new Message(5, 'Developer', 'Did you do the First Time Setup?', 'left'),
  new Message(6, 'You', 'No, let me try that out.', 'right'),
  new Message(7, 'You', 'I did it now', 'right', 'Hello! How can I help you?'),
  new Message(8, 'Developer', 'And is it working now?', 'left', 'I did it now'),
  new Message(9, 'You', "Yes, it's working now", 'right'),
  new Message(10, 'Developer', 'Ok good!', 'left'),
  new Message(11, 'Developer', 'Have a nice day!', 'left'),
  new Message(12, 'You', 'Goodbye!', 'right'),
  new ConversationEvent(13, 'closed', ['You']),
];

const conv2_messages = [
  new ConversationEvent(1, 'create', ['You', ['Feature']]),
  new Message(
    2,
    'You',
    'Hello! I would like to suggest you a feature. Would it be possible to make a button that would allow us to upload images to this support chat?',
    'right'
  ),
  new Message(3, 'Developer', 'Great suggestion!', 'left'),
  new Message(4, 'Developer', "I'll get to work on adding this.", 'left'),
  new ConversationEvent(5, 'fixing', ['Developer']),
  new Message(6, 'You', 'Ok. Thank you.', 'right'),
  new Message(7, 'Developer', 'This has been added.', 'left'),
  new Message(8, 'You', 'Nice!', 'right'),
  new ConversationEvent(9, 'closed', ['You']),
];

const ChatEvent = ({ event }: { event: ConversationEvent }) => {
  return (
    <div className="flex items-center w-full justify-center pb-4">
      <div className="flex-1 h-px bg-muted-foreground mx-2"></div>
      <span className="text-xs whitespace-nowrap text-muted-foreground">
        {event.text}
      </span>
      <div className="flex-1 h-px bg-muted-foreground mx-2"></div>
    </div>
  );
};

const ChatMessage = ({
  message,
  message_index,
  messages,
  reply_func,
  searchText,
  globalMatchStartIndex,
  currentMatch,
}: any) => {
  const isRight = message.side === 'right';
  const nextMessage = messages[message_index + 1];
  const isSameSideNext = nextMessage?.side === message.side;

  const messageContainerClass = `flex gap-1 ${
    isRight ? 'justify-end' : 'justify-start'
  } text-sm ${isSameSideNext ? 'pb-2' : 'pb-4'} group`;

  const messageContentClass = `p-3 rounded-lg relative group ${
    isRight
      ? isSameSideNext
        ? ''
        : 'rounded-br-none'
      : isSameSideNext
      ? ''
      : 'rounded-bl-none'
  } bg-gray-200 text-black dark:bg-[#303030] dark:text-foreground`;

  return (
    <div className={messageContainerClass} id={`message-${message_index}`}>
      <div
        className={`flex-col gap-1 flex ${isRight ? 'items-end' : 'items-start'}`}
      >
        <div className="flex gap-1">
          {isRight && (
            <Button
              className="hidden group-hover:block text-xs p-1 bg-transparent border-none"
              variant="secondary"
              onClick={() => reply_func(message.text, message.username)}
            >
              <Reply className="w-4 h-4" />
            </Button>
          )}
          <div className={`${messageContentClass} flex flex-col gap-1 max-w-96`}>
            {message.reference && (
              <div className="p-2 border-l-4 border-gray-400 dark:border-gray-600">
                <p className="text-xs text-gray-600 dark:text-gray-300">
                  {message.reference}
                </p>
              </div>
            )}
            <div
              dangerouslySetInnerHTML={{
                __html: highlightText(
                  convertMarkdownToHTML(message.text),
                  searchText,
                  globalMatchStartIndex,
                  currentMatch
                ),
              }}
            />
          </div>
          {!isRight && (
            <Button
              className="hidden group-hover:block text-xs p-1 bg-transparent border-none"
              variant="outline"
              onClick={() => reply_func(message.text, message.username)}
            >
              <Reply className="w-4 h-4" />
            </Button>
          )}
        </div>
        {!isSameSideNext && (
          <p
            className={`text-xs text-muted-foreground ${
              isRight ? 'text-end' : ''
            }`}
          >
            {message.username} {message.reference && 'replied'}
          </p>
        )}
      </div>
    </div>
  );
};

function SearchBox({
  searchText,
  setSearchText,
  currentMatch,
  totalMatches,
  handleNextMatch,
  handlePreviousMatch,
  setShowSearchBox,
}: any) {
  const { theme } = useTheme();
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSearchKeyDown = (event: any) => {
    if (event.key === 'Enter') {
      handleNextMatch();
    } else if (event.key === 'ArrowDown') {
      handleNextMatch();
    } else if (event.key === 'ArrowUp') {
      handlePreviousMatch();
    }
  };

  return (
    <div
      style={{
        position: 'absolute',
        top: '70px',
        left: 'calc(57.5% - 100px)',
        width: '250px',
        zIndex: 1000,
        backgroundColor: theme === 'dark' ? '#000' : '#fff',
      }}
      className={`p-1 rounded-lg shadow-md border border-${
        theme === 'dark' ? 'white' : 'gray-400'
      }`}
    >
      <div className="flex items-center h-6">
        <input
          id="searchInput"
          ref={inputRef}
          className={`bg-transparent border-none pl-1 ${
            theme === 'dark' ? 'text-white' : 'text-black'
          } w-full focus:outline-none h-full text-xs`}
          placeholder="Search messages..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          onKeyDown={handleSearchKeyDown}
          autoComplete="off"
        />

        <div
          style={{
            width: '1px',
            height: '20px',
            backgroundColor: 'transparent',
            margin: '0 8px',
          }}
        ></div>
        <div className="flex items-center gap-1">
          {searchText && totalMatches > 0 ? (
            <span className="text-xs">{`${currentMatch + 1}/${totalMatches}`}</span>
          ) : searchText ? (
            <span className="text-xs">0/0</span>
          ) : (
            ''
          )}
          <div className="flex flex-col">
            <Button
              variant="ghost"
              className="p-0 h-3 min-h-0"
              style={{ width: '24px' }}
              onClick={handlePreviousMatch}
            >
              <ChevronUp
                className="w-3 h-3"
                style={{ color: theme === 'dark' ? 'white' : 'black' }}
              />
            </Button>
            <Button
              variant="ghost"
              className="p-0 h-3 min-h-0"
              style={{ width: '24px' }}
              onClick={handleNextMatch}
            >
              <ChevronDown
                className="w-3 h-3"
                style={{ color: theme === 'dark' ? 'white' : 'black' }}
              />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const { theme } = useTheme();
  const [conversations, setConversations] = useState<Conversation[]>([
    new Conversation('Broken Steering', 1, ['You', 'Developer'], conv1_messages, [
      'Bugs',
      'Closed',
    ]),
    new Conversation('Uploading Images', 2, ['You', 'Developer'], conv2_messages, [
      'Feedback',
      'Open',
    ]),
  ]);
  const [conversationIndex, setConversationIndex] = useState(0);
  const [textboxText, setTextboxText] = useState('');
  const [replyingTo, setReplyingTo] = useState<{
    username: string;
    text: string;
  } | null>(null);
  const [showSearchBox, setShowSearchBox] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [currentMatch, setCurrentMatch] = useState(0);
  const [totalMatches, setTotalMatches] = useState(0);
  const [messageMatchStarts, setMessageMatchStarts] = useState<
    Record<number, number>
  >({});
  const conversationData = conversations[conversationIndex];
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const matchElements = useRef<(HTMLElement | null)[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    if (!isSearching) {
      scrollToBottom();
    }
  }, [conversationData.messages]);

  useEffect(() => {
    updateMatches();
  }, [searchText, conversationData.messages]);

  const updateMatches = () => {
    let globalMatchIndex = 0;
    const matches: { messageIndex: number; globalMatchIndex: number }[] = [];
    const newMessageMatchStarts: Record<number, number> = {};

    conversationData.messages.forEach((message, messageIndex) => {
      newMessageMatchStarts[messageIndex] = globalMatchIndex;

      if (message instanceof Message && searchText) {
        const matchArray =
          message.text.match(new RegExp(escapeRegExp(searchText), 'gi')) || [];

        matchArray.forEach(() => {
          matches.push({ messageIndex, globalMatchIndex });
          globalMatchIndex++;
        });
      }
    });

    setMessageMatchStarts(newMessageMatchStarts);
    setTotalMatches(globalMatchIndex);
    setCurrentMatch(0);
    matchElements.current = matches.map(({ messageIndex }) =>
      document.getElementById(`message-${messageIndex}`)
    );

    if (matches.length > 0) {
      setIsSearching(true);
      scrollToMatch(0);
    } else {
      setIsSearching(false);
    }
  };

  const scrollToMatch = (index: number) => {
    const matchElement = matchElements.current[index];
    if (matchElement && scrollAreaRef.current) {
      const container = scrollAreaRef.current;
      const containerHeight = container.clientHeight;
      const elementTop = matchElement.offsetTop;
      const elementHeight = matchElement.offsetHeight;
      const scrollPosition = elementTop - containerHeight / 2 + elementHeight / 2;

      const maxScrollTop = container.scrollHeight - containerHeight;
      const targetScrollTop = Math.max(0, Math.min(scrollPosition, maxScrollTop));

      container.scrollTo({
        top: targetScrollTop,
        behavior: 'smooth',
      });
    }
  };

  const handleNextMatch = () => {
    if (totalMatches > 0) {
      const nextMatch = (currentMatch + 1) % totalMatches;
      setCurrentMatch(nextMatch);
      scrollToMatch(nextMatch);
    }
  };

  const handlePreviousMatch = () => {
    if (totalMatches > 0) {
      const prevMatch = (currentMatch - 1 + totalMatches) % totalMatches;
      setCurrentMatch(prevMatch);
      scrollToMatch(prevMatch);
    }
  };

  const handleKeyDown = (event: any) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage(textboxText);
    }
  };

  const changeConversation = (index: number) => {
    setConversationIndex(index);
    setTimeout(() => {
      scrollToBottom();
    }, 50);
  };

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTo({
        top: scrollAreaRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  };

  const sendMessage = (text: string) => {
    const cleanedText = text.trim();
    if (cleanedText === '') {
      toast.error('Message cannot be empty!');
      return;
    }

    const updatedMessages = [
      ...conversations[conversationIndex].messages,
      new Message(
        conversations[conversationIndex].messages.length + 1,
        'You',
        cleanedText,
        'right',
        replyingTo ? replyingTo.text : undefined
      ),
    ];

    const updatedConversation = {
      ...conversations[conversationIndex],
      messages: updatedMessages,
    };

    const updatedConversations = [...conversations];
    updatedConversations[conversationIndex] = updatedConversation;

    setConversations(updatedConversations);
    setReplyingTo(null);
    setTextboxText('');

    setTimeout(() => {
      scrollToBottom();
    }, 100);
  };

  const reply = (message_text: string, username: string) => {
    setReplyingTo({ text: message_text, username });
    inputRef.current?.focus();
  };

  const toggleSearchBox = () => {
    if (showSearchBox) {
      setSearchText('');
      setTotalMatches(0);
      setCurrentMatch(0);
    }
    setShowSearchBox(!showSearchBox);
  };

  const handleNewConversation = () => {
    const newConversation = new Conversation(
      'New Conversation',
      conversations.length + 1,
      ['You', 'Developer'],
      [],
      ['New']
    );
    setConversations([...conversations, newConversation]);
    setConversationIndex(conversations.length);

    setTimeout(() => {
      scrollToBottom();
    }, 50);
  };

  useEffect(() => {
    const handleGlobalKeyDown = (event: any) => {
      if (event.ctrlKey && event.key === 'f') {
        event.preventDefault();
        toggleSearchBox();
        setTimeout(() => {
          document.getElementById('searchInput')?.focus();
        }, 0);
      } else if (event.key === 'ArrowDown') {
        handleNextMatch();
      }
    };

    document.addEventListener('keydown', handleGlobalKeyDown);

    return () => {
      document.removeEventListener('keydown', handleGlobalKeyDown);
    };
  }, [showSearchBox]);

  return (
    <div className="flex flex-col w-full h-full overflow-auto rounded-t-md items-center">
      {showSearchBox && (
        <SearchBox
          searchText={searchText}
          setSearchText={setSearchText}
          currentMatch={currentMatch}
          totalMatches={totalMatches}
          handleNextMatch={handleNextMatch}
          handlePreviousMatch={handlePreviousMatch}
          setShowSearchBox={setShowSearchBox}
        />
      )}

      <ResizablePanelGroup direction="horizontal">
        <ResizablePanel defaultSize={20}>
          <div className="flex flex-col h-full w-full space-y-3 overflow-y-auto max-h-full relative">
            <div className="absolute bottom-0 right-0 top-0 w-12 bg-gradient-to-l from-background pointer-events-none" />
            <div className="flex flex-col gap-2">
              <TooltipProvider>
                <Button
                  variant="secondary"
                  className="items-center justify-start text-sm w-full rounded-r-none"
                  onClick={handleNewConversation}
                >
                  Create a new conversation
                </Button>
                <br />
                {conversations.map((conversation, index) => (
                  <div className="items-center justify-start text-sm" key={index}>
                    <Tooltip delayDuration={0} disableHoverableContent>
                      <TooltipTrigger className="items-center justify-start text-sm w-full">
                        <Button
                          variant={conversationIndex === index ? 'secondary' : 'ghost'}
                          className="items-center justify-start text-sm w-full rounded-r-none"
                          onClick={() => changeConversation(index)}
                        >
                          {conversation.name}
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent className="bg-transparent">
                        <div className="flex gap-2 text-start p-2 rounded-lg backdrop-blur-md backdrop-brightness-75">
                          {conversation.tags.map((tag, idx) => (
                            <Badge key={idx} variant="default" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                ))}
                <p className="p-4 text-muted-foreground text-xs">
                  Please note that nothing on this page is real, and you cannot yet use it.
                </p>
              </TooltipProvider>
            </div>
          </div>
        </ResizablePanel>
        <ResizablePanel defaultSize={80}>
          <div className="w-full pb-2 h-full flex flex-col justify-between relative">
            <div className="absolute top-0 left-0 w-full h-12 bg-gradient-to-b from-background to-transparent pointer-events-none z-50"></div>
            <div
              ref={scrollAreaRef}
              className="flex flex-col gap-1 relative z-0 overflow-y-auto custom-scrollbar"
            >
              <div className="flex flex-col gap-1 p-2 relative">
                <p className="h-4"></p>
                {conversationData.messages.map((message, index) => {
                  if (message instanceof Message) {
                    return (
                      <ChatMessage
                        key={message.id}
                        message={message}
                        message_index={index}
                        messages={conversationData.messages}
                        reply_func={reply}
                        searchText={searchText}
                        globalMatchStartIndex={messageMatchStarts[index] || 0}
                        currentMatch={currentMatch}
                      />
                    );
                  } else if (message instanceof ConversationEvent) {
                    return <ChatEvent key={message.id} event={message} />;
                  }
                  return null;
                })}
                <p className="h-4"></p>
              </div>
            </div>

            <div className="relative w-full">
              {replyingTo && (
                <div
                  className={`absolute p-2 rounded-md flex justify-between items-center border bg-background`}
                  style={{
                    width: 'calc(100% - 101px)',
                    top: '-80%',
                    left: '0%',
                    height: '60%',
                  }}
                >
                  <span className="text-xs">
                    Replying to {replyingTo.username}: "{replyingTo.text}"
                  </span>
                  <Button
                    className="-mx-2"
                    variant="ghost"
                    onClick={() => setReplyingTo(null)}
                  >
                    X
                  </Button>
                </div>
              )}

              <div className="relative z-10 flex flex-row">
                <Textarea
                  ref={inputRef}
                  className={`p-2 border rounded-lg w-full resize-none h-14 ${
                    theme === 'dark' ? 'bg-[#000000] text-white' : 'bg-gray-50 text-black'
                  }`}
                  placeholder="Type a message"
                  value={textboxText}
                  onChange={(e) => setTextboxText(e.target.value)}
                  onKeyDown={handleKeyDown}
                />
                <Button
                  className="w-1/12 h-15 mr-4 ml-2"
                  onClick={() => sendMessage(textboxText)}
                >
                  <Forward className="w-6 h-6" />
                </Button>
              </div>
            </div>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}
