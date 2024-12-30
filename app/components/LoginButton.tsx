'use client'

import { signOut, useSession } from "next-auth/react"
import { useRouter } from 'next/navigation'

export function LoginButton() {
  const { data: session } = useSession()
  const router = useRouter()

  if (session) {
    return (
      <button
        onClick={() => signOut()}
        className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
      >
        Çıkış Yap
      </button>
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