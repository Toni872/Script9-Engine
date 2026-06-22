import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  EnvelopeSimple,
  Phone,
  Buildings,
  User,
  ChatText,
  ArrowRight,
} from '@phosphor-icons/react';
import { Button } from '@/components/ui/Button';
import { GlassCard } from '@/components/ui/GlassCard';
import { GridBackground } from '@/components/ui/GridBackground';
import { NeuroSphere } from '@/components/ui/NeuroSphere';
import { GlowBackground } from '@/components/ui/GlowBackground';
import { AnimatedSection } from '@/components/animations/AnimatedSection';
import { StaggerChildren } from '@/components/animations/StaggerChildren';

interface FormState {
  nombre: string;
  email: string;
  empresa: string;
  telefono: string;
  mensaje: string;
}

type Status = 'idle' | 'loading' | 'success' | 'error';

function formatSlug(slug: string): string {
  return slug
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (l) => l.toUpperCase());
}

export function LeadForm() {
  const { slug = '' } = useParams<{ slug: string }>();
  const ownerName = formatSlug(slug);
  const [form, setForm] = useState<FormState>({
    nombre: '',
    email: '',
    empresa: '',
    telefono: '',
    mensaje: '',
  });
  const [status, setStatus] = useState<Status>('idle');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [qualified, setQualified] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');
    setErrorMsg(null);

    try {
      const res = await fetch('/api/v1/public/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, slug }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? 'Error al enviar el formulario');
      }

      const data = await res.json();
      setQualified(data.qualified ?? false);
      setStatus('success');
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Error desconocido');
      setStatus('error');
    }
  };

  // ── Success state ──────────────────────────────────────────────────────────
  if (status === 'success') {
    return (
      <div className="relative min-h-screen bg-slate-950 overflow-hidden">
        <GridBackground />
        <GlowBackground />

        <div className="relative z-10 min-h-screen flex items-center justify-center px-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
            className="w-full max-w-md"
          >
            <GlassCard className="text-center">
              {/* Animated check */}
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
                className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center mx-auto mb-6"
              >
                {qualified ? (
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.25 }}
                    className="text-3xl"
                  >
                    🎉
                  </motion.span>
                ) : (
                  <motion.svg
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ delay: 0.2, duration: 0.4 }}
                    width="28"
                    height="28"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#34d399"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polyline points="20 6 9 17 4 12" />
                  </motion.svg>
                )}
              </motion.div>

              <motion.h2
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-2xl font-bold text-white font-space mb-3"
              >
                {qualified ? '¡Gracias por tu interés!' : 'Formulario enviado'}
              </motion.h2>

              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-slate-400 text-sm leading-relaxed mb-8"
              >
                {qualified
                  ? 'Recibimos tu información. Un experto de nuestro equipo se pondrá en contacto contigo muy pronto.'
                  : 'Hemos recibido tu mensaje. Te contactaremos pronto.'}
              </motion.p>

              {qualified && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                  className="mb-6 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20"
                >
                  <p className="text-emerald-400 text-xs font-medium">
                    Priority lead — tu solicitud fue marcada como prioritaria
                  </p>
                </motion.div>
              )}

              <Button
                variant="secondary"
                size="sm"
                onClick={() => window.location.reload()}
              >
                Enviar otro mensaje
              </Button>
            </GlassCard>
          </motion.div>
        </div>
      </div>
    );
  }

  // ── Form state ──────────────────────────────────────────────────────────────
  return (
    <div className="relative min-h-screen bg-slate-950 overflow-hidden">
      {/* Background layers */}
      <GridBackground />
      <GlowBackground />

      {/* NeuroSphere ambient */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <NeuroSphere />
      </div>

      {/* Header */}
      <div className="relative z-10 pt-16 pb-8 px-6">
        <AnimatedSection>
          <div className="text-center mb-2">
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-400/80 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-3 py-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Formulario de contacto
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-white font-space mb-3">
            Conecta con{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
              {ownerName}
            </span>
          </h1>
          <p className="text-slate-400 text-sm max-w-md mx-auto">
            Completa el formulario y un experto se pondrá en contacto contigo en menos de 24 horas.
          </p>
        </AnimatedSection>
      </div>

      {/* Form */}
      <div className="relative z-10 px-6 pb-20">
        <StaggerChildren initialDelay={0.1} className="max-w-xl mx-auto">
          <GlassCard className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Nombre */}
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-300">
                  Nombre completo <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <User
                    size={16}
                    className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
                  />
                  <input
                    type="text"
                    name="nombre"
                    value={form.nombre}
                    onChange={handleChange}
                    required
                    placeholder="Tu nombre completo"
                    className="w-full rounded-lg border border-slate-700/60 bg-slate-900/50 backdrop-blur pl-10 pr-4 py-3 text-sm text-slate-100 placeholder-slate-600 transition-all focus:border-emerald-500/50 focus:bg-slate-900/70 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                  />
                </div>
              </div>

              {/* Email */}
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-300">
                  Email profesional <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <EnvelopeSimple
                    size={16}
                    className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
                  />
                  <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    required
                    placeholder="tu@empresa.com"
                    className="w-full rounded-lg border border-slate-700/60 bg-slate-900/50 backdrop-blur pl-10 pr-4 py-3 text-sm text-slate-100 placeholder-slate-600 transition-all focus:border-emerald-500/50 focus:bg-slate-900/70 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                  />
                </div>
              </div>

              {/* Empresa */}
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-300">
                  Empresa <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <Buildings
                    size={16}
                    className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
                  />
                  <input
                    type="text"
                    name="empresa"
                    value={form.empresa}
                    onChange={handleChange}
                    required
                    placeholder="Nombre de tu empresa"
                    className="w-full rounded-lg border border-slate-700/60 bg-slate-900/50 backdrop-blur pl-10 pr-4 py-3 text-sm text-slate-100 placeholder-slate-600 transition-all focus:border-emerald-500/50 focus:bg-slate-900/70 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                  />
                </div>
              </div>

              {/* Teléfono */}
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-300">
                  Teléfono{' '}
                  <span className="text-slate-600 font-normal">(opcional)</span>
                </label>
                <div className="relative">
                  <Phone
                    size={16}
                    className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
                  />
                  <input
                    type="tel"
                    name="telefono"
                    value={form.telefono}
                    onChange={handleChange}
                    placeholder="+34 600 000 000"
                    className="w-full rounded-lg border border-slate-700/60 bg-slate-900/50 backdrop-blur pl-10 pr-4 py-3 text-sm text-slate-100 placeholder-slate-600 transition-all focus:border-emerald-500/50 focus:bg-slate-900/70 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                  />
                </div>
              </div>

              {/* Mensaje */}
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-slate-300">
                  ¿Cómo podemos ayudarte? <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <ChatText
                    size={16}
                    className="absolute left-4 top-4 text-slate-500"
                  />
                  <textarea
                    name="mensaje"
                    value={form.mensaje}
                    onChange={handleChange}
                    required
                    rows={4}
                    placeholder="Cuéntanos qué necesitas, qué herramientas usas hoy, cuántos comerciales tienes..."
                    className="w-full rounded-lg border border-slate-700/60 bg-slate-900/50 backdrop-blur pl-10 pr-4 py-3 text-sm text-slate-100 placeholder-slate-600 transition-all focus:border-emerald-500/50 focus:bg-slate-900/70 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 resize-none"
                  />
                </div>
              </div>

              {/* Error */}
              {errorMsg && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="rounded-lg bg-red-500/10 border border-red-500/20 px-4 py-3"
                >
                  <p className="text-red-400 text-sm">{errorMsg}</p>
                </motion.div>
              )}

              {/* Submit */}
              <Button
                type="submit"
                variant="primary"
                size="lg"
                loading={status === 'loading'}
                disabled={status === 'loading'}
                className="w-full group"
              >
                {status === 'loading' ? (
                  'Enviando...'
                ) : (
                  <>
                    Enviar mensaje
                    <ArrowRight
                      size={16}
                      className="ml-2 transition-transform group-hover:translate-x-1"
                    />
                  </>
                )}
              </Button>

              <p className="text-center text-xs text-slate-600">
                Al enviar aceptas que nos pongamos en contacto contigo.
                Tu información está protegida y nunca se comparte.
              </p>
            </form>
          </GlassCard>
        </StaggerChildren>
      </div>
    </div>
  );
}
