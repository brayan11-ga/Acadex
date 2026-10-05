// authSlice
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { adminApi } from "../services/adminApi";

export interface UsuarioAuth {
    id_ususario: number;
    correo_electronico: string;
    es_admin: boolean;
}

interface AuthState {
    usuario: UsuarioAuth | null;
    loading: boolean;
    error:string | null;
}

const initialState: AuthState={
    usuario:null,
    loading:false,
    error:null,
}

// carga el usuario actual 
export const fetchUsuarioActual=createAsyncThunk(
    "auth/fetchUsuarioActual",
    async (_,{rejectWithValue})=>{
        const usuario=await adminApi.obtenerMe<UsuarioAuth>();
        if (!usuario) return rejectWithValue("No se puede obtener el usuario actual.");
    return usuario;
    }
);

const authSlice=createSlice({
    name:"auth",
    initialState,
    reducers:{
        cerrarSesion:(state)=>{
            state.usuario =null;
            localStorage.removeItem("access_token");
        },
    },
    extraReducers:(builder)=>{
        builder
        .addCase(fetchUsuarioActual.pending,(state)=>{
            state.loading=true;
            state.error=null;
        })
        .addCase (fetchUsuarioActual.fulfilled,(state, action)=>{
            state.loading=false;
            state.usuario=action.payload;
        })
        .addCase(fetchUsuarioActual.rejected,(state, action)=>{
            state.loading=false;
            state.error=action.payload as string;
            state.usuario=null;
        });
    },
});

export const {cerrarSesion}= authSlice.actions;
export default authSlice.reducer;