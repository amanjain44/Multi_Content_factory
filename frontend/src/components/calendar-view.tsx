import { useState, useEffect, useMemo } from 'react';
import { ScheduleWithProject } from '@/types/schedule';
import { ScheduleService } from '@/lib/services/schedule.service';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CalendarIcon, Clock, Link as LinkIcon, Trash2, Edit2 } from 'lucide-react';
import { toast } from 'sonner';
import { format, parseISO, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, isSameDay } from 'date-fns';
import Link from 'next/link';
import { ScheduleDialog } from './schedule-dialog';

const getPlatformStyles = (platform: string) => {
  switch (platform.toLowerCase()) {
    case 'linkedin': return 'bg-blue-500/10 text-blue-500 border-blue-500/20 shadow-blue-500/10';
    case 'twitter':
    case 'twitter / x': return 'bg-sky-500/10 text-sky-500 border-sky-500/20 shadow-sky-500/10';
    case 'instagram': return 'bg-pink-500/10 text-pink-500 border-pink-500/20 shadow-pink-500/10';
    case 'youtube': return 'bg-red-500/10 text-red-500 border-red-500/20 shadow-red-500/10';
    case 'tiktok': return 'bg-zinc-500/10 text-foreground border-zinc-500/20 shadow-zinc-500/10';
    default: return 'bg-primary/10 text-primary border-primary/20 shadow-primary/10';
  }
};

