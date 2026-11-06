import ToggleButton from '@mui/material/ToggleButton'
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup'
import Typography from '@mui/material/Typography'

// Escala Likert de 1 a 5 usada en las preguntas de confianza (OE3).
// eslint-disable-next-line react-refresh/only-export-components
export const NIVELES_CONFIANZA = ['Nada', 'Poca', 'Regular', 'Bastante', 'Mucha']

interface Props {
  valor: number | ''
  onCambio: (v: number) => void
}

export function EscalaConfianza({ valor, onCambio }: Props) {
  return (
    <ToggleButtonGroup
      exclusive
      fullWidth
      size="small"
      color="primary"
      value={valor}
      onChange={(_, v: number | null) => v != null && onCambio(v)}
    >
      {NIVELES_CONFIANZA.map((etiqueta, i) => (
        <ToggleButton
          key={etiqueta}
          value={i + 1}
          sx={{ flexDirection: 'column', py: 0.75, textTransform: 'none' }}
        >
          <Typography sx={{ fontWeight: 700, lineHeight: 1.2 }}>{i + 1}</Typography>
          <Typography variant="caption" sx={{ lineHeight: 1.2, fontSize: 10.5 }}>
            {etiqueta}
          </Typography>
        </ToggleButton>
      ))}
    </ToggleButtonGroup>
  )
}
