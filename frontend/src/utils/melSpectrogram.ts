// Conversión de audio -> espectrograma de Mel (log-mel) en el navegador.
//
// IMPORTANTE: estos parámetros DEBEN coincidir con los que se usen al entrenar
// el modelo CNN (en Python/librosa). Si cambian allá, cambian aquí. Este
// espectrograma es la ENTRADA del CNN y también la imagen que se guardará en BD.
export const MEL_CONFIG = {
  sampleRate: 22050, // Hz de trabajo (se remuestrea el audio a esto)
  nFft: 1024, // tamaño de ventana FFT (potencia de 2)
  hopLength: 512, // salto entre ventanas
  nMels: 128, // número de bandas Mel (alto de la imagen)
  fMin: 0,
  fMax: 11025, // sampleRate / 2
  topDb: 80, // rango dinámico para normalizar el log-mel
} as const

export interface EspectrogramaMel {
  dataUrl: string // PNG del espectrograma (lo que se muestra y se guardaría en BD)
  width: number // número de frames temporales
  height: number // número de bandas Mel
  duracionSeg: number
  matriz: Float32Array // log-mel normalizado [0..1], tamaño width*height (entrada al CNN)
}

// --- Decodificación y remuestreo del audio a mono @ sampleRate objetivo ---
export async function decodificarAudio(blob: Blob): Promise<AudioBuffer> {
  const arrayBuffer = await blob.arrayBuffer()
  const ctx = new AudioContext()
  try {
    return await ctx.decodeAudioData(arrayBuffer)
  } finally {
    void ctx.close()
  }
}

async function remuestrearMono(buffer: AudioBuffer, sr: number): Promise<Float32Array> {
  const largo = Math.ceil(buffer.duration * sr)
  const offline = new OfflineAudioContext(1, largo, sr)
  const fuente = offline.createBufferSource()
  fuente.buffer = buffer
  fuente.connect(offline.destination)
  fuente.start()
  const rendered = await offline.startRendering()
  return rendered.getChannelData(0)
}

// --- FFT iterativa (Cooley-Tukey radix-2), in-place sobre re[] e im[] ---
function fft(re: Float32Array, im: Float32Array): void {
  const n = re.length
  for (let i = 1, j = 0; i < n; i++) {
    let bit = n >> 1
    for (; j & bit; bit >>= 1) j ^= bit
    j ^= bit
    if (i < j) {
      ;[re[i], re[j]] = [re[j], re[i]]
      ;[im[i], im[j]] = [im[j], im[i]]
    }
  }
  for (let largo = 2; largo <= n; largo <<= 1) {
    const ang = (-2 * Math.PI) / largo
    const wRe = Math.cos(ang)
    const wIm = Math.sin(ang)
    for (let i = 0; i < n; i += largo) {
      let curRe = 1
      let curIm = 0
      for (let k = 0; k < largo / 2; k++) {
        const a = i + k
        const b = i + k + largo / 2
        const tRe = curRe * re[b] - curIm * im[b]
        const tIm = curRe * im[b] + curIm * re[b]
        re[b] = re[a] - tRe
        im[b] = im[a] - tIm
        re[a] += tRe
        im[a] += tIm
        const nxtRe = curRe * wRe - curIm * wIm
        curIm = curRe * wIm + curIm * wRe
        curRe = nxtRe
      }
    }
  }
}

// --- Banco de filtros Mel triangulares (fórmula HTK) ---
function hzAMel(hz: number): number {
  return 2595 * Math.log10(1 + hz / 700)
}
function melAHz(mel: number): number {
  return 700 * (10 ** (mel / 2595) - 1)
}

function bancoMel(): Float32Array[] {
  const { nMels, nFft, sampleRate, fMin, fMax } = MEL_CONFIG
  const nBins = nFft / 2 + 1
  const melMin = hzAMel(fMin)
  const melMax = hzAMel(fMax)
  const puntosMel = new Array(nMels + 2)
  for (let i = 0; i < nMels + 2; i++) {
    puntosMel[i] = melMin + ((melMax - melMin) * i) / (nMels + 1)
  }
  const binPorPunto = puntosMel.map((m) =>
    Math.floor(((nFft + 1) * melAHz(m)) / sampleRate),
  )
  const filtros: Float32Array[] = []
  for (let m = 1; m <= nMels; m++) {
    const filtro = new Float32Array(nBins)
    const izq = binPorPunto[m - 1]
    const cen = binPorPunto[m]
    const der = binPorPunto[m + 1]
    for (let k = izq; k < cen; k++) {
      if (cen !== izq) filtro[k] = (k - izq) / (cen - izq)
    }
    for (let k = cen; k < der; k++) {
      if (der !== cen) filtro[k] = (der - k) / (der - cen)
    }
    filtros.push(filtro)
  }
  return filtros
}

