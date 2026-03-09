'use client'

import Sidebar from '@/components/layout/Sidebar'

export default function Layout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      <Sidebar />
      <main className="lg:pl-64">
        <div className="p-4 lg:p-8">
          {children}
        </div>
      </main>
    </>
  )
}
