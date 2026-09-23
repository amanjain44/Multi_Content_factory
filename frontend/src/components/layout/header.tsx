"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState, useRef, useEffect } from "react"
import { Calendar, LayoutDashboard, Plus, Menu, Settings2, Activity, Layers, ChevronDown, LogIn } from "lucide-react"
import { ThemeToggle } from "@/components/theme-toggle"
import { useAuth } from "@/contexts/AuthContext"

function UserDropdown() {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const { user, logout } = useAuth()
  
  // Format user email to display name
  const displayName = user?.email?.split('@')[0] || "Creative Director"
  // Capitalize first letter
  const formattedName = displayName.charAt(0).toUpperCase() + displayName.slice(1)
  const initial = formattedName.charAt(0).toUpperCase()

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  return (
    <div className="relative pointer-events-auto" ref={dropdownRef}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="hidden sm:flex items-center gap-2 rounded-full border border-border/50 bg-background/20 px-3 py-1.5 text-sm font-medium cursor-pointer hover:bg-background/80 hover:scale-105 active:scale-95 transition-all shadow-sm"
      >
        <div className="flex h-5 w-5 items-center justify-center rounded-full bg-primary/20 text-primary font-bold text-[10px]">
          {initial}
        </div>
        <span className="text-foreground">{formattedName}</span>
        <ChevronDown className="h-3 w-3 text-muted-foreground ml-1" />
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-64 rounded-xl border border-slate-200 dark:border-border bg-white dark:bg-card p-4 shadow-xl flex flex-col z-50 animate-in fade-in zoom-in-95 duration-200">
          <div className="flex flex-col gap-1 mb-4">
            <span className="font-semibold text-foreground">{formattedName}</span>
            <span className="text-sm text-slate-500 dark:text-muted-foreground">{user?.email || "Not signed in"}</span>
            <div className="mt-2 flex items-center gap-2 rounded-full border border-slate-200 dark:border-border bg-slate-50 dark:bg-muted/50 px-2.5 py-0.5 w-max">
              <div className={`h-1.5 w-1.5 rounded-full ${user ? 'bg-emerald-500' : 'bg-slate-400'}`} />
              <span className="text-[10px] font-semibold text-slate-600 dark:text-muted-foreground uppercase tracking-wider">
                {user ? "Active Session" : "Guest Session"}
              </span>
            </div>
          </div>
          
          <div className="h-px w-full bg-slate-100 dark:bg-border/50 my-2" />
          
          <div className="flex flex-col gap-1 my-2">
            <Link href="/diagnostics" onClick={() => setIsOpen(false)} className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-700 dark:text-foreground/80 hover:bg-slate-50 dark:hover:bg-muted transition-colors w-full text-left">
              <Activity className="h-4 w-4 text-primary" />
              Diagnostics & Workflows
            </Link>
            <Link href="/settings" onClick={() => setIsOpen(false)} className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-700 dark:text-foreground/80 hover:bg-slate-50 dark:hover:bg-muted transition-colors w-full text-left">
              <Settings2 className="h-4 w-4 text-slate-500" />
              Settings & Providers
            </Link>
          </div>
          
          <div className="h-px w-full bg-slate-100 dark:bg-border/50 my-2 mb-4" />
          
          {user ? (
            <button 
              onClick={() => { setIsOpen(false); logout(); }}
              className="flex w-full items-center justify-center gap-2 bg-white dark:bg-card border border-slate-200 dark:border-border text-destructive hover:bg-red-50 dark:hover:bg-red-950/30 hover:text-red-600 dark:hover:text-red-400 shadow-sm px-4 py-2.5 text-sm font-semibold rounded-lg transition-all active:scale-95"
            >
              Sign Out
            </button>
          ) : (
            <Link 
              href="/login" 
              onClick={() => setIsOpen(false)}
              className="flex w-full items-center justify-center gap-2 bg-white dark:bg-card border border-slate-200 dark:border-border text-slate-700 dark:text-foreground hover:bg-slate-50 dark:hover:bg-muted shadow-sm px-4 py-2.5 text-sm font-semibold rounded-lg transition-all active:scale-95"
            >
              <LogIn className="h-4 w-4" />
              Sign In / Create Account
            </Link>
          )}
        </div>
      )}
    </div>
  )
}

