import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@utils/network'
import styles from '@styles/Main.module.css'

const BoardMain = () => {
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSend = async () => {
    if(!message.trim()) return
    setLoading(true)
    try {
      // AI Agent(ai-agent.py)가 메시지를 분석하여 CREATE, UPDATE, DELETE를 판단.
      const res = await api.post('/api/chat', { message })
      if (res.data.redirect) {
        navigate(res.data.redirect)
      } else {
        navigate('/list')
      }
    } catch (error) {
      alert("에이전트 통신 중 오류가 발생했습니다.")
    } finally {
      setLoading(false)
      setMessage('')
    }
  }

  return (
    <div className={styles.container}>
    <h1 className={styles.title}>オネガイ Agent</h1>
    <br /><br /><br /><br /><br /><br />
    <div className={styles.inputWrapper}>
      <input 
        className={styles.input}
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="등록, 수정, 삭제 요청을 입력하세요..."
        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
      />
      <button className={styles.sendButton} onClick={handleSend} disabled={loading}>
        {loading ? '...' : '↑'}
      </button>
    </div>
  </div>
  )
}
export default BoardMain