import React, { useState, useEffect } from 'react'
import { detectionApi } from '@/lib/api'
import { ModelInfo, BrandDatabase } from '@/lib/types'
import { Server, Database, Cpu, Users, AlertCircle, CheckCircle, RefreshCw } from 'lucide-react'

export const SystemStatus: React.FC = () => {
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null)
  const [healthStatus, setHealthStatus] = useState<{ status: string; model_ready: boolean } | null>(null)
  const [brandsCount, setBrandsCount] = useState<number>(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSystemStatus = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const [healthResponse, modelResponse, brandsResponse] = await Promise.all([
        detectionApi.healthCheck(),
        detectionApi.getModelInfo(),
        detectionApi.getBrandsDatabase()
      ])

      if (healthResponse.success) {
        setHealthStatus(healthResponse.data!)
      }

      if (modelResponse.success) {
        setModelInfo(modelResponse.data!)
      }

      if (brandsResponse.success) {
        const brands = brandsResponse.data!
        const totalProducts = Object.values(brands).reduce((sum, brand) => sum + brand.products.length, 0)
        setBrandsCount(totalProducts)
      }
    } catch (err) {
      setError('Gagal memuat status sistem')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchSystemStatus()
    
    // Auto refresh every 30 seconds
    const interval = setInterval(fetchSystemStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
        <div className="flex items-center space-x-2 mb-4">
          <Server className="h-5 w-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">Status Sistem</h3>
        </div>
        <div className="flex items-center justify-center py-8">
          <RefreshCw className="h-6 w-6 text-blue-500 animate-spin" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
        <div className="flex items-center space-x-2 mb-4">
          <Server className="h-5 w-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">Status Sistem</h3>
        </div>
        <div className="text-center py-8">
          <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
          <p className="text-red-600">{error}</p>
          <button
            onClick={fetchSystemStatus}
            className="mt-2 text-blue-600 hover:text-blue-800 text-sm"
          >
            Coba Lagi
          </button>
        </div>
      </div>
    )
  }

  const isSystemHealthy = healthStatus?.status === 'healthy' && healthStatus?.model_ready

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className={`p-4 ${isSystemHealthy ? 'bg-green-50 border-b border-green-100' : 'bg-red-50 border-b border-red-100'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Server className="h-5 w-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Status Sistem</h3>
          </div>
          <div className="flex items-center space-x-2">
            {isSystemHealthy ? (
              <>
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium text-green-700">Online</span>
              </>
            ) : (
              <>
                <AlertCircle className="h-4 w-4 text-red-500" />
                <span className="text-sm font-medium text-red-700">Offline</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* API Status */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-2">
            <Database className="h-4 w-4 text-gray-600" />
            <span className="font-medium text-gray-700">API Server</span>
          </div>
          <div className="flex items-center space-x-2">
            {healthStatus?.status === 'healthy' ? (
              <>
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-green-600">Aktif</span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                <span className="text-sm text-red-600">Tidak Aktif</span>
              </>
            )}
          </div>
        </div>

        {/* Model Status */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-2">
            <Cpu className="h-4 w-4 text-gray-600" />
            <span className="font-medium text-gray-700">AI Model</span>
          </div>
          <div className="flex items-center space-x-2">
            {healthStatus?.model_ready ? (
              <>
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-green-600">Siap</span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                <span className="text-sm text-red-600">Tidak Siap</span>
              </>
            )}
          </div>
        </div>

        {/* Model Information */}
        {modelInfo && modelInfo.status === 'ready' && (
          <div className="space-y-3">
            <div className="border-t pt-3">
              <h4 className="font-medium text-gray-900 mb-2">Informasi Model</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="text-gray-500">Tipe:</span>
                  <div className="font-medium">{modelInfo.model_type}</div>
                </div>
                <div>
                  <span className="text-gray-500">Estimators:</span>
                  <div className="font-medium">{modelInfo.n_estimators}</div>
                </div>
                <div>
                  <span className="text-gray-500">Max Depth:</span>
                  <div className="font-medium">{modelInfo.max_depth}</div>
                </div>
                <div>
                  <span className="text-gray-500">Features:</span>
                  <div className="font-medium">{modelInfo.feature_count}</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Database Information */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-2">
            <Users className="h-4 w-4 text-gray-600" />
            <span className="font-medium text-gray-700">Database Produk</span>
          </div>
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900">{brandsCount}</div>
            <div className="text-xs text-gray-500">produk terdaftar</div>
          </div>
        </div>

        {/* Refresh Button */}
        <div className="pt-2">
          <button
            onClick={fetchSystemStatus}
            disabled={isLoading}
            className="w-full flex items-center justify-center space-x-2 py-2 px-4 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh Status</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default SystemStatus