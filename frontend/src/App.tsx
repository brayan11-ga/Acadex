import { ThemeProvider} from "./contexts/ThemeContext";
import { BrowserRouter } from "react-router-dom";
import AppRouter from "./router/AppRouter";

function App() {
  return (
    <ThemeProvider>
    <div className="App">
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </div>
    </ThemeProvider>
  );
}

export default App;