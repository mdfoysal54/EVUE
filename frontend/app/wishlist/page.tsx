"use client";
import {useEffect,useState} from "react";
import Link from "next/link";
import type {Product} from "@/lib/catalog";
import ProductCard from "@/components/ProductCard";
export default function Wishlist(){const [products,setProducts]=useState<Product[]>([]),[ids,setIds]=useState<string[]>([]);useEffect(()=>{const f=()=>{try{setIds(JSON.parse(localStorage.getItem("evu_wishlist_v1")||"[]"))}catch{setIds([])}};f();window.addEventListener("evu:wishlist",f);fetch("/api/catalog").then(r=>r.json()).then(setProducts).catch(()=>{});return()=>window.removeEventListener("evu:wishlist",f)},[]);const saved=products.filter(p=>ids.includes(p.id));return <main className="shop-page"><div className="shop-heading"><span className="eyebrow">YOUR PERSONAL EDIT</span><h1>Saved <em>pieces.</em></h1></div>{saved.length?<div className="editorial-grid">{saved.map((p,i)=><ProductCard key={p.id} product={p} index={i}/>)}</div>:<div className="empty-state"><h3>Nothing saved yet.</h3><p>Tap the heart on a product to keep it here on this device.</p><Link className="dark-button" href="/shop">EXPLORE COLLECTION ↗</Link></div>}</main>}
