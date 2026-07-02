"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Drawer } from "antd"
import { MenuOutlined } from "@ant-design/icons"
import { moduleMenus } from "@/lib/menu-config"
import { ModuleIcon, SearchIcon, BellIcon } from "@/components/icons"

interface TopNavProps {
  onMenuClick?: () => void
  showMenuButton?: boolean
}

export function TopNav({ onMenuClick, showMenuButton = false }: TopNavProps) {
  const pathname = usePathname()
  const activeModule = pathname.split("/")[1] || "production"
  const [moduleDrawerOpen, setModuleDrawerOpen] = useState(false)

  return (
    <header className="h-14 md:h-16 bg-[var(--color-canvas)] border-b border-[var(--color-hairline)] flex items-center px-3 md:px-5 shrink-0 gap-2">
      {/* Mobile: Hamburger */}
      {showMenuButton && (
        <button
          onClick={onMenuClick}
          className="md:hidden w-9 h-9 flex items-center justify-center rounded-[var(--rounded-sm)] text-[var(--color-charcoal)] hover:bg-[var(--color-surface)] transition-colors shrink-0"
          aria-label="菜单"
        >
          <MenuOutlined className="text-[20px]" />
        </button>
      )}

      {/* Logo */}
      <div className="flex items-center gap-2.5 mr-2 md:mr-10 shrink-0">
        <div className="w-7 h-7 rounded-[var(--rounded-md)] bg-[var(--color-primary)] flex items-center justify-center">
          <span className="text-white text-xs font-semibold">API</span>
        </div>
        <span className="hidden sm:inline text-[var(--color-charcoal)] text-[15px] font-semibold tracking-tight">
          原料药
        </span>
      </div>

      {/* Desktop: Module Tabs */}
      <nav className="hidden md:flex items-center gap-0.5 flex-1 overflow-x-auto scrollbar-hide h-full">
        {moduleMenus.map((mod) => {
          const isActive = activeModule === mod.key
          return (
            <Link
              key={mod.key}
              href={mod.path}
              className={`
                flex items-center gap-1.5 px-3 h-full text-[14px] font-medium transition-colors whitespace-nowrap relative
                ${isActive
                  ? "text-[var(--color-ink)]"
                  : "text-[var(--color-steel)] hover:text-[var(--color-charcoal)]"
                }
              `}
            >
              <ModuleIcon name={mod.icon} className="w-4 h-4" />
              {mod.label}
              {isActive && (
                <span className="absolute bottom-0 left-3 right-3 h-[2px] bg-[var(--color-primary)] rounded-full" />
              )}
            </Link>
          )
        })}
      </nav>

      {/* Mobile: Module Selector (icon-only button + drawer) */}
      <div className="md:hidden flex-1 min-w-0">
        <button
          onClick={() => setModuleDrawerOpen(true)}
          className="flex items-center gap-2 h-9 px-3 rounded-[var(--rounded-sm)] bg-[var(--color-surface)] text-[var(--color-charcoal)] text-[14px] font-medium max-w-full"
        >
          <ModuleIcon name={moduleMenus.find(m => m.key === activeModule)?.icon || 'factory'} className="w-4 h-4 shrink-0" />
          <span className="truncate">
            {moduleMenus.find(m => m.key === activeModule)?.label || '模块'}
          </span>
        </button>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-1 ml-1 md:ml-4 shrink-0">
        <button className="hidden sm:flex w-8 h-8 items-center justify-center rounded-[var(--rounded-sm)] text-[var(--color-steel)] hover:text-[var(--color-charcoal)] hover:bg-[var(--color-surface)] transition-colors">
          <SearchIcon className="w-[18px] h-[18px]" />
        </button>
        <button className="w-8 h-8 flex items-center justify-center rounded-[var(--rounded-sm)] text-[var(--color-steel)] hover:text-[var(--color-charcoal)] hover:bg-[var(--color-surface)] transition-colors relative">
          <BellIcon className="w-[18px] h-[18px]" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[var(--color-error)] rounded-full" />
        </button>
        <div className="ml-1 md:ml-2 w-8 h-8 rounded-full bg-[var(--color-primary)] flex items-center justify-center text-white text-xs font-semibold">
          J
        </div>
      </div>

      {/* Mobile Module Drawer */}
      <Drawer
        title="选择模块"
        placement="top"
        open={moduleDrawerOpen}
        onClose={() => setModuleDrawerOpen(false)}
        size="large"
        styles={{ body: { padding: '12px 16px' } }}
        className="md:hidden"
      >
        <div className="grid grid-cols-3 gap-2">
          {moduleMenus.map((mod) => {
            const isActive = activeModule === mod.key
            return (
              <Link
                key={mod.key}
                href={mod.path}
                onClick={() => setModuleDrawerOpen(false)}
                className={`
                  flex flex-col items-center gap-1.5 py-3 px-2 rounded-[var(--rounded-md)] border text-[13px] transition-colors
                  ${isActive
                    ? "border-[var(--color-primary)] bg-[var(--color-primary-light)] text-[var(--color-primary)] font-semibold"
                    : "border-[var(--color-hairline)] text-[var(--color-charcoal)] hover:bg-[var(--color-surface)]"
                  }
                `}
              >
                <ModuleIcon name={mod.icon} className="w-5 h-5" />
                <span className="text-center leading-tight">{mod.label}</span>
              </Link>
            )
          })}
        </div>
      </Drawer>
    </header>
  )
}
