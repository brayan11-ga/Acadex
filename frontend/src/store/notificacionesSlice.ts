// src/store/notificacionesSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit'; // <-- Añade 'type' aquí
import { apiFetch } from '../services/api';

export interface Notificacion {
  id_notificacion: number;
  titulo: string;
  detalles: string;
  fecha_envio: string;
  estado: boolean;
  tipo: string;
}

interface NotificacionesState {
  lista: Notificacion[];
  cargando: boolean;
  error: string | null;
}

const initialState: NotificacionesState = {
  lista: [],
  cargando: false,
  error: null,
};

export const obtenerNotificaciones = createAsyncThunk(
  'notificaciones/obtenerNotificaciones',
  async () => {
    const data = await apiFetch<Notificacion[]>('/notificaciones/');
    return data;
  }
);

export const notificacionesSlice = createSlice({
  name: 'notificaciones',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(obtenerNotificaciones.pending, (state) => {
        state.cargando = true;
        state.error = null;
      })
      .addCase(obtenerNotificaciones.fulfilled, (state, action: PayloadAction<Notificacion[]>) => {
        state.cargando = false;
        state.lista = action.payload;
      })
      .addCase(obtenerNotificaciones.rejected, (state, action) => {
        state.cargando = false;
        state.error = action.error.message || 'Error al cargar notificaciones';
      });
  },
});

export default notificacionesSlice.reducer;