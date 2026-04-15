import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '@utils/network'
import styles from '@styles/Board.module.css'

const BoardView = () => {
  const { id } = useParams()
  const [post, setPost] = useState(null)

  useEffect(() => {
    api.get(`/api/boards/${id}`).then(res => setPost(res.data))
  }, [id])

  if (!post) return <div className={styles.container}>Loading...</div>

  return (
    <div className={styles.container}>
      <h2 style={{ marginBottom: '30px' }}>オネガイ Agent Feed 상세</h2>
      <div className={styles.card} style={{cursor: 'default'}}>
        <div className={styles.header}>
          <div className={styles.avatar}>
            {post.name ? post.name.charAt(0).toUpperCase() : '?'}
          </div>
          <span style={{fontWeight: '600'}}>{post.name}</span>
        </div>
        <h3 className={styles.contentTitle}>{post.title}</h3>
        <p style={{ lineHeight: '1.8', color: '#ccc' }}>{post.content}</p>
      </div>
    </div>
  )
}
export default BoardView