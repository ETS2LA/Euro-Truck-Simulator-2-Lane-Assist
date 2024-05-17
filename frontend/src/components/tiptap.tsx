import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'

const Tiptap = ({ className }: { className?: string }) => {
    className = className + " !outline-none" || '!outline-none'
    const editor = useEditor({
        extensions: [
            StarterKit,
        ],
        content: 'You can use markdown keybindings to format your text! (ctrl+b, ctrl+i)<br>You can also use markdown directly (e.g. # H1, ## H2...)',
        editorProps: {
            attributes: {
                class: className,

            },
        },
    })

    return (
        <EditorContent editor={editor} className={className + " !outline-none"} />
    )
}

export default Tiptap