import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface StylePreset {
  id: number;
  name: string;
  description: string;
  artist: string;
  style_period: string;
  color_palette: string[];
  usage_count: number;
}

interface HistoryItem {
  id: number;
  content_image_path: string;
  style_image_path: string;
  result_image_path: string;
  model_type: string;
  style_strength: number;
  processing_time: number;
  created_at: string;
}

interface EnhancedControlsProps {
  onStyleTransfer: (options: any) => void;
  loading: boolean;
  contentImage: File | null;
  styleImage: File | null;
}

export default function EnhancedControls({ 
  onStyleTransfer, 
  loading, 
  contentImage, 
  styleImage 
}: EnhancedControlsProps) {
  const [styleStrength, setStyleStrength] = useState(1.0);
  const [preserveContent, setPreserveContent] = useState(0.0);
  const [artisticFilter, setArtisticFilter] = useState('none');
  const [modelType, setModelType] = useState('adain');
  const [presets, setPresets] = useState<StylePreset[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showPresets, setShowPresets] = useState(false);

  useEffect(() => {
    fetchPresets();
    fetchHistory();
  }, []);

  const fetchPresets = async () => {
    try {
      const response = await fetch('/api/v1/presets');
      if (response.ok) {
        const data = await response.json();
        setPresets(data.presets);
      }
    } catch (error) {
      console.error('Failed to fetch presets:', error);
    }
  };

  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/history?limit=10', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setHistory(data.history);
      }
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

  const handleAdvancedTransfer = () => {
    const options = {
      style_strength: styleStrength,
      preserve_content: preserveContent,
      artistic_filter: artisticFilter,
      model_type: modelType,
    };
    onStyleTransfer(options);
  };

  const createStylePreview = async () => {
    if (!contentImage) return;
    
    try {
      const formData = new FormData();
      formData.append('content', contentImage);
      
      const response = await fetch('/api/v1/style-preview?styles=oil_painting&styles=watercolor&styles=pencil_sketch', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        // Open preview in new window
        const newWindow = window.open('', '_blank');
        if (newWindow) {
          newWindow.document.write(`
            <html>
              <head><title>Style Preview</title></head>
              <body style="margin:0; background:#000; display:flex; justify-content:center; align-items:center; min-height:100vh;">
                <img src="${url}" style="max-width:90vw; max-height:90vh;" />
              </body>
            </html>
          `);
        }
      }
    } catch (error) {
      console.error('Failed to create preview:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Advanced Controls */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
      >
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          ⚙️ Advanced Controls
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Style Strength */}
          <div>
            <label className="block text-white font-semibold mb-2">
              Style Strength: {styleStrength.toFixed(1)}
            </label>
            <input
              type="range"
              min="0.1"
              max="2.0"
              step="0.1"
              value={styleStrength}
              onChange={(e) => setStyleStrength(parseFloat(e.target.value))}
              className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Content Preservation */}
          <div>
            <label className="block text-white font-semibold mb-2">
              Preserve Content: {(preserveContent * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={preserveContent}
              onChange={(e) => setPreserveContent(parseFloat(e.target.value))}
              className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Model Type */}
          <div>
            <label className="block text-white font-semibold mb-2">Model Type</label>
            <select
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
              className="w-full p-2 rounded-lg bg-white/20 text-white border border-white/30"
            >
              <option value="adain">AdaIN (Fast)</option>
              <option value="cartoon">Cartoon Style</option>
            </select>
          </div>

          {/* Artistic Filter */}
          <div>
            <label className="block text-white font-semibold mb-2">Artistic Filter</label>
            <select
              value={artisticFilter}
              onChange={(e) => setArtisticFilter(e.target.value)}
              className="w-full p-2 rounded-lg bg-white/20 text-white border border-white/30"
            >
              <option value="none">None</option>
              <option value="oil_painting">Oil Painting</option>
              <option value="watercolor">Watercolor</option>
              <option value="pencil_sketch">Pencil Sketch</option>
              <option value="vintage">Vintage</option>
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 mt-6">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleAdvancedTransfer}
            disabled={!contentImage || !styleImage || loading}
            className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 px-6 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '🎨 Processing...' : '🎨 Advanced Transfer'}
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={createStylePreview}
            disabled={!contentImage}
            className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white py-3 px-6 rounded-xl font-semibold disabled:opacity-50"
          >
            👁️ Preview Styles
          </motion.button>
        </div>
      </motion.div>

      {/* Style Presets */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-white">🎭 Style Presets</h3>
          <button
            onClick={() => setShowPresets(!showPresets)}
            className="text-white/70 hover:text-white"
          >
            {showPresets ? '↑ Hide' : '↓ Show'}
          </button>
        </div>

        {showPresets && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {presets.slice(0, 6).map((preset) => (
              <motion.div
                key={preset.id}
                whileHover={{ scale: 1.03 }}
                className="bg-white/5 rounded-xl p-4 border border-white/10 hover:bg-white/10 transition-all cursor-pointer"
              >
                <h4 className="font-bold text-white">{preset.name}</h4>
                <p className="text-purple-200 text-sm">{preset.artist}</p>
                <p className="text-white/70 text-xs mt-1">{preset.description}</p>
                <div className="flex gap-1 mt-2">
                  {preset.color_palette.map((color, idx) => (
                    <div
                      key={idx}
                      className="w-4 h-4 rounded border border-white/20"
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
                <p className="text-purple-200 text-xs mt-2">Used {preset.usage_count} times</p>
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>

      {/* History */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-white">📚 Recent History</h3>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="text-white/70 hover:text-white"
          >
            {showHistory ? '↑ Hide' : '↓ Show'}
          </button>
        </div>

        {showHistory && (
          <div className="space-y-3">
            {history.length === 0 ? (
              <p className="text-white/60 text-center py-4">No style transfers yet</p>
            ) : (
              history.slice(0, 5).map((item) => (
                <motion.div
                  key={item.id}
                  whileHover={{ scale: 1.02 }}
                  className="bg-white/5 rounded-xl p-4 border border-white/10 hover:bg-white/10 transition-all"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-white font-semibold">
                        {item.model_type.toUpperCase()} Transfer
                      </p>
                      <p className="text-purple-200 text-sm">
                        Strength: {item.style_strength} • {item.processing_time.toFixed(1)}s
                      </p>
                      <p className="text-white/60 text-xs">
                        {new Date(item.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <div className="w-12 h-12 bg-white/20 rounded border border-white/20"></div>
                      <div className="text-white">→</div>
                      <div className="w-12 h-12 bg-white/20 rounded border border-white/20"></div>
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        )}
      </motion.div>
    </div>
  );
}