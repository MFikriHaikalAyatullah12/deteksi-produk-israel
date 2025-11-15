import { DetectionResult, ApiResponse, ModelInfo, BrandDatabase } from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class DetectionApi {
  private static async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    try {
      if (!response.ok) {
        const errorData = await response.json()
        return {
          success: false,
          error: errorData.detail || `HTTP ${response.status}: ${response.statusText}`
        }
      }
      
      const data = await response.json()
      return {
        success: true,
        data
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      }
    }
  }

  static async analyzeImage(imageFile: File): Promise<ApiResponse<DetectionResult>> {
    try {
      const formData = new FormData()
      formData.append('image', imageFile)

      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        body: formData,
      })

      return this.handleResponse<DetectionResult>(response)
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error'
      }
    }
  }

  static async analyzeImageFromBlob(imageBlob: Blob): Promise<ApiResponse<DetectionResult>> {
    try {
      const formData = new FormData()
      formData.append('image', imageBlob, 'capture.jpg')

      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        body: formData,
      })

      return this.handleResponse<DetectionResult>(response)
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error'
      }
    }
  }

  static async analyzeBatch(imageFiles: File[]): Promise<ApiResponse<{ results: DetectionResult[] }>> {
    try {
      const formData = new FormData()
      imageFiles.forEach((file, index) => {
        formData.append('images', file)
      })

      const response = await fetch(`${API_BASE_URL}/analyze/batch`, {
        method: 'POST',
        body: formData,
      })

      return this.handleResponse<{ results: DetectionResult[] }>(response)
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error'
      }
    }
  }

  static async getModelInfo(): Promise<ApiResponse<ModelInfo>> {
    try {
      const response = await fetch(`${API_BASE_URL}/model/info`)
      return this.handleResponse<ModelInfo>(response)
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error'
      }
    }
  }

  static async getBrandsDatabase(): Promise<ApiResponse<BrandDatabase>> {
    try {
      const response = await fetch(`${API_BASE_URL}/brands/database`)
      return this.handleResponse<BrandDatabase>(response)
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error'
      }
    }
  }

  static async healthCheck(): Promise<ApiResponse<{ status: string; model_ready: boolean }>> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      return this.handleResponse<{ status: string; model_ready: boolean }>(response)
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error'
      }
    }
  }
}

export const detectionApi = DetectionApi