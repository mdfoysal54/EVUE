"use client";
import {useState} from "react";
import {ArrowUpRight} from "lucide-react";
export default function Newsletter(){const [email,setEmail]=useState(""),[message,setMessage]=useState("");function submit(e:React.FormEvent){e.preventDefault();setMessage("Newsletter registration will be available when subscriptions are connected to the backend.")}return <form className="newsletter-form" onSubmit={submit}><label htmlFor="newsletter-email">EMAIL ADDRESS</label><div><input id="newsletter-email" type="email" required placeholder="you@example.com" value={email} onChange={e=>setEmail(e.target.value)}/><button aria-label="Join EVU Circle"><ArrowUpRight/></button></div>{message&&<p role="status">{message}</p>}</form>}
