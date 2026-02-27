"use client";

import React from "react";

interface PhotoResult {
    originalUrl: string;
    enhancedUrls: string[];
}

interface ResultGalleryProps {
    results: PhotoResult[];
    visible: boolean;
}

export default function ResultGallery({
    results,
    visible,
}: ResultGalleryProps) {
    if (!visible || results.length === 0) return null;

    const allEnhanced = results.flatMap((r) => r.enhancedUrls);

    const handleDownload = async (url: string, name: string) => {
        try {
            const response = await fetch(url);
            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = blobUrl;
            a.download = name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(blobUrl);
        } catch {
            window.open(url, "_blank");
        }
    };

    const handleDownloadAll = async () => {
        for (let r = 0; r < results.length; r++) {
            for (let i = 0; i < results[r].enhancedUrls.length; i++) {
                await handleDownload(
                    results[r].enhancedUrls[i],
                    `glowup-photo${r + 1}-v${i + 1}.jpg`
                );
                await new Promise((resolve) => setTimeout(resolve, 400));
            }
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
                    marginBottom: "24px",
                }}
            >
                <div>
                    <h2 style={{ fontSize: "24px", fontWeight: 700, marginBottom: "4px" }}>
                        ✨ Your Enhanced Photos
                    </h2>
                    <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
                        {results.length} photo{results.length > 1 ? "s" : ""} ·{" "}
                        {allEnhanced.length} variation{allEnhanced.length > 1 ? "s" : ""}
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

            {/* Per-photo result groups */}
            {results.map((photoResult, photoIdx) => (
                <div
                    key={photoIdx}
                    className="fade-in"
                    style={{
                        marginBottom: photoIdx < results.length - 1 ? "32px" : 0,
                        animationDelay: `${photoIdx * 0.2}s`,
                        opacity: 0,
                    }}
                >
                    {results.length > 1 && (
                        <p
                            style={{
                                fontSize: "13px",
                                fontWeight: 600,
                                color: "var(--text-muted)",
                                textTransform: "uppercase",
                                letterSpacing: "0.05em",
                                marginBottom: "12px",
                            }}
                        >
                            Photo {photoIdx + 1}
                        </p>
                    )}

                    <div
                        style={{
                            display: "grid",
                            gridTemplateColumns: `repeat(${Math.min(photoResult.enhancedUrls.length + 1, 3)}, 1fr)`,
                            gap: "14px",
                        }}
                    >
                        {/* Original */}
                        <div className="glass-card" style={{ overflow: "hidden" }}>
                            <div
                                style={{
                                    padding: "6px 12px",
                                    borderBottom: "1px solid var(--border-subtle)",
                                    fontSize: "11px",
                                    fontWeight: 600,
                                    color: "var(--text-muted)",
                                    textTransform: "uppercase",
                                    letterSpacing: "0.05em",
                                }}
                            >
                                Original
                            </div>
                            <img
                                src={photoResult.originalUrl}
                                alt={`Original photo ${photoIdx + 1}`}
                                style={{ width: "100%", height: "auto", display: "block" }}
                            />
                        </div>

                        {/* Enhanced variations */}
                        {photoResult.enhancedUrls.map((url, i) => (
                            <div
                                key={i}
                                className="result-card glass-card fade-in"
                                style={{ animationDelay: `${(photoIdx * 3 + i) * 0.12}s`, opacity: 0 }}
                            >
                                <div
                                    style={{
                                        padding: "6px 12px",
                                        borderBottom: "1px solid var(--border-subtle)",
                                        display: "flex",
                                        justifyContent: "space-between",
                                        alignItems: "center",
                                    }}
                                >
                                    <span
                                        style={{
                                            fontSize: "11px",
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
                                        alt={`Enhanced photo ${photoIdx + 1} variation ${i + 1}`}
                                        style={{ width: "100%", height: "auto", display: "block" }}
                                    />
                                    <div className="overlay">
                                        <button
                                            className="btn-gradient"
                                            onClick={() =>
                                                handleDownload(url, `glowup-photo${photoIdx + 1}-v${i + 1}.jpg`)
                                            }
                                            style={{
                                                padding: "8px 16px",
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
            ))}
        </div>
    );
}
