"use client"

import * as React from "react"
import { Sparkles, FileUp, Link as LinkIcon, ArrowRight, ChevronRight, Check } from "lucide-react"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const PRESETS = [
  {
    id: 1,
    title: "How Autonomous AI Agents are Transforming Software Development",
  },
  {
    id: 2,
    title: "Event-Driven Microservices vs Modular Monoliths in 2026",
  },
  {
    id: 3,
    title: "Why Modern SaaS Companies are Replacing Google Analytics with Seline",
  },
  {
    id: 4,
    title: "Artificial Intelligence in Early Detection of Heart Disease",
  },
]

export function CreateWorkspace() {
  const [activeTab, setActiveTab] = React.useState("prompt")

  return (
    <div className="mx-auto max-w-4xl w-full">
      <div className="flex flex-col items-center mb-12 text-center">
        <Badge variant="secondary" className="mb-4">
          <Sparkles className="mr-1.5 h-3 w-3 text-primary" />
          Rapid Relief Content Engine
        </Badge>
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4">
          What are you making today?
        </h1>
        <p className="text-muted-foreground text-lg max-w-xl">
          Turn an idea, document, or research paper into verified, high-retention content assets in minutes.
        </p>
      </div>

      <Card className="p-2 sm:p-6 mb-12 bg-card/50 backdrop-blur border-border/50">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-6 bg-background/50">
            <TabsTrigger value="prompt" className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              <span className="hidden sm:inline">Idea / Prompt</span>
              <span className="sm:hidden">Prompt</span>
            </TabsTrigger>
            <TabsTrigger value="document" className="flex items-center gap-2">
              <FileUp className="h-4 w-4" />
              <span className="hidden sm:inline">Upload Document</span>
              <span className="sm:hidden">Upload</span>
            </TabsTrigger>
            <TabsTrigger value="url" className="flex items-center gap-2">
              <LinkIcon className="h-4 w-4" />
              <span className="hidden sm:inline">Research URL</span>
              <span className="sm:hidden">URL</span>
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="prompt" className="mt-0">
            <Textarea 
              placeholder="What do you want to talk about? (e.g. 'How autonomous AI agents are scaling...')" 
              className="min-h-[160px] text-base resize-none border-border/50 bg-background/50 focus-visible:ring-1"
            />
          </TabsContent>

          <TabsContent value="document" className="mt-0">
            <div className="border-2 border-dashed border-border/50 rounded-lg p-12 flex flex-col items-center justify-center bg-background/20 text-center hover:bg-background/40 transition-colors cursor-pointer">
              <FileUp className="h-10 w-10 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-1">Click to upload or drag and drop</h3>
              <p className="text-sm text-muted-foreground">PDF, DOCX, TXT, or MD (max. 50MB)</p>
            </div>
          </TabsContent>

          <TabsContent value="url" className="mt-0">
            <div className="flex flex-col gap-4">
              <Input 
                placeholder="https://arxiv.org/abs/..." 
                className="h-14 text-base border-border/50 bg-background/50"
              />
              <p className="text-sm text-muted-foreground pl-1">
                Paste a link to a research paper, news article, or blog post.
              </p>
            </div>
          </TabsContent>

          <div className="mt-6">
            <Button className="w-full h-12 text-base font-semibold group">
              Continue to Outline 
              <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Button>
          </div>
        </Tabs>
      </Card>

      <div className="flex flex-col items-center">
        <h3 className="text-sm font-bold tracking-widest text-muted-foreground uppercase mb-6">
          Or start with a proven industry preset:
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
          {PRESETS.map((preset) => (
            <div 
              key={preset.id}
              className="group flex items-center justify-between p-5 rounded-xl border border-border/40 bg-card hover:bg-card/80 hover:border-primary/50 transition-all cursor-pointer shadow-sm hover:shadow-md"
            >
              <span className="text-sm font-medium pr-4 leading-relaxed text-foreground group-hover:text-primary transition-colors">
                {preset.title}
              </span>
              <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors flex-shrink-0" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
