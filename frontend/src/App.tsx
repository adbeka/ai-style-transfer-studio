import { useState } from 'react'
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
      const response = await fetch('http://localhost:8000/api/v1/style-transfer', {
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
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-4xl w-full">
        <h1 className="text-3xl font-bold text-center mb-8">AI Style Transfer Studio</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Content Image</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setContentImage(e.target.files?.[0] || null)}
              className="w-full"
            />
            {contentImage && <img src={URL.createObjectURL(contentImage)} alt="Content" className="mt-2 max-w-full h-48 object-cover" />}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Style Image</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setStyleImage(e.target.files?.[0] || null)}
              className="w-full"
            />
            {styleImage && <img src={URL.createObjectURL(styleImage)} alt="Style" className="mt-2 max-w-full h-48 object-cover" />}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Result</label>
            {resultImage && <img src={resultImage} alt="Result" className="mt-2 max-w-full h-48 object-cover" />}
          </div>
        </div>
        <div className="text-center">
          <button
            onClick={handleStyleTransfer}
            disabled={!contentImage || !styleImage || loading}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Apply Style Transfer'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