function MobileMenu() {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const pathname = usePathname()
  const isActive = (path: string) => pathname === path
  const { user, logout } = useAuth()

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  return (
    <div className="flex md:hidden relative pointer-events-auto" ref={dropdownRef}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-center h-9 w-9 rounded-full bg-background border border-border/50 hover:bg-muted active:scale-95 transition-all"
      >
        <Menu className="h-4 w-4 text-foreground" />
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-56 rounded-xl border border-slate-200 dark:border-border bg-white dark:bg-card p-2 shadow-xl flex flex-col z-50 animate-in fade-in zoom-in-95 duration-200">
          <Link href="/" onClick={() => setIsOpen(false)} className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-700 dark:text-foreground/80 hover:bg-slate-50 dark:hover:bg-muted transition-colors w-full text-left">
            <Plus className="h-4 w-4" />
            Create
          </Link>
          <Link href="/projects" onClick={() => setIsOpen(false)} className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors w-full text-left ${isActive('/projects') ? 'bg-slate-50 dark:bg-muted text-blue-500' : 'text-slate-700 dark:text-foreground/80 hover:bg-slate-50 dark:hover:bg-muted'}`}>
            <LayoutDashboard className="h-4 w-4" />
            Projects
          </Link>
          <Link href="/calendar" onClick={() => setIsOpen(false)} className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors w-full text-left ${isActive('/calendar') ? 'bg-slate-50 dark:bg-muted text-emerald-500' : 'text-slate-700 dark:text-foreground/80 hover:bg-slate-50 dark:hover:bg-muted'}`}>
            <Calendar className="h-4 w-4" />
            Calendar
          </Link>
          
          <div className="h-px w-full bg-slate-100 dark:bg-border/50 my-2" />
          
          <Link href="/diagnostics" onClick={() => setIsOpen(false)} className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-700 dark:text-foreground/80 hover:bg-slate-50 dark:hover:bg-muted transition-colors w-full text-left">
            <Activity className="h-4 w-4 text-primary" />
            Health
          </Link>
          <Link href="/settings" onClick={() => setIsOpen(false)} className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-700 dark:text-foreground/80 hover:bg-slate-50 dark:hover:bg-muted transition-colors w-full text-left">
            <Settings2 className="h-4 w-4 text-slate-500" />
            Settings
          </Link>
          
          <div className="h-px w-full bg-slate-100 dark:bg-border/50 my-2" />
          
          {user ? (
            <button 
              onClick={() => { setIsOpen(false); logout(); }}
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold text-destructive hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors w-full text-left"
            >
              Sign Out
            </button>
          ) : (
            <Link 
              href="/login"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold text-slate-700 dark:text-foreground/80 hover:bg-slate-50 dark:hover:bg-muted transition-colors w-full text-left"
            >
              <LogIn className="h-4 w-4" />
              Sign In
            </Link>
          )}
        </div>
      )}
    </div>
  )
}

export function Header() {
  const pathname = usePathname()
  const isActive = (path: string) => pathname === path

  return (
    <header className="fixed top-4 sm:top-6 left-0 right-0 z-50 flex justify-center w-full px-2 sm:px-4 pointer-events-none">
      <div className="flex h-12 sm:h-14 items-center justify-between px-4 sm:px-6 rounded-full glass-panel pointer-events-auto w-full max-w-5xl relative">
        
        {/* Left: Logo */}
        <div className="flex items-center w-1/3">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 font-bold text-white shadow-[0_0_15px_rgba(99,102,241,0.4)] group-hover:shadow-[0_0_25px_rgba(99,102,241,0.6)] group-hover:scale-105 active:scale-95 transition-all">
              <Layers className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-black leading-tight tracking-tight text-gradient-multi uppercase">MCF</span>
            </div>
          </Link>
        </div>

        {/* Center: Main Nav */}
        <nav className="hidden md:flex items-center gap-1 absolute left-1/2 -translate-x-1/2">
          <Link href="/" className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm">
            <Plus className="h-4 w-4" />
            Create
          </Link>
          <div className="w-px h-4 bg-border/50 mx-2" />
          <Link href="/projects" className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ${isActive('/projects') ? 'bg-background/80 text-foreground shadow-[inset_0_1px_4px_rgba(0,0,0,0.1)] dark:shadow-[inset_0_1px_4px_rgba(255,255,255,0.05)] border border-border/50' : 'text-muted-foreground hover:text-foreground hover:bg-background/40'}`}>
            <LayoutDashboard className={`h-4 w-4 ${isActive('/projects') ? 'text-blue-500' : ''}`} />
            Projects
          </Link>
          <Link href="/calendar" className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ${isActive('/calendar') ? 'bg-background/80 text-foreground shadow-[inset_0_1px_4px_rgba(0,0,0,0.1)] dark:shadow-[inset_0_1px_4px_rgba(255,255,255,0.05)] border border-border/50' : 'text-muted-foreground hover:text-foreground hover:bg-background/40'}`}>
            <Calendar className={`h-4 w-4 ${isActive('/calendar') ? 'text-emerald-500' : ''}`} />
            Calendar
          </Link>
        </nav>

        {/* Right: Actions */}
        <div className="flex items-center justify-end gap-2 sm:gap-4 w-1/3">
          <ThemeToggle />
          <UserDropdown />
          <MobileMenu />
        </div>
        
      </div>
    </header>
  )
}
