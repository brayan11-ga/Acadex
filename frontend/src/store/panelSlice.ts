// src/store/panelSlice.ts
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { obtenerDatosPanel, type DatosPanel } from "../services/panelService";

interface PanelState {
  data: DatosPanel | null;
  loading: boolean;
  error: string | null;
}

const initialState: PanelState = {
  data: null,
  loading: false,
  error: null,
};

export const fetchPanelData = createAsyncThunk(
  "panel/fetchPanelData",
  async (_, { rejectWithValue }) => {
    try {
      const response = await obtenerDatosPanel();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || "Error al cargar la información del panel.");
    }
  }
);

const panelSlice = createSlice({
  name: "panel",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchPanelData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPanelData.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchPanelData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export default panelSlice.reducer;