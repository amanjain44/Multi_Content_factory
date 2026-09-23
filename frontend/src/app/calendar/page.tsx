"use client";

import { CalendarView } from "@/components/calendar-view";

export default function CalendarPage() {
  return (
    <div className="flex-1 flex flex-col w-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-4 relative z-10">
      <CalendarView />
    </div>
  );
}
