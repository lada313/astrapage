import React, { useEffect, useState } from "react"

export default function LeadsPage(){
  const [health, setHealth] = useState(null)

  useEffect(()=>{
    fetch("http://localhost:8000/api/health").then(r=>r.json()).then(setHealth).catch(()=>setHealth({ok:false}))
  },[])

  return (
    <div style={{padding:20,fontFamily:"sans-serif"}}>
      <h1>CRM Shop</h1>
      <p>API health: {health ? JSON.stringify(health) : "..."}</p>
      <p>Импорты доступны в API:</p>
      <ul>
        <li>POST /api/v1/import/clients</li>
        <li>POST /api/v1/import/loyalty</li>
        <li>POST /api/v1/import/purchases</li>
      </ul>
      <p>Приоритизация идентификаторов: <b>телефон → client_id → email</b>.</p>
    </div>
  )
}
