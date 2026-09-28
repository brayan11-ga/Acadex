// src/store/store.ts
import { configureStore } from "@reduxjs/toolkit";
import panelReducer from "./panelSlice";
import authReducer from "./authSlice";

export const store = configureStore({
  reducer: {
    panel: panelReducer,
    auth:authReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;