"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Search, ShoppingBag, UserRound, Heart, Menu, X, Globe2 } from "lucide-react";
import SearchOverlay from "@/components/SearchOverlay";
import BagDrawer from "@/components/BagDrawer";
import { useBag } from "@/components/BagProvider";
export default function SiteHeader(){
 const [scrolled,setScrolled]=useState(false),[search,setSearch]=useState(false),[bag,setBag]=useState(false),[mobile,setMobile]=useState(false);
 const {count}=useBag();
 useEffect(()=>{const f=()=>setScrolled(window.scrollY>24);f();window.addEventListener("scroll",f,{passive:true});return()=>window.removeEventListener("scroll",f)},[]);
 useEffect(()=>{const f=(e:KeyboardEvent)=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==="k"){e.preventDefault();setSearch(true)}};window.addEventListener("keydown",f);return()=>window.removeEventListener("keydown",f)},[]);
 return <><div className="utility"><span>THE EVU EDITION — CONTEMPORARY WARDROBE</span><span><Globe2 size={12}/> Bangladesh · BDT</span></div><header className={`site-header ${scrolled?"is-scrolled":""}`}><div className="header-inner"><button className="icon-btn mobile-toggle" aria-label="Toggle menu" onClick={()=>setMobile(!mobile)}>{mobile?<X/>:<Menu/>}</button><Link className="wordmark" href="/" aria-label="EVU home">EVU<span>•</span></Link><nav className={mobile?"nav-links mobile-open":"nav-links"} aria-label="Main navigation"><Link onClick={()=>setMobile(false)} href="/shop">SHOP ALL</Link><Link onClick={()=>setMobile(false)} href="/shop?edit=new">NEW ARRIVALS</Link><Link onClick={()=>setMobile(false)} href="/editorial">THE JOURNAL</Link><Link onClick={()=>setMobile(false)} href="/about">OUR HOUSE</Link></nav><div className="header-actions"><button className="icon-btn search-action" aria-label="Search products" onClick={()=>setSearch(true)}><Search size={19}/></button><Link className="icon-btn" aria-label="Wishlist" href="/wishlist"><Heart size={19}/></Link><Link className="icon-btn" aria-label="Account" href="/account"><UserRound size={19}/></Link><button className="icon-btn bag-trigger" aria-label={`Shopping bag, ${count} items`} onClick={()=>setBag(true)}><ShoppingBag size={19}/><span className="bag-count">{count}</span></button></div></div></header><SearchOverlay open={search} onClose={()=>setSearch(false)}/><BagDrawer open={bag} onClose={()=>setBag(false)}/></>;
}