export function CalendarView() {
  const [schedules, setSchedules] = useState<ScheduleWithProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());

  // Dialog state
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [selectedSchedule, setSelectedSchedule] = useState<ScheduleWithProject | undefined>(undefined);
  const [initialDate, setInitialDate] = useState<string | undefined>(undefined);

  useEffect(() => {
    loadSchedules();
  }, []);

  const loadSchedules = async () => {
    try {
      setLoading(true);
      const data = await ScheduleService.getSchedules();
      setSchedules(data);
    } catch (error) {
      console.error('Failed to load schedules', error);
      toast.error('Failed to load schedule data');
    } finally {
      setLoading(false);
    }
  };

  const deleteSchedule = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation(); // prevent opening edit dialog
    if (!confirm('Are you sure you want to delete this scheduled item?')) return;
    
    try {
      await ScheduleService.deleteSchedule(id);
      toast.success('Schedule deleted');
      loadSchedules();
    } catch (error) {
      console.error('Failed to delete schedule', error);
      toast.error('Failed to delete schedule');
    }
  };

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const openNewScheduleDialog = (day: Date) => {
    // Offset for local timezone correctly
    const offset = day.getTimezoneOffset();
    const localDate = new Date(day.getTime() - (offset * 60 * 1000));
    setInitialDate(localDate.toISOString().split('T')[0]);
    setSelectedSchedule(undefined);
    setIsDialogOpen(true);
  };

  const openEditDialog = (e: React.MouseEvent, schedule: ScheduleWithProject) => {
    e.stopPropagation();
    setSelectedSchedule(schedule);
    setIsDialogOpen(true);
  };

  const days = useMemo(() => {
    const start = startOfMonth(currentDate);
    const end = endOfMonth(currentDate);
    return eachDayOfInterval({ start, end });
  }, [currentDate]);

  if (loading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <div className="text-muted-foreground animate-pulse">Loading calendar...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground mb-2">Content Calendar</h2>
          <p className="text-muted-foreground mt-1">Manage and schedule your content across all platforms.</p>
        </div>
        <div className="flex items-center space-x-2 bg-white dark:bg-card p-1 rounded-lg border border-slate-200 dark:border-border shadow-sm">
          <Button variant="ghost" onClick={prevMonth} className="hover:bg-primary/10 hover:text-primary transition-colors">Previous</Button>
          <div className="relative text-base font-bold min-w-[160px] text-center px-4 hover:text-primary transition-colors cursor-pointer flex items-center justify-center" onClick={() => setShowDatePicker(!showDatePicker)}>
            {format(currentDate, 'MMMM yyyy')}
            
            {showDatePicker && (
              <>
                <div className="fixed inset-0 z-40" onClick={(e) => { e.stopPropagation(); setShowDatePicker(false); }} />
                <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 z-50 bg-white dark:bg-card border border-slate-200 dark:border-border rounded-xl shadow-xl p-3 w-64 animate-in fade-in zoom-in-95 duration-200 cursor-default" onClick={(e) => e.stopPropagation()}>
                  <div className="flex justify-between items-center mb-3">
                    <Button variant="ghost" size="sm" className="h-7 px-2" onClick={(e) => { e.stopPropagation(); setCurrentDate(new Date(currentDate.getFullYear() - 1, currentDate.getMonth(), 1)); }}>
                      &lt;
                    </Button>
                    <span className="font-bold text-foreground">{currentDate.getFullYear()}</span>
                    <Button variant="ghost" size="sm" className="h-7 px-2" onClick={(e) => { e.stopPropagation(); setCurrentDate(new Date(currentDate.getFullYear() + 1, currentDate.getMonth(), 1)); }}>
                      &gt;
                    </Button>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].map((m, i) => (
                      <div 
                        key={m} 
                        className={`text-sm py-1.5 rounded-md cursor-pointer text-center transition-colors ${currentDate.getMonth() === i ? 'bg-primary text-primary-foreground font-bold shadow-sm' : 'text-slate-600 dark:text-muted-foreground hover:bg-slate-100 dark:hover:bg-muted'}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          setCurrentDate(new Date(currentDate.getFullYear(), i, 1));
                          setShowDatePicker(false);
                        }}
                      >
                        {m}
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
          <Button variant="ghost" onClick={nextMonth} className="hover:bg-primary/10 hover:text-primary transition-colors">Next</Button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-4">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
          <div key={day} className="text-center font-medium text-muted-foreground py-2">
            {day}
          </div>
        ))}

        {Array.from({ length: days[0].getDay() }).map((_, i) => (
          <div key={`empty-${i}`} className="h-32 rounded-md border border-dashed border-border/50 bg-muted/20" />
        ))}

        {days.map((day: Date, dayIdx: number) => {
          const daySchedules = schedules.filter((s) => isSameDay(parseISO(s.scheduledAt), day));
          
          return (
            <div 
              key={day.toString()} 
              className={`h-36 rounded-xl border p-2.5 overflow-y-auto space-y-2 cursor-pointer transition-all duration-200 hover:scale-[1.02] hover:shadow-md hover:border-primary/30 dark:hover:border-primary/50 ${
                isToday(day) ? 'bg-primary/5 dark:bg-primary/10 border-primary/30 dark:border-primary/50 shadow-inner' : 'bg-white dark:bg-card border-slate-200 dark:border-border shadow-sm'
              }`}
              onClick={() => openNewScheduleDialog(day)}
            >
              <div className="flex justify-between items-center mb-2">
                <span className={`text-sm font-bold flex items-center justify-center w-7 h-7 rounded-full ${isToday(day) ? 'bg-primary text-primary-foreground shadow-md shadow-primary/30' : 'text-muted-foreground'}`}>
                  {format(day, 'd')}
                </span>
                {daySchedules.length > 0 && (
                  <span className="text-xs bg-muted px-1.5 py-0.5 rounded-full">
                    {daySchedules.length}
                  </span>
                )}
              </div>

              {daySchedules.map((schedule) => (
                <div 
                  key={schedule.id} 
                  className={`group relative text-[11px] p-2 rounded-lg border shadow-sm flex flex-col gap-1.5 cursor-pointer transition-all hover:scale-[1.02] hover:shadow-md ${getPlatformStyles(schedule.platform).replace('text-', 'hover:border-').split(' ')[0]} bg-white dark:bg-card`}
                  onClick={(e) => openEditDialog(e, schedule)}
                >
                  <div className="font-bold truncate pr-6 text-foreground/90 leading-tight" title={schedule.projectTitle}>
                    {schedule.projectTitle}
                  </div>
                  <div className="flex items-center justify-between text-[10px] font-medium">
                    <span className="flex items-center gap-1 text-slate-500 dark:text-muted-foreground bg-slate-50 dark:bg-muted/50 px-1.5 py-0.5 rounded-md border border-slate-200 dark:border-border shadow-sm">
                      <Clock className="w-3 h-3 opacity-70" /> {format(parseISO(schedule.scheduledAt), 'HH:mm')}
                    </span>
                    <span className={`px-1.5 py-0.5 rounded-md border ${getPlatformStyles(schedule.platform)}`}>
                      {schedule.platform}
                    </span>
                  </div>
                  
                  {/* Hover actions */}
                  <div className="absolute top-1 right-1 hidden group-hover:flex bg-white dark:bg-card rounded-md gap-1 p-0.5 shadow-md border border-slate-200 dark:border-border">
                    <Link href={`/projects/${schedule.projectId}`} title="View Project" onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" size="icon" className="h-5 w-5 hover:bg-background/50">
                        <LinkIcon className="h-3 w-3" />
                      </Button>
                    </Link>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="h-5 w-5 hover:bg-background/50 text-muted-foreground"
                      onClick={(e) => openEditDialog(e, schedule)}
                      title="Edit Schedule"
                    >
                      <Edit2 className="h-3 w-3" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="h-5 w-5 hover:bg-destructive/10 hover:text-destructive text-muted-foreground"
                      onClick={(e) => deleteSchedule(e, schedule.id)}
                      title="Delete Schedule"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          );
        })}
      </div>
      
      {schedules.length === 0 && (
        <Card className="bg-slate-50 dark:bg-muted/30 border-dashed border-2 border-slate-200 dark:border-border/50 shadow-sm cursor-pointer hover:bg-slate-100 dark:hover:bg-muted/50 transition-all duration-300 hover:border-primary/30 group overflow-hidden relative" onClick={() => openNewScheduleDialog(new Date())}>
          <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
          <CardContent className="flex flex-col items-center justify-center py-20 text-center relative z-10">
            <div className="w-20 h-20 rounded-full bg-white dark:bg-card border border-slate-200 dark:border-border shadow-sm flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500">
              <CalendarIcon className="h-10 w-10 text-slate-400 dark:text-muted-foreground group-hover:text-primary transition-colors" />
            </div>
            <h3 className="text-2xl font-bold mb-3 text-foreground">No content scheduled yet</h3>
            <p className="text-slate-500 dark:text-muted-foreground max-w-md text-base leading-relaxed">
              Your calendar is currently empty. Click anywhere on the calendar or right here to start planning your content strategy across all platforms.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Reusable Dialog for creating/editing */}
      <ScheduleDialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        onScheduled={loadSchedules}
        existingSchedule={selectedSchedule}
        initialDate={initialDate}
      />
    </div>
  );
}
