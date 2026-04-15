import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@utils/network'
import styles from '@styles/Board.module.css'

const BoardList = () => {
  const [posts, setPosts] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/api/boards').then(res => setPosts(res.data))
  }, [])

  return (
    <div className={styles.container}>
      <h2 style={{ marginBottom: '30px' }}>オネガイ Agent Feed 목록</h2>
      {posts.map((post) => (
        <div key={post.id} className={styles.card} onClick={() => navigate(`/view/${post.id}`)}>
          <div className={styles.header}>
            <div className={styles.avatar}>
              {post.name ? post.name.charAt(0).toUpperCase() : '?'}
            </div>
            <span style={{ fontWeight: '600' }}>{post.name}</span>
          </div>
          <div>
            <div className={styles.contentTitle}>{post.title}</div>
            <div style={{ color: '#aaa', marginTop: '8px' }}>{post.content}</div>
            <div style={{ color: '#5f6368', fontSize: '12px', marginTop: '12px' }}>
              {new Date(post.reg_date).toLocaleDateString()}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
export default BoardList