import axios from 'axios'
import type { TripPlanRequest, TripPlan } from '../types'
const api = axios.create({
  baseURL: '/api',
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})
api.interceptors.request.use(
  config => {
    console.log('发送请求:', config)
    return config
  },
  error => Promise.reject(error)
)
api.interceptors.response.use(
  response => {
    console.log('收到响应:', response)
    return response
  },
  error => {
    console.error('请求失败:', error)
    return Promise.reject(error)
  }
)
export const generateTripPlan = async (request: TripPlanRequest): Promise<TripPlan> => {
  const response = await api.post<TripPlan>('/trip/plan', request)
  return response.data
}
