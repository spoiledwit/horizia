export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="absolute inset-0 -m-6 -my-12">
      {children}
    </div>
  )
}