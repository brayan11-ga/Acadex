// src/store/hooks.ts
import { useDispatch, useSelector } from 'react-redux'
import type { RootState, AppDispatch } from '../store/store'

// Usa estos en lugar de los hooks normales de react-redux
export const useAppDispatch = () => useDispatch<AppDispatch>()
export const useAppSelector = <T>(selector: (state: RootState) => T) => useSelector(selector)