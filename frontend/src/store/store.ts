// src/store/store.ts
import { configureStore } from "@reduxjs/toolkit";
import panelReducer from "./panelSlice";
import notificacionesReducer from "./notificacionesSlice";

export const store = configureStore({
  reducer: {
    panel: panelReducer,
    notificaciones: notificacionesReducer
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;