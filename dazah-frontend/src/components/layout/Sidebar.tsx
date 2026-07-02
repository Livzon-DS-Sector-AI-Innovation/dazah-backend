"use client"

import { usePathname, useRouter } from "next/navigation"
import { Menu } from "antd"
import type { MenuProps } from "antd"
import { getModuleByKey, type SubMenuItem } from "@/lib/menu-config"

type MenuItem = NonNullable<MenuProps['items']>[number]

function buildMenuItems(children: SubMenuItem[]): MenuItem[] {
  return children.map((item) => {
    if (item.children && item.children.length > 0) {
      return {
        type: 'submenu' as const,
        key: item.key || item.label,
        label: item.label,
        children: buildMenuItems(item.children),
      }
    }
    return {
      type: 'item' as const,
      key: item.path || item.key || item.label,
      label: item.label,
    }
  })
}

interface SidebarProps {
  onNavigate?: () => void
}

export function Sidebar({ onNavigate }: SidebarProps = {}) {
  const pathname = usePathname()
  const router = useRouter()
  const moduleKey = pathname.split("/")[1] || "production"
  const currentModule = getModuleByKey(moduleKey)

  if (!currentModule) return null

  const menuItems = buildMenuItems(currentModule.children)

  // 查找当前选中的菜单项（按路径长度排序，优先精确匹配）
  const findSelectedKey = (items: SubMenuItem[], path: string): string | null => {
    // 收集所有匹配的菜单项
    const matchedItems: { path: string; key: string }[] = []
    
    const collectMatches = (items: SubMenuItem[]) => {
      for (const item of items) {
        if (item.path) {
          // 精确匹配或前缀匹配
          if (path === item.path || path.startsWith(item.path + "/")) {
            matchedItems.push({ path: item.path, key: item.path })
          }
        }
        if (item.children) {
          collectMatches(item.children)
        }
      }
    }
    
    collectMatches(items)
    
    // 按路径长度降序排序，优先匹配更长的路径（更精确）
    matchedItems.sort((a, b) => b.path.length - a.path.length)
    
    return matchedItems.length > 0 ? matchedItems[0].key : null
  }

  const selectedKey = findSelectedKey(currentModule.children, pathname) || currentModule.children[0]?.path

  const handleClick: MenuProps['onClick'] = ({ key }) => {
    router.push(key)
    onNavigate?.()
  }

  return (
    <aside className="w-56 bg-[var(--color-canvas)] border-r border-[var(--color-hairline)] flex flex-col shrink-0 overflow-y-auto h-full">
      <div className="px-4 pt-5 pb-3">
        <h2 className="text-[18px] font-semibold text-[var(--color-charcoal)]">
          {currentModule.label}
        </h2>
      </div>

      <Menu
        mode="inline"
        selectedKeys={[selectedKey || '']}
        items={menuItems}
        onClick={handleClick}
        className="sidebar-menu flex-1"
        style={{ borderInlineEnd: 'none' }}
      />

      <div className="px-4 py-3 border-t border-[var(--color-hairline-soft)]">
        <p className="text-[12px] text-[var(--color-stone)]">
          v0.1.0
        </p>
      </div>
    </aside>
  )
}