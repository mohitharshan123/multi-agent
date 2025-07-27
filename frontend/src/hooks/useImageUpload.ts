import { useState } from 'react'
import { DropzoneInputProps, DropzoneRootProps, useDropzone } from 'react-dropzone'

interface UseImageUploadReturn {
  uploadedImage: File | null
  setUploadedImage: (file: File | null) => void
  removeImage: () => void
  getRootProps: () => DropzoneRootProps
  getInputProps: () => DropzoneInputProps
  isDragActive: boolean
}

export const useImageUpload = (): UseImageUploadReturn => {
  const [uploadedImage, setUploadedImage] = useState<File | null>(null)

  const handleImageDrop = (acceptedFiles: File[]): void => {
    const file = acceptedFiles[0]
    if (file) {
      setUploadedImage(file)
    }
  }

  const removeImage = (): void => {
    setUploadedImage(null)
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleImageDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024 // 10MB
  })

  return {
    uploadedImage,
    setUploadedImage,
    removeImage,
    getRootProps,
    getInputProps,
    isDragActive
  }
} 