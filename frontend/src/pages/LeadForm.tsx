import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { EnvelopeSimple, Phone, Buildings, User, ChatText } from '@phosphor-icons/react';
import { Button } from '@/components/ui/Button';
import { SectionHeader } from '@/components/ui/SectionHeader';

interface FormState {
  nombre: string;
  email: string;
  empresa: string;
  telefono: string;
  mensaje: string;
}

type Status = 'idle' | 'loading' | 'success' | 'error';

export function LeadForm() {
  const { slug = '' } = useParams<{ slug: string }>();
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

  if (status === 'success') {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-md"
        >
          <div className="text-6xl mb-6">{qualified ? '🎉' : '✅'}</div>
          <h1 className="text-2xl font-bold text-white font-space mb-4">
            {qualified
              ? '¡Gracias por tu interés!'
              : 'Formulario enviado'}
          </h1>
          <p className="text-slate-400 mb-8">
            {qualified
              ? 'Recibimos tu información. Un experto de nuestro equipo se pondrá en contacto contigo muy pronto.'
              : 'Hemos recibido tu mensaje. Te contactaremos pronto.'}
          </p>
          <Button variant="secondary" onClick={() => window.location.reload()}>
            Enviar otro mensaje
          </Button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-6 py-16">
      <div className="w-full max-w-xl">
        <SectionHeader
          title={`Conecta con ${slug.replace(/-/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}`}
          subtitle="Completa el formulario y un experto se pondrá en contacto contigo."
          align="center"
          className="mb-10"
        />

        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          onSubmit={handleSubmit}
          className="space-y-5"
        >
          {/* Nombre */}
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-300">
              Nombre completo *
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
                className="w-full rounded-lg border border-slate-700/80 bg-slate-900/60 pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 transition-colors focus:border-emerald-500/50 focus:outline-none focus:ring-1 focus:ring-emerald-500/30"
                placeholder="Tu nombre"
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-300">
              Email profesional *
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
                className="w-full rounded-lg border border-slate-700/80 bg-slate-900/60 pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 transition-colors focus:border-emerald-500/50 focus:outline-none focus:ring-1 focus:ring-emerald-500/30"
                placeholder="tu@empresa.com"
              />
            </div>
          </div>

          {/* Empresa */}
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-300">
              Empresa *
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
                className="w-full rounded-lg border border-slate-700/80 bg-slate-900/60 pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 transition-colors focus:border-emerald-500/50 focus:outline-none focus:ring-1 focus:ring-emerald-500/30"
                placeholder="Nombre de tu empresa"
              />
            </div>
          </div>

          {/* Teléfono */}
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-300">
              Teléfono <span className="text-slate-600">(opcional)</span>
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
                className="w-full rounded-lg border border-slate-700/80 bg-slate-900/60 pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 transition-colors focus:border-emerald-500/50 focus:outline-none focus:ring-1 focus:ring-emerald-500/30"
                placeholder="+34 600 000 000"
              />
            </div>
          </div>

          {/* Mensaje */}
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-300">
              ¿Cómo podemos ayudarte? *
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
                className="w-full rounded-lg border border-slate-700/80 bg-slate-900/60 pl-10 pr-4 py-3 text-sm text-slate-100 placeholder-slate-500 transition-colors focus:border-emerald-500/50 focus:outline-none focus:ring-1 focus:ring-emerald-500/30 resize-none"
                placeholder="Cuéntanos en qué podemos ayudarte..."
              />
            </div>
          </div>

          {/* Error */}
          {errorMsg && (
            <div className="rounded-lg bg-red-500/10 px-4 py-3 text-sm text-red-400">
              {errorMsg}
            </div>
          )}

          {/* Submit */}
          <Button
            type="submit"
            variant="primary"
            size="lg"
            loading={status === 'loading'}
            disabled={status === 'loading'}
            className="w-full"
          >
            Enviar mensaje
          </Button>

          <p className="text-center text-xs text-slate-600">
            Al enviar aceptas que nos pongamos en contacto contigo.
            Tu información está protegida.
          </p>
        </motion.form>
      </div>
    </div>
  );
}
