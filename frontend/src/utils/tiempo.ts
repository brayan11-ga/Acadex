// utensils/tiempo.ts
export const formatearMinutos=(totalMin:number):string=>{
    const total=Math.round(totalMin);
    const h= Math.floor(total/60);
    const m= total %60;
    if (h === 0) return `${m} min`;
    return m === 0 ? `${h} h`: `${h} h ${m} min`;
}