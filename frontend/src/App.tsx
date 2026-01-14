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
  const [prompt, setPrompt] = useState("");
  const [promptResult, setPromptResult] = useState<string | null>(null);
  const [promptLoading, setPromptLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(true);

  const handlePromptGenerate = async () => {
    if (!prompt.trim()) return;
    setPromptLoading(true);
    try {
      // Replace with your backend endpoint for text-to-image
      const response = await fetch("/api/v1/text-to-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setPromptResult(url);
      }
    } catch (error) {
      console.error("Prompt error:", error);
    } finally {
      setPromptLoading(false);
    }
  };
  
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
    <div className={`${darkMode ? 'dark' : ''} min-h-screen relative flex flex-col items-center justify-start w-full font-sans overflow-x-hidden bg-white dark:bg-[#18181b] transition-colors duration-300`}> 
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
      <div className="w-full bg-gradient-to-r from-[#a259cf] via-[#5f5fff] to-[#00e0d3] text-white text-center py-2 text-sm font-medium tracking-wide shadow-lg flex items-center justify-between px-4">
        <div>
          <span className="drop-shadow">GPT-Image-1.5</span> <a href="#" className="underline ml-2 hover:text-white/80">Available Now</a>
        </div>
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="ml-4 px-3 py-1 rounded-full bg-white/20 text-white font-semibold shadow hover:bg-[#a259cf] transition flex items-center gap-2"
          aria-label="Toggle dark/light mode"
        >
          {darkMode ? <span className="material-icons">light_mode</span> : <span className="material-icons">dark_mode</span>}
          {darkMode ? 'Light' : 'Dark'} Mode
        </button>
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
              <span className="bg-white/10 px-4 py-2 rounded-xl shadow-lg backdrop-blur-md">Turn your images into art with neural style transfer or text-to-image generation. Fast, creative, and easy to use.</span>
            </p>
            <div className="flex flex-col items-center gap-4 w-full mb-6">
              <div className="w-full flex flex-col md:flex-row gap-4 items-center justify-center">
                <input
                  type="text"
                  value={prompt}
                  onChange={e => setPrompt(e.target.value)}
                  placeholder="Describe your image (e.g. A cat in Van Gogh style)"
                  className="w-full md:w-2/3 px-4 py-3 rounded-xl border border-white/20 bg-white/20 text-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-[#a259cf]"
                  disabled={promptLoading}
                />
                <motion.button
                  whileHover={{ scale: 1.08 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={handlePromptGenerate}
                  disabled={promptLoading || !prompt.trim()}
                  className="bg-gradient-to-r from-[#a259cf] via-[#5f5fff] to-[#00e0d3] hover:from-[#5f5fff] hover:to-[#a259cf] text-white font-bold py-3 px-8 rounded-full shadow-2xl text-lg transition-all duration-300 mt-2 md:mt-0 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {promptLoading ? "Generating..." : "Generate from Prompt"}
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.08 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => {
                    setPrompt('A futuristic cityscape in the style of Monet');
                    setTimeout(() => {
                      handlePromptGenerate();
                      document.querySelector('.mt-4')?.scrollIntoView({ behavior: 'smooth' });
                    }, 100);
                  }}
                  className="ml-2 bg-gradient-to-r from-[#00e0d3] to-[#a259cf] text-white font-bold py-3 px-8 rounded-full shadow-2xl text-lg transition-all duration-300 mt-2 md:mt-0"
                >
                  Try Demo
                </motion.button>
              </div>
              {promptResult && (
                <div className="mt-4 w-full flex flex-col items-center">
                  <img src={promptResult} alt="Prompt Result" className="max-w-xs rounded-xl shadow-lg border border-white/10" />
                  <div className="flex gap-3 mt-2">
                    <a href={promptResult} download="prompt-image.png" className="bg-gradient-to-r from-[#a259cf] to-[#00e0d3] text-white px-4 py-2 rounded-full shadow hover:from-[#5f5fff] hover:to-[#a259cf] font-semibold">Download</a>
                    <button onClick={() => navigator.share && navigator.share({ title: 'AI Generated Image', url: promptResult })} className="bg-gradient-to-r from-[#5f5fff] to-[#a259cf] text-white px-4 py-2 rounded-full shadow font-semibold">Share</button>
                  </div>
                  <button onClick={() => setPromptResult(null)} className="mt-2 text-white/70 hover:text-[#a259cf] text-sm">Clear</button>
                </div>
              )}
            </div>
            <div className="flex items-center gap-2 mb-6">
              <span className="text-yellow-400 text-3xl">★</span>
              <span className="text-yellow-400 text-3xl">★</span>
              <span className="text-yellow-400 text-3xl">★</span>
              <span className="text-yellow-400 text-3xl">★</span>
              <span className="text-yellow-400 text-3xl">★</span>
              <span className="text-white/90 ml-2 font-semibold text-lg">4.8 • 49K Ratings on the Google Play Store</span>
            </div>
            <motion.button
              whileHover={{ scale: 1.12 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => document.getElementById('upload-section')?.scrollIntoView({ behavior: 'smooth' })}
              className="bg-gradient-to-r from-[#a259cf] via-[#5f5fff] to-[#00e0d3] hover:from-[#5f5fff] hover:to-[#a259cf] text-white font-extrabold py-5 px-16 rounded-full shadow-2xl text-2xl transition-all duration-300 mt-4 glow-btn flex items-center gap-3"
            >
              <span role="img" aria-label="sparkle" className="text-3xl">✨</span>
              <span>Start Creating Art Now</span>
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
          {/* Style Presets */}
          <div className="flex gap-2 mb-4 flex-wrap justify-center">
            {[
              { name: "Van Gogh", src: "/public/preset-vangogh.jpg" },
              { name: "Picasso", src: "/public/preset-picasso.jpg" },
              { name: "Monet", src: "/public/preset-monet.jpg" },
              { name: "Pop Art", src: "/public/preset-popart.jpg" }
            ].map((preset) => (
              <button
                key={preset.name}
                type="button"
                className="bg-gradient-to-r from-[#a259cf] to-[#00e0d3] text-white px-3 py-1 rounded-full shadow font-semibold text-sm hover:from-[#5f5fff] hover:to-[#a259cf] flex items-center gap-2"
                onClick={() => {
                  fetch(preset.src)
                    .then(res => res.blob())
                    .then(blob => {
                      const file = new File([blob], `${preset.name}.jpg`, { type: blob.type });
                      setStyleImage(file);
                    });
                }}
              >
                <img src={preset.src} alt={preset.name} className="w-6 h-6 rounded-full border border-white/30" />
                {preset.name}
              </button>
            ))}
          </div>
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
            <>
              <img src={resultImage} alt="Result" className="mt-2 max-w-full h-40 object-cover rounded-xl border border-white/10 shadow-lg result-animate" />
              <div className="flex gap-3 mt-2">
                <a href={resultImage} download="styled-image.png" className="bg-gradient-to-r from-[#a259cf] to-[#00e0d3] text-white px-4 py-2 rounded-full shadow hover:from-[#5f5fff] hover:to-[#a259cf] font-semibold">Download</a>
                <button onClick={() => navigator.share && navigator.share({ title: 'AI Generated Image', url: resultImage })} className="bg-gradient-to-r from-[#5f5fff] to-[#a259cf] text-white px-4 py-2 rounded-full shadow font-semibold">Share</button>
              </div>
            </>
          ) : (
            <div className="mt-2 w-full h-40 bg-[#23242a]/80 rounded-xl flex items-center justify-center text-white/30 text-3xl">?</div>
          )}
        </div>
      </section>
        {/* Example Gallery Section */}
        <section className="w-full max-w-5xl mx-auto mt-12 mb-8 px-4">
          <h2 className="text-3xl font-bold text-white mb-6 text-center drop-shadow">Gallery: AI Generated Art</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
            {["/public/example1.jpg", "/public/example2.jpg", "/public/example3.jpg"].map((src, idx) => (
              <div key={idx} className="bg-white/10 rounded-xl shadow-lg border border-white/10 p-4 flex flex-col items-center">
                <img src={src} alt={`Example ${idx+1}`} className="rounded-lg max-h-64 object-cover mb-2" />
                <span className="text-white/80 text-base font-medium">Example {idx+1}</span>
              </div>
            ))}
          </div>
        </section>
        {/* Recent Generations Carousel */}
        <section className="w-full max-w-4xl mx-auto mb-12 px-4">
          <h2 className="text-2xl font-bold text-white mb-4 text-center drop-shadow">Recent Generations</h2>
          <div className="relative flex items-center justify-center">
            <button className="absolute left-0 top-1/2 -translate-y-1/2 bg-white/20 text-white rounded-full p-2 shadow-lg hover:bg-[#a259cf] transition">&#8592;</button>
            <div className="flex gap-6 overflow-x-auto scrollbar-hide py-2 px-8">
              {["/public/recent1.jpg", "/public/recent2.jpg", "/public/recent3.jpg", "/public/recent4.jpg"].map((src, idx) => (
                <div key={idx} className="bg-white/10 rounded-xl shadow-lg border border-white/10 p-2 flex flex-col items-center min-w-[220px]">
                  <img src={src} alt={`Recent ${idx+1}`} className="rounded-lg max-h-40 object-cover mb-2" />
                  <span className="text-white/70 text-sm">Recent {idx+1}</span>
                </div>
              ))}
            </div>
            <button className="absolute right-0 top-1/2 -translate-y-1/2 bg-white/20 text-white rounded-full p-2 shadow-lg hover:bg-[#a259cf] transition">&#8594;</button>
          </div>
        </section>
        {/* FAQ / How it works Section */}
        <section className="w-full max-w-3xl mx-auto mb-16 px-4">
          <h2 className="text-2xl font-bold text-white mb-6 text-center drop-shadow">FAQ & How It Works</h2>
          <div className="space-y-4">
            {[{
              q: "What is AI style transfer?",
              a: "AI style transfer uses neural networks to blend the artistic style of one image with the content of another, creating unique artwork."
            }, {
              q: "How do I use text-to-image generation?",
              a: "Enter a description in the prompt box and click 'Generate from Prompt'. The AI will create an image based on your description."
            }, {
              q: "Can I use my own images?",
              a: "Yes! Upload your own content and style images, or use the style presets for quick results."
            }, {
              q: "Is this free to use?",
              a: "The demo is free. For advanced features, check our pricing or contact us."
            }].map((item, idx) => (
              <details key={idx} className="bg-white/10 rounded-xl p-4 border border-white/20 shadow">
                <summary className="text-lg font-semibold text-white cursor-pointer select-none">{item.q}</summary>
                <p className="text-white/80 mt-2 text-base">{item.a}</p>
              </details>
            ))}
          </div>
        </section>
        {/* User Testimonials Section */}
        <section className="w-full max-w-4xl mx-auto mb-16 px-4">
          <h2 className="text-2xl font-bold text-white mb-6 text-center drop-shadow">What Users Say</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[{
              name: "Alex P.",
              review: "Absolutely stunning results! The style presets are a game changer.",
              avatar: "/public/user1.jpg",
              rating: 5
            }, {
              name: "Maria L.",
              review: "I love how easy it is to turn my photos into art. Highly recommended!",
              avatar: "/public/user2.jpg",
              rating: 5
            }, {
              name: "Samir T.",
              review: "The text-to-image feature is super creative. Great for inspiration.",
              avatar: "/public/user3.jpg",
              rating: 4
            }].map((user, idx) => (
              <div key={idx} className="bg-white/10 rounded-xl p-6 border border-white/20 shadow flex flex-col items-center">
                <img src={user.avatar} alt={user.name} className="w-16 h-16 rounded-full mb-3 border-2 border-[#a259cf] shadow-lg" />
                <div className="flex gap-1 mb-2">
                  {Array.from({ length: user.rating }).map((_, i) => (
                    <span key={i} className="text-yellow-400 text-xl">★</span>
                  ))}
                  {user.rating < 5 && <span className="text-white/30 text-xl">★</span>}
                </div>
                <p className="text-white/90 text-base text-center mb-2">{user.review}</p>
                <span className="text-white/70 text-sm font-semibold">{user.name}</span>
              </div>
            ))}
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
