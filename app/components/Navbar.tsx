'use client'

import { LoginButton } from './LoginButton'

export function Navbar() {
  return (
    <div className="fixed w-full flex justify-center p-4 z-50">
      <nav className="backdrop-blur-md bg-white/10 rounded-full border border-white/10 shadow-lg w-[95%]">
        <div className="px-8 py-3">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-bold text-blue-500">Midas Vergi</h1>
            <LoginButton />
          </div>
        </div>
      </nav>
    </div>
  )
}