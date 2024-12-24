import React, { createContext, useContext, useState, Dispatch, SetStateAction } from 'react';

// Define the shape of your context state
interface CollapsedContextType {
    isCollapsed: boolean;
    setIsCollapsed: Dispatch<SetStateAction<boolean>>;
}

// Create the context with a default value
const CollapsedContext = createContext<CollapsedContextType | undefined>(undefined);

export const useCollapsed = () => {
    const context = useContext(CollapsedContext);
    if (!context) {
        throw new Error('useCollapsed must be used within a CollapsedProvider');
    }
    return context;
};

export const CollapsedProvider = ({ children }: { children: React.ReactNode }) => {
    const [isCollapsed, setIsCollapsed] = useState(false);
    return (
        <CollapsedContext.Provider value={{ isCollapsed, setIsCollapsed }}>
            {children}
        </CollapsedContext.Provider>
    );
};
