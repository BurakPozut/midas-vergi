'use client'

import { signOut, useSession } from "next-auth/react"
import { useRouter } from 'next/navigation'

export function LoginButton() {
  const { data: session } = useSession()
  const router = useRouter()

  if (session) {
    return (
      <div className="flex items-center space-x-4">
        <span className="text-gray-200 font-medium">
          {session.user?.name || session.user?.email}
        </span>
        <button
          onClick={() => signOut()}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          Çıkış Yap
        </button>
      </div>
    )
  }

  return (
    <button
      onClick={() => router.push('/auth/signin')}
      className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
    >
      Giriş Yap
    </button>
  )
}