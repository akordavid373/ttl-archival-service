import React, { useState, useEffect } from 'react';

interface OptimizedImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  webpSrc?: string;
  lowResSrc?: string;
  alt: string;
  className?: string;
  aspectRatio?: string;
}

const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  webpSrc,
  lowResSrc,
  alt,
  className = '',
  aspectRatio,
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [currentSrc, setCurrentSrc] = useState(lowResSrc || src);

  useEffect(() => {
    const img = new Image();
    img.src = src;
    img.onload = () => {
      setIsLoaded(true);
      setCurrentSrc(src);
    };
  }, [src]);

  const containerStyle: React.CSSProperties = {
    position: 'relative',
    overflow: 'hidden',
    aspectRatio: aspectRatio,
  };

  const imageStyle: React.CSSProperties = {
    filter: isLoaded ? 'none' : 'blur(10px)',
    transition: 'filter 0.5s ease-in-out',
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  };

  return (
    <div style={containerStyle} className={`optimized-image-container ${className}`}>
      <picture>
        {webpSrc && <source srcSet={webpSrc} type="image/webp" />}
        <img
          {...props}
          src={currentSrc}
          alt={alt}
          loading="lazy"
          onLoad={() => setIsLoaded(true)}
          style={imageStyle}
          className={`optimized-image ${isLoaded ? 'loaded' : 'loading'}`}
        />
      </picture>
      {!isLoaded && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" aria-hidden="true" />
      )}
    </div>
  );
};

export default OptimizedImage;
