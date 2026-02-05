import { Link } from 'react-router-dom';

const Sidebar = () => {
  return (
    <aside className="sidebar">
      <nav>
        <ul>
          <li>
            <Link to="/">Dashboard</Link>
          </li>
          <li>
            <Link to="/learning">Learning Path</Link>
          </li>
          <li>
            <Link to="/chat">Q&A Assistant</Link>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
