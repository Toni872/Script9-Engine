import { useEffect, useRef } from 'react'

interface NeuroSphereProps {
  /** Number of particles on the sphere surface */
  particleCount?: number
  /** CSS color string for particles and connections */
  color?: string
  /** Scale multiplier relative to the canvas size */
  scale?: number
  className?: string
  width?: number
  height?: number
}

interface Particle {
  x: number
  y: number
  z: number
  origX: number
  origY: number
  origZ: number
  size: number
  opacity: number
}

/**
 * NeuroSphere — animated 3D particle sphere, canvas-based.
 * Uses Fibonacci sphere distribution for uniform coverage.
 * Reacts to mouse/pointer movement for a living, organic feel.
 *
 * @example
 * <NeuroSphere particleCount={180} color="#10b981" />
 */
export function NeuroSphere({
  particleCount = 160,
  color = '#10b981',
  scale = 1,
  className = '',
  width = 500,
  height = 500,
}: NeuroSphereProps) {
  const canvasRef  = useRef<HTMLCanvasElement>(null)
  const mouseRef   = useRef({ x: 0, y: 0 })
  const frameRef   = useRef<number>(0)
  const rotRef     = useRef({ x: 0.003, y: 0.006 })

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Handle HiDPI
    const dpr = window.devicePixelRatio || 1
    canvas.width  = width  * dpr
    canvas.height = height * dpr
    canvas.style.width  = `${width}px`
    canvas.style.height = `${height}px`
    ctx.scale(dpr, dpr)

    const cx = width  / 2
    const cy = height / 2
    const radius = (Math.min(width, height) / 2.5) * scale

    // Fibonacci sphere distribution
    const particles: Particle[] = []
    const phi = Math.PI * (3 - Math.sqrt(5))
    for (let i = 0; i < particleCount; i++) {
      const y3d  = 1 - (i / (particleCount - 1)) * 2
      const r    = Math.sqrt(1 - y3d * y3d)
      const theta = phi * i
      const x3d  = Math.cos(theta) * r
      const z3d  = Math.sin(theta) * r
      particles.push({
        x: x3d * radius,
        y: y3d * radius,
        z: z3d * radius,
        origX: x3d * radius,
        origY: y3d * radius,
        origZ: z3d * radius,
        size: Math.random() * 1.5 + 0.8,
        opacity: Math.random() * 0.5 + 0.4,
      })
    }

    let rotX = 0
    let rotY = 0

    const project = (x: number, y: number, z: number) => {
      const fov = 400
      const scale3d = fov / (fov + z)
      return {
        sx: cx + x * scale3d,
        sy: cy + y * scale3d,
        sz: z,
        scale3d,
      }
    }

    const rotateY = (x: number, z: number, angle: number) => {
      return {
        x: x * Math.cos(angle) - z * Math.sin(angle),
        z: x * Math.sin(angle) + z * Math.cos(angle),
      }
    }

    const rotateX = (y: number, z: number, angle: number) => {
      return {
        y: y * Math.cos(angle) - z * Math.sin(angle),
        z: y * Math.sin(angle) + z * Math.cos(angle),
      }
    }

    const hexToRgb = (hex: string) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
      return result
        ? {
            r: parseInt(result[1] ?? '00', 16),
            g: parseInt(result[2] ?? '00', 16),
            b: parseInt(result[3] ?? '00', 16),
          }
        : { r: 16, g: 185, b: 129 }
    }

    const rgb = hexToRgb(color)
    const CONNECTION_DIST = radius * 0.55

    const draw = () => {
      ctx!.clearRect(0, 0, width, height)

      // Slowly drift rotation; mouse nudges it
      const targetRX = -mouseRef.current.y * 0.0008
      const targetRY =  mouseRef.current.x * 0.0008
      rotRef.current.x += (targetRX - rotRef.current.x) * 0.05
      rotRef.current.y += (targetRY - rotRef.current.y) * 0.05

      rotX += rotRef.current.x
      rotY += rotRef.current.y

      // Apply rotation to each particle
      const rotated = particles.map((p) => {
        const ry = rotateY(p.origX, p.origZ, rotY)
        const rx = rotateX(p.origY, ry.z, rotX)
        return { ...p, x: ry.x, y: rx.y, z: rx.z }
      })

      // Sort back-to-front
      const sorted = [...rotated].sort((a, b) => a.z - b.z)

      // Draw connections
      for (let i = 0; i < sorted.length; i++) {
        const pi = sorted[i]!
        const projI = project(pi.x, pi.y, pi.z)
        for (let j = i + 1; j < sorted.length; j++) {
          const pj = sorted[j]!
          const projJ = project(pj.x, pj.y, pj.z)
          const dx = pi.x - pj.x
          const dy = pi.y - pj.y
          const dz = pi.z - pj.z
          const dist = Math.sqrt(dx * dx + dy * dy + dz * dz)
          if (dist < CONNECTION_DIST) {
            const alpha = (1 - dist / CONNECTION_DIST) * 0.2
            ctx!.beginPath()
            ctx!.strokeStyle = `rgba(${rgb.r},${rgb.g},${rgb.b},${alpha})`
            ctx!.lineWidth = 0.5
            ctx!.moveTo(projI.sx, projI.sy)
            ctx!.lineTo(projJ.sx, projJ.sy)
            ctx!.stroke()
          }
        }
      }

      // Draw particles
      sorted.forEach((p) => {
        const { sx, sy, scale3d } = project(p.x, p.y, p.z)
        const depth = (p.z + radius) / (radius * 2) // 0..1
        const alpha = p.opacity * (0.3 + depth * 0.7)
        const size  = p.size * scale3d * 0.6

        // Soft glow
        const gradient = ctx!.createRadialGradient(sx, sy, 0, sx, sy, size * 3)
        gradient.addColorStop(0, `rgba(${rgb.r},${rgb.g},${rgb.b},${alpha})`)
        gradient.addColorStop(1, `rgba(${rgb.r},${rgb.g},${rgb.b},0)`)
        ctx!.beginPath()
        ctx!.fillStyle = gradient
        ctx!.arc(sx, sy, size * 3, 0, Math.PI * 2)
        ctx!.fill()

        // Core dot
        ctx!.beginPath()
        ctx!.fillStyle = `rgba(${rgb.r},${rgb.g},${rgb.b},${Math.min(alpha * 1.5, 1)})`
        ctx!.arc(sx, sy, size, 0, Math.PI * 2)
        ctx!.fill()
      })

      frameRef.current = requestAnimationFrame(draw)
    }

    // Mouse tracking (relative to canvas centre)
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect()
      mouseRef.current = {
        x: e.clientX - rect.left - cx,
        y: e.clientY - rect.top  - cy,
      }
    }
    window.addEventListener('mousemove', handleMouseMove)

    frameRef.current = requestAnimationFrame(draw)

    return () => {
      cancelAnimationFrame(frameRef.current)
      window.removeEventListener('mousemove', handleMouseMove)
    }
  }, [particleCount, color, scale, width, height])

  return (
    <canvas
      ref={canvasRef}
      className={className}
      aria-hidden
    />
  )
}
