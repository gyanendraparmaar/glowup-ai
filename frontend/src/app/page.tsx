"use client";

import React, { useState, useCallback, useRef, useEffect } from "react";
import PhotoUploader from "@/components/PhotoUploader";
import ProgressDisplay from "@/components/ProgressDisplay";
import ReviewDashboard from "@/components/ReviewDashboard";
import { Sparkles, UploadCloud, AlertCircle } from "lucide-react";

type AppState = "idle" | "uploaded" | "processing" | "done" | "error";

interface PhotoEntry {
  file: File;
  preview: string;
}

export interface ProfileReview {
  photo_review: {
    id: number;
    critique: string;
    is_keeper: boolean;
  }[];
  prompt_review: {
    question: string;
    critique: string;
    suggested_rewrite: string;
  }[];
  overall_score: number;
  actionable_advice: string[];
  suggested_openers: string[];
  suggested_prompts?: {
    prompt_name: string;
    suggested_answer: string;
  }[];
}

const STAGE_MESSAGES = [
  "🔍 Vision AI extracting text and analyzing photos...",
  "🧠 Weighing extracted data against 2024/2025 Hinge meta...",
  "✍️ Crafting brutally honest, actionable advice...",
  "🎯 Generating custom opening lines for your vibe...",
  "✨ Finalizing your Profile Review Dashboard...",
];

