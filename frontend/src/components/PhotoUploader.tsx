"use client";

import React, { useCallback, useRef, useState } from "react";

interface PhotoUploaderProps {
    onFileSelected: (file: File, preview: string) => void;
    disabled?: boolean;
}

export default function PhotoUploader({
    onFileSelected,
    disabled,
}: PhotoUploaderProps) {
    const [dragOver, setDragOver] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    const handleFile = useCallback(
        (file: File) => {
            if (!file.type.startsWith("image/")) return;
            const reader = new FileReader();
            reader.onload = () => {
                onFileSelected(file, reader.result as string);
            };
            reader.readAsDataURL(file);
        },
        [onFileSelected]
    );

    const onDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            setDragOver(false);
            if (disabled) return;
            const file = e.dataTransfer.files[0];
            if (file) handleFile(file);
        },
        [disabled, handleFile]
    );

    const onDragOver = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            if (!disabled) setDragOver(true);
        },
        [disabled]
    );

    const onDragLeave = useCallback(() => setDragOver(false), []);

    const onClickSelect = useCallback(() => {
        if (!disabled) inputRef.current?.click();
    }, [disabled]);

    const onInputChange = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
        },
        [handleFile]
    );

    return (
        <div
            className={`drop-zone ${dragOver ? "drag-over" : ""}`}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onClick={onClickSelect}
            style={{
                padding: "48px 32px",
                textAlign: "center",
                opacity: disabled ? 0.5 : 1,
                pointerEvents: disabled ? "none" : "auto",
            }}
        >
            <input
                ref={inputRef}
                type="file"
                accept="image/*"
                onChange={onInputChange}
                style={{ display: "none" }}
            />

            {/* Upload Icon */}
            <div
                style={{
                    fontSize: "48px",
                    marginBottom: "16px",
                    filter: dragOver ? "brightness(1.3)" : "none",
                    transition: "filter 0.3s",
                }}
            >
                📸
            </div>

            <p
                style={{
                    fontSize: "18px",
                    fontWeight: 600,
                    color: "var(--text-primary)",
                    marginBottom: "8px",
                }}
            >
                {dragOver ? "Drop it here!" : "Drop your photo here"}
            </p>

            <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
                or{" "}
                <span
                    style={{ color: "var(--accent-purple)", textDecoration: "underline" }}
                >
                    browse files
                </span>{" "}
                · JPG, PNG up to 10 MB
            </p>
        </div>
    );
}
