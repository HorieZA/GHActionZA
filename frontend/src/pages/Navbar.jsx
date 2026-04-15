import { useNavigate, useLocation } from 'react-router-dom'
import styles from '@styles/Navbar.module.css'

const Navbar = () => {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <nav className={styles.navBar}>
      <div className={styles.navContainer}>
        <button 
          className={`${styles.navButton} ${location.pathname === '/' ? styles.active : ''}`}
          onClick={() => navigate('/')}>
            オネガイ Agent
        </button>
        <button 
          className={`${styles.navButton} ${location.pathname === '/list' ? styles.active : ''}`}
          onClick={() => navigate('/list')}>
            オネガイ Agent 목록
        </button>
      </div>
    </nav>
  )
}

export default Navbar