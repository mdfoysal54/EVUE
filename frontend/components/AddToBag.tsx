"use client";
import {useState} from "react";
import Link from "next/link";
import {ShoppingBag} from "lucide-react";
import {api} from "@/lib/client-api";
import {notifyBag} from "@/components/BagProvider";
export default function AddToBag({id}:{id:string}){const [quantity,setQuantity]=useState(1),[status,setStatus]=useState(""),[busy,setBusy]=useState(false);async function add(){setBusy(true);setStatus("");try{await api("commerce/cart/","POST",{product_id:id,quantity});notifyBag();setStatus("Added to your bag.")}catch(e){setStatus(e instanceof Error?e.message:"Could not add item")}finally{setBusy(false)}}return <div className="purchase-controls"><label className="quantity-control">QUANTITY <input aria-label="Quantity" type="number" min="1" max="20" value={quantity} onChange={e=>setQuantity(Math.max(1,Math.min(20,Number(e.target.value)||1)))}/></label><button className="dark-button" disabled={busy} onClick={add}><ShoppingBag size={16}/>{busy?"ADDING...":"ADD TO BAG"}</button><p role="status">{status} {status.toLowerCase().includes("auth")&&<Link href="/account">Sign in</Link>}</p></div>}
