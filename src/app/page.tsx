'use client'

import React, { useState, useRef, useCallback } from 'react'
import dynamic from 'next/dynamic'
import { Camera, Upload, AlertTriangle, CheckCircle, XCircle, BarChart3, Scan } from 'lucide-react'
import { DetectionResult } from '@/lib/types'
import { DetectionResultCard } from '@/components/DetectionResultCard'
import { DetectionHistory } from '@/components/DetectionHistory'
import { SystemStatus } from '@/components/SystemStatus'
import { detectionApi } from '@/lib/api'
import { dataURLtoFile, downloadResult } from '@/lib/utils'

// Dynamically import Webcam to avoid SSR issues
const Webcam = dynamic(() => import('react-webcam'), { ssr: false })

export default function Dashboard() {
  const [isDetecting, setIsDetecting] = useState(false)
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [isWebcamActive, setIsWebcamActive] = useState(false)
  const [detectionHistory, setDetectionHistory] = useState<DetectionResult[]>([])
  
  const webcamRef = useRef<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const capture = useCallback(async () => {
    if (!webcamRef.current) return
    
    const imageSrc = webcamRef.current.getScreenshot()
    if (imageSrc) {
      setCapturedImage(imageSrc)
      await detectProduct(imageSrc)
    }
  }, [webcamRef])

  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = async (e) => {
      const imageSrc = e.target?.result as string
      setCapturedImage(imageSrc)
      await detectProduct(imageSrc)
    }
    reader.readAsDataURL(file)
  }, [])

  const detectProduct = async (imageData: string) => {
    setIsDetecting(true)
    setError(null)
    
    try {
      // Convert base64 to File object
      const imageFile = dataURLtoFile(imageData, 'capture.jpg')
      
      // Use API to detect
      const result = await detectionApi.analyzeImage(imageFile)
      
      if (!result.success) {
        throw new Error(result.error || 'Gagal melakukan deteksi produk')
      }
      
      const data = result.data!
      setDetectionResult(data)
      setDetectionHistory((prev: DetectionResult[]) => [data, ...prev.slice(0, 9)]) // Keep last 10 results
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Terjadi kesalahan saat deteksi')
      console.error('Detection error:', err)
    } finally {
      setIsDetecting(false)
    }
  }

  const toggleWebcam = () => {
    setIsWebcamActive(!isWebcamActive)
    if (isWebcamActive) {
      setCapturedImage(null)
      setDetectionResult(null)
    }
  }

  const handleDownloadResult = () => {
    if (detectionResult) {
      downloadResult(detectionResult, `detection-${Date.now()}.json`)
    }
  }

  const handleSelectHistoryResult = (result: DetectionResult) => {
    setDetectionResult(result)
    setCapturedImage(null) // Clear captured image when viewing history
  }

  return (
    <div className="min-h-screen p-4 md:p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-3 rounded-xl">
                <Scan className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Deteksi Produk Israel
                </h1>
                <p className="text-gray-600">
                  Sistem deteksi produk terafiliasi Israel menggunakan AI
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="bg-green-100 px-3 py-1 rounded-full">
                <span className="text-green-700 text-sm font-medium">
                  AI Ready
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Camera/Upload Section */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                Deteksi Produk
              </h2>
              <div className="flex space-x-2">
                <button
                  onClick={toggleWebcam}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-xl font-medium transition-colors ${
                    isWebcamActive
                      ? 'bg-red-100 text-red-700 hover:bg-red-200'
                      : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                  }`}
                >
                  <Camera className="h-4 w-4" />
                  <span>{isWebcamActive ? 'Stop Kamera' : 'Buka Kamera'}</span>
                </button>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-100 text-green-700 rounded-xl font-medium hover:bg-green-200 transition-colors"
                >
                  <Upload className="h-4 w-4" />
                  <span>Upload Gambar</span>
                </button>
              </div>
            </div>

            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="image/*"
              className="hidden"
            />

            {/* Camera/Image Display */}
            <div className="bg-gray-50 rounded-xl p-4 min-h-[400px] flex items-center justify-center">
              {isWebcamActive && !capturedImage ? (
                <div className="relative">
                  <Webcam
                    ref={webcamRef}
                    audio={false}
                    screenshotFormat="image/jpeg"
                    className="rounded-xl max-w-full max-h-[400px]"
                    videoConstraints={{
                      width: 640,
                      height: 480,
                      facingMode: "user"
                    }}
                  />
                  <button
                    onClick={capture}
                    disabled={isDetecting}
                    className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-full font-medium transition-colors flex items-center space-x-2"
                  >
                    <Camera className="h-4 w-4" />
                    <span>{isDetecting ? 'Mendeteksi...' : 'Ambil Foto'}</span>
                  </button>
                </div>
              ) : capturedImage ? (
                <div className="relative">
                  <img
                    src={capturedImage}
                    alt="Captured"
                    className="rounded-xl max-w-full max-h-[400px] object-contain"
                  />
                  {isDetecting && (
                    <div className="absolute inset-0 bg-black bg-opacity-50 rounded-xl flex items-center justify-center">
                      <div className="loading-dots">
                        <div></div>
                        <div></div>
                        <div></div>
                        <div></div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center">
                  <div className="bg-gray-200 rounded-full p-4 w-20 h-20 mx-auto mb-4 flex items-center justify-center">
                    <Camera className="h-8 w-8 text-gray-400" />
                  </div>
                  <p className="text-gray-500">
                    Buka kamera atau upload gambar untuk memulai deteksi
                  </p>
                </div>
              )}
            </div>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                  <span className="text-red-700">{error}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        <div className="space-y-6">
          {/* Detection Result */}
          {detectionResult && (
            <DetectionResultCard 
              result={detectionResult} 
              onDownload={handleDownloadResult}
            />
          )}

          {/* System Status */}
          <SystemStatus />

          {/* Detection History */}
          <DetectionHistory 
            history={detectionHistory}
            onSelectResult={handleSelectHistoryResult}
          />
        </div>
      </div>
    </div>
  )
}