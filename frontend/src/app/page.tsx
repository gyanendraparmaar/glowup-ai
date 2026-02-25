"use client";

import React, { useState, useCallback, useRef, useEffect } from "react";
import PhotoUploader from "@/components/PhotoUploader";
import VibeSelector from "@/components/VibeSelector";
import ProgressDisplay from "@/components/ProgressDisplay";
import ResultGallery from "@/components/ResultGallery";

type AppState = "idle" | "uploaded" | "processing" | "done" | "error";

interface EnhanceResult {
  job_id: string;
  images: string[];
  original: string;
}

const STAGE_MESSAGES = [
  "📸 Scouting reference photos from the web…",
  "✍️ Analyzing photo & crafting enhancement prompt…",
  "🎨 Generating enhanced image with Nano Banana Pro…",
  "🔍 Quality inspector evaluating realism…",
  "🖌️ Applying post-production realism touches…",
];

export default function Home() {
  /* ── State ── */
  const [appState, setAppState] = useState<AppState>("idle");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [selectedVibe, setSelectedVibe] = useState<string | null>(null);
  const [numVariations, setNumVariations] = useState(2);

  const [stage, setStage] = useState(0);
  const [progress, setProgress] = useState(0);
  const [stageMessage, setStageMessage] = useState("");

  const [result, setResult] = useState<EnhanceResult | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  const progressTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  /* ── Cleanup timer ── */
  useEffect(() => {
    return () => {
      if (progressTimer.current) clearInterval(progressTimer.current);
    };
  }, []);

  /* ── Photo Selected ── */
  const handleFileSelected = useCallback((file: File, preview: string) => {
    setSelectedFile(file);
    setPreviewUrl(preview);
    setAppState("uploaded");
    setResult(null);
    setErrorMsg("");
  }, []);

  /* ── Simulated Progress ── */
  const startProgressSimulation = useCallback(() => {
    let currentProgress = 0;
    let currentStage = 0;

    setStage(0);
    setProgress(0);
    setStageMessage(STAGE_MESSAGES[0]);

    progressTimer.current = setInterval(() => {
      // Slowly increment progress
      const increment = Math.random() * 2 + 0.5;
      currentProgress = Math.min(currentProgress + increment, 92); // Cap at 92% until real completion
      setProgress(currentProgress);

      // Advance stages based on progress thresholds
      const newStage =
        currentProgress < 15
          ? 0
          : currentProgress < 35
            ? 1
            : currentProgress < 60
              ? 2
              : currentProgress < 80
                ? 3
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
    setStage(5); // all done
    setStageMessage("");
  }, []);

  /* ── Enhance ── */
  const handleEnhance = useCallback(async () => {
    if (!selectedFile) return;

    setAppState("processing");
    setResult(null);
    setErrorMsg("");
    startProgressSimulation();

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      if (selectedVibe) formData.append("vibe", selectedVibe);
      formData.append("num_variations", String(numVariations));

      const response = await fetch("/api/enhance", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || `Server error ${response.status}`);
      }

      const data = await response.json();

      stopProgressSimulation();
      setResult(data);
      setAppState("done");
    } catch (err) {
      stopProgressSimulation();
      setErrorMsg(err instanceof Error ? err.message : "Something went wrong");
      setAppState("error");
    }
  }, [selectedFile, selectedVibe, numVariations, startProgressSimulation, stopProgressSimulation]);

  /* ── Reset ── */
  const handleReset = useCallback(() => {
    setAppState("idle");
    setSelectedFile(null);
    setPreviewUrl("");
    setSelectedVibe(null);
    setResult(null);
    setErrorMsg("");
    setProgress(0);
    setStage(0);
    setStageMessage("");
  }, []);

  /* ── Render ── */
  const isProcessing = appState === "processing";

  return (
    <main
      style={{
        position: "relative",
        zIndex: 1,
        maxWidth: "960px",
        margin: "0 auto",
        padding: "48px 20px 80px",
      }}
    >
      {/* ═══ Hero ═══ */}
      <header style={{ textAlign: "center", marginBottom: "48px" }}>
        <div
          style={{
            fontSize: "48px",
            marginBottom: "12px",
          }}
        >
          🔥
        </div>
        <h1
          style={{
            fontSize: "36px",
            fontWeight: 800,
            lineHeight: 1.15,
            marginBottom: "12px",
          }}
        >
          <span className="gradient-text">GlowUp AI</span>
        </h1>
        <p
          style={{
            fontSize: "16px",
            color: "var(--text-secondary)",
            maxWidth: "440px",
            margin: "0 auto",
            lineHeight: 1.6,
          }}
        >
          Upload your photo → 5 AI agents enhance it → Download stunning,
          realistic results
        </p>
      </header>

      {/* ═══ Main Card ═══ */}
      <div
        className="glass-card"
        style={{
          padding: "32px",
          marginBottom: "24px",
        }}
      >
        {/* Upload Area or Preview */}
        {!previewUrl ? (
          <PhotoUploader
            onFileSelected={handleFileSelected}
            disabled={isProcessing}
          />
        ) : (
          <div className="fade-in">
            {/* Preview Image */}
            <div
              style={{
                borderRadius: "14px",
                overflow: "hidden",
                marginBottom: "20px",
                position: "relative",
              }}
            >
              <img
                src={previewUrl}
                alt="Your uploaded photo"
                style={{
                  width: "100%",
                  maxHeight: "400px",
                  objectFit: "contain",
                  display: "block",
                  background: "rgba(0,0,0,0.3)",
                }}
              />
              {!isProcessing && appState !== "done" && (
                <button
                  onClick={handleReset}
                  style={{
                    position: "absolute",
                    top: "12px",
                    right: "12px",
                    background: "rgba(0,0,0,0.6)",
                    backdropFilter: "blur(8px)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    color: "var(--text-primary)",
                    borderRadius: "8px",
                    padding: "6px 12px",
                    fontSize: "13px",
                    cursor: "pointer",
                    transition: "background 0.2s",
                  }}
                  onMouseEnter={(e) =>
                  ((e.target as HTMLElement).style.background =
                    "rgba(0,0,0,0.8)")
                  }
                  onMouseLeave={(e) =>
                  ((e.target as HTMLElement).style.background =
                    "rgba(0,0,0,0.6)")
                  }
                >
                  ✕ Change photo
                </button>
              )}
            </div>

            {/* Vibe Selector */}
            {appState === "uploaded" && (
              <VibeSelector
                selected={selectedVibe}
                onSelect={setSelectedVibe}
                disabled={isProcessing}
              />
            )}

            {/* Variations Slider */}
            {appState === "uploaded" && (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  marginTop: "16px",
                  padding: "0 4px",
                }}
              >
                <span
                  style={{ fontSize: "13px", color: "var(--text-secondary)" }}
                >
                  Variations:
                </span>
                <input
                  type="range"
                  min={1}
                  max={4}
                  value={numVariations}
                  onChange={(e) => setNumVariations(Number(e.target.value))}
                  style={{ flex: 1, accentColor: "var(--accent-purple)" }}
                />
                <span
                  style={{
                    fontSize: "14px",
                    fontWeight: 600,
                    color: "var(--text-primary)",
                    minWidth: "16px",
                    textAlign: "center",
                  }}
                >
                  {numVariations}
                </span>
              </div>
            )}

            {/* Enhance Button */}
            {appState === "uploaded" && (
              <button
                className="btn-gradient"
                onClick={handleEnhance}
                style={{
                  width: "100%",
                  padding: "16px 24px",
                  fontSize: "17px",
                  marginTop: "20px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                }}
              >
                ✨ Enhance Photo
              </button>
            )}
          </div>
        )}
      </div>

      {/* ═══ Progress ═══ */}
      <ProgressDisplay
        visible={isProcessing}
        currentStage={stage}
        stageMessage={stageMessage}
        progress={progress}
      />

      {/* ═══ Error ═══ */}
      {appState === "error" && (
        <div
          className="glass-card fade-in"
          style={{
            padding: "24px",
            borderColor: "rgba(239, 68, 68, 0.3)",
            marginTop: "16px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "12px",
            }}
          >
            <span style={{ fontSize: "24px" }}>❌</span>
            <div>
              <p
                style={{
                  fontWeight: 600,
                  marginBottom: "4px",
                  color: "#ef4444",
                }}
              >
                Enhancement failed
              </p>
              <p
                style={{
                  fontSize: "14px",
                  color: "var(--text-secondary)",
                  marginBottom: "12px",
                }}
              >
                {errorMsg}
              </p>
              <button
                className="btn-gradient"
                onClick={handleEnhance}
                style={{ padding: "8px 20px", fontSize: "14px" }}
              >
                🔄 Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ═══ Results ═══ */}
      {result && (
        <ResultGallery
          originalUrl={previewUrl}
          enhancedUrls={result.images}
          visible={appState === "done"}
        />
      )}

      {/* ═══ Done — Enhance Another ═══ */}
      {appState === "done" && (
        <div style={{ textAlign: "center", marginTop: "32px" }}>
          <button
            onClick={handleReset}
            style={{
              background: "none",
              border: "1px solid var(--border-subtle)",
              color: "var(--text-secondary)",
              padding: "12px 28px",
              borderRadius: "12px",
              fontSize: "15px",
              cursor: "pointer",
              transition: "all 0.2s",
            }}
            onMouseEnter={(e) => {
              (e.target as HTMLElement).style.borderColor =
                "var(--border-glow)";
              (e.target as HTMLElement).style.color = "var(--text-primary)";
            }}
            onMouseLeave={(e) => {
              (e.target as HTMLElement).style.borderColor =
                "var(--border-subtle)";
              (e.target as HTMLElement).style.color = "var(--text-secondary)";
            }}
          >
            ✨ Enhance Another Photo
          </button>
        </div>
      )}

      {/* ═══ Footer ═══ */}
      <footer
        style={{
          textAlign: "center",
          marginTop: "64px",
          fontSize: "12px",
          color: "var(--text-muted)",
        }}
      >
        <p>
          Powered by 5 AI agents · Nano Banana Pro · Gemini 2.5 Flash & Pro
        </p>
        <p style={{ marginTop: "4px" }}>
          Photos are AI-enhanced. Be transparent on dating apps.
        </p>
      </footer>
    </main>
  );
}
