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

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const moduleKey = pathname.split("/")[1] || "production"
  const currentModule = getModuleByKey(moduleKey)

  if (!currentModule) return null

  const menuItems = buildMenuItems(currentModule.children)

  // 查找当前选中的菜单项
  const findSelectedKey = (items: SubMenuItem[], path: string): string | null => {
    for (const item of items) {
      if (item.path && (path === item.path || path.startsWith(item.path + "/"))) {
        return item.path
      }
      if (item.children) {
        const found = findSelectedKey(item.children, path)
        if (found) return found
      }
    }
    return null
  }

  const selectedKey = findSelectedKey(currentModule.children, pathname) || currentModule.children[0]?.path

  const handleClick: MenuProps['onClick'] = ({ key }) => {
    router.push(key)
  }

  return (
    <aside className="w-56 bg-[var(--color-canvas)] border-r border-[var(--color-hairline)] flex flex-col shrink-0 overflow-y-auto">
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