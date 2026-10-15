"use client";
import {useMemo,useState} from "react";
import ProductCard from "@/components/ProductCard";
import type {Product} from "@/lib/catalog";
export default function CollectionGrid({products}:{products:Product[]}){const [filter,setFilter]=useState("All pieces");const categories=useMemo(()=>["All pieces",...new Set(products.map(p=>p.category).filter(Boolean))].slice(0,7),[products]);const filtered=filter==="All pieces"?products:products.filter(p=>p.category===filter);return <><div className="filter-row" role="group" aria-label="Filter collection">{categories.map(c=><button className={filter===c?"filter-pill selected":"filter-pill"} key={c} onClick={()=>setFilter(c)} aria-pressed={filter===c}>{c}</button>)}</div>{filtered.length?<div className="editorial-grid">{filtered.map((p,i)=><ProductCard key={p.id} product={p} index={i}/>)}</div>:<div className="empty-state"><h3>Coming into focus.</h3><p>Our next collection is being prepared. Please return soon.</p></div>}</>}
