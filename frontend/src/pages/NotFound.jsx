import notFoundGif from "@images/404.gif"

const NotFound = () => {
  return (
    <div className="info text-center">
      <img src={notFoundGif} alt="페이지를 찾을 수 없습니다." title="404 ERROR" />
    </div>
  )
}

export default NotFound