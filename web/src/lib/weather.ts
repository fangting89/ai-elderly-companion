import { useQuery } from '@tanstack/react-query'

// Fixed Singapore coordinate -- this app has no real elder-location concept,
// and every seeded detail (Bukit Merah, Chinatown) already assumes Singapore.
const LATITUDE = 1.29
const LONGITUDE = 103.85

export type WeatherScene = 'clear' | 'cloudy' | 'rain' | 'storm'

export type WeatherNow = {
  tempC: number
  isDay: boolean
  scene: WeatherScene
  description: string
}

// WMO weather codes -> a small scene + plain-language description.
// https://open-meteo.com/en/docs (weather_code)
function describeWeatherCode(code: number): {
  scene: WeatherScene
  description: string
} {
  if (code === 0) return { scene: 'clear', description: 'Clear skies' }
  if (code <= 3) return { scene: 'cloudy', description: 'Partly cloudy' }
  if (code === 45 || code === 48)
    return { scene: 'cloudy', description: 'Hazy' }
  if (code >= 51 && code <= 67)
    return { scene: 'rain', description: 'Light rain' }
  if (code >= 80 && code <= 82) return { scene: 'rain', description: 'Showers' }
  if (code >= 95) return { scene: 'storm', description: 'Thunderstorms' }
  return { scene: 'cloudy', description: 'Overcast' }
}

async function fetchWeather(): Promise<WeatherNow> {
  const params = new URLSearchParams({
    latitude: String(LATITUDE),
    longitude: String(LONGITUDE),
    current: 'temperature_2m,weather_code,is_day',
    timezone: 'Asia/Singapore',
  })
  const response = await fetch(
    `https://api.open-meteo.com/v1/forecast?${params}`,
  )
  if (!response.ok)
    throw new Error(`Weather request failed: ${response.status}`)
  const data = await response.json()
  const { scene, description } = describeWeatherCode(data.current.weather_code)
  return {
    tempC: Math.round(data.current.temperature_2m),
    isDay: data.current.is_day === 1,
    scene,
    description,
  }
}

export function useWeather() {
  return useQuery({
    queryKey: ['weather'],
    queryFn: fetchWeather,
    staleTime: 10 * 60 * 1000,
    refetchInterval: 10 * 60 * 1000,
  })
}
