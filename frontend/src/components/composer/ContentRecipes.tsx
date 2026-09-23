"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ArrowRight, BookOpen, Lightbulb, TrendingUp, Newspaper, ChevronDown } from "lucide-react"

const RECIPES = [
  {
    id: 1,
    icon: BookOpen,
    title: "Research Paper",
    outcome: "Educational Series",
    content: "Analyze the attached research paper on 'Attention is All You Need' and create a 5-part educational LinkedIn series explaining Transformers to a non-technical audience.",
    color: "text-blue-500",
    bg: "bg-blue-50 dark:bg-blue-500/10",
    hoverBorder: "hover:border-blue-300 dark:hover:border-blue-500/50"
  },
  {
    id: 2,
    icon: TrendingUp,
    title: "Product Launch",
    outcome: "Multi-platform Campaign",
    content: "We are launching a new AI-powered code editor called 'Antigravity'. Write a compelling launch announcement for Twitter, a detailed blog post for developers, and an email newsletter for our waitlist.",
    color: "text-emerald-500",
    bg: "bg-emerald-50 dark:bg-emerald-500/10",
    hoverBorder: "hover:border-emerald-300 dark:hover:border-emerald-500/50"
  },
  {
    id: 3,
    icon: Newspaper,
    title: "Industry News",
    outcome: "LinkedIn Thought Leadership",
    content: "Based on the recent news about Apple's new M4 chip, draft a thought leadership post for my LinkedIn profile discussing the implications for local AI development.",
    color: "text-orange-500",
    bg: "bg-orange-50 dark:bg-orange-500/10",
    hoverBorder: "hover:border-orange-300 dark:hover:border-orange-500/50"
  },
  {
    id: 4,
    icon: Lightbulb,
    title: "Raw Idea",
    outcome: "Content Strategy & Brief",
    content: "I have a raw idea: 'Developers spend too much time configuring tools instead of writing code'. Turn this into a full content strategy including 3 blog post ideas and 5 tweet variations.",
    color: "text-amber-500",
    bg: "bg-amber-50 dark:bg-amber-500/10",
    hoverBorder: "hover:border-amber-300 dark:hover:border-amber-500/50"
  },
]

interface ContentRecipesProps {
  onSelect?: (content: string) => void;
}

export function ContentRecipes({ onSelect }: ContentRecipesProps) {
  const [expandedId, setExpandedId] = React.useState<number | null>(null);

  const handleToggle = (id: number) => {
    setExpandedId(prev => prev === id ? null : id);
  }

  const handleUseRecipe = (content: string) => {
    if (onSelect) {
      onSelect(content);
      // Optional: scroll up to text area so user sees it populated
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="flex flex-col w-full mt-8"
    >
      <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-muted-foreground mb-4 pl-1">
        Quick Starts & Recipes
      </h3>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {RECIPES.map((recipe, index) => {
          const isExpanded = expandedId === recipe.id;
          
          return (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.7 + (index * 0.1), ease: [0.16, 1, 0.3, 1] }}
              key={recipe.id}
              className={`group flex flex-col w-full rounded-xl border border-slate-200 dark:border-border bg-white dark:bg-card shadow-sm hover:shadow-md transition-all overflow-hidden ${isExpanded ? 'ring-1 ring-slate-200 dark:ring-border shadow-md' : recipe.hoverBorder}`}
            >
              <button 
                onClick={() => handleToggle(recipe.id)}
                className="relative flex items-center justify-between p-4 w-full text-left"
              >
                {/* Subtle hover background */}
                <div className="absolute inset-0 bg-slate-50 dark:bg-white/[0.02] opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                
                <div className="relative z-10 flex items-center gap-4 w-full">
                  <div className={`shrink-0 flex h-10 w-10 items-center justify-center rounded-lg shadow-sm border border-slate-100 dark:border-transparent transition-colors ${recipe.bg} ${recipe.color}`}>
                    <recipe.icon className="h-5 w-5" />
                  </div>
                  <div className="flex flex-col min-w-0 flex-1">
                    <span className="text-sm font-bold text-foreground group-hover:text-foreground transition-colors truncate">{recipe.title}</span>
                    <span className="text-[13px] font-medium text-slate-500 dark:text-muted-foreground transition-colors truncate">{recipe.outcome}</span>
                  </div>
                  <div className={`shrink-0 relative z-10 flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 dark:bg-muted text-slate-400 dark:text-muted-foreground transition-all duration-300 ${isExpanded ? 'rotate-180' : 'group-hover:text-foreground'}`}>
                    <ChevronDown className="h-4 w-4" />
                  </div>
                </div>
              </button>

              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                    className="overflow-hidden"
                  >
                    <div className="p-4 pt-0">
                      <div className="p-3 rounded-lg bg-slate-50 dark:bg-muted/50 border border-slate-100 dark:border-border/50 mb-3">
                        <p className="text-sm text-slate-600 dark:text-muted-foreground leading-relaxed">
                          "{recipe.content}"
                        </p>
                      </div>
                      <button 
                        onClick={() => handleUseRecipe(recipe.content)}
                        className="flex items-center justify-center gap-2 w-full px-4 py-2 bg-primary text-primary-foreground text-sm font-semibold rounded-lg shadow-sm hover:opacity-90 active:scale-[0.98] transition-all"
                      >
                        <ArrowRight className="h-4 w-4" />
                        Use this Recipe
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )
        })}
      </div>
    </motion.div>
  )
}
