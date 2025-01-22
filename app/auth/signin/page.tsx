'use client'

import { signIn } from "next-auth/react"
import Image from "next/image"
import { useState } from "react"
import { Register } from "@/components/Register"

export default function SignIn() {
  const [isRegistering, setIsRegistering] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await signIn('credentials', {
        email,
        password,
        redirect: false
      })

      if (result?.error) {
        setError('Email veya şifre hatalı')
      } else if (result?.ok) {
        window.location.href = '/'
      }
    } catch (err) {
      setError('Bir hata oluştu')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-navy-900 flex items-center justify-center px-4">
      <div className="backdrop-blur-lg bg-white/10 p-8 rounded-3xl border border-white/20 shadow-xl w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-white mb-2">
            {isRegistering ? 'Kayıt Ol' : 'Giriş Yap'}
          </h1>
          <p className="text-gray-200">
            {isRegistering ? 'Yeni hesap oluşturun' : 'Hesabınıza giriş yapın'}
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-500 text-sm">
            {error}
          </div>
        )}

        {isRegistering ? (
          <Register
            onError={setError}
            setLoading={setLoading}
            loading={loading}
          />
        ) : (
          <form onSubmit={handleLogin} className="space-y-4 mb-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-200 mb-1">
                Email
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="ornek@email.com"
                required
                disabled={loading}
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-200 mb-1">
                Şifre
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="••••••••"
                required
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              className="w-full py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading}
            >
              {loading ? 'İşleniyor...' : 'Giriş Yap'}
            </button>
          </form>
        )}

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/20"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 text-gray-200 bg-[#0f172a]">veya</span>
          </div>
        </div>

        <button
          onClick={() => signIn('google', { callbackUrl: '/' })}
          className="flex items-center justify-center w-full gap-3 px-4 py-3 text-gray-700 transition-all bg-white rounded-xl hover:bg-gray-50 active:bg-gray-100"
          disabled={loading}
        >
          <Image
            src="/google.svg"
            alt="Google Logo"
            width={20}
            height={20}
            className="w-5 h-5"
          />
          <span>
            {isRegistering ? 'Google ile Kayıt Ol' : 'Google ile Giriş Yap'}
          </span>
        </button>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsRegistering(!isRegistering)
              setError('')
            }}
            className="text-blue-400 hover:text-blue-300 transition-colors text-sm"
            disabled={loading}
          >
            {isRegistering
              ? 'Zaten hesabınız var mı? Giriş yapın'
              : 'Hesabınız yok mu? Kayıt olun'}
          </button>
        </div>
      </div>
    </div>
  )
} 