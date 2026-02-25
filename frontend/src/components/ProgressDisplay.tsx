"use client";

import React from "react";

const STAGES = [
    { emoji: "📸", label: "Photo Scout", description: "Finding reference photos…" },
    { emoji: "✍️", label: "Prompt Architect", description: "Analyzing & writing prompt…" },
    { emoji: "🎨", label: "Image Enhancer", description: "Generating enhanced image…" },
    { emoji: "🔍", label: "Quality Inspector", description: "Evaluating realism…" },
    { emoji: "🖌️", label: "Post-Production", description: "Applying final touches…" },
];

interface ProgressDisplayProps {
    visible: boolean;
    currentStage: number; // 0-4
    stageMessage?: string;
    progress: number; // 0-100
}

export default function ProgressDisplay({
    visible,
    currentStage,
    stageMessage,
    progress,
}: ProgressDisplayProps) {
    if (!visible) return null;

    return (
        <div className="glass-card slide-up" style={{ padding: "28px 24px" }}>
            {/* Overall Progress Bar */}
            <div style={{ marginBottom: "24px" }}>
                <div
                    style={{
                        display: "flex",
                        justifyContent: "space-between",
                        marginBottom: "8px",
                    }}
                >
                    <span
                        style={{
                            fontSize: "13px",
                            fontWeight: 600,
                            color: "var(--text-secondary)",
                            textTransform: "uppercase",
                            letterSpacing: "0.05em",
                        }}
                    >
                        Enhancing your photo
                    </span>
                    <span
                        style={{
                            fontSize: "13px",
                            color: "var(--text-muted)",
                            fontFamily: "var(--font-geist-mono)",
                        }}
                    >
                        {Math.round(progress)}%
                    </span>
                </div>
                <div className="progress-track" style={{ height: "6px" }}>
                    <div
                        className="progress-fill"
                        style={{ width: `${progress}%`, height: "100%" }}
                    />
                </div>
            </div>

            {/* Stage Dots + Labels */}
            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    gap: "4px",
                }}
            >
                {STAGES.map((stage, i) => {
                    const state = i < currentStage ? "done" : i === currentStage ? "active" : "pending";
                    return (
                        <div
                            key={stage.label}
                            style={{
                                flex: 1,
                                display: "flex",
                                flexDirection: "column",
                                alignItems: "center",
                                gap: "8px",
                                opacity: state === "pending" ? 0.35 : 1,
                                transition: "opacity 0.4s ease",
                            }}
                        >
                            <div className={`stage-dot ${state}`} />
                            <span style={{ fontSize: "18px" }}>{stage.emoji}</span>
                            <span
                                style={{
                                    fontSize: "11px",
                                    fontWeight: state === "active" ? 600 : 400,
                                    color:
                                        state === "active"
                                            ? "var(--text-primary)"
                                            : state === "done"
                                                ? "#22c55e"
                                                : "var(--text-muted)",
                                    textAlign: "center",
                                    lineHeight: 1.3,
                                }}
                            >
                                {stage.label}
                            </span>
                        </div>
                    );
                })}
            </div>

            {/* Current Stage Message */}
            {stageMessage && (
                <div
                    style={{
                        marginTop: "20px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: "10px",
                    }}
                >
                    <div className="spinner" />
                    <span style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
                        {stageMessage}
                    </span>
                </div>
            )}
        </div>
    );
}
