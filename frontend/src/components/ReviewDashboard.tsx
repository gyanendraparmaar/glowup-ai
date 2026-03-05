import React from "react";
import { ProfileReview } from "@/app/page";
import { CheckCircle2, XCircle, MessageSquareQuote, Target, Lightbulb, Zap, RefreshCcw, Camera, TextQuote } from "lucide-react";
import { motion } from "framer-motion";

interface Props {
    review: ProfileReview;
    screenshots: string[];
    onReset: () => void;
}

export default function ReviewDashboard({ review, screenshots, onReset }: Props) {
    const score = review.overall_score || 0;
    const advises = review.actionable_advice || [];
    const openers = review.suggested_openers || [];
    const photos = review.photo_review || [];
    const prompts = review.prompt_review || [];

    const getScoreColor = (s: number) => {
        if (s >= 8) return "text-emerald-400";
        if (s >= 5) return "text-amber-400";
        return "text-rose-400";
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-col gap-6 max-w-5xl mx-auto w-full"
        >
            {/* Overview Score Card */}
            <div className="bg-zinc-900/50 backdrop-blur-xl border border-white/10 rounded-3xl p-8 sm:p-12 relative overflow-hidden shadow-2xl">
                {/* Decorative background glow */}
                <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-indigo-500/20 rounded-full blur-[100px]" />

                <div className="flex flex-col md:flex-row items-center justify-between gap-10 relative z-10">
                    <div className="flex-1 space-y-4 text-center md:text-left">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm font-medium tracking-wide">
                            <Target size={16} />
                            Analysis Complete
                        </div>
                        <h2 className="text-4xl font-bold tracking-tight text-white">
                            Profile Diagnosis
                        </h2>
                        <p className="text-zinc-400 text-lg leading-relaxed max-w-xl mx-auto md:mx-0">
                            We've analyzed your profile against the 2024/2025 algorithm meta. Based on photo quality, prompt engagement, and overall vibe, here is your definitive score.
                        </p>
                    </div>

                    <div className="flex flex-col items-center justify-center bg-black/40 rounded-full shrink-0 h-48 w-48 border border-white/5 shadow-inner">
                        <span className={`text-7xl font-black tracking-tighter ${getScoreColor(score)}`}>
                            {score}
                        </span>
                        <span className="text-xs font-bold tracking-[0.2em] text-zinc-500 mt-2">OUT OF 10</span>
                    </div>
                </div>
            </div>

            {/* Two Column Section: Action Plan & Openers */}
            <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-zinc-900/50 backdrop-blur-xl border border-white/10 rounded-3xl p-8 h-full">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-3 text-white">
                        <Zap className="text-indigo-400" size={24} />
                        Action Plan
                    </h3>
                    <ul className="space-y-5">
                        {advises.map((advice, i) => (
                            <motion.li
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.2 + (i * 0.1) }}
                                key={i}
                                className="flex gap-4 group"
                            >
                                <div className="mt-1.5 flex-shrink-0">
                                    <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 group-hover:scale-150 transition-transform" />
                                </div>
                                <span className="text-zinc-300 leading-relaxed font-medium">{advice}</span>
                            </motion.li>
                        ))}
                    </ul>
                </div>

                <div className="bg-zinc-900/50 backdrop-blur-xl border border-white/10 rounded-3xl p-8 h-full">
                    <div className="flex flex-col h-full">
                        <h3 className="text-xl font-bold mb-2 flex items-center gap-3 text-white">
                            <MessageSquareQuote className="text-teal-400" size={24} />
                            Custom Openers
                        </h3>
                        <p className="text-zinc-500 text-sm mb-6">Personalized lines based on your profile's unique attributes.</p>

                        <div className="space-y-4 flex-1 flex flex-col justify-center">
                            {openers.map((opener, i) => (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.98 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: 0.4 + (i * 0.1) }}
                                    key={i}
                                    className="bg-black/40 border border-white/5 hover:border-teal-500/30 transition-colors rounded-2xl p-5 text-zinc-200 font-medium shadow-sm relative overflow-hidden group"
                                >
                                    <div className="absolute top-0 left-0 w-1 h-full bg-teal-500/50 group-hover:w-1.5 transition-all" />
                                    <p className="pl-2">"{opener}"</p>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Prompt Teardown */}
            {prompts.length > 0 && (
                <div className="bg-zinc-900/50 backdrop-blur-xl border border-white/10 rounded-3xl p-8">
                    <h3 className="text-2xl font-bold mb-8 flex items-center gap-3 text-white">
                        <TextQuote className="text-amber-400" size={28} />
                        Prompt Teardown
                    </h3>
                    <div className="grid md:grid-cols-2 gap-6">
                        {prompts.map((p, i) => (
                            <div key={i} className="bg-black/30 rounded-2xl p-6 border border-white/5 flex flex-col">
                                <p className="text-xs font-extrabold text-zinc-500 uppercase tracking-widest mb-3">The Prompt</p>
                                <p className="font-semibold text-white text-lg mb-6 leading-snug">
                                    {p.question || "Unknown Prompt"}
                                </p>

                                <p className="text-xs font-extrabold text-zinc-500 uppercase tracking-widest mb-2 mt-auto">Critique</p>
                                <div className="text-rose-200/90 text-sm mb-5 bg-rose-500/10 p-4 rounded-xl border border-rose-500/20 leading-relaxed">
                                    {p.critique}
                                </div>

                                <p className="text-xs font-extrabold text-zinc-500 uppercase tracking-widest mb-2">Rewrite Suggestion</p>
                                <div className="text-emerald-200/90 text-sm bg-emerald-500/10 p-4 rounded-xl border border-emerald-500/20 font-medium leading-relaxed">
                                    {p.suggested_rewrite}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Suggested Prompts */}
            {review.suggested_prompts && review.suggested_prompts.length > 0 && (
                <div className="bg-gradient-to-b from-zinc-900/80 to-zinc-900/30 backdrop-blur-xl border border-indigo-500/20 rounded-3xl p-8 relative overflow-hidden">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-px bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent" />

                    <h3 className="text-2xl font-bold mb-3 flex items-center gap-3 text-white">
                        <Lightbulb className="text-indigo-400" fill="currentColor" fillOpacity={0.2} size={28} />
                        Top Tier Prompt Strategy
                    </h3>
                    <p className="text-zinc-400 mb-8">Replace your weakest prompts with these high-converting alternatives tailored to your profile.</p>

                    <div className="grid md:grid-cols-3 gap-6">
                        {review.suggested_prompts.map((p, i) => (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.3 + (i * 0.1) }}
                                key={i}
                                className="bg-black/50 rounded-2xl p-6 border border-indigo-500/10 hover:border-indigo-500/30 transition-colors flex flex-col h-full"
                            >
                                <p className="text-xs font-extrabold text-indigo-400 uppercase tracking-widest mb-3">Prompt Option {i + 1}</p>
                                <p className="font-bold text-white mb-6 text-lg leading-snug">
                                    {p.prompt_name}
                                </p>
                                <div className="mt-auto">
                                    <p className="text-indigo-200/80 text-sm bg-indigo-500/10 p-5 rounded-xl border border-indigo-500/20 leading-relaxed font-medium">
                                        "{p.suggested_answer}"
                                    </p>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}

            {/* Analyzed Context */}
            <div className="bg-zinc-900/30 backdrop-blur-sm border border-white/5 rounded-3xl p-8 mt-4">
                <h3 className="text-lg font-bold mb-6 flex items-center gap-3 text-zinc-300">
                    <Camera size={20} className="text-zinc-500" />
                    Analyzed Context
                </h3>
                <div className="flex gap-4 overflow-x-auto pb-4 snap-x hide-scrollbar">
                    {screenshots.map((src, i) => (
                        <div key={i} className="shrink-0 snap-center relative group">
                            <img
                                src={src}
                                alt={`Screenshot ${i + 1}`}
                                className="h-[240px] w-auto max-w-[160px] object-cover rounded-2xl border border-white/10 shadow-lg group-hover:border-white/20 transition-colors"
                            />
                            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors rounded-2xl pointer-events-none" />
                        </div>
                    ))}
                </div>
            </div>

            {/* Reset CTA */}
            <div className="flex justify-center mt-4 mb-20">
                <button
                    onClick={onReset}
                    className="group flex items-center gap-3 px-8 py-4 rounded-full bg-white text-black font-bold hover:scale-105 active:scale-95 transition-all shadow-[0_0_40px_rgba(255,255,255,0.1)] hover:shadow-[0_0_60px_rgba(255,255,255,0.2)]"
                >
                    <RefreshCcw size={18} className="group-hover:-rotate-180 transition-transform duration-500" />
                    Review Another Profile
                </button>
            </div>

        </motion.div>
    );
}
