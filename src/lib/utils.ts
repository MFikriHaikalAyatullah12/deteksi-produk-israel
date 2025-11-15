export const formatConfidence = (confidence: number): string => {
  return `${(confidence * 100).toFixed(1)}%`
}

export const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return 'text-red-600'
  if (confidence >= 0.6) return 'text-orange-600' 
  if (confidence >= 0.4) return 'text-yellow-600'
  return 'text-green-600'
}

export const getConfidenceBgColor = (confidence: number): string => {
  if (confidence >= 0.8) return 'bg-red-50 border-red-200'
  if (confidence >= 0.6) return 'bg-orange-50 border-orange-200'
  if (confidence >= 0.4) return 'bg-yellow-50 border-yellow-200'
  return 'bg-green-50 border-green-200'
}

export const getRiskLevelColor = (riskLevel: 'high' | 'medium' | 'low'): string => {
  switch (riskLevel) {
    case 'high':
      return 'bg-red-100 text-red-800 border-red-200'
    case 'medium':
      return 'bg-orange-100 text-orange-800 border-orange-200'
    case 'low':
      return 'bg-green-100 text-green-800 border-green-200'
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200'
  }
}

export const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp)
  return date.toLocaleString('id-ID', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

export const formatFileSize = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 Bytes'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

export const dataURLtoFile = (dataurl: string, filename: string): File => {
  const arr = dataurl.split(',')
  const mime = arr[0].match(/:(.*?);/)![1]
  const bstr = atob(arr[1])
  let n = bstr.length
  const u8arr = new Uint8Array(n)
  
  while(n--){
    u8arr[n] = bstr.charCodeAt(n)
  }
  
  return new File([u8arr], filename, { type: mime })
}

export const downloadResult = (result: any, filename: string = 'detection-result.json') => {
  const dataStr = JSON.stringify(result, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  
  const exportFileDefaultName = filename
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
}