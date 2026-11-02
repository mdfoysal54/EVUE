"use client";
import {useState} from 'react';
import {ArrowUpRight} from 'lucide-react';
export default function Newsletter(){
 const [email,setEmail]=useState(''),[consent,setConsent]=useState(false),[message,setMessage]=useState(''),[busy,setBusy]=useState(false);
 async function submit(e:React.FormEvent){e.preventDefault();setBusy(true);setMessage('');try{
 const r=await fetch('/api/newsletter/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,consent})});
 const data=await r.json();setMessage(data.message||data.error||'Unable to subscribe');if(r.ok){setEmail('');setConsent(false)}
 }catch{setMessage('Service unavailable')}finally{setBusy(false)}}
 return <form className="newsletter-form" onSubmit={submit}><label htmlFor="newsletter-email">EMAIL ADDRESS</label>
 <div><input id="newsletter-email" type="email" required placeholder="you@example.com" value={email} onChange={e=>setEmail(e.target.value)}/>
 <button disabled={busy||!consent} aria-label="Join EVU Circle"><ArrowUpRight/></button></div>
 <label style={{display:'block',marginTop:12}}><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)}/> I agree to receive EVU marketing emails.</label>
 {message&&<p role="status">{message}</p>}</form>;
}