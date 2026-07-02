"use client"

import { useState, useEffect } from "react"
import { Drawer } from "antd"
import { MenuOutlined } from "@ant-design/icons"
import { TopNav } from "./TopNav"
import { Sidebar } from "./Sidebar"

interface AppShellProps {
  children: React.ReactNode
}

export function AppShell({ children }: AppShellProps) {
  const [isMobile, setIsMobile] = useState(false)
  const [drawerOpen, setDrawerOpen] = useState(false)

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 768px)")
    const update = () => setIsMobile(mq.matches)
    update()
    mq.addEventListener("change", update)
    return () => mq.removeEventListener("change", update)
  }, [])

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <TopNav
        onMenuClick={() => setDrawerOpen(true)}
        showMenuButton={isMobile}
      />
      <div className="flex flex-1 overflow-hidden">
        {!isMobile && <Sidebar />}
        {isMobile && (
          <Drawer
            placement="left"
            open={drawerOpen}
            onClose={() => setDrawerOpen(false)}
            width={260}
            styles={{ body: { padding: 0 } }}
            className="mobile-sidebar-drawer"
          >
            <Sidebar onNavigate={() => setDrawerOpen(false)} />
          </Drawer>
        )}
        <main className="flex-1 overflow-y-auto bg-[var(--color-surface)] p-3 md:p-6 w-full overflow-x-hidden">
          {children}
        </main>
      </div>
    </div>
  )
}
