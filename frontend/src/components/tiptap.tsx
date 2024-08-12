"use client"
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import { useEffect } from 'react'

const Tiptap = ({ className, onUpdate }: { className?: string, onUpdate:any }) => {
    className = className + " !outline-none" || '!outline-none'
    const editor = useEditor({
        extensions: [
            StarterKit,
        ],
        editorProps: {
            attributes: {
                class: className,

            },
        },
    })

    useEffect(() => {
        if (editor) {
            editor.on("update", onUpdate);
        }
    }, [editor, onUpdate]);

    return (
        <EditorContent editor={editor} className={className + " !outline-none"} />
    )
}

export default Tiptap