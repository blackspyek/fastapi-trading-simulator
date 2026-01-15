import { AuthProvider } from "./context/AuthContext";
import { Router } from "./Router";
import "./index.css";

function App() {
  return (
    <AuthProvider>
      <Router />
    </AuthProvider>
  );
}

export default App;
