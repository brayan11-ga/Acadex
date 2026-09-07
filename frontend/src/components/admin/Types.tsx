export interface ColumnConfig<T> {
    key: keyof T;
    label: string;
    render?: (row: T) => React.ReactNode;
}

export interface FieldConfig {
    name: string;
    label: string;
    type: 'text' | 'email' | 'number' | 'select' | 'checkbox' | 'date' | 'datetime-local' | 'textarea';
    options?: string[];
    optionsSource?:string;
    optionLabelKey?: string;
    optionValueKey?:string;
    min?:number;
    max?:number;
    required?: boolean;
}