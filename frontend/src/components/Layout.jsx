import { Link} from "react-router-dom";
import PropTypes from "prop-types";

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen">
      <header className="container mx-auto px-4 py-6 flex items-center justify-center gap-4">
        <Link to="/" className="no-underline">
          <h1 className="text-3xl font-black text-gray-700 uppercase tracking-wider m-0">
            AI Canadian Benefit Assistant
          </h1>
        </Link>
      </header>
      <main className="mx-auto px-4 w-full">
        {children}
      </main>
    </div>
  );
};

Layout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default Layout;
