export type CartItem = { product_id:string; name:string; quantity:number; unit_price:string; currency:string };
export type Order = {id:string;status:string;currency:string;total:string;expires_at:string;items:{name:string;quantity:number;unit_price:string}[]};
function csrfToken(): string { return decodeURIComponent(document.cookie.split("; ").find(x=>x.startsWith("csrftoken="))?.split("=")[1] || ""); }
export async function api<T>(path:string, method:"GET"|"POST"|"DELETE"="GET", body?:unknown):Promise<T> {
  if(method!=="GET" && !csrfToken()) await fetch("/api/proxy/auth/csrf/",{credentials:"same-origin",cache:"no-store"});
  const response = await fetch(`/api/proxy/${path}`, {method,credentials:"same-origin",cache:"no-store",headers:method==="GET"?{}:{"Content-Type":"application/json","X-CSRFToken":csrfToken()},body:method==="GET"?undefined:JSON.stringify(body||{})});
  const data = await response.json();
  if(!response.ok) throw new Error(typeof data.error==="string"?data.error:JSON.stringify(data.error||"Request failed"));
  return data as T;
}
