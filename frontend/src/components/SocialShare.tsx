import React, { useState } from 'react'
import { 
  Share2, 
  Twitter, 
  Facebook, 
  Linkedin, 
  Link2, 
  Mail,
  Check,
  Copy
} from 'lucide-react'
import { cn } from '../lib/utils'

interface ShareData {
  title: string
  description: string
  url: string
  imageUrl?: string
}

interface SocialShareProps {
  data: ShareData
  className?: string
  showAnalytics?: boolean
}

export function SocialShare({ data, className, showAnalytics = true }: SocialShareProps) {
  const [copied, setCopied] = useState(false)
  const [analytics, setAnalytics] = useState({
    twitter: 0,
    facebook: 0,
    linkedin: 0,
    email: 0,
    copy: 0
  })

  const encodedUrl = encodeURIComponent(data.url)
  const encodedTitle = encodeURIComponent(data.title)
  const encodedDescription = encodeURIComponent(data.description)

  const shareUrls = {
    twitter: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}&via=ttl_archival`,
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
    email: `mailto:?subject=${encodedTitle}&body=${encodedDescription}%0A%0A${data.url}`
  }

  const trackShare = (platform: keyof typeof shareUrls) => {
    if (showAnalytics) {
      setAnalytics(prev => ({ ...prev, [platform]: prev[platform] + 1 }))
      
      // Send analytics event to backend
      fetch('/api/analytics/share', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform, url: data.url, timestamp: new Date().toISOString() })
      }).catch(() => {}) // Silently fail analytics
    }
  }

  const handleShare = (platform: keyof typeof shareUrls) => {
    trackShare(platform)
    window.open(shareUrls[platform], '_blank', 'width=600,height=400,scrollbars=yes,resizable=yes')
  }

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(data.url)
      setCopied(true)
      trackShare('copy')
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea')
      textArea.value = data.url
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      setCopied(true)
      trackShare('copy')
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleNativeShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: data.title,
          text: data.description,
          url: data.url
        })
        trackShare('twitter') // Track as general share
      } catch (err) {
        // User cancelled or error occurred
      }
    } else {
      handleCopyLink()
    }
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Share Header */}
      <div className="flex items-center gap-2">
        <Share2 className="h-5 w-5 text-muted-foreground" />
        <h3 className="font-semibold text-sm">Share this content</h3>
      </div>

      {/* Share Buttons */}
      <div className="flex flex-wrap gap-2">
        {/* Native Share (Mobile) */}
        <button
          onClick={handleNativeShare}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-colors text-sm font-medium"
        >
          <Share2 className="h-4 w-4" />
          Share
        </button>

        {/* Twitter */}
        <button
          onClick={() => handleShare('twitter')}
          className="flex items-center gap-2 px-4 py-2 bg-[#1DA1F2] text-white rounded-xl hover:bg-[#1a8cd8] transition-colors text-sm font-medium"
        >
          <Twitter className="h-4 w-4" />
          Twitter
        </button>

        {/* Facebook */}
        <button
          onClick={() => handleShare('facebook')}
          className="flex items-center gap-2 px-4 py-2 bg-[#1877F2] text-white rounded-xl hover:bg-[#166fe5] transition-colors text-sm font-medium"
        >
          <Facebook className="h-4 w-4" />
          Facebook
        </button>

        {/* LinkedIn */}
        <button
          onClick={() => handleShare('linkedin')}
          className="flex items-center gap-2 px-4 py-2 bg-[#0A66C2] text-white rounded-xl hover:bg-[#0958a6] transition-colors text-sm font-medium"
        >
          <Linkedin className="h-4 w-4" />
          LinkedIn
        </button>

        {/* Email */}
        <button
          onClick={() => handleShare('email')}
          className="flex items-center gap-2 px-4 py-2 bg-accent text-accent-foreground rounded-xl hover:bg-accent/90 transition-colors text-sm font-medium"
        >
          <Mail className="h-4 w-4" />
          Email
        </button>

        {/* Copy Link */}
        <button
          onClick={handleCopyLink}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-xl transition-colors text-sm font-medium',
            copied 
              ? 'bg-emerald-500 text-white' 
              : 'bg-muted hover:bg-muted/80 text-muted-foreground'
          )}
        >
          {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
          {copied ? 'Copied!' : 'Copy Link'}
        </button>
      </div>

      {/* Analytics (if enabled) */}
      {showAnalytics && (
        <div className="mt-4 p-3 bg-accent/30 rounded-xl">
          <p className="text-xs font-medium text-muted-foreground mb-2">Share Analytics</p>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs">
            <div className="text-center">
              <div className="font-bold text-sm">{analytics.twitter}</div>
              <div className="text-muted-foreground">Twitter</div>
            </div>
            <div className="text-center">
              <div className="font-bold text-sm">{analytics.facebook}</div>
              <div className="text-muted-foreground">Facebook</div>
            </div>
            <div className="text-center">
              <div className="font-bold text-sm">{analytics.linkedin}</div>
              <div className="text-muted-foreground">LinkedIn</div>
            </div>
            <div className="text-center">
              <div className="font-bold text-sm">{analytics.email}</div>
              <div className="text-muted-foreground">Email</div>
            </div>
            <div className="text-center">
              <div className="font-bold text-sm">{analytics.copy}</div>
              <div className="text-muted-foreground">Copy</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Hook for managing Open Graph meta tags
export function useOpenGraph(data: ShareData) {
  React.useEffect(() => {
    // Update or create meta tags
    const updateMetaTag = (property: string, content: string) => {
      let tag = document.querySelector(`meta[property="${property}"]`) || 
                document.querySelector(`meta[name="${property}"]`)
      
      if (!tag) {
        tag = document.createElement('meta')
        tag.setAttribute('property', property)
        document.head.appendChild(tag)
      }
      tag.setAttribute('content', content)
    }

    // Set Open Graph tags
    updateMetaTag('og:title', data.title)
    updateMetaTag('og:description', data.description)
    updateMetaTag('og:url', data.url)
    updateMetaTag('og:type', 'website')
    updateMetaTag('og:site_name', 'TTL Archival Service')
    
    if (data.imageUrl) {
      updateMetaTag('og:image', data.imageUrl)
      updateMetaTag('og:image:alt', data.title)
    }

    // Twitter Card tags
    updateMetaTag('twitter:card', 'summary_large_image')
    updateMetaTag('twitter:title', data.title)
    updateMetaTag('twitter:description', data.description)
    updateMetaTag('twitter:url', data.url)
    updateMetaTag('twitter:site', '@ttl_archival')
    
    if (data.imageUrl) {
      updateMetaTag('twitter:image', data.imageUrl)
    }

    // Clean up on unmount
    return () => {
      // Optionally clean up meta tags if needed
    }
  }, [data])
}
