"use client";

import React from "react";

const VIBES = [
    { id: "coffee_shop", emoji: "☕", label: "Café" },
    { id: "outdoors", emoji: "🏔️", label: "Outdoors" },
    { id: "dog_lover", emoji: "🐕", label: "Pets" },
    { id: "formal", emoji: "🥂", label: "Formal" },
    { id: "creative", emoji: "🎸", label: "Creative" },
    { id: "fitness", emoji: "💪", label: "Fitness" },
];

interface VibeSelectorProps {
    selected: string | null;
    onSelect: (vibe: string | null) => void;
    disabled?: boolean;
}

export default function VibeSelector({
    selected,
    onSelect,
    disabled,
}: VibeSelectorProps) {
    const [open, setOpen] = React.useState(false);

    return (
        <div style={{ opacity: disabled ? 0.5 : 1 }}>
            <button
                onClick={() => setOpen(!open)}
                disabled={disabled}
                style={{
                    background: "none",
                    border: "none",
                    color: "var(--text-secondary)",
                    fontSize: "14px",
                    cursor: disabled ? "not-allowed" : "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "8px 0",
                    transition: "color 0.2s",
                }}
                onMouseEnter={(e) =>
                    !disabled &&
                    ((e.target as HTMLElement).style.color = "var(--text-primary)")
                }
                onMouseLeave={(e) =>
                    ((e.target as HTMLElement).style.color = "var(--text-secondary)")
                }
            >
                <span
                    style={{
                        transform: open ? "rotate(90deg)" : "rotate(0deg)",
                        transition: "transform 0.2s",
                        display: "inline-block",
                    }}
                >
                    ▸
                </span>
                Optional: Change the vibe
                {selected && (
                    <span
                        style={{
                            background: "rgba(168, 85, 247, 0.2)",
                            color: "var(--accent-purple)",
                            padding: "2px 8px",
                            borderRadius: "6px",
                            fontSize: "12px",
                            fontWeight: 600,
                        }}
                    >
                        {VIBES.find((v) => v.id === selected)?.emoji}{" "}
                        {VIBES.find((v) => v.id === selected)?.label}
                    </span>
                )}
            </button>

            {open && (
                <div
                    className="fade-in"
                    style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(3, 1fr)",
                        gap: "10px",
                        marginTop: "8px",
                    }}
                >
                    {VIBES.map((vibe) => (
                        <button
                            key={vibe.id}
                            className={`vibe-card ${selected === vibe.id ? "selected" : ""}`}
                            disabled={disabled}
                            onClick={() =>
                                onSelect(selected === vibe.id ? null : vibe.id)
                            }
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "8px",
                                fontSize: "14px",
                                color: "var(--text-primary)",
                            }}
                        >
                            <span style={{ fontSize: "20px" }}>{vibe.emoji}</span>
                            {vibe.label}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
