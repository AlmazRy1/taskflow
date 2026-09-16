import { useEffect, useState } from 'react'
import { Task, listTasks, createTask, toggleTask, deleteTask } from './api'

const statusLabel: Record<number,string> = {1:'TODO',2:'IN PROGRESS',3:'DONE'}
const priorityLabel: Record<number,string> = {1:'LOW',2:'MEDIUM',3:'HIGH'}

export default function App(){
  const [tasks, setTasks] = useState<Task[]>([])
  const [title, setTitle] = useState('')
  const [desc, setDesc] = useState('')
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<number>(0)

  const refresh = async () => {
    try { setTasks(await listTasks()) } finally { setLoading(false) }
  }
  useEffect(()=>{ refresh() }, [])

  const onCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if(!title.trim()) return
    const t = await createTask({title, description:desc, status:1, priority:2})
    setTasks(prev=>[t, ...prev])
    setTitle(''); setDesc('')
  }

  const filtered = tasks.filter(t => filter===0 || t.status===filter)

  return (
    <div style={{maxWidth:900, margin:'0 auto', padding:'32px 16px'}}>
      <h1 style={{fontSize:32, fontWeight:800, letterSpacing:-1}}>TaskFlow <span style={{color:'#888', fontWeight:400, fontSize:16}}>gRPC + SQLAlchemy + React + moon</span></h1>
      <p style={{color:'#888'}}>Бэкенд: Python gRPC на :50051, HTTP-bridge :8000. Фронт: React через HTTP bridge (в проде замени на grpc-web).</p>

      <form onSubmit={onCreate} className="card" style={{display:'flex', gap:12, marginTop:24, flexDirection:'column'}}>
        <div style={{display:'flex', gap:12}}>
          <input className="input" placeholder="Новая задача... напр. Сделать демо" value={title} onChange={e=>setTitle(e.target.value)} />
          <button className="btn" type="submit">Добавить</button>
        </div>
        <input className="input" placeholder="Описание (опционально)" value={desc} onChange={e=>setDesc(e.target.value)} />
      </form>

      <div style={{display:'flex', gap:8, marginTop:20}}>
        {[0,1,2,3].map(s => (
          <button key={s} onClick={()=>setFilter(s)} className="btn" style={{background: filter===s ? '#fff':'#222', color: filter===s ? '#000':'#fff'}}>{s===0 ? 'ALL' : statusLabel[s]}</button>
        ))}
        <button onClick={refresh} className="btn" style={{marginLeft:'auto', background:'#222', color:'#fff'}}>↻ Обновить</button>
      </div>

      {loading ? <p>Загрузка...</p> : (
        <div style={{display:'grid', gap:12, marginTop:16}}>
          {filtered.map(t=>(
            <div key={t.id} className="card" style={{display:'flex', justifyContent:'space-between', opacity: t.completed ? .6 : 1}}>
              <div>
                <div style={{display:'flex', gap:8, alignItems:'center'}}>
                  <input type="checkbox" checked={t.completed} onChange={async ()=>{ await toggleTask(t.id); refresh() }} />
                  <strong style={{textDecoration: t.completed ? 'line-through': 'none'}}>{t.title}</strong>
                  <span className="badge">{statusLabel[t.status] || t.status}</span>
                  <span className="badge" style={{borderColor: t.priority===3 ? '#f55':'#333'}}>{priorityLabel[t.priority]}</span>
                </div>
                {t.description && <div style={{color:'#888', marginTop:6, fontSize:14}}>{t.description}</div>}
              </div>
              <button onClick={async ()=>{ await deleteTask(t.id); setTasks(prev=>prev.filter(x=>x.id!==t.id)) }} style={{background:'transparent', border:0, color:'#666', cursor:'pointer'}}>✕</button>
            </div>
          ))}
          {filtered.length===0 && <div className="card" style={{textAlign:'center', color:'#666'}}>Задач нет. Создай первую!</div>}
        </div>
      )}

      <div className="card" style={{marginTop:32, fontSize:12, color:'#666'}}>
        <b>Как это работает:</b> proto/tasks.proto → Python gRPC server (SQLAlchemy) → FastAPI bridge /api → React (TypeScript). Тесты: pytest для бэка, vitest для фронта. Запуск через moonrepo.
      </div>
    </div>
  )
}
