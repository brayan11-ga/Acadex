// authSlice
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { adminApi, ApiRequestError } from "../services/adminapi";

export interface UsuarioAuth {
    id_ususario: number;
    correo_electronico: string;
    es_admin: boolean;
}

interface AuthState {
    usuario: UsuarioAuth | null;
    loading: boolean;
    error:string | null;
    errorStatus: number | null;
}

interface AuthFetchError {
    message: string;
    status: number | null;
}

const initialState: AuthState={
    usuario:null,
    loading:false,
    error:null,
    errorStatus:null,
}

// carga el usuario actual 
export const fetchUsuarioActual=createAsyncThunk<
    UsuarioAuth,
    void,
    { rejectValue: AuthFetchError }
>(
    "auth/fetchUsuarioActual",
    async (_,{rejectWithValue})=>{
        try {
            return await adminApi.obtenerMe<UsuarioAuth>();
        } catch (error) {
            const status = error instanceof ApiRequestError ? error.status : null;
            return rejectWithValue({
                status,
                message: status === 401
                    ? "La sesión ya no es válida. Inicia sesión de nuevo."
                    : "No pudimos verificar la sesión. Revisa tu conexión e inténtalo de nuevo.",
            });
        }
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
            state.errorStatus=null;
        })
        .addCase (fetchUsuarioActual.fulfilled,(state, action)=>{
            state.loading=false;
            state.usuario=action.payload;
            state.error=null;
            state.errorStatus=null;
        })
        .addCase(fetchUsuarioActual.rejected,(state, action)=>{
            state.loading=false;
            state.error=action.payload?.message ?? "No pudimos verificar la sesión.";
            state.errorStatus=action.payload?.status ?? null;
            state.usuario=null;
        });
    },
});

export const {cerrarSesion}= authSlice.actions;
export default authSlice.reducer;
