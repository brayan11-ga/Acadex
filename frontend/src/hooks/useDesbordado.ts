import { useEffect, useRef, useState } from "react";

export function useDesbordado<T extends HTMLElement>(dep?:unknown){
    const ref = useRef<T>(null);
    const [desborda, setDesborda]=useState(false);

    useEffect(()=>{
        const el = ref.current;
        if (!el) return;
        const medir =()=> setDesborda(el.scrollWidth> el.clientWidth + 1);
        medir();
        const ro = new ResizeObserver(medir);
        ro.observe(el);
        return ()=> ro.disconnect();
    },[dep]);

    return [ref, desborda] as const;
}