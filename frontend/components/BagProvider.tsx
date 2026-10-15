"use client";
import {createContext,useContext,useEffect,useState,useCallback} from "react";
import {api,CartItem} from "@/lib/client-api";
type BagContext={items:CartItem[];count:number;loading:boolean;refresh:()=>Promise<void>;};
const Context=createContext<BagContext>({items:[],count:0,loading:false,refresh:async()=>{}});
export function BagProvider({children}:{children:React.ReactNode}){const [items,setItems]=useState<CartItem[]>([]),[loading,setLoading]=useState(false);const refresh=useCallback(async()=>{setLoading(true);try{const d=await api<{items:CartItem[]}>("commerce/cart/");setItems(d.items||[])}catch{setItems([])}finally{setLoading(false)}},[]);useEffect(()=>{void refresh();const f=()=>void refresh();window.addEventListener("evu:bag-updated",f);return()=>window.removeEventListener("evu:bag-updated",f)},[refresh]);return <Context.Provider value={{items,count:items.reduce((n,x)=>n+x.quantity,0),loading,refresh}}>{children}</Context.Provider>}
export const useBag=()=>useContext(Context);
export const notifyBag=()=>{if(typeof window!=="undefined")window.dispatchEvent(new Event("evu:bag-updated"))};
