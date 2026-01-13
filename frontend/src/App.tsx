import { useState, useEffect } from 'react'
  // Parallax effect for floating shapes
  useEffect(() => {
    const handleParallax = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 2;
      const y = (e.clientY / window.innerHeight - 0.5) * 2;
      const shapes = document.querySelectorAll<HTMLElement>('.floating-shape');
      shapes.forEach((shape, i) => {
        const factor = (i + 1) * 8;
        shape.style.transform = `translate(${x * factor}px, ${y * factor}px)`;
      });
    };
    window.addEventListener('mousemove', handleParallax);
    return () => window.removeEventListener('mousemove', handleParallax);
  }, []);
import { motion } from 'framer-motion'
import './App.css'

function App() {
  const [contentImage, setContentImage] = useState<File | null>(null)
  const [styleImage, setStyleImage] = useState<File | null>(null)
  const [resultImage, setResultImage] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  
    // Parallax effect for floating shapes
    useEffect(() => {
      const handleParallax = (e: MouseEvent) => {
        const x = (e.clientX / window.innerWidth - 0.5) * 2;
        const y = (e.clientY / window.innerHeight - 0.5) * 2;
        const shapes = document.querySelectorAll<HTMLElement>('.floating-shape');
        shapes.forEach((shape, i) => {
          const factor = (i + 1) * 8;
          shape.style.transform = `translate(${x * factor}px, ${y * factor}px)`;
        });
      };
      window.addEventListener('mousemove', handleParallax);
      return () => window.removeEventListener('mousemove', handleParallax);
    }, []);

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
    <div className="min-h-screen relative flex flex-col items-center justify-start w-full font-sans overflow-x-hidden">
      {/* Animated Gradient Background */}
      <div className="absolute inset-0 -z-10 animate-gradient-move bg-gradient-to-br from-[#a259cf]/40 via-[#5f5fff]/30 to-[#00e0d3]/40 blur-2xl opacity-80" />
      {/* Animated Floating Shapes */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="floating-shape shape1" />
        <div className="floating-shape shape2" />
        <div className="floating-shape shape3" />
        <div className="floating-shape shape4" />
      </div>
      {/* Top bar */}
      <div className="w-full bg-gradient-to-r from-[#a259cf] via-[#5f5fff] to-[#00e0d3] text-white text-center py-2 text-sm font-medium tracking-wide shadow-lg">
        <span className="drop-shadow">GPT-Image-1.5</span> <a href="#" className="underline ml-2 hover:text-white/80">Available Now</a>
      </div>
      {/* Header/Nav */}
      <header className="w-full flex items-center justify-between px-8 py-6 max-w-7xl mx-auto backdrop-blur-xl bg-white/5 rounded-xl shadow-lg mt-6">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-[#a259cf] to-[#00e0d3] rounded-full w-12 h-12 flex items-center justify-center shadow-lg">
            <span className="text-3xl font-extrabold text-white drop-shadow">L</span>
          </div>
          <span className="text-white text-2xl font-extrabold tracking-tight drop-shadow">Leonardo.AI</span>
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
        <button className="border border-white/40 rounded-full px-6 py-2 text-white font-semibold hover:bg-gradient-to-r hover:from-[#a259cf] hover:to-[#00e0d3] hover:text-white transition shadow-lg">Launch App</button>
      </header>
      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center py-20 px-4 w-full max-w-3xl mx-auto">
        <div className="relative w-full">
          <div className="absolute -inset-2 z-0 rounded-3xl bg-gradient-to-br from-[#a259cf]/60 via-[#5f5fff]/40 to-[#00e0d3]/60 blur-2xl opacity-80" style={{ filter: 'blur(40px)' }} />
          <div className="relative z-10 p-10 rounded-3xl bg-white/10 backdrop-blur-2xl shadow-2xl border border-white/20 flex flex-col items-center" style={{ boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)' }}>
            <h1 className="text-6xl md:text-7xl font-extrabold text-center mb-4 leading-tight tracking-tight drop-shadow-xl">
              <span className="block bg-gradient-to-r from-[#a259cf] via-[#5f5fff] to-[#00e0d3] bg-clip-text text-transparent animate-gradient-x">
                AI Style Transfer Studio
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-white/90 text-center max-w-2xl mb-6 font-medium">
              <span className="bg-white/10 px-4 py-2 rounded-xl shadow-lg backdrop-blur-md">Turn your images into art with neural style transfer. Fast, creative, and easy to use.</span>
            </p>
            <div className="flex items-center gap-2 mb-6">
              <span className="text-yellow-400 text-3xl">★</span>
              <span className="text-yellow-400 text-3xl">★</span>
              <span className="text-yellow-400 text-3xl">★</span>
              <span className="text-yellow-400 text-3xl">★</span>
              <span className="text-yellow-400 text-3xl">★</span>
              <span className="text-white/90 ml-2 font-semibold text-lg">4.8 • 49K Ratings on the Google Play Store</span>
            </div>
            <motion.button
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => document.getElementById('upload-section')?.scrollIntoView({ behavior: 'smooth' })}
              className="bg-gradient-to-r from-[#a259cf] via-[#5f5fff] to-[#00e0d3] hover:from-[#5f5fff] hover:to-[#a259cf] text-white font-bold py-4 px-12 rounded-full shadow-2xl text-xl transition-all duration-300 mt-2 glow-btn"
            >
              Generate AI image
            </motion.button>
          </div>
        </div>
      </section>
      {/* Upload Section with glassmorphism */}
      <section id="upload-section" className="w-full max-w-4xl mx-auto bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl p-8 mt-10 flex flex-col md:flex-row gap-8 items-start justify-center border border-white/20">
        <div className="flex-1 flex flex-col items-center">
          <label className="block text-lg font-semibold text-white mb-2">Content Image</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setContentImage(e.target.files?.[0] || null)}
            className="w-full text-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-[#a259cf] file:to-[#00e0d3] file:text-white hover:file:bg-[#5f5fff] transition mb-4"
          />
          {contentImage && <img src={URL.createObjectURL(contentImage)} alt="Content" className="mt-2 max-w-full h-40 object-cover rounded-xl border border-white/10 shadow-lg" />}
        </div>
        <div className="flex-1 flex flex-col items-center">
          <label className="block text-lg font-semibold text-white mb-2">Style Image</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setStyleImage(e.target.files?.[0] || null)}
            className="w-full text-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-[#5f5fff] file:to-[#a259cf] file:text-white hover:file:bg-[#a259cf] transition mb-4"
          />
          {styleImage && <img src={URL.createObjectURL(styleImage)} alt="Style" className="mt-2 max-w-full h-40 object-cover rounded-xl border border-white/10 shadow-lg" />}
        </div>
        <div className="flex-1 flex flex-col items-center">
          <label className="block text-lg font-semibold text-white mb-2">Result</label>
          {resultImage ? (
            <img src={resultImage} alt="Result" className="mt-2 max-w-full h-40 object-cover rounded-xl border border-white/10 shadow-lg result-animate" />
          ) : (
            <div className="mt-2 w-full h-40 bg-[#23242a]/80 rounded-xl flex items-center justify-center text-white/30 text-3xl">?</div>
          )}
        </div>
      </section>
      <div className="w-full flex justify-center mt-8 mb-8">
        <motion.button
          whileHover={{ scale: 1.07 }}
          whileTap={{ scale: 0.97 }}
          onClick={handleStyleTransfer}
          disabled={!contentImage || !styleImage || loading}
          className="bg-gradient-to-r from-[#a259cf] to-[#5f5fff] hover:from-[#5f5fff] hover:to-[#a259cf] text-white font-bold py-3 px-10 rounded-full shadow-xl text-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Processing...' : 'Apply Style Transfer'}
        </motion.button>
      </div>
      {/* Footer */}
      <footer className="w-full py-6 flex flex-col items-center justify-center text-white/70 text-sm mt-auto">
        <div className="flex gap-4 mb-2">
          <a href="#" className="hover:text-[#a259cf] transition">Twitter</a>
          <a href="#" className="hover:text-[#5f5fff] transition">GitHub</a>
          <a href="#" className="hover:text-[#00e0d3] transition">Docs</a>
        </div>
        <span>© 2026 Leonardo.AI. All rights reserved.</span>
      </footer>
    </div>
  )
}

export default App
