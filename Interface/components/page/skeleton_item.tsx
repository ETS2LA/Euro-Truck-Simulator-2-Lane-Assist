import { Skeleton } from "@/components/ui/skeleton"

export function SkeletonItem() {
  return (
    <div className="flex gap-2 w-full">
      <Skeleton className="h-7 w-7 rounded-xl" />
      <Skeleton className="h-7 flex-grow" />
    </div>
  )
}
