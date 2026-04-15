import { Routes, Route } from 'react-router-dom'
import BoardList from '@pages/BoardList'
import BoardMain from '@pages/BoardMain'
import BoardView from '@pages/BoardView'
import Navbar from '@pages/Navbar'
import NotFound from '@pages/NotFound.jsx'

function App() {
  const paths = [
    {path: "/", element: <BoardMain />},
    {path: "/list", element: <BoardList />},
    {path: "/view/:id", element: <BoardView />},
    {path: "*", element: <NotFound />},
  ]
  return (
    <>
      <Navbar />
      <Routes>
        { paths?.map((v, i) => <Route key={i} path={v.path} element={v.element} />) }
      </Routes>
    </>
  )
}

export default App