export default function Home() {
  /* ── State ── */
  const [appState, setAppState] = useState<AppState>("idle");
  const [photos, setPhotos] = useState<PhotoEntry[]>([]);

  const [stage, setStage] = useState(0);
  const [progress, setProgress] = useState(0);
  const [stageMessage, setStageMessage] = useState("");

  const [reviewData, setReviewData] = useState<ProfileReview | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  const progressTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => {
      if (progressTimer.current) clearInterval(progressTimer.current);
    };
  }, []);

  /* ── Photos Selected ── */
  const handleFilesSelected = useCallback(
    (newFiles: { file: File; preview: string }[]) => {
      setPhotos((prev) => [...prev, ...newFiles].slice(0, 6)); // Hinge has max 6
      setAppState("uploaded");
      setReviewData(null);
      setErrorMsg("");
    },
    []
  );

  /* ── Remove a photo ── */
  const handleRemovePhoto = useCallback((index: number) => {
    setPhotos((prev) => {
      const next = prev.filter((_, i) => i !== index);
      if (next.length === 0) setAppState("idle");
      return next;
    });
  }, []);

  /* ── Progress Simulation ── */
  const startProgressSimulation = useCallback(() => {
    let currentProgress = 0;
    let currentStage = 0;
    setStage(0);
    setProgress(0);
    setStageMessage(STAGE_MESSAGES[0]);

    progressTimer.current = setInterval(() => {
      const increment = Math.random() * 2 + 0.5;
      currentProgress = Math.min(currentProgress + increment, 96);
      setProgress(currentProgress);

      const newStage =
        currentProgress < 20 ? 0
          : currentProgress < 40 ? 1
            : currentProgress < 65 ? 2
              : currentProgress < 85 ? 3
                : 4;

      if (newStage !== currentStage) {
        currentStage = newStage;
        setStage(currentStage);
        setStageMessage(STAGE_MESSAGES[currentStage]);
      }
    }, 800);
  }, []);

  const stopProgressSimulation = useCallback(() => {
    if (progressTimer.current) {
      clearInterval(progressTimer.current);
      progressTimer.current = null;
    }
    setProgress(100);
    setStage(5);
    setStageMessage("");
  }, []);

  /* ── Get Review ── */
  const handleGetReview = useCallback(async () => {
    if (photos.length === 0) return;

    setAppState("processing");
    setReviewData(null);
    setErrorMsg("");
    startProgressSimulation();

    try {
      const formData = new FormData();
      photos.forEach(p => {
        formData.append("files", p.file);
      });

      const response = await fetch("/api/review", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || `Server error ${response.status}`);
      }

      const data = await response.json();
      stopProgressSimulation();
      setReviewData(data.review);
      setAppState("done");

    } catch (err) {
      stopProgressSimulation();
      setErrorMsg(err instanceof Error ? err.message : "Something went wrong parsing the review.");
      setAppState("error");
    }
  }, [photos, startProgressSimulation, stopProgressSimulation]);

  /* ── Reset ── */
  const handleReset = useCallback(() => {
    setAppState("idle");
    setPhotos([]);
    setReviewData(null);
    setErrorMsg("");
    setProgress(0);
    setStage(0);
    setStageMessage("");
  }, []);

  const isProcessing = appState === "processing";

  return (
    <main
      style={{
        position: "relative",
        zIndex: 1,
        maxWidth: "1000px",
        margin: "0 auto",
        padding: "48px 20px 80px",
      }}
    >
      {/* ═══ Hero ═══ */}
      <header style={{ textAlign: "center", marginBottom: "40px" }}>
        <div style={{ display: "flex", justifyContent: "center", marginBottom: "16px" }}>
          <div style={{
            background: "linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(236, 72, 153, 0.2))",
            padding: "16px",
            borderRadius: "50%",
            boxShadow: "0 0 30px rgba(168, 85, 247, 0.3)"
          }}>
            <Sparkles size={40} className="text-purple-400" />
          </div>
        </div>
        <h1 style={{ fontSize: "42px", fontWeight: 800, lineHeight: 1.15, marginBottom: "16px" }}>
          <span className="gradient-text">Hinge Profile Reviewer</span>
        </h1>
        <p style={{ fontSize: "18px", color: "var(--text-secondary)", maxWidth: "500px", margin: "0 auto", lineHeight: 1.6 }}>
          Upload screenshots of your Hinge profile. Our two-stage AI pipeline (Groq Vision + Gemini Strategy) will critique your photos, roast your prompts, and give you actionable advice based on the 2024/2025 dating meta.
        </p>
      </header>

      {/* ═══ Main Card ═══ */}
      {appState !== "done" && (
        <div className="glass-card" style={{ padding: "32px", marginBottom: "24px" }}>
          {/* Photo Thumbnails */}
          {photos.length > 0 && (
            <div className="fade-in" style={{ marginBottom: "20px" }}>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(3, 1fr)",
                  gap: "12px",
                  marginBottom: "24px",
                }}
              >
                {photos.map((photo, i) => (
                  <div
                    key={i}
                    style={{
                      position: "relative",
                      borderRadius: "16px",
                      overflow: "hidden",
                      border: "1px solid var(--border-subtle)",
                      aspectRatio: "9/16", // Standard phone screenshot ratio
                      boxShadow: "0 10px 30px rgba(0,0,0,0.2)"
                    }}
                  >
                    <img
                      src={photo.preview}
                      alt={`Screenshot ${i + 1}`}
                      style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
                    />
                    {!isProcessing && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemovePhoto(i);
                        }}
                        style={{
                          position: "absolute",
                          top: "8px",
                          right: "8px",
                          width: "28px",
                          height: "28px",
                          borderRadius: "50%",
                          background: "rgba(0,0,0,0.8)",
                          border: "1px solid rgba(255,255,255,0.2)",
                          color: "white",
                          fontSize: "14px",
                          cursor: "pointer",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        ✕
                      </button>
                    )}
                    <div
                      style={{
                        position: "absolute",
                        bottom: "8px",
                        left: "8px",
                        background: "rgba(0,0,0,0.8)",
                        color: "white",
                        fontSize: "12px",
                        fontWeight: 600,
                        padding: "4px 8px",
                        borderRadius: "8px",
                        border: "1px solid rgba(255,255,255,0.1)",
                      }}
                    >
                      Shot {i + 1}
                    </div>
                  </div>
                ))}

                {/* Add More Slot */}
                {photos.length < 6 && !isProcessing && (
                  <div
                    onClick={() => {
                      const input = document.createElement("input");
                      input.type = "file";
                      input.accept = "image/*";
                      input.multiple = true;
                      input.onchange = (e) => {
                        const files = (e.target as HTMLInputElement).files;
                        if (!files) return;
                        const fileArray = Array.from(files)
                          .filter((f) => f.type.startsWith("image/"))
                          .slice(0, 6 - photos.length);
                        let processed: { file: File; preview: string }[] = [];
                        let count = 0;
                        fileArray.forEach((file) => {
                          const reader = new FileReader();
                          reader.onload = () => {
                            processed.push({ file, preview: reader.result as string });
                            count++;
                            if (count === fileArray.length) handleFilesSelected(processed);
                          };
                          reader.readAsDataURL(file);
                        });
                      };
                      input.click();
                    }}
                    style={{
                      borderRadius: "16px",
                      border: "2px dashed rgba(168, 85, 247, 0.3)",
                      aspectRatio: "9/16",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                      gap: "8px",
                      background: "rgba(168, 85, 247, 0.05)"
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = "var(--accent-purple)";
                      e.currentTarget.style.background = "rgba(168, 85, 247, 0.1)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = "rgba(168, 85, 247, 0.3)";
                      e.currentTarget.style.background = "rgba(168, 85, 247, 0.05)";
                    }}
                  >
                    <UploadCloud size={32} color="var(--text-muted)" />
                    <span style={{ fontSize: "14px", color: "var(--text-secondary)", fontWeight: 500 }}>
                      Add Screenshot
                    </span>
                  </div>
                )}
              </div>

              {/* Get Review Button */}
              {!isProcessing && (
                <button
                  className="btn-gradient"
                  onClick={handleGetReview}
                  style={{
                    width: "100%",
                    padding: "18px 24px",
                    fontSize: "18px",
                    fontWeight: 700,
                    marginTop: "16px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "10px",
                    borderRadius: "16px",
                    boxShadow: "0 10px 25px rgba(236, 72, 153, 0.3)"
                  }}
                >
                  <Sparkles size={20} />
                  Analyze {photos.length} Screenshot{photos.length > 1 ? "s" : ""}
                </button>
              )}
            </div>
          )}

          {/* Drop Zone (when no photos) */}
          {photos.length === 0 && (
            <PhotoUploader
              onFilesSelected={handleFilesSelected}
              currentCount={photos.length}
              disabled={isProcessing}
            />
          )}
        </div>
      )}

      {/* ═══ Progress ═══ */}
      {isProcessing && (
        <div className="mt-8">
          <ProgressDisplay
            visible={true}
            currentStage={stage}
            stageMessage={stageMessage}
            progress={progress}
          />
        </div>
      )}

      {/* ═══ Error ═══ */}
      {appState === "error" && (
        <div className="glass-card fade-in" style={{ padding: "24px", borderColor: "rgba(239, 68, 68, 0.3)", marginTop: "16px" }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "16px" }}>
            <AlertCircle size={32} color="#ef4444" style={{ flexShrink: 0 }} />
            <div>
              <p style={{ fontSize: "18px", fontWeight: 700, marginBottom: "8px", color: "#ef4444" }}>
                Analysis Failed
              </p>
              <p style={{ fontSize: "15px", color: "var(--text-secondary)", marginBottom: "20px", lineHeight: 1.5 }}>
                {errorMsg}
              </p>
              <button className="btn-gradient" onClick={handleGetReview} style={{ padding: "10px 24px", fontSize: "15px", borderRadius: "10px" }}>
                🔄 Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ═══ Review Dashboard Results ═══ */}
      {appState === "done" && reviewData && (
        <ReviewDashboard review={reviewData} screenshots={photos.map(p => p.preview)} onReset={handleReset} />
      )}

      {/* ═══ Footer ═══ */}
      <footer style={{ textAlign: "center", marginTop: "64px", fontSize: "13px", color: "var(--text-muted)", opacity: 0.7 }}>
        <p>Architected with Next.js & Tailwind CSS.</p>
        <p style={{ marginTop: "6px" }}>Powered by Groq Vision 90B & Gemini 2.5 Pro.</p>
      </footer>
    </main>
  );
}
