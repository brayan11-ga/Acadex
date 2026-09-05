import type { ColumnConfig,FieldConfig } from '../components/admin/Types';

export interface Usuarios{
    id_usuario:number;
    correo_electronico:string;
    fecha_registro:string;
    es_admin:boolean; 
}

export interface Categoria{
    id_categoria:number;
    nombre_categoria:string;
}

export interface Grupo {
    id_grupo: number;
    nombre_grupo: string;
    descripcion: string;
    codigo_acceso: string;
    fecha_creacion: string;
}

export interface Tarea {
    id_tarea: number;
    nombre: string;
    descripcion: string;
    fecha_entrega: string;
    estado: string;
    dificultad_estimada: number;
    tiempo_estimado: number;
    prioridad: number | null;
    id_usuario: number | null;
    id_grupo: number | null;
    id_categoria: number;
}

export interface Integrante {
    id_integrante: number;
    rol: string;
    fecha_ingreso: string;
    id_usuario: number;
    id_grupo: number;
}

export interface EntidadConfig<T> {
    clave: string;
    titulo: string;
    columnas: ColumnConfig<T>[];
    campos: FieldConfig[];
    valoresVacios: Record<string, unknown>;
    soloLectura?: boolean;
}

export const usuariosConfig: EntidadConfig<Usuarios> = {
    clave: 'usuarios',
    titulo:'Usuarios',
    columnas:[
        {key:'correo_electronico',label:'Correo'},
        {key:'fecha_registro',label:'Fecha de registro'},
        {key:'es_admin', label:'admin',render:(row)=>(row.es_admin ? 'Si':'No'),},
    ],
    campos:[
        {name:'correo_electronico',label:'Correo electronico',type:'email',required:true},
        {name:'es_admin',label:'¿Es administrador?', type:'checkbox'},
            // 'contrasena' no se expone: se maneja aparte (registro/reset),
    ],
    valoresVacios:{correo_electronico:'',es_admin:false},
};

export const categoriasConfig: EntidadConfig<Categoria> = {
    clave: 'categorias',
    titulo: 'Categorías',
    columnas: [{ key: 'nombre_categoria', label: 'Nombre' }],
    campos: [
    { name: 'nombre_categoria', label: 'Nombre de la categoría', type: 'text', required: true },
    ],

    valoresVacios: { nombre_categoria: '' },
};

export const gruposConfig: EntidadConfig<Grupo> = {
    clave: 'grupos',
    titulo: 'Grupos',
    columnas: [
    { key: 'nombre_grupo', label: 'Nombre' },
    { key: 'codigo_acceso', label: 'Código de acceso' },
    { key: 'fecha_creacion', label: 'Fecha creación' },
    ],

    campos: [
    { name: 'nombre_grupo', label: 'Nombre del grupo', type: 'text', required: true },
    { name: 'descripcion', label: 'Descripción', type: 'textarea', required: false },
    { name: 'codigo_acceso', label: 'Código de acceso', type: 'text', required: true },
    ],

    valoresVacios: { nombre_grupo: '', descripcion: '', codigo_acceso: '' },
};

export const tareasConfig: EntidadConfig<Tarea> = {
    clave: 'tareas',
    titulo: 'Tareas',
    columnas: [
    { key: 'nombre', label: 'Nombre' },
    { key: 'estado', label: 'Estado' },
    { key: 'fecha_entrega', label: 'Fecha entrega' },
    { key: 'dificultad_estimada', label: 'Dificultad' },
    ],

    campos: [
    { name: 'nombre', label: 'Nombre', type: 'text', required: true },
    { name: 'descripcion', label: 'Descripción', type: 'textarea' },
    { name: 'fecha_entrega', label: 'Fecha de entrega', type: 'datetime-local', required: true },
    {name: 'estado',label: 'Estado',type: 'select',options: ['pendiente', 'en_progreso', 'completada'],required: true,},
    {name: 'dificultad_estimada',label: 'Dificultad estimada (1-5)',type: 'number',min: 1,max: 5,required: true,},
    { name: 'tiempo_estimado', label: 'Tiempo estimado (min)', type: 'number', min: 1, required: true },
    { name: 'prioridad', label: 'Prioridad', type: 'number', min: 1, required: false },
    {name: 'id_categoria',label: 'Categoría',type: 'select',optionsSource: 'categorias',optionValueKey: 'id_categoria',optionLabelKey: 'nombre_categoria',required: true,},
    ],

    valoresVacios: {
    nombre: '',
    descripcion: '',
    fecha_entrega: '',
    estado: 'pendiente',
    dificultad_estimada: 1,
    tiempo_estimado: 30,
    prioridad: null,
    id_categoria: '',
    },
};

export const integrantesConfig: EntidadConfig<Integrante> = {
    clave: 'integrantes',
    titulo: 'Integrantes',
    columnas: [
    { key: 'rol', label: 'Rol' },
    { key: 'fecha_ingreso', label: 'Fecha ingreso' },
    { key: 'id_usuario', label: 'ID Usuario' },
    { key: 'id_grupo', label: 'ID Grupo' },
    ],

    campos: [
    {name:'rol',label: 'Rol',type: 'select',options: ['lider', 'miembro'],required: true,},
    {name:'id_usuario',label: 'Usuario',type: 'select',optionsSource: 'usuarios',optionValueKey: 'id_usuario',optionLabelKey: 'correo_electronico',required: true,},
    {name:'id_grupo',label: 'Grupo',type: 'select',optionsSource: 'grupos',optionValueKey: 'id_grupo',optionLabelKey: 'nombre_grupo',required: true,},
    ],
    valoresVacios: { rol: 'miembro', id_usuario: '', id_grupo: '' },
};

export const TABS: EntidadConfig<any>[] = [
    usuariosConfig,
    categoriasConfig,
    gruposConfig,
    tareasConfig,
    integrantesConfig,
];