// --- Colormap tipo "magma" para pintar el espectrograma ---
const MAGMA: [number, number, number][] = [
  [0, 0, 4],
  [60, 15, 110],
  [140, 40, 120],
  [230, 90, 60],
  [250, 235, 160],
]
function color(v: number): [number, number, number] {
  const x = Math.max(0, Math.min(1, v)) * (MAGMA.length - 1)
  const i = Math.floor(x)
  const f = x - i
  const a = MAGMA[i]
  const b = MAGMA[Math.min(i + 1, MAGMA.length - 1)]
  return [
    Math.round(a[0] + (b[0] - a[0]) * f),
    Math.round(a[1] + (b[1] - a[1]) * f),
    Math.round(a[2] + (b[2] - a[2]) * f),
  ]
}

export async function generarEspectrogramaMel(
  blob: Blob,
): Promise<EspectrogramaMel> {
  const { nFft, hopLength, nMels, sampleRate, topDb } = MEL_CONFIG
  const buffer = await decodificarAudio(blob)
  const senal = await remuestrearMono(buffer, sampleRate)

  const frames = Math.max(1, 1 + Math.floor((senal.length - nFft) / hopLength))
  const filtros = bancoMel()
  const nBins = nFft / 2 + 1

  // Ventana de Hann precalculada.
  const ventana = new Float32Array(nFft)
  for (let i = 0; i < nFft; i++) {
    ventana[i] = 0.5 - 0.5 * Math.cos((2 * Math.PI * i) / (nFft - 1))
  }

  const logMel = new Float32Array(frames * nMels)
  let maxDb = -Infinity

  const re = new Float32Array(nFft)
  const im = new Float32Array(nFft)
  const potencia = new Float32Array(nBins)

  for (let t = 0; t < frames; t++) {
    const off = t * hopLength
    for (let i = 0; i < nFft; i++) {
      const s = off + i < senal.length ? senal[off + i] : 0
      re[i] = s * ventana[i]
      im[i] = 0
    }
    fft(re, im)
    for (let k = 0; k < nBins; k++) {
      potencia[k] = re[k] * re[k] + im[k] * im[k]
    }
    for (let m = 0; m < nMels; m++) {
      const filtro = filtros[m]
      let acc = 0
      for (let k = 0; k < nBins; k++) acc += filtro[k] * potencia[k]
      const db = 10 * Math.log10(Math.max(acc, 1e-10))
      logMel[t * nMels + m] = db
      if (db > maxDb) maxDb = db
    }
  }

  // Normalizar a [0..1] recortando a topDb por debajo del máximo.
  const matriz = new Float32Array(frames * nMels)
  for (let i = 0; i < logMel.length; i++) {
    const v = (logMel[i] - maxDb + topDb) / topDb
    matriz[i] = Math.max(0, Math.min(1, v))
  }

  // Pintar a un canvas (frecuencia grave abajo) y exportar como PNG.
  const off = document.createElement('canvas')
  off.width = frames
  off.height = nMels
  const octx = off.getContext('2d')!
  const img = octx.createImageData(frames, nMels)
  for (let t = 0; t < frames; t++) {
    for (let m = 0; m < nMels; m++) {
      const [r, g, b] = color(matriz[t * nMels + m])
      const y = nMels - 1 - m // invertir: graves abajo
      const idx = (y * frames + t) * 4
      img.data[idx] = r
      img.data[idx + 1] = g
      img.data[idx + 2] = b
      img.data[idx + 3] = 255
    }
  }
  octx.putImageData(img, 0, 0)

  return {
    dataUrl: off.toDataURL('image/png'),
    width: frames,
    height: nMels,
    duracionSeg: buffer.duration,
    matriz,
  }
}
