import { useState } from 'react';

export default function LoginForm({ onLogin }: { onLogin: (token: string) => void }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isRegister, setIsRegister] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      if (isRegister) {
        // Registration
        const registerResponse = await fetch('/api/v1/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email,
            username: email,
            full_name: fullName,
            password
          }),
        });
        
        if (!registerResponse.ok) {
          const errorData = await registerResponse.json();
          setError(errorData.detail || 'Registration failed');
          setLoading(false);
          return;
        }
        
        // Auto-login after successful registration
        const loginFormData = new URLSearchParams({ username: email, password });
        const loginResponse = await fetch('/api/v1/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: loginFormData,
        });
        
        if (loginResponse.ok) {
          const data = await loginResponse.json();
          onLogin(data.access_token);
        }
      } else {
        // Login
        const response = await fetch('/api/v1/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({ username: email, password }),
        });
        
        if (!response.ok) {
          setError('Invalid credentials');
          setLoading(false);
          return;
        }
        
        const data = await response.json();
        onLogin(data.access_token);
      }
    } catch (err) {
      setError(isRegister ? 'Registration failed' : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900 flex items-center justify-center p-4">
      <form onSubmit={handleSubmit} className="bg-white/10 backdrop-blur-xl p-8 rounded-2xl shadow-2xl w-full max-w-md border border-white/20">
        <h2 className="text-3xl font-bold mb-6 text-center text-white">
          {isRegister ? 'Create Account' : 'Welcome Back'}
        </h2>
        
        {isRegister && (
          <input
            type="text"
            placeholder="Full Name"
            value={fullName}
            onChange={e => setFullName(e.target.value)}
            className="w-full mb-4 p-3 border border-white/30 rounded-xl bg-white/20 text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-purple-500"
            required
          />
        )}
        
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          className="w-full mb-4 p-3 border border-white/30 rounded-xl bg-white/20 text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-purple-500"
          required
        />
        
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          className="w-full mb-4 p-3 border border-white/30 rounded-xl bg-white/20 text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-purple-500"
          required
        />
        
        {error && (
          <div className="text-red-300 text-sm mb-4 bg-red-900/30 p-2 rounded">
            {error}
          </div>
        )}
        
        <button
          type="submit"
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-xl hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 font-semibold text-lg transition-all duration-300"
          disabled={loading}
        >
          {loading ? (isRegister ? 'Creating Account...' : 'Logging in...') : (isRegister ? 'Create Account' : 'Login')}
        </button>
        
        <div className="mt-6 text-center">
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setError('');
            }}
            className="text-purple-300 hover:text-white transition-colors"
          >
            {isRegister ? 'Already have an account? Login' : 'Need an account? Register'}
          </button>
        </div>
        
        {!isRegister && (
          <div className="mt-4 text-center text-sm text-purple-200">
            Demo account: test@example.com / testpassword
          </div>
        )}
      </form>
    </div>
  );
}
