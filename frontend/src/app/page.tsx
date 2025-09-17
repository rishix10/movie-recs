'use client'

import { useState, useEffect } from 'react'
import { Search, Star, Calendar, Play } from 'lucide-react'

interface Movie {
  id: string
  title: string
  overview: string | null
  poster_url: string | null
  release_year: number | null
  rating: number | null
}

interface RecommendResponse {
  results: Movie[]
}

export default function Home() {
  const [movies, setMovies] = useState<Movie[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const fetchRecommendations = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          limit: 12
        })
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch recommendations')
      }
      
      const data: RecommendResponse = await response.json()
      setMovies(data.results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const searchMovies = async (query: string) => {
    if (!query.trim()) {
      fetchRecommendations()
      return
    }
    
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/movies/search?q=${encodeURIComponent(query)}&limit=12`)
      
      if (!response.ok) {
        throw new Error('Failed to search movies')
      }
      
      const data: RecommendResponse = await response.json()
      setMovies(data.results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRecommendations()
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    searchMovies(searchQuery)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-white">
              🎬 MovieRecs
            </h1>
            <div className="text-sm text-gray-300">
              AI-Powered Movie Recommendations
            </div>
          </div>
        </div>
      </header>

      {/* Search Bar */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <form onSubmit={handleSearch} className="relative">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search for movies..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <button
              type="submit"
              className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-xl transition-colors"
            >
              Search
            </button>
          </div>
        </form>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        {error && (
          <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-2xl font-bold text-white">
                {searchQuery ? `Search Results for "${searchQuery}"` : 'Recommended Movies'}
              </h2>
              {!searchQuery && (
                <button
                  onClick={fetchRecommendations}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Refresh Recommendations
                </button>
              )}
            </div>

            {movies.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-lg">
                  {searchQuery ? 'No movies found for your search.' : 'No recommendations available.'}
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {movies.map((movie) => (
                  <div
                    key={movie.id}
                    className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl overflow-hidden hover:bg-white/20 transition-all duration-300 group"
                  >
                    <div className="aspect-[2/3] relative overflow-hidden">
                      {movie.poster_url ? (
                        <img
                          src={movie.poster_url}
                          alt={movie.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                      ) : (
                        <div className="w-full h-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                          <Play className="w-12 h-12 text-white opacity-50" />
                        </div>
                      )}
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300" />
                    </div>
                    
                    <div className="p-4">
                      <h3 className="font-bold text-white text-lg mb-2 line-clamp-2">
                        {movie.title}
                      </h3>
                      
                      {movie.overview && (
                        <p className="text-gray-300 text-sm mb-3 line-clamp-3">
                          {movie.overview}
                        </p>
                      )}
                      
                      <div className="flex items-center justify-between text-sm text-gray-400">
                        <div className="flex items-center space-x-1">
                          <Star className="w-4 h-4 text-yellow-400 fill-current" />
                          <span>{movie.rating?.toFixed(1) || 'N/A'}</span>
                        </div>
                        {movie.release_year && (
                          <div className="flex items-center space-x-1">
                            <Calendar className="w-4 h-4" />
                            <span>{movie.release_year}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-black/20 backdrop-blur-sm border-t border-white/10 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-400">
            <p>Built with Next.js, FastAPI, and AI/ML for personalized movie recommendations</p>
            <p className="mt-2 text-sm">
              Data powered by TMDB • Recommendations by hybrid ML models
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}