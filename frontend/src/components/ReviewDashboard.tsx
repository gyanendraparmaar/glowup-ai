import React from "react";
import { ProfileReview } from "@/app/page";
import { CheckCircle2, XCircle, MessageSquareQuote, Target, Lightbulb, Zap, RefreshCcw } from "lucide-react";
import { motion } from "framer-motion";

interface Props {
    review: ProfileReview;
    screenshots: string[];
    onReset: () => void;
}

export default function ReviewDashboard({ review, screenshots, onReset }: Props) {
    // Safe fallbacks in case Gemini misses a key
    const score = review.overall_score || 0;
    const advises = review.actionable_advice || [];
    const openers = review.suggested_openers || [];
    const photos = review.photo_review || [];
    const prompts = review.prompt_review || [];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex flex-col gap-8"
        >
            {/* Overview Score Card */}
            <div className="glass-card flex flex-col md:flex-row items-center justify-between p-8 gap-8 border-t-4 border-t-purple-500">
                <div className="flex-1">
                    <h2 className="text-3xl font-bold mb-4 flex items-center gap-3">
                        <Target className="text-purple-400" size={32} />
                        Profile Diagnosis
                    </h2>
                    <p className="text-gray-300 text-lg leading-relaxed">
                        We've analyzed your Hinge profile against current 2024/2025 dating app algorithms and general modern attractiveness meta. Here is your strategic breakdown.
                    </p>
                </div>
                <div className="flex flex-col items-center justify-center bg-black/40 rounded-3xl p-8 border border-white/5 shadow-2xl">
                    <span className="text-6xl font-black gradient-text">{score}</span>
                    <span className="text-sm font-semibold tracking-widest text-gray-400 mt-2 uppercase">Out of 10</span>
                </div>
            </div>

            {/* Actionable Advice & Openers Grid */}
            <div className="grid md:grid-cols-2 gap-6">
                <div className="glass-card p-6">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-2 text-pink-400">
                        <Zap size={24} />
                        Core Action Plan
                    </h3>
                    <ul className="space-y-4">
                        {advises.map((advice, i) => (
                            <motion.li
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.2 + (i * 0.1) }}
                                key={i}
                                className="flex gap-3 text-gray-200"
                            >
                                <div className="mt-1 flex-shrink-0">
                                    <div className="w-2 h-2 rounded-full bg-pink-500" />
                                </div>
                                <span className="leading-relaxed">{advice}</span>
                            </motion.li>
                        ))}
                    </ul>
                </div>

                <div className="glass-card p-6 bg-gradient-to-br from-purple-900/10 to-indigo-900/10">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-2 text-indigo-400">
                        <MessageSquareQuote size={24} />
                        Custom Openers
                    </h3>
                    <p className="text-sm text-gray-400 mb-4 italic">Try these specific opening lines based on your profile's vibe:</p>
                    <div className="space-y-4">
                        {openers.map((opener, i) => (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: 0.4 + (i * 0.1) }}
                                key={i}
                                className="bg-black/50 border border-indigo-500/20 rounded-xl p-4 text-gray-100 font-medium tracking-wide shadow-inner"
                            >
                                "{opener}"
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Prompts Review */}
            {prompts.length > 0 && (
                <div className="glass-card p-8">
                    <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
                        <Lightbulb className="text-yellow-400" size={28} />
                        Prompt Teardown
                    </h3>
                    <div className="grid md:grid-cols-2 gap-6">
                        {prompts.map((p, i) => (
                            <div key={i} className="bg-black/30 rounded-2xl p-5 border border-white/5">
                                <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">The Prompt</p>
                                <p className="font-semibold text-gray-100 mb-4 text-lg border-l-2 border-yellow-500 pl-3">
                                    {p.question || "Unknown Prompt"}
                                </p>

                                <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1 mt-4">Critique</p>
                                <p className="text-red-300 text-sm mb-4 bg-red-950/30 p-3 rounded-lg border border-red-900/50">
                                    {p.critique}
                                </p>

                                <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1 mt-4">Suggested Rewrite</p>
                                <p className="text-green-300 text-sm bg-green-950/30 p-3 rounded-lg border border-green-900/50 font-medium">
                                    {p.suggested_rewrite}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Suggested Prompts */}
            {review.suggested_prompts && review.suggested_prompts.length > 0 && (
                <div className="glass-card p-8 mt-4 bg-gradient-to-br from-green-900/10 to-emerald-900/10">
                    <h3 className="text-2xl font-bold mb-6 flex items-center gap-3 text-green-400">
                        <Lightbulb className="text-green-400" size={28} />
                        Top Tier Prompt Suggestions
                    </h3>
                    <p className="text-gray-300 mb-6">Based on your photos and vibe, here are 3 highly tailored, 2024/2025 Meta prompts you should use:</p>
                    <div className="grid md:grid-cols-3 gap-6">
                        {review.suggested_prompts.map((p, i) => (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.3 + (i * 0.1) }}
                                key={i} className="bg-black/40 rounded-2xl p-6 border border-green-500/20 shadow-[0_0_15px_rgba(34,197,94,0.1)] flex flex-col h-full"
                            >
                                <p className="text-xs font-bold text-green-500 uppercase tracking-wider mb-3">Prompt</p>
                                <p className="font-bold text-gray-100 mb-4 text-lg">
                                    {p.prompt_name}
                                </p>
                                <div className="mt-auto">
                                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Suggested Answer</p>
                                    <p className="text-green-100 text-sm bg-green-950/40 p-4 rounded-xl border border-green-900/50 italic leading-relaxed">
                                        "{p.suggested_answer}"
                                    </p>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}

            {/* The Uploaded Screenshots context */}
            <div className="glass-card p-8 mt-4">
                <h3 className="text-xl font-bold mb-6 text-gray-300 border-b border-white/10 pb-4">
                    Analyzed Context
                </h3>
                <div className="flex gap-4 overflow-x-auto pb-4 snap-x">
                    {screenshots.map((src, i) => (
                        <img
                            key={i}
                            src={src}
                            alt={`Screenshot ${i + 1}`}
                            className="h-[300px] w-auto object-cover rounded-xl border border-white/10 snap-center shadow-lg"
                        />
                    ))}
                </div>
            </div>

            {/* Reset CTA */}
            <div className="flex justify-center mt-12 mb-8">
                <button
                    onClick={onReset}
                    className="flex items-center gap-2 px-8 py-4 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all font-semibold text-gray-200"
                >
                    <RefreshCcw size={18} />
                    Review Another Profile
                </button>
            </div>

        </motion.div>
    );
}
