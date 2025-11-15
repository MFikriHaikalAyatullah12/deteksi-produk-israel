export interface DetectionResult {
  is_israeli_product: boolean
  confidence: number
  detected_features: {
    barcode_729: boolean
    made_in_israel_text: boolean
    hebrew_text: boolean
    israeli_brand: boolean
    kosher_certification: boolean
  }
  brand_info?: {
    name: string
    category: string
    risk_level: 'high' | 'medium' | 'low'
  }
  timestamp: string
  processing_time_ms?: number
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface ModelInfo {
  status: string
  model_type?: string
  n_estimators?: number
  max_depth?: number
  feature_count?: number
  feature_names?: string[]
  brands_count?: number
}

export interface BrandDatabase {
  [key: string]: {
    products: string[]
    category: string
    risk_level: 'high' | 'medium' | 'low'
  }
}