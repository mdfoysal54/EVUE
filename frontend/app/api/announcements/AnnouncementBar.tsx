"use client";
import {useEffect,useState} from 'react';
import Link from 'next/link';
type Notice={id:number;title:string;cta_url:string;cta_label:string};
export default function AnnouncementBar(){
 const [items,setItems]=useState<Notice[]>([]);
 useEffect(()=>{const controller=new AbortController();
 const load=()=>fetch('/api/announcements?placement=bar',{signal:controller.signal,cache:'no-store'}).then(r=>r.ok?r.json():{results:[]}).then(d=>setItems(d.results||[])).catch(()=>{});
 load();const interval=setInterval(load,60000);return()=>{controller.abort();clearInterval(interval)};
 },[]);
 if(!items.length)return null;
 const n=items[0];
 return <div className="utility" role="status" aria-live="polite" style={{justifyContent:'center'}}>
  {n.cta_url?.startsWith('/')&&!n.cta_url.startsWith('//')?<Link href={n.cta_url}>{n.title} {n.cta_label||'Explore'}</Link>:<span>{n.title}</span>}
 </div>;
}