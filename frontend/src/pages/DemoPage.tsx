/**
 * DemoPage.tsx — Script9 Engine Design System
 *
 * Página de referencia visual. Muestra todos los componentes en contexto.
 * Ruta sugerida: /design-system (solo en desarrollo)
 *
 * Uso:
 *   <Route path="/design-system" element={<DemoPage />} />
 */

import { motion } from 'framer-motion'
import { TechBadge }       from '../components/ui/TechBadge'
import { GlassCard }       from '../components/ui/GlassCard'
import { MetricNumber }    from '../components/ui/MetricNumber'
import { GlowBackground }  from '../components/ui/GlowBackground'
import { GridBackground }  from '../components/ui/GridBackground'
import { SectionHeader }   from '../components/ui/SectionHeader'
import { Button }          from '../components/ui/Button'
import { NeuroSphere }     from '../components/ui/NeuroSphere'
import { AnimatedSection } from '../components/animations/AnimatedSection'
import { StaggerChildren, itemVariants } from '../components/animations/StaggerChildren'
import { CardHover }       from '../components/animations/CardHover'

function Divider({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-4 my-12">
      <div className="h-px flex-1 bg-slate-800" />
      <span className="text-xs font-mono text-slate-500 uppercase tracking-widest">{label}</span>
      <div className="h-px flex-1 bg-slate-800" />
    </div>
  )
}

