// src/store/store.ts
import { configureStore } from "@reduxjs/toolkit";
import panelReducer from "./panelSlice";
import authReducer from "./authSlice";
import notificacionesReducer from "./notificacionesSlice";

export const store = configureStore({
  reducer: {
    panel: panelReducer,
    auth: authReducer,
    notificaciones: notificacionesReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;