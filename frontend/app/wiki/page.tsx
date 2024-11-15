export default function Wiki() {
    return (
        <iframe 
            className="absolute w-full h-full rounded-md" 
            src="https://ets2la.github.io/documentation/"
            style={{ // clear header
                transform: 'translateY(-80px)',
                height: 'calc(100% + 80px)'
            }}
        />
    )
}