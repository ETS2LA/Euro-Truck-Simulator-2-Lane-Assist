declare const require: {
    context: (path: string, deep?: boolean, filter?: RegExp) => {
        keys: () => string[];
        <T>(id: string): T;
    };
};