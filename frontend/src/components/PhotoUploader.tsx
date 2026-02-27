"use client";

import React, { useCallback, useRef, useState } from "react";

interface PhotoUploaderProps {
    onFilesSelected: (files: { file: File; preview: string }[]) => void;
    currentCount: number;
    disabled?: boolean;
}

const MAX_PHOTOS = 5;

export default function PhotoUploader({
    onFilesSelected,
    currentCount,
    disabled,
}: PhotoUploaderProps) {
    const [dragOver, setDragOver] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    const handleFiles = useCallback(
        (fileList: FileList | File[]) => {
            const files = Array.from(fileList).filter((f) =>
                f.type.startsWith("image/")
            );
            const remaining = MAX_PHOTOS - currentCount;
            const toProcess = files.slice(0, remaining);
            if (toProcess.length === 0) return;

            let processed: { file: File; preview: string }[] = [];
            let count = 0;

            toProcess.forEach((file) => {
                const reader = new FileReader();
                reader.onload = () => {
                    processed.push({ file, preview: reader.result as string });
                    count++;
                    if (count === toProcess.length) {
                        onFilesSelected(processed);
                    }
                };
                reader.readAsDataURL(file);
            });
        },
        [onFilesSelected, currentCount]
    );

    const onDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            setDragOver(false);
            if (disabled) return;
            handleFiles(e.dataTransfer.files);
        },
        [disabled, handleFiles]
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
            if (e.target.files) handleFiles(e.target.files);
            e.target.value = "";
        },
        [handleFiles]
    );

    const spotsLeft = MAX_PHOTOS - currentCount;

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
                opacity: disabled || spotsLeft <= 0 ? 0.5 : 1,
                pointerEvents: disabled || spotsLeft <= 0 ? "none" : "auto",
            }}
        >
            <input
                ref={inputRef}
                type="file"
                accept="image/*"
                multiple
                onChange={onInputChange}
                style={{ display: "none" }}
            />

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
                {dragOver
                    ? "Drop them here!"
                    : currentCount === 0
                        ? "Drop your photos here"
                        : `Add more photos (${spotsLeft} spot${spotsLeft !== 1 ? "s" : ""} left)`}
            </p>

            <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
                or{" "}
                <span
                    style={{ color: "var(--accent-purple)", textDecoration: "underline" }}
                >
                    browse files
                </span>{" "}
                · Up to {MAX_PHOTOS} photos · JPG, PNG
            </p>
        </div>
    );
}
