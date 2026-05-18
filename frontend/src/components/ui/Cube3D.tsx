import './cube3d.css';

export function Cube3D() {
  return (
    <div className="cube-container">
      <div className="cube-wrapper">
        <div className="cube">
          <div className="cube-face front" />
          <div className="cube-face back" />
          <div className="cube-face right" />
          <div className="cube-face left" />
          <div className="cube-face top" />
          <div className="cube-face bottom" />
        </div>
      </div>
    </div>
  );
}
