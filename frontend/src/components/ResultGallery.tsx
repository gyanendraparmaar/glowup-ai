"use client";

import React from "react";

interface ResultGalleryProps {
    originalUrl: string;
    enhancedUrls: string[];
    visible: boolean;
}

export default function ResultGallery({
    originalUrl,
    enhancedUrls,
    visible,
}: ResultGalleryProps) {
    if (!visible || enhancedUrls.length === 0) return null;

    const handleDownload = async (url: string, index: number) => {
        try {
            const response = await fetch(url);
            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = blobUrl;
            a.download = `glowup-enhanced-${index + 1}.jpg`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(blobUrl);
        } catch {
            window.open(url, "_blank");
        }
    };

    const handleDownloadAll = async () => {
        for (let i = 0; i < enhancedUrls.length; i++) {
            await handleDownload(enhancedUrls[i], i);
            // Small delay between downloads
            await new Promise((r) => setTimeout(r, 500));
        }
    };

    return (
        <div className="slide-up" style={{ marginTop: "32px" }}>
            {/* Header */}
            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "20px",
                }}
            >
                <div>
                    <h2
                        style={{
                            fontSize: "24px",
                            fontWeight: 700,
                            marginBottom: "4px",
                        }}
                    >
                        ✨ Your Enhanced Photos
                    </h2>
                    <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
                        {enhancedUrls.length} variation{enhancedUrls.length > 1 ? "s" : ""}{" "}
                        generated
                    </p>
                </div>

                <button
                    className="btn-gradient"
                    onClick={handleDownloadAll}
                    style={{
                        padding: "10px 20px",
                        fontSize: "14px",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                    }}
                >
                    📦 Download All
                </button>
            </div>

            {/* Results Grid */}
            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: `repeat(${Math.min(enhancedUrls.length + 1, 3)}, 1fr)`,
                    gap: "16px",
                }}
            >
                {/* Original */}
                <div className="glass-card" style={{ overflow: "hidden" }}>
                    <div
                        style={{
                            padding: "8px 12px",
                            borderBottom: "1px solid var(--border-subtle)",
                            fontSize: "12px",
                            fontWeight: 600,
                            color: "var(--text-muted)",
                            textTransform: "uppercase",
                            letterSpacing: "0.05em",
                        }}
                    >
                        Original
                    </div>
                    <img
                        src={originalUrl}
                        alt="Original photo"
                        style={{
                            width: "100%",
                            height: "auto",
                            display: "block",
                        }}
                    />
                </div>

                {/* Enhanced */}
                {enhancedUrls.map((url, i) => (
                    <div
                        key={i}
                        className="result-card glass-card fade-in"
                        style={{ animationDelay: `${i * 0.15}s`, opacity: 0 }}
                    >
                        <div
                            style={{
                                padding: "8px 12px",
                                borderBottom: "1px solid var(--border-subtle)",
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                            }}
                        >
                            <span
                                style={{
                                    fontSize: "12px",
                                    fontWeight: 600,
                                    textTransform: "uppercase",
                                    letterSpacing: "0.05em",
                                }}
                            >
                                <span className="gradient-text">Enhanced #{i + 1}</span>
                            </span>
                        </div>
                        <div style={{ position: "relative" }}>
                            <img
                                src={url}
                                alt={`Enhanced variation ${i + 1}`}
                                style={{
                                    width: "100%",
                                    height: "auto",
                                    display: "block",
                                }}
                            />
                            <div className="overlay">
                                <button
                                    className="btn-gradient"
                                    onClick={() => handleDownload(url, i)}
                                    style={{
                                        padding: "8px 18px",
                                        fontSize: "13px",
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "6px",
                                    }}
                                >
                                    📥 Download
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
