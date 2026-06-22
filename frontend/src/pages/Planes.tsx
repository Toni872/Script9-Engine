import { GridBackground } from '@/components/ui/GridBackground';
import { GlowBackground } from '@/components/ui/GlowBackground';
import { GlassCard } from '@/components/ui/GlassCard';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Button } from '@/components/ui/Button';
import { Presentation, ArrowRight } from '@phosphor-icons/react';

export function Planes() {
  return (
    <div className="relative min-h-screen bg-slate-950">
      <GridBackground className="absolute inset-0 -z-10 opacity-50" />
      <GlowBackground color="emerald" className="absolute -top-20 left-1/2 -translate-x-1/2" />

      <div className="relative z-10 max-w-4xl mx-auto px-6 py-24">
        <SectionHeader
          title="Potencia tu agencia con IA"
          subtitle="Script9 Engine es la plataforma de agentes IA para equipos comerciales que quieren escalar sin límites."
          align="center"
          className="mb-16"
        />

        <div className="grid md:grid-cols-2 gap-6">
          <GlassCard hover className="p-8 flex flex-col items-center text-center gap-6">
            <Presentation size={48} className="text-emerald-400" />
            <h3 className="text-2xl font-bold font-space text-white">Solicitar demo personalizada</h3>
            <p className="text-slate-400 font-inter">
              Ve cómo Script9 Engine se adapta a los flujos de tu agencia. Sin compromiso.
            </p>
            <Button
              variant="primary"
              size="lg"
              onClick={() => window.location.href = '/aceptar-invitacion'}
            >
              Agendar demo
            </Button>
          </GlassCard>

          <GlassCard hover className="p-8 flex flex-col items-center text-center gap-6">
            <ArrowRight size={48} className="text-emerald-400" />
            <h3 className="text-2xl font-bold font-space text-white">Ya tengo invitación</h3>
            <p className="text-slate-400 font-inter">
              Si tu equipo ya recibió un enlace de acceso, activá tu cuenta aquí.
            </p>
            <Button
              variant="secondary"
              size="lg"
              onClick={() => window.location.href = '/aceptar-invitacion'}
            >
              Activar cuenta
            </Button>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