export default function DemoPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white px-6 py-16 max-w-5xl mx-auto">

      {/* ─── Hero ────────────────────────────────── */}
      <div className="relative mb-24 text-center">
        <GridBackground className="absolute inset-0 -z-10 opacity-50" />
        <GlowBackground color="emerald" />

        <TechBadge className="mb-6">Script9 Design System</TechBadge>
        <h1 className="text-5xl md:text-6xl font-bold font-space tracking-tight text-white mb-4">
          Componentes &{' '}
          <span className="text-gradient-animated">Tokens</span>
        </h1>
        <p className="text-slate-400 font-inter font-light text-lg max-w-xl mx-auto">
          Referencia visual completa. Todos los componentes usan slate-950 + emerald-500.
        </p>
      </div>

      {/* ─── TechBadge ───────────────────────────── */}
      <Divider label="TechBadge" />
      <div className="flex flex-wrap gap-3">
        <TechBadge>Default</TechBadge>
        <TechBadge variant="success">✓ Activo</TechBadge>
        <TechBadge variant="warning">⚠ Advertencia</TechBadge>
        <TechBadge variant="error">✕ Error 500</TechBadge>
        <TechBadge>FastAPI</TechBadge>
        <TechBadge>PostgreSQL</TechBadge>
        <TechBadge>Redis</TechBadge>
      </div>

      {/* ─── Button ──────────────────────────────── */}
      <Divider label="Button" />
      <div className="flex flex-wrap gap-4 mb-6">
        <Button variant="primary">Crear agente</Button>
        <Button variant="secondary">Ver detalles</Button>
        <Button variant="ghost">Cancelar</Button>
        <Button variant="danger">Eliminar</Button>
      </div>
      <div className="flex flex-wrap gap-4 mb-6">
        <Button variant="primary" size="sm">Small</Button>
        <Button variant="primary" size="md">Medium</Button>
        <Button variant="primary" size="lg">Large</Button>
      </div>
      <div className="flex flex-wrap gap-4">
        <Button variant="primary" loading>Guardando…</Button>
        <Button variant="primary" disabled>Deshabilitado</Button>
      </div>

      {/* ─── MetricNumber ────────────────────────── */}
      <Divider label="MetricNumber" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
        <MetricNumber value="98.7%" label="Uptime" trend="up" />
        <MetricNumber value="1,240" label="Ejecuciones hoy" trend="down" />
        <MetricNumber value="0.3s"  label="Latencia media" trend="neutral" />
        <MetricNumber value="12"    label="Agentes activos" />
      </div>

      {/* ─── GlassCard ───────────────────────────── */}
      <Divider label="GlassCard" />
      <div className="grid md:grid-cols-3 gap-6">
        <GlassCard>
          <TechBadge className="mb-3">Sin hover</TechBadge>
          <p className="text-slate-400 text-sm font-inter">
            GlassCard base — surface oscura con borde slate-800.
          </p>
        </GlassCard>
        <GlassCard hover>
          <TechBadge variant="success" className="mb-3">Con hover</TechBadge>
          <p className="text-slate-400 text-sm font-inter">
            Hover activa glow emerald y eleva la card.
          </p>
        </GlassCard>
        <GlassCard hover compact>
          <TechBadge variant="warning" className="mb-3">Compact</TechBadge>
          <p className="text-slate-400 text-sm font-inter">
            Variante compact para listas densas.
          </p>
        </GlassCard>
      </div>

      {/* ─── SectionHeader ───────────────────────── */}
      <Divider label="SectionHeader" />
      <div className="space-y-12">
        <SectionHeader
          eyebrow="Automatización"
          title="Orquesta tus agentes de IA"
          subtitle="Script9 Engine gestiona el ciclo completo de ejecución: activación, contexto, reintentos y observabilidad."
        />
        <SectionHeader
          eyebrow="Plataforma"
          title="Multi-tenant. Asíncrono. Escalable."
          subtitle="Diseñado para equipos que necesitan fiabilidad en producción desde el primer día."
          align="center"
        />
      </div>

      {/* ─── GridBackground + GlowBackground ─────── */}
      <Divider label="GridBackground + GlowBackground" />
      <div className="relative h-64 rounded-2xl overflow-hidden border border-slate-800">
        <GridBackground className="absolute inset-0" />
        <GlowBackground color="emerald" />
        <GlowBackground color="blue" className="translate-x-1/3" />
        <div className="relative z-10 flex items-center justify-center h-full">
          <p className="font-space font-semibold text-xl text-white">
            Grid + Glow combinados
          </p>
        </div>
      </div>

      {/* ─── NeuroSphere ─────────────────────────── */}
      <Divider label="NeuroSphere" />
      <div className="flex justify-center">
        <NeuroSphere particleCount={160} color="#10b981" width={400} height={400} />
      </div>

      {/* ─── AnimatedSection ─────────────────────── */}
      <Divider label="AnimatedSection (scroll down)" />
      <AnimatedSection>
        <GlassCard>
          <p className="text-slate-300 font-inter">
            Este bloque se reveló con <span className="text-emerald-400 font-mono">AnimatedSection</span> — fade + slide desde abajo al entrar en el viewport.
          </p>
        </GlassCard>
      </AnimatedSection>

      <AnimatedSection delay={0.15} className="mt-4">
        <GlassCard>
          <p className="text-slate-300 font-inter">
            Una segunda <span className="text-emerald-400 font-mono">AnimatedSection</span> con delay de 150ms.
          </p>
        </GlassCard>
      </AnimatedSection>

      {/* ─── StaggerChildren ─────────────────────── */}
      <Divider label="StaggerChildren" />
      <StaggerChildren className="grid md:grid-cols-4 gap-4" stagger={0.08}>
        {['Python', 'FastAPI', 'Redis', 'PostgreSQL'].map((tech) => (
          <motion.div key={tech} variants={itemVariants}>
            <GlassCard hover compact className="text-center">
              <TechBadge>{tech}</TechBadge>
            </GlassCard>
          </motion.div>
        ))}
      </StaggerChildren>

      {/* ─── CardHover ───────────────────────────── */}
      <Divider label="CardHover" />
      <div className="grid md:grid-cols-3 gap-6">
        {['Agentes', 'Scripts', 'Pipelines'].map((item) => (
          <CardHover key={item}>
            <GlassCard>
              <MetricNumber value={Math.floor(Math.random() * 99 + 1)} label={item} />
            </GlassCard>
          </CardHover>
        ))}
      </div>

      {/* ─── Color tokens ────────────────────────── */}
      <Divider label="Color Tokens" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { name: 'bg (#020617)',      cls: 'bg-slate-950 border border-slate-800' },
          { name: 'surface (#0f172a)', cls: 'bg-slate-900 border border-slate-800' },
          { name: 'border (#1e293b)',  cls: 'bg-slate-800' },
          { name: 'accent (#10b981)', cls: 'bg-emerald-500' },
          { name: 'accent-400',       cls: 'bg-emerald-400' },
          { name: 'text-secondary',   cls: 'bg-slate-400' },
          { name: 'text-tertiary',    cls: 'bg-slate-500' },
          { name: 'danger (#ef4444)', cls: 'bg-red-500' },
        ].map(({ name, cls }) => (
          <div key={name} className="flex flex-col gap-2">
            <div className={`h-12 rounded-xl ${cls}`} />
            <span className="text-xs font-mono text-slate-400">{name}</span>
          </div>
        ))}
      </div>

      {/* ─── Typography ──────────────────────────── */}
      <Divider label="Tipografía" />
      <div className="space-y-4">
        <p className="font-space font-bold text-5xl text-white">Space Grotesk — Bold 700</p>
        <p className="font-space font-semibold text-3xl text-white">Space Grotesk — SemiBold 600</p>
        <p className="font-inter font-light text-lg text-slate-400">Inter — Light 300 — cuerpo de texto principal, subtítulos y descripciones</p>
        <p className="font-inter text-base text-slate-300">Inter — Regular 400 — párrafos normales</p>
        <p className="font-inter font-medium text-sm text-slate-300">Inter — Medium 500 — labels de UI</p>
        <p className="font-mono text-sm text-emerald-400">JetBrains Mono — badges técnicos, métricas, código</p>
      </div>

      <div className="h-24" />
    </div>
  )
}
