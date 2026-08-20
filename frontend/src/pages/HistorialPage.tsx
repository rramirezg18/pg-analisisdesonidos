import HistoryIcon from '@mui/icons-material/History'
import Box from '@mui/material/Box'
import Card from '@mui/material/Card'
import Typography from '@mui/material/Typography'

export function HistorialPage() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Historial
      </Typography>

      <Card
        variant="outlined"
        sx={{
          p: 5,
          textAlign: 'center',
          bgcolor: 'background.paper',
        }}
      >
        <HistoryIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
        <Typography variant="body1" sx={{ fontWeight: 600 }}>
          Sin diagnósticos todavía
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Tus análisis aparecerán aquí ordenados por fecha.
        </Typography>
      </Card>
    </Box>
  )
}
