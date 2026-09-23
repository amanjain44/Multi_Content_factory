import { Composer } from "@/components/composer/Composer"
import { WorkflowPreview } from "@/components/composer/WorkflowPreview"

export default function Home() {
  return (
    <div className="flex-1 flex justify-center px-4 sm:px-6 md:px-8 py-4 overflow-y-auto relative z-10 pb-20">
      <div className="w-full max-w-4xl flex flex-col gap-12 min-h-max mt-4">
        
        {/* Main Workspace */}
        <div className="w-full flex flex-col pt-0">
          <Composer />
        </div>

        {/* Pipeline Preview */}
        <div className="w-full pt-8 border-t border-border/50">
          <WorkflowPreview />
        </div>

      </div>
    </div>
  )
}
