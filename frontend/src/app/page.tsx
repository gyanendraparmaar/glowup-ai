"use client";

import React, { useState, useCallback, useRef, useEffect } from "react";
import PhotoUploader from "@/components/PhotoUploader";
import VibeSelector from "@/components/VibeSelector";
import ProgressDisplay from "@/components/ProgressDisplay";
import ResultGallery from "@/components/ResultGallery";

type AppState = "idle" | "uploaded" | "processing" | "done" | "error";

interface PhotoEntry {
  file: File;
  preview: string;
}

interface PhotoResult {
  originalUrl: string;
  enhancedUrls: string[];
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
  const [photos, setPhotos] = useState<PhotoEntry[]>([]);
  const [selectedVibe, setSelectedVibe] = useState<string | null>(null);
  const [numVariations, setNumVariations] = useState(2);

  const [stage, setStage] = useState(0);
  const [progress, setProgress] = useState(0);
  const [stageMessage, setStageMessage] = useState("");
  const [processingLabel, setProcessingLabel] = useState("");

  const [results, setResults] = useState<PhotoResult[]>([]);
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
      setPhotos((prev) => [...prev, ...newFiles].slice(0, 5));
      setAppState("uploaded");
      setResults([]);
      setErrorMsg("");
    },
    []
  );

  /* ── Remove a photo ── */
  const handleRemovePhoto = useCallback((index: number) => {
    setPhotos((prev) => {
      const next = prev.filter((_, i) => i !== index);
      if (next.length === 0) return next;
      return next;
    });
    setPhotos((prev) => {
      if (prev.length === 0) {
        setAppState("idle");
      }
      return prev;
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
      currentProgress = Math.min(currentProgress + increment, 92);
      setProgress(currentProgress);
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
    setStage(5);
    setStageMessage("");
  }, []);

  /* ── Enhance All Photos ── */
  const handleEnhance = useCallback(async () => {
    if (photos.length === 0) return;

    setAppState("processing");
    setResults([]);
    setErrorMsg("");

    const allResults: PhotoResult[] = [];

    for (let i = 0; i < photos.length; i++) {
      setProcessingLabel(
        photos.length > 1
          ? `Photo ${i + 1} of ${photos.length}`
          : ""
      );
      startProgressSimulation();

      try {
        const formData = new FormData();
        formData.append("file", photos[i].file);
        if (selectedVibe) formData.append("vibe", selectedVibe);
        formData.append("num_variations", String(numVariations));

        const response = await fetch("/api/enhance", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => null);
          throw new Error(
            errData?.detail || `Server error ${response.status}`
          );
        }

        const data = await response.json();
        stopProgressSimulation();

        allResults.push({
          originalUrl: photos[i].preview,
          enhancedUrls: data.images,
        });
      } catch (err) {
        stopProgressSimulation();
        setErrorMsg(
          `Photo ${i + 1}: ${err instanceof Error ? err.message : "Something went wrong"}`
        );
        setAppState("error");
        setResults(allResults); // show partial results
        return;
      }
    }

    setResults(allResults);
    setProcessingLabel("");
    setAppState("done");
  }, [photos, selectedVibe, numVariations, startProgressSimulation, stopProgressSimulation]);

  /* ── Reset ── */
  const handleReset = useCallback(() => {
    setAppState("idle");
    setPhotos([]);
    setSelectedVibe(null);
    setResults([]);
    setErrorMsg("");
    setProgress(0);
    setStage(0);
    setStageMessage("");
    setProcessingLabel("");
  }, []);

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
        <div style={{ fontSize: "48px", marginBottom: "12px" }}>🔥</div>
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
          Upload up to 5 photos → AI agents enhance them → Download stunning
          results
        </p>
      </header>

      {/* ═══ Main Card ═══ */}
      <div
        className="glass-card"
        style={{ padding: "32px", marginBottom: "24px" }}
      >
        {/* Photo Thumbnails */}
        {photos.length > 0 && (
          <div className="fade-in" style={{ marginBottom: "20px" }}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(5, 1fr)",
                gap: "10px",
                marginBottom: "16px",
              }}
            >
              {photos.map((photo, i) => (
                <div
                  key={i}
                  style={{
                    position: "relative",
                    borderRadius: "12px",
                    overflow: "hidden",
                    border: "1px solid var(--border-subtle)",
                    aspectRatio: "1",
                  }}
                >
                  <img
                    src={photo.preview}
                    alt={`Photo ${i + 1}`}
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                      display: "block",
                    }}
                  />
                  {!isProcessing && appState !== "done" && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemovePhoto(i);
                      }}
                      style={{
                        position: "absolute",
                        top: "4px",
                        right: "4px",
                        width: "22px",
                        height: "22px",
                        borderRadius: "50%",
                        background: "rgba(0,0,0,0.7)",
                        border: "none",
                        color: "white",
                        fontSize: "12px",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        lineHeight: 1,
                      }}
                    >
                      ✕
                    </button>
                  )}
                  <div
                    style={{
                      position: "absolute",
                      bottom: "4px",
                      left: "4px",
                      background: "rgba(0,0,0,0.6)",
                      color: "white",
                      fontSize: "10px",
                      fontWeight: 700,
                      padding: "2px 6px",
                      borderRadius: "4px",
                    }}
                  >
                    {i + 1}
                  </div>
                </div>
              ))}

              {/* Add More Slot */}
              {photos.length < 5 && !isProcessing && appState !== "done" && (
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
                        .slice(0, 5 - photos.length);
                      let processed: { file: File; preview: string }[] = [];
                      let count = 0;
                      fileArray.forEach((file) => {
                        const reader = new FileReader();
                        reader.onload = () => {
                          processed.push({
                            file,
                            preview: reader.result as string,
                          });
                          count++;
                          if (count === fileArray.length) {
                            handleFilesSelected(processed);
                          }
                        };
                        reader.readAsDataURL(file);
                      });
                    };
                    input.click();
                  }}
                  style={{
                    borderRadius: "12px",
                    border: "2px dashed rgba(168, 85, 247, 0.25)",
                    aspectRatio: "1",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: "pointer",
                    transition: "all 0.2s",
                    gap: "2px",
                  }}
                  onMouseEnter={(e) =>
                  ((e.currentTarget as HTMLElement).style.borderColor =
                    "var(--accent-purple)")
                  }
                  onMouseLeave={(e) =>
                  ((e.currentTarget as HTMLElement).style.borderColor =
                    "rgba(168, 85, 247, 0.25)")
                  }
                >
                  <span style={{ fontSize: "20px" }}>+</span>
                  <span
                    style={{
                      fontSize: "10px",
                      color: "var(--text-muted)",
                    }}
                  >
                    Add
                  </span>
                </div>
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
                  Variations per photo:
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
                ✨ Enhance {photos.length} Photo
                {photos.length > 1 ? "s" : ""}
              </button>
            )}
          </div>
        )}

        {/* Drop Zone (when no photos or room for more) */}
        {photos.length === 0 && (
          <PhotoUploader
            onFilesSelected={handleFilesSelected}
            currentCount={photos.length}
            disabled={isProcessing}
          />
        )}
      </div>

      {/* ═══ Progress ═══ */}
      {isProcessing && (
        <div>
          {processingLabel && (
            <p
              style={{
                textAlign: "center",
                fontSize: "14px",
                fontWeight: 600,
                color: "var(--accent-purple)",
                marginBottom: "12px",
              }}
            >
              {processingLabel}
            </p>
          )}
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
      <ResultGallery results={results} visible={appState === "done" || (appState === "error" && results.length > 0)} />

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
              (e.target as HTMLElement).style.borderColor = "var(--border-glow)";
              (e.target as HTMLElement).style.color = "var(--text-primary)";
            }}
            onMouseLeave={(e) => {
              (e.target as HTMLElement).style.borderColor = "var(--border-subtle)";
              (e.target as HTMLElement).style.color = "var(--text-secondary)";
            }}
          >
            ✨ Enhance More Photos
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
