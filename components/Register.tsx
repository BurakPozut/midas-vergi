'use client'

import { useState } from "react"
import { signIn } from "next-auth/react"
import { RegisterSchema } from "@/schemas"
import { register } from "@/actions/register"

interface RegisterProps {
  onError: (error: string) => void
  setLoading: (loading: boolean) => void
  loading: boolean
}

export function Register({ onError, setLoading, loading }: RegisterProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    onError('')
    setLoading(true)
    // console.log("e: ", e)

    try {
      const formData = {
        email: email.trim(),
        password,
        name: name.trim()
      }

      console.log("formData: ", formData)

      // Validate the data
      const validationResult = RegisterSchema.safeParse(formData)
      if (!validationResult.success) {
        onError(validationResult.error.issues[0].message)
        setLoading(false)
        return
      }

      // Call the server action
      const result = await register(validationResult.data)

      if (result.error) {
        onError(result.error)
      } else {
        // After successful registration, sign in
        await signIn('credentials', {
          email: formData.email,
          password: formData.password,
          callbackUrl: '/'
        })
      }
    } catch (err) {
      onError('Bir hata oluştu')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 mb-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-200 mb-1">
          Ad Soyad
        </label>
        <input
          type="text"
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ad Soyad"
          required
          disabled={loading}
        />
      </div>
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
        {loading ? 'İşleniyor...' : 'Kayıt Ol'}
      </button>
    </form>
  )
} 