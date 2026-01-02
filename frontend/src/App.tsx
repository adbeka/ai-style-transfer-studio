import { useState } from 'react'
import { motion } from 'framer-motion'
import './App.css'

function App() {
  const [contentImage, setContentImage] = useState<File | null>(null)
  const [styleImage, setStyleImage] = useState<File | null>(null)
  const [resultImage, setResultImage] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleStyleTransfer = async () => {
    if (!contentImage || !styleImage) return
    setLoading(true)
    const formData = new FormData()
    formData.append('content', contentImage)
    formData.append('style', styleImage)
    try {
      const response = await fetch('/api/v1/style-transfer', {
        method: 'POST',
        body: formData,
      })
      if (response.ok) {
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        setResultImage(url)
      }
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#11131a] flex flex-col items-center justify-start w-full font-sans">
      {/* Top bar */}
      <div className="w-full bg-[#a259cf] text-white text-center py-2 text-sm font-medium tracking-wide">
        GPT-Image-1.5 <a href="#" className="underline ml-2 hover:text-white/80">Available Now</a>
      </div>
      {/* Header/Nav */}
      <header className="w-full flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="bg-white rounded-full w-10 h-10 flex items-center justify-center">
            <span className="text-2xl font-bold text-[#a259cf]">L</span>
          </div>
          <span className="text-white text-2xl font-bold tracking-tight">Leonardo.AI</span>
        </div>
        <nav className="hidden md:flex gap-8 text-white/90 text-base font-medium">
          <a href="#" className="hover:text-[#a259cf] transition">Features</a>
          <a href="#" className="hover:text-[#a259cf] transition">Solutions</a>
          <a href="#" className="hover:text-[#a259cf] transition">Learn</a>
          <a href="#" className="hover:text-[#a259cf] transition">For Teams</a>
          <a href="#" className="hover:text-[#a259cf] transition">For Developers</a>
          <a href="#" className="hover:text-[#a259cf] transition">Pricing</a>
          <a href="#" className="hover:text-[#a259cf] transition">Contact</a>
        </nav>
        <button className="border border-white/40 rounded-full px-6 py-2 text-white font-semibold hover:bg-[#a259cf] hover:text-white transition">Launch App</button>
      </header>
      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center py-20 px-4 w-full max-w-3xl mx-auto">
        <h1 className="text-6xl md:text-7xl font-extrabold text-center mb-4 leading-tight tracking-tight drop-shadow-xl">
          <span className="block bg-gradient-to-r from-[#a259cf] via-[#5f5fff] to-[#00e0d3] bg-clip-text text-transparent animate-gradient-x">
            AI Style Transfer Studio
          </span>
        </h1>
        <p className="text-xl md:text-2xl text-white/90 text-center max-w-2xl mb-6 font-medium">
          Turn your images into art with neural style transfer. Fast, creative, and easy to use.
        </p>
        <div className="flex items-center gap-2 mb-6">
          <span className="text-yellow-400 text-3xl">★</span>
          <span className="text-yellow-400 text-3xl">★</span>
          <span className="text-yellow-400 text-3xl">★</span>
          <span className="text-yellow-400 text-3xl">★</span>
          <span className="text-yellow-400 text-3xl">★</span>
          <span className="text-white/90 ml-2 font-semibold text-lg">4.8 • 49K Ratings on the Google Play Store</span>
        </div>
        <button
          onClick={() => document.getElementById('upload-section')?.scrollIntoView({ behavior: 'smooth' })}
          className="bg-gradient-to-r from-[#a259cf] via-[#5f5fff] to-[#00e0d3] hover:from-[#5f5fff] hover:to-[#a259cf] text-white font-bold py-4 px-12 rounded-full shadow-2xl text-xl transition-all duration-300 mt-2"
        >
          Generate AI image
        </button>
      </section>
      {/* Upload Section */}
      <section id="upload-section" className="w-full max-w-4xl mx-auto bg-[#181a20] rounded-2xl shadow-xl p-8 mt-10 flex flex-col md:flex-row gap-8 items-start justify-center">
        <div className="flex-1 flex flex-col items-center">
          <label className="block text-lg font-semibold text-white mb-2">Content Image</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setContentImage(e.target.files?.[0] || null)}
            className="w-full text-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-[#a259cf] file:text-white hover:file:bg-[#5f5fff] transition mb-4"
          />
          {contentImage && <img src={URL.createObjectURL(contentImage)} alt="Content" className="mt-2 max-w-full h-40 object-cover rounded-xl border border-white/10 shadow" />}
        </div>
        <div className="flex-1 flex flex-col items-center">
          <label className="block text-lg font-semibold text-white mb-2">Style Image</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setStyleImage(e.target.files?.[0] || null)}
            className="w-full text-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-[#5f5fff] file:text-white hover:file:bg-[#a259cf] transition mb-4"
          />
          {styleImage && <img src={URL.createObjectURL(styleImage)} alt="Style" className="mt-2 max-w-full h-40 object-cover rounded-xl border border-white/10 shadow" />}
        </div>
        <div className="flex-1 flex flex-col items-center">
          <label className="block text-lg font-semibold text-white mb-2">Result</label>
          {resultImage ? (
            <img src={resultImage} alt="Result" className="mt-2 max-w-full h-40 object-cover rounded-xl border border-white/10 shadow" />
          ) : (
            <div className="mt-2 w-full h-40 bg-[#23242a] rounded-xl flex items-center justify-center text-white/30 text-3xl">?</div>
          )}
        </div>
      </section>
      <div className="w-full flex justify-center mt-8 mb-8">
        <button
          onClick={handleStyleTransfer}
          disabled={!contentImage || !styleImage || loading}
          className="bg-gradient-to-r from-[#a259cf] to-[#5f5fff] hover:from-[#5f5fff] hover:to-[#a259cf] text-white font-bold py-3 px-10 rounded-full shadow-lg text-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Processing...' : 'Apply Style Transfer'}
        </button>
      </div>
    </div>
  )
}

export default App
