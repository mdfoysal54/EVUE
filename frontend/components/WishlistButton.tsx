"use client";
import {useEffect,useState} from "react";
import {Heart} from "lucide-react";
const KEY="evu_wishlist_v1";
function read():string[]{try{return JSON.parse(localStorage.getItem(KEY)||"[]") as string[]}catch{return []}}
export default function WishlistButton({id}:{id:string}){const [saved,setSaved]=useState(false);useEffect(()=>{setSaved(read().includes(id))},[id]);function toggle(){const s=new Set(read());if(s.has(id))s.delete(id);else s.add(id);localStorage.setItem(KEY,JSON.stringify([...s]));setSaved(s.has(id));window.dispatchEvent(new Event("evu:wishlist"))}return <button type="button" className={`wishlist-button ${saved?"active":""}`} aria-label={saved?"Remove from wishlist":"Add to wishlist"} aria-pressed={saved} onClick={toggle}><Heart size={18} fill={saved?"currentColor":"none"}/></button>